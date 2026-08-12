"""Automated quality assurance for the CNV GIS pipeline.

Run with:  python -m pytest

Checks CRS consistency, geometry validity, identifier uniqueness, plausible population
values, containment within the study area, source metadata presence, and — most
importantly — the privacy and terminology constraints the project is bound by.
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from common import DATA_PROCESSED, OUTPUTS, load_study_area  # noqa: E402

CFG = load_study_area()
ANALYSIS_CRS = CFG["crs"]["analysis"]

LAYERS = {
    "cnv_boundary.gpkg": ["cnv_boundary", "cnv_neighbourhoods"],
    "cnv_census_2021.gpkg": ["cnv_census_da"],
    "cnv_housing.gpkg": ["cnv_housing_da"],
    "residential_buildings.gpkg": ["buildings"],
    "cnv_roads.gpkg": ["roads", "intersections"],
    "cnv_transit.gpkg": ["transit_stops"],
    "cnv_parking.gpkg": ["parking_occupancy", "parking_lots"],
    "cnv_traffic.gpkg": ["signalised_intersections"],
    "cnv_elections.gpkg": ["voting_places"],
    "cnv_public_space_scores.gpkg": ["public_space_scores"],
}

METADATA_EXEMPT = {"cnv_census_da"}  # carries its own richer provenance fields


def all_layers():
    for gpkg, layers in LAYERS.items():
        for layer in layers:
            yield gpkg, layer


@pytest.fixture(scope="session")
def census():
    return gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da")


@pytest.fixture(scope="session")
def boundary():
    return gpd.read_file(DATA_PROCESSED / "cnv_boundary.gpkg", layer="cnv_boundary")


@pytest.fixture(scope="session")
def scores():
    return gpd.read_file(DATA_PROCESSED / "cnv_public_space_scores.gpkg",
                         layer="public_space_scores")


# --- structure --------------------------------------------------------------

@pytest.mark.parametrize("gpkg,layer", list(all_layers()))
def test_layer_exists_and_is_non_empty(gpkg, layer):
    path = DATA_PROCESSED / gpkg
    assert path.exists(), f"{gpkg} was not produced"
    gdf = gpd.read_file(path, layer=layer)
    assert len(gdf) > 0, f"{gpkg}:{layer} is empty"


@pytest.mark.parametrize("gpkg,layer", list(all_layers()))
def test_crs_is_the_analysis_crs(gpkg, layer):
    gdf = gpd.read_file(DATA_PROCESSED / gpkg, layer=layer)
    assert gdf.crs is not None, f"{gpkg}:{layer} has no CRS"
    assert gdf.crs.to_epsg() == int(ANALYSIS_CRS.split(":")[1]), (
        f"{gpkg}:{layer} is {gdf.crs.to_epsg()}, expected {ANALYSIS_CRS}")


@pytest.mark.parametrize("gpkg,layer", list(all_layers()))
def test_geometries_are_valid_and_present(gpkg, layer):
    gdf = gpd.read_file(DATA_PROCESSED / gpkg, layer=layer)
    assert gdf.geometry.notna().all(), f"{gpkg}:{layer} has null geometry"
    assert not gdf.geometry.is_empty.any(), f"{gpkg}:{layer} has empty geometry"
    assert gdf.geometry.is_valid.all(), f"{gpkg}:{layer} has invalid geometry"


@pytest.mark.parametrize("gpkg,layer", list(all_layers()))
def test_source_metadata_present(gpkg, layer):
    if layer in METADATA_EXEMPT:
        return
    gdf = gpd.read_file(DATA_PROCESSED / gpkg, layer=layer)
    assert "source" in gdf.columns, f"{gpkg}:{layer} has no 'source' column"
    assert gdf["source"].notna().all(), f"{gpkg}:{layer} has rows without a source"


# --- identifiers ------------------------------------------------------------

def test_dauids_are_unique(census):
    assert census["DAUID"].is_unique
    assert len(census) == 79


def test_intersection_ids_are_unique():
    inter = gpd.read_file(DATA_PROCESSED / "cnv_roads.gpkg", layer="intersections")
    assert inter["intersection_id"].is_unique


def test_no_duplicate_intersection_geometries():
    inter = gpd.read_file(DATA_PROCESSED / "cnv_roads.gpkg", layer="intersections")
    coords = inter.geometry.apply(lambda g: (round(g.x, 1), round(g.y, 1)))
    assert coords.is_unique, "two intersections share the same location"


def test_no_duplicate_buildings():
    b = gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg", layer="buildings")
    assert b["building_id"].is_unique


# --- population plausibility ------------------------------------------------

def test_population_reconciles_with_published_csd_total(census):
    total = census["population_2021"].sum()
    assert abs(total - 58120) / 58120 < 0.02, (
        f"DA population sum {total} deviates from the published CSD total 58,120")


def test_no_impossible_population_values(census):
    assert (census["population_2021"] >= 0).all()
    assert (census["adult_population_18plus_proxy"] >= 0).all()
    assert (census["adult_population_18plus_proxy"]
            <= census["population_2021"] + 1e-6).all(), "18+ exceeds total population"
    assert (census["senior_population_65plus"]
            <= census["adult_population_18plus_proxy"] + 1e-6).all()
    assert (census["senior_population_85plus"]
            <= census["senior_population_65plus"] + 1e-6).all()


def test_densities_use_land_area_not_legal_boundary(census, boundary):
    """Densities must divide by StatCan land area, not the water-inclusive legal area."""
    land = census["land_area_km2"].sum()
    legal = boundary.geometry.area.sum() / 1e6
    assert 11.0 < land < 12.5, f"land area {land} is not the expected ~11.8 km2"
    assert legal > land, "legal boundary should exceed land area (it includes foreshore)"
    recomputed = census["population_2021"] / census["land_area_km2"]
    assert (recomputed - census["population_density"]).abs().max() < 1.0


def test_dwelling_structure_types_sum_to_total(census):
    parts = census[["dw_single_detached", "dw_semi_detached", "dw_row_house",
                    "dw_apartment_duplex", "dw_apartment_lt5_storeys",
                    "dw_apartment_5plus_storeys", "dw_other_single_attached",
                    "dw_movable"]].sum(axis=1, min_count=1)
    diff = (parts - census["dwellings_by_structure_total"]).abs()
    # Statistics Canada random rounding to 5 permits small per-DA discrepancies.
    assert diff.max() <= 15, f"dwelling components diverge from the total by {diff.max()}"


# --- spatial containment ----------------------------------------------------

def test_all_das_are_inside_the_municipality(census, boundary):
    outside = census[~census.geometry.representative_point().within(
        boundary.geometry.union_all().buffer(50))]
    assert len(outside) == 0, f"{len(outside)} DAs fall outside the CNV boundary"


def test_intersections_are_inside_the_municipality(boundary):
    inter = gpd.read_file(DATA_PROCESSED / "cnv_roads.gpkg", layer="intersections")
    outside = inter[~inter.geometry.within(boundary.geometry.union_all().buffer(1))]
    assert len(outside) == 0, f"{len(outside)} intersections fall outside CNV"


def test_voting_places_are_inside_the_municipality(boundary):
    vp = gpd.read_file(DATA_PROCESSED / "cnv_elections.gpkg", layer="voting_places")
    assert vp["inside_cnv_boundary"].all()


def test_study_area_is_the_city_not_the_district(boundary):
    name = boundary.iloc[0]["ADMIN_AREA_NAME"]
    assert name == "City of North Vancouver"
    assert "District" not in name


# --- privacy and terminology (project-critical) -----------------------------

FORBIDDEN = [f.lower() for f in CFG["privacy"]["forbidden_field_names"]]


@pytest.mark.parametrize("gpkg,layer", list(all_layers()))
def test_no_forbidden_field_names_in_any_layer(gpkg, layer):
    gdf = gpd.read_file(DATA_PROCESSED / gpkg, layer=layer)
    bad = [c for c in gdf.columns if c.lower() in FORBIDDEN]
    assert not bad, f"{gpkg}:{layer} contains forbidden field(s): {bad}"


def test_no_csv_output_uses_the_term_eligible_voters():
    offenders = []
    for csv in (OUTPUTS / "tables").glob("*.csv"):
        head = pd.read_csv(csv, nrows=0)
        if any("eligible_voter" in c.lower() for c in head.columns):
            offenders.append(csv.name)
    assert not offenders, f"'eligible_voters' used as a column in: {offenders}"


def test_adult_proxy_field_is_correctly_named(census):
    assert "adult_population_18plus_proxy" in census.columns
    assert "eligible_voters" not in census.columns


def test_adult_proxy_carries_its_disclaimer(census):
    assert "adult_proxy_disclaimer" in census.columns
    text = str(census["adult_proxy_disclaimer"].iloc[0]).lower()
    assert "not a count of eligible" in text


def test_public_space_score_contains_no_political_variable(scores):
    banned = ("party", "vote_share", "candidate", "political", "affiliation",
              "partisan", "support")
    cols = [c.lower() for c in scores.columns]
    for term in banned:
        hits = [c for c in cols
                if term in c and not c.startswith("political_neutrality")]
        assert not hits, f"public-space score contains political field(s): {hits}"


def test_public_space_score_declares_neutrality(scores):
    assert "political_neutrality_statement" in scores.columns
    assert scores["political_neutrality_statement"].notna().all()


# --- data integrity of derived measures -------------------------------------

def test_missing_collision_data_is_not_treated_as_zero(scores):
    """Intersections with no ICBC match must be NaN, never a safe score of zero."""
    unmatched = scores[~scores["collision_data_available"].fillna(False).astype(bool)]
    assert unmatched["collision_count"].isna().all(), (
        "unmatched intersections were scored as having zero collisions")
    assert unmatched["safety_score"].isna().all(), (
        "unmatched intersections received a safety score they cannot support")


def test_score_components_are_within_range(scores):
    for col in ("traffic_score", "transit_score", "pedestrian_proxy_score",
                "parking_access_score", "safety_score", "visibility_score",
                "public_space_composite"):
        if col in scores.columns:
            v = scores[col].dropna()
            assert v.between(0, 100).all(), f"{col} has values outside 0-100"


def test_signal_timing_is_never_estimated():
    sig = gpd.read_file(DATA_PROCESSED / "cnv_traffic.gpkg",
                        layer="signalised_intersections")
    assert (sig["signal_timing_status"] == "REQUEST_REQUIRED").all()
    numeric_timing = [c for c in sig.columns
                      if any(t in c.lower() for t in ("cycle_length", "phase_split",
                                                      "walk_interval"))]
    assert not numeric_timing, f"signal timing values must not be invented: {numeric_timing}"


def test_parking_occupancy_declares_it_is_not_real_time():
    occ = gpd.read_file(DATA_PROCESSED / "cnv_parking.gpkg", layer="parking_occupancy")
    assert "data_nature" in occ.columns
    assert "NOT a real-time" in str(occ["data_nature"].iloc[0])
    assert "survey_period" in occ.columns


def test_transit_frequency_is_present_and_plausible():
    stops = gpd.read_file(DATA_PROCESSED / "cnv_transit.gpkg", layer="transit_stops")
    assert (stops["trips_per_weekday"] >= 0).all()
    assert stops["trips_per_weekday"].max() < 2000, "implausible departures per stop"
    assert stops["trips_per_weekday"].sum() > 1000


# --- outputs ----------------------------------------------------------------

REQUIRED_TABLES = [
    "neighbourhood_rankings.csv", "census_area_rankings.csv", "housing_rankings.csv",
    "polling_location_summary.csv", "traffic_intersection_summary.csv",
    "transit_intersection_summary.csv", "parking_intersection_summary.csv",
    "safety_intersection_summary.csv", "public_space_summary.csv",
    "data_inventory.csv", "data_gaps.csv",
]


@pytest.mark.parametrize("name", REQUIRED_TABLES)
def test_required_table_exists_and_has_rows(name):
    path = OUTPUTS / "tables" / name
    assert path.exists(), f"{name} was not produced"
    assert len(pd.read_csv(path)) > 0, f"{name} is empty"


@pytest.mark.parametrize("name", [t for t in REQUIRED_TABLES
                                  if t.endswith("rankings.csv") or "summary" in t])
def test_ranking_tables_carry_provenance(name):
    df = pd.read_csv(OUTPUTS / "tables" / name)
    for col in ("rank", "source", "methodology_note"):
        assert col in df.columns, f"{name} lacks a '{col}' column"


def test_data_inventory_records_every_source_status():
    df = pd.read_csv(OUTPUTS / "tables" / "data_inventory.csv")
    assert len(df) >= 70
    assert df["status"].isin(["ok", "cached", "FAILED"]).all()
    failed = df[df["status"] == "FAILED"]
    assert failed.empty, f"unresolved download failures: {list(failed['source_id'])}"


def test_maps_were_generated():
    pngs = list((OUTPUTS / "maps").glob("*.png"))
    assert len(pngs) >= 13, f"expected at least 13 maps, found {len(pngs)}"


@pytest.mark.parametrize("page", ["index.html", "recommendations.html"])
def test_published_pages_declare_neutrality_and_proxy_status(page):
    """Any page a reader could act on must state the proxy and neutrality caveats."""
    path = OUTPUTS / "interactive" / page
    assert path.exists(), f"{page} was not produced"
    # Collapse whitespace: the assertion is about wording, not line wrapping.
    html = " ".join(path.read_text(encoding="utf-8").lower().split())
    assert "proxy" in html, f"{page} does not mention the proxy caveat"
    assert "no political variable" in html, f"{page} does not state political neutrality"
    assert "demographics to political preference" in html, (
        f"{page} does not rule out demographic-to-preference inference")


def test_recommendations_page_carries_the_legal_caveat():
    """Campaigning near voting places is legally restricted; the page must say so."""
    raw = (OUTPUTS / "interactive" / "recommendations.html").read_text(encoding="utf-8").lower()
    html = " ".join(raw.split())
    assert "voting place" in html and ("restrict" in html or "chief election officer" in html)


def test_recommendations_contain_no_political_field():
    import pandas as pd  # noqa: PLC0415
    df = pd.read_csv(OUTPUTS / "tables" / "campaign_visibility_recommendations.csv")
    banned = ("party", "candidate", "vote_share", "political", "partisan", "affiliation",
              "support", "turnout")
    for col in df.columns:
        low = col.lower()
        if low in ("neutrality", "basis", "legal_note", "reason_text"):
            continue
        assert not any(b in low for b in banned), f"political field in recommendations: {col}"


def test_interactive_data_layers_exist():
    for f in ("intersections.geojson", "recommendations.geojson"):
        assert (OUTPUTS / "interactive" / "data" / f).exists(), f"{f} missing"
