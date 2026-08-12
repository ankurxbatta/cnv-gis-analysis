#!/usr/bin/env python3
"""Build the CNV building layer with a documented classification.

Combines three municipal sources:
  * building footprints (11,834 polygons, geometry + name/status only)
  * high-rise buildings >18 m (height, year built, unit counts, occupancy)
  * affordable housing (tenure, eligibility, operator, total units)

Output: data/processed/residential_buildings.gpkg
  buildings              - all footprints with classification and joined attributes
  residential_buildings  - the residential subset
  seniors_housing        - facilities identified as seniors housing, with provenance

Classification is evidence-based: every feature records WHY it received its class in
`classification_basis`, and anything without evidence stays UNKNOWN rather than being
guessed. Condominium tenure is not inferred from building form.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_PROCESSED,
    clip_to_cnv,
    get_logger,
    load_boundary,
    load_raw_vector,
    load_study_area,
    tag_source,
    utc_now,
)

log = get_logger("06_prepare_buildings")

CLASSES = [
    "SINGLE_FAMILY", "TOWNHOUSE_ROW", "LOW_RISE_APARTMENT", "HIGH_RISE_APARTMENT",
    "MIXED_USE", "SENIORS_RESIDENCE", "INSTITUTIONAL", "OTHER", "UNKNOWN",
]

SENIORS_PATTERNS = re.compile(
    r"senior|elder|care home|long.?term care|assisted living|retirement|"
    r"independent living|manor|lodge",
    re.I,
)
INSTITUTIONAL_PATTERNS = re.compile(
    r"school|church|hospital|library|city hall|recreation|community centre|"
    r"community center|fire hall|police|university|college|arena|museum",
    re.I,
)

# Storey height assumption used only to convert metres to an approximate storey count
# for buildings that publish height but not storeys.
METRES_PER_STOREY = 3.0


SENIORS_ELIGIBILITY = re.compile(r"55\+|65\+|senior", re.I)
NON_RESIDENTIAL_OCCUPANCY = re.compile(r"office|retail|shopping|industrial|warehouse", re.I)


def sval(row, key: str) -> str:
    """Fetch a field as a clean string. Guards against NaN stringifying to 'nan'."""
    v = row.get(key)
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).strip()
    return "" if s.lower() in {"nan", "none", "<na>"} else s


def fnum(row, key):
    v = row.get(key)
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def classify(row) -> tuple[str, str]:
    """Return (classification, basis). Basis records the evidence actually used."""
    name = sval(row, "BUILDING_NAME")
    occupancy = sval(row, "Occupancy")
    ah_type = sval(row, "ah_type")
    ah_elig = sval(row, "ah_eligibility")
    units = fnum(row, "NosUnits")
    ah_units = fnum(row, "ah_total_units")
    height = fnum(row, "BUILDING_Z")

    # 1. Seniors housing - eligibility and occupancy are municipal statements of use.
    if SENIORS_ELIGIBILITY.search(ah_elig):
        return "SENIORS_RESIDENCE", f"affordable-housing eligibility '{ah_elig}'"
    if re.search(r"independent living|assisted living|care", occupancy, re.I):
        return "SENIORS_RESIDENCE", f"occupancy '{occupancy}'"
    # A seniors-sounding building NAME is not evidence. "Manor" and "Lodge" are ordinary
    # apartment-building names in CNV, so name matching alone produced false positives and
    # was removed. Such buildings are flagged for review instead (see seniors_name_candidates).

    # 2. Institutional use.
    if INSTITUTIONAL_PATTERNS.search(" ".join([name, occupancy])):
        return "INSTITUTIONAL", f"name/occupancy matched institutional keyword ('{name or occupancy}')"

    # 3. Occupancy is the strongest published statement of building use.
    if occupancy:
        has_apt = re.search(r"\bapt\b|apartment", occupancy, re.I)
        if has_apt and re.search(r"hi-rise|high rise", occupancy, re.I):
            return "HIGH_RISE_APARTMENT", f"occupancy '{occupancy}'"
        if has_apt and re.search(r"low rise|elevator", occupancy, re.I):
            return "LOW_RISE_APARTMENT", f"occupancy '{occupancy}'"
        if NON_RESIDENTIAL_OCCUPANCY.search(occupancy):
            return "OTHER", f"non-residential occupancy '{occupancy}'"
        if has_apt:
            return "LOW_RISE_APARTMENT", f"occupancy '{occupancy}'"

    # 4. Published height, for buildings in the >18 m layer without a usable occupancy.
    if height is not None and height >= 18:
        storeys = round(height / METRES_PER_STOREY)
        return "HIGH_RISE_APARTMENT", (
            f"CNV high-rise layer, height {height:.1f} m "
            f"(~{storeys} storeys assuming {METRES_PER_STOREY} m/storey)"
        )

    # 5. Unit counts from either attribute source.
    u = units if units is not None else ah_units
    if u is not None:
        src = "high-rise layer" if units is not None else "affordable-housing layer"
        if u >= 5:
            return "LOW_RISE_APARTMENT", f"unit count {u:.0f} ({src})"
        if u >= 2:
            return "TOWNHOUSE_ROW", f"unit count {u:.0f} ({src})"
        return "SINGLE_FAMILY", f"unit count {u:.0f} ({src})"

    if ah_type:
        return "OTHER", f"affordable-housing record, type '{ah_type}', no unit count published"

    return "UNKNOWN", "footprint only: CNV publishes no height, unit count or use for this building"


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    boundary = load_boundary()
    out = DATA_PROCESSED / "residential_buildings.gpkg"

    footprints = load_raw_vector("cnv/cnv_buildings.geojson", crs)
    footprints = clip_to_cnv(footprints, boundary, how="within")
    footprints = footprints[~footprints.geometry.is_empty].copy()
    footprints["building_id"] = range(1, len(footprints) + 1)
    footprints["footprint_area_m2"] = footprints.geometry.area
    log.info("building footprints inside CNV: %d", len(footprints))

    # --- attach high-rise attributes ---------------------------------------
    hr = load_raw_vector("cnv/cnv_highrise_buildings.geojson", crs)
    hr = clip_to_cnv(hr, boundary, how="within")
    hr_cols = [c for c in ["BUILDING_Z", "YearBuilt", "NosUnits", "Occupancy", "CivicAddress",
                           "SUBTYPE_DESCRIPTION", "StrataUnitArea"] if c in hr.columns]
    hr_pts = hr.copy()
    hr_pts["geometry"] = hr.geometry.representative_point()
    hr_pts["hr_record"] = range(len(hr_pts))
    joined = gpd.sjoin(hr_pts[hr_cols + ["hr_record", "geometry"]],
                       footprints[["building_id", "geometry"]],
                       predicate="within", how="inner")
    # Overlapping footprints can catch the same high-rise twice; keep one footprint per record.
    joined = joined.drop_duplicates("hr_record")
    log.info("high-rise records matched to a footprint: %d of %d", len(joined), len(hr))

    hr_attrs = joined.drop(columns=["geometry", "hr_record"]).drop_duplicates("building_id")
    footprints = footprints.merge(hr_attrs.drop(columns=["index_right"], errors="ignore"),
                                  on="building_id", how="left")

    # --- attach affordable-housing attributes -------------------------------
    ah = load_raw_vector("cnv/cnv_affordable_housing.geojson", crs)
    ah = clip_to_cnv(ah, boundary, how="within")
    rename = {"Type": "ah_type", "Tenure_Type": "ah_tenure", "Eligibility": "ah_eligibility",
              "Name": "ah_name", "Operator_Developer": "ah_operator", "Total_Units": "ah_total_units",
              "Address": "ah_address", "Status": "ah_status"}
    ah = ah.rename(columns={k: v for k, v in rename.items() if k in ah.columns})
    ah_cols = [v for v in rename.values() if v in ah.columns]

    ah_pts = ah.copy()
    ah_pts["geometry"] = ah.geometry.representative_point()
    ah_join = gpd.sjoin(ah_pts[ah_cols + ["geometry"]], footprints[["building_id", "geometry"]],
                        predicate="within", how="inner")
    log.info("affordable-housing records matched to a footprint: %d of %d", len(ah_join), len(ah))
    ah_attrs = ah_join.drop(columns="geometry").drop_duplicates("building_id")
    footprints = footprints.merge(ah_attrs.drop(columns=["index_right"], errors="ignore"),
                                  on="building_id", how="left")

    # --- classify -----------------------------------------------------------
    results = footprints.apply(classify, axis=1, result_type="expand")
    footprints["classification"] = results[0]
    footprints["classification_basis"] = results[1]

    footprints["units_known"] = footprints["NosUnits"].notna() if "NosUnits" in footprints else False
    footprints["height_m"] = footprints.get("BUILDING_Z")
    footprints["year_built"] = footprints.get("YearBuilt")

    # Condominium tenure is recorded ONLY where the City's own Occupancy field says
    # 'STRATA'. It is never inferred from building form or height.
    occ = footprints["Occupancy"].astype("string").fillna("") if "Occupancy" in footprints else ""
    footprints["condominium_tenure"] = (
        occ.str.contains("STRATA", case=False, na=False) if len(footprints) else False
    )
    footprints["condominium_basis"] = footprints["condominium_tenure"].map(
        {True: "CNV Occupancy attribute contains 'STRATA'",
         False: "no strata evidence published; tenure unknown, not assumed"}
    )

    footprints = tag_source(
        footprints,
        "City of North Vancouver ArcGIS - building footprints, high-rise buildings, affordable housing",
        "https://gisext2.cnv.org/arcgis/rest/services",
    )
    footprints["classification_note"] = (
        "Classification derives from published CNV attributes only. UNKNOWN means the City "
        "publishes no height, unit count or use for that footprint - it does not mean the "
        "building is non-residential. Condominium tenure is never inferred from building form."
    )
    footprints.to_file(out, layer="buildings", driver="GPKG")

    log.info("-" * 60)
    log.info("classification results:")
    for k, v in footprints["classification"].value_counts().items():
        log.info("    %-22s %6d  (%4.1f%%)", k, v, 100 * v / len(footprints))

    residential = footprints[footprints["classification"].isin(
        ["SINGLE_FAMILY", "TOWNHOUSE_ROW", "LOW_RISE_APARTMENT", "HIGH_RISE_APARTMENT",
         "SENIORS_RESIDENCE", "MIXED_USE"])].copy()
    residential.to_file(out, layer="residential_buildings", driver="GPKG")
    log.info("residential subset: %d buildings", len(residential))

    seniors = footprints[footprints["classification"] == "SENIORS_RESIDENCE"].copy()
    if len(seniors):
        seniors.to_file(out, layer="seniors_housing", driver="GPKG")
        log.info("seniors housing: %d buildings", len(seniors))
        for _, r in seniors.iterrows():
            label = sval(r, "ah_name") or sval(r, "BUILDING_NAME") or sval(r, "ah_address") or "(unnamed)"
            log.info("    %-40s %s", label[:40], r["classification_basis"][:70])
    else:
        log.warning("no seniors residences identified from municipal attributes")

    # Buildings whose NAME merely suggests seniors housing, held separately for review
    # rather than classified. These are candidates, not findings.
    name_hits = footprints[
        footprints["BUILDING_NAME"].astype("string").fillna("").str.contains(
            SENIORS_PATTERNS, na=False)
        & (footprints["classification"] != "SENIORS_RESIDENCE")
    ].copy()
    if len(name_hits):
        name_hits["review_status"] = "UNVERIFIED_NAME_MATCH"
        name_hits["review_note"] = (
            "The building name contains a seniors-suggestive keyword, but no municipal "
            "eligibility or occupancy attribute supports it. NOT classified as seniors "
            "housing. Verify against Vancouver Coastal Health or BC Housing before use."
        )
        name_hits.to_file(out, layer="seniors_name_candidates", driver="GPKG")
        log.info("seniors NAME candidates held for review (not classified): %d", len(name_hits))
        for _, r in name_hits.iterrows():
            log.info("    %s", sval(r, "BUILDING_NAME") or "(unnamed)")

    # Height/unit coverage is a headline limitation - report it explicitly.
    with_height = footprints["height_m"].notna().sum() if "height_m" in footprints else 0
    with_units = footprints["NosUnits"].notna().sum() if "NosUnits" in footprints else 0
    with_year = footprints["year_built"].notna().sum() if "year_built" in footprints else 0
    log.info("-" * 60)
    log.info("attribute coverage across %d footprints:", len(footprints))
    log.info("    height known     %5d (%4.1f%%)", with_height, 100 * with_height / len(footprints))
    log.info("    unit count known %5d (%4.1f%%)", with_units, 100 * with_units / len(footprints))
    log.info("    year built known %5d (%4.1f%%)", with_year, 100 * with_year / len(footprints))
    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
