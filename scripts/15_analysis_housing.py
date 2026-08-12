#!/usr/bin/env python3
"""Housing analysis and rankings at dissemination-area level.

Output: outputs/tables/housing_rankings.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA_PROCESSED, OUTPUTS, get_logger  # noqa: E402

log = get_logger("15_analysis_housing")

SOURCE = "Statistics Canada, 2021 Census Profile 98-401-X2021006, dissemination areas"
METHOD = "Occupied private dwellings by structural type, directly from the Census Profile."


def main() -> int:
    tables = OUTPUTS / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    h = gpd.read_file(DATA_PROCESSED / "cnv_housing.gpkg", layer="cnv_housing_da")
    log.info("housing DAs: %d", len(h))

    metrics = ["housing_density", "multiunit_share", "apartment_share", "highrise_share",
               "townhouse_share", "single_family_share", "one_person_household_share",
               "occupied_private_dwellings", "persons_per_dwelling"]

    rows = []
    for metric in metrics:
        if metric not in h.columns:
            continue
        sub = h[["DAUID", metric, "dominant_dwelling_type"]].dropna(subset=[metric])
        sub = sub.sort_values(metric, ascending=False).reset_index(drop=True)
        for i, r in sub.iterrows():
            rows.append({
                "rank": i + 1,
                "feature_id": r["DAUID"],
                "feature_name": f"DA {r['DAUID']}",
                "metric": metric,
                "value": round(float(r[metric]), 4),
                "dominant_dwelling_type": r["dominant_dwelling_type"],
                "source": SOURCE,
                "methodology_note": METHOD,
            })
    pd.DataFrame(rows).to_csv(tables / "housing_rankings.csv", index=False)
    log.info("wrote housing_rankings.csv (%d rows)", len(rows))

    log.info("-" * 70)
    log.info("Top 10 DAs by housing density (occupied dwellings/km2):")
    for _, r in h.nlargest(10, "housing_density").iterrows():
        log.info("    DA %s %8.0f /km2   apt %4.0f%%   dominant=%s",
                 r["DAUID"], r["housing_density"], 100 * (r["apartment_share"] or 0),
                 r["dominant_dwelling_type"])

    log.info("-" * 70)
    log.info("Top 10 DAs by high-rise (5+ storey apartment) share:")
    for _, r in h.nlargest(10, "highrise_share").iterrows():
        log.info("    DA %s  %5.1f%%  (%.0f of %.0f dwellings)", r["DAUID"],
                 100 * r["highrise_share"], r["dw_apartment_5plus_storeys"],
                 r["dwellings_by_structure_total"])

    b = gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg", layer="buildings")
    log.info("-" * 70)
    log.info("building classification coverage: %d footprints, %d classified beyond UNKNOWN",
             len(b), int((b["classification"] != "UNKNOWN").sum()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
