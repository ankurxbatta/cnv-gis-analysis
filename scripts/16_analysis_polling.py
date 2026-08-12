#!/usr/bin/env python3
"""Polling-location analysis: where voting places sit relative to population.

Every voter-related figure here is aggregate. The 18+ measure is a demographic PROXY for
potential electorate size and is never presented as an elector count.

Output: outputs/tables/polling_location_context.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_PROCESSED, OUTPUTS, get_logger, load_study_area,
)

log = get_logger("16_analysis_polling")


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    tables = OUTPUTS / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    places = gpd.read_file(DATA_PROCESSED / "cnv_elections.gpkg", layer="voting_places").to_crs(crs)
    census = gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da").to_crs(crs)
    turnout = pd.read_csv(OUTPUTS / "tables" / "election_turnout_series.csv")

    disclaimer = cfg["privacy"]["adult_population_disclaimer"].strip()

    # Residents and 18+ proxy within walking distances of each voting place.
    da_area = census.geometry.area
    rows = []
    for _, p in places.iterrows():
        rec = {"place_name": p["place_name"], "address": p["address"],
               "place_type": p["place_type"],
               "mayoral_votes_2022": p.get("mayoral_votes_2022")}
        for radius in (400, 800, 1600):
            inter = census.geometry.intersection(p.geometry.buffer(radius))
            frac = (inter.area / da_area).clip(0, 1).fillna(0)
            rec[f"residents_within_{radius}m"] = round(float((census["population_2021"] * frac).sum()))
            rec[f"adult_18plus_proxy_within_{radius}m"] = round(
                float((census["adult_population_18plus_proxy"] * frac).sum()))
            rec[f"seniors_65plus_within_{radius}m"] = round(
                float((census["senior_population_65plus"] * frac).sum()))
        rows.append(rec)

    df = pd.DataFrame(rows).sort_values("residents_within_800m", ascending=False)
    df["source"] = "CNV official election records; Statistics Canada 2021 Census Profile"
    df["methodology_note"] = (
        "Resident counts are areally interpolated from 2021 dissemination areas into "
        "circular buffers and are estimates, not counts."
    )
    df["adult_proxy_disclaimer"] = disclaimer
    df["polling_boundary_status"] = "NOT_AVAILABLE"
    df.to_csv(tables / "polling_location_context.csv", index=False)

    log.info("=" * 78)
    log.info("VOTING PLACES IN CONTEXT (2022)")
    log.info("  %-38s %8s %8s %8s", "place", "res 800m", "18+ 800m", "65+ 800m")
    for _, r in df.iterrows():
        log.info("  %-38s %8.0f %8.0f %8.0f", r["place_name"][:38],
                 r["residents_within_800m"], r["adult_18plus_proxy_within_800m"],
                 r["seniors_65plus_within_800m"])

    log.info("-" * 78)
    log.info("CITY-WIDE ELECTORAL CONTEXT")
    t2022 = turnout[turnout["year"] == 2022].iloc[0]
    adult_proxy = census["adult_population_18plus_proxy"].sum()
    citizens = census["canadian_citizens_18plus"].sum()
    log.info("  registered electors 2022 (official)          %8.0f", t2022["registered_voters"])
    log.info("  turnout 2022 (official)                      %8.2f%%", t2022["turnout_pct"])
    log.info("  adult_population_18plus_proxy (2021 Census)  %8.0f", adult_proxy)
    log.info("  Canadian citizens 18+ (2021 Census)          %8.0f", citizens)
    log.info("")
    log.info("  INTERPRETATION: the 2021 Census counted an estimated %.0f residents aged 18+,",
             adult_proxy)
    log.info("  of whom %.0f were Canadian citizens. CNV recorded %.0f registered electors in",
             citizens, t2022["registered_voters"])
    log.info("  2022. The citizen figure sits within %.1f%% of the registered total, which is a",
             100 * abs(citizens - t2022["registered_voters"]) / t2022["registered_voters"])
    log.info("  useful consistency check - NOT a claim that these measure the same thing.")
    log.info("  %s", disclaimer.replace("\n", " "))

    log.info("-" * 78)
    log.info("turnout trend (last 6 elections):")
    for _, r in turnout.head(6).iterrows():
        bar = "#" * int(r["turnout_pct"])
        log.info("    %d  %5.2f%%  %s", r["year"], r["turnout_pct"], bar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
