#!/usr/bin/env python3
"""Build the portable interactive web map into outputs/interactive/.

Produces a self-contained Leaflet page plus simplified GeoJSON layers. Geometry is
generalised for display only; analysis data is never simplified.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA_PROCESSED, OUTPUTS, get_logger, load_study_area  # noqa: E402
from web_template import INDEX_HTML  # noqa: E402

log = get_logger("19_create_interactive_map")

OUT = OUTPUTS / "interactive"
DATA = OUT / "data"


def export(gdf: gpd.GeoDataFrame, name: str, cols: list[str], tol: float,
           simplify: bool = True) -> dict:
    keep = [c for c in cols if c in gdf.columns]
    g = gdf[keep + ["geometry"]].copy()
    g = g[~g.geometry.is_empty & g.geometry.notna()]
    if simplify and tol:
        g["geometry"] = g.geometry.simplify(tol, preserve_topology=True)
    g = g.to_crs("EPSG:4326")

    # Round coordinates to ~1 m to keep the payload small.
    path = DATA / f"{name}.geojson"
    path.write_text(json.dumps(json.loads(g.to_json()), separators=(",", ":")), encoding="utf-8")
    kb = path.stat().st_size / 1024
    log.info("  %-26s %5d features  %7.0f KB", name, len(g), kb)
    return {"name": name, "features": len(g), "kb": round(kb)}


def main() -> int:
    cfg = load_study_area()
    tol = cfg["analysis"]["web_simplify_tolerance_m"]
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    log.info("exporting web layers (simplify tolerance %.1f m):", tol)

    export(gpd.read_file(DATA_PROCESSED / "cnv_boundary.gpkg", layer="cnv_boundary"),
           "boundary", ["ADMIN_AREA_NAME", "area_km2", "source"], tol)

    export(gpd.read_file(DATA_PROCESSED / "cnv_neighbourhoods_stats.gpkg",
                         layer="cnv_neighbourhoods_stats"),
           "neighbourhoods",
           ["neighbourhood", "population_2021", "adult_population_18plus_proxy",
            "senior_population_65plus", "population_density", "adult_population_density",
            "housing_density", "apartment_share", "occupied_private_dwellings",
            "building_count", "methodology_note"], tol)

    export(gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da"),
           "census_da",
           ["DAUID", "population_2021", "population_density",
            "adult_population_18plus_proxy", "adult_population_density",
            "canadian_citizens_18plus", "citizen_adult_density",
            "age_0_14", "age_18_34_proxy", "age_35_49", "age_50_64",
            "senior_population_65plus", "senior_population_75plus",
            "senior_population_85plus", "senior_density",
            "occupied_private_dwellings", "housing_density", "land_area_km2"], tol)

    export(gpd.read_file(DATA_PROCESSED / "cnv_public_space_scores.gpkg",
                         layer="public_space_scores"),
           "intersections",
           ["intersection_id", "street_names", "neighbourhood", "public_space_composite",
            "composite_rank", "traffic_score", "transit_score", "pedestrian_proxy_score",
            "parking_access_score", "intersection_prominence_score", "safety_score",
            "visibility_score", "signalised", "full_signal", "collision_count",
            "collision_data_available", "transit_stops_250m", "transit_departures_250m",
            "onstreet_supply_250m", "onstreet_peak_occupancy_250m", "population_2021_400m",
            "components_available"], 0, simplify=False)

    export(gpd.read_file(DATA_PROCESSED / "cnv_housing.gpkg", layer="cnv_housing_da"),
           "housing_da",
           ["DAUID", "dominant_dwelling_type", "occupied_private_dwellings",
            "dw_single_detached", "dw_semi_detached", "dw_row_house",
            "dw_apartment_duplex", "dw_apartment_lt5_storeys", "dw_apartment_5plus_storeys",
            "single_family_share", "townhouse_share", "apartment_share", "highrise_share",
            "multiunit_share", "housing_density"], tol)

    export(gpd.read_file(DATA_PROCESSED / "cnv_elections.gpkg", layer="voting_places"),
           "voting_places",
           ["place_name", "address", "place_type", "year", "mayoral_votes_2022",
            "polling_boundary_status"], 0, simplify=False)

    export(gpd.read_file(DATA_PROCESSED / "cnv_roads.gpkg", layer="roads"),
           "roads", ["full_street_name", "ROADCLASS", "NOLANES", "ONEWAY"], tol)

    tr = gpd.read_file(DATA_PROCESSED / "cnv_transit.gpkg", layer="transit_stops")
    export(tr[tr["in_cnv"]] if "in_cnv" in tr else tr, "transit_stops",
           ["stop_name", "stop_id", "trips_per_weekday", "trips_am_peak", "routes_serving",
            "am_peak_avg_headway_min"], 0, simplify=False)

    export(gpd.read_file(DATA_PROCESSED / "cnv_parking.gpkg", layer="parking_occupancy"),
           "parking_occupancy",
           ["supply_spaces", "occupancy_peak", "occupancy_mean", "peak_period",
            "at_practical_capacity"], tol)

    export(gpd.read_file(DATA_PROCESSED / "cnv_parking.gpkg", layer="parking_lots"),
           "parking_lots",
           ["LOT_NAME", "ADDRESS", "Operator", "SPACES_WEEKDAY", "ACCESSIBLE_PARKING_SPACES",
            "PAY_PARKING"], 0, simplify=False)

    export(gpd.read_file(DATA_PROCESSED / "cnv_safety.gpkg", layer="intersection_crashes"),
           "collisions", ["intersection_id", "crash_count", "icbc_locations"], 0, simplify=False)

    try:
        export(gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg",
                             layer="seniors_housing"),
               "seniors_housing",
               ["ah_name", "BUILDING_NAME", "ah_address", "ah_total_units", "ah_eligibility",
                "classification_basis"], 1.0)
    except Exception as exc:  # noqa: BLE001
        log.warning("seniors layer skipped: %s", exc)

    # Headline statistics for the sidebar tiles, computed from the real layers.
    census = gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da")
    scores = gpd.read_file(DATA_PROCESSED / "cnv_public_space_scores.gpkg",
                           layer="public_space_scores")
    stops_all = gpd.read_file(DATA_PROCESSED / "cnv_transit.gpkg", layer="transit_stops")
    occ = gpd.read_file(DATA_PROCESSED / "cnv_parking.gpkg", layer="parking_occupancy")
    in_cnv = stops_all[stops_all["in_cnv"]] if "in_cnv" in stops_all else stops_all

    stats = {
        "population": int(census["population_2021"].sum()),
        "adults": int(census["adult_population_18plus_proxy"].sum()),
        "citizens": int(census["canadian_citizens_18plus"].sum()),
        "seniors": int(census["senior_population_65plus"].sum()),
        "dwellings": int(census["occupied_private_dwellings"].sum()),
        "land_km2": round(float(census["land_area_km2"].sum()), 2),
        "density": int(census["population_2021"].sum() / census["land_area_km2"].sum()),
        "das": int(len(census)),
        "intersections": int(len(scores)),
        "transit_stops": int(len(in_cnv)),
        "departures": int(in_cnv["trips_per_weekday"].sum()),
        "parking_segments": int(len(occ)),
        "parking_spaces": int(occ["supply_spaces"].sum()),
        "multiunit_pct": round(
            100 * census["multiunit_dwellings"].sum()
            / census["dwellings_by_structure_total"].sum(), 1),
    }
    (DATA / "stats.json").write_text(json.dumps(stats), encoding="utf-8")
    log.info("wrote stats.json for the sidebar tiles")

    # Copy CSV tables so the page can offer downloads.
    dl = OUT / "tables"
    dl.mkdir(exist_ok=True)
    for csv in (OUTPUTS / "tables").glob("*.csv"):
        shutil.copy(csv, dl / csv.name)
    log.info("copied %d CSV tables for download", len(list(dl.glob('*.csv'))))

    (OUT / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    log.info("wrote %s", OUT / "index.html")
    log.info("open with: python -m http.server --directory %s", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
