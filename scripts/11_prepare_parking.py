#!/usr/bin/env python3
"""Prepare CNV parking layers.

The on-street occupancy layer pairs an OCCUPIED COUNT with a published PERCENTAGE for
each surveyed period. Field naming is inconsistent between weekday and weekend blocks, so
this script identifies the numeric count field per period, recomputes occupancy from
count/supply, and validates the result against the published percentage before use.

These are SURVEY OBSERVATIONS, not a real-time availability feed. Nothing here may be
presented as live parking availability.

Output: data/processed/cnv_parking.gpkg
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
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
)

log = get_logger("11_prepare_parking")
CNV_ARCGIS = "https://gisext2.cnv.org/arcgis/rest/services"

# Surveyed periods. Each entry lists the candidate source columns for that period;
# whichever is numeric is the occupied count, whichever is a '%' string is the
# published percentage.
PERIODS = {
    "weekday_0709": ["Weekday_07", "Weekday_08"],
    "weekday_1113": ["Weekday_11", "Weekday_12"],
    "weekday_1618": ["Weekday_16", "Weekday_17"],
    "weekday_2123": ["Weekday_21", "Weekday_22"],
    "weekend_0709": ["Weekend_09", "Weekend_07"],
    "weekend_1113": ["Weekend_11", "Weekend_12"],
    "weekend_1618": ["Weekend_16", "Weekend_17"],
    "weekend_2123": ["Weekend_21", "Weekend_22"],
}


def as_count(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace("%", "", regex=False), errors="coerce")


def is_percent_column(series: pd.Series) -> bool:
    sample = series.dropna().astype(str).head(50)
    return bool(len(sample)) and (sample.str.contains("%").mean() > 0.5)


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    boundary = load_boundary()
    out = DATA_PROCESSED / "cnv_parking.gpkg"

    # --- on-street occupancy survey ----------------------------------------
    occ = load_raw_vector("parking/cnv_parking_occupancy.geojson", crs)
    occ = clip_to_cnv(occ, boundary)
    occ = occ[~occ.geometry.is_empty].copy()
    log.info("on-street parking survey segments inside CNV: %d", len(occ))

    supply = as_count(occ["Supply"])
    occ["supply_spaces"] = supply
    log.info("total surveyed on-street supply: %.0f spaces", supply.sum())

    checks = []
    for period, cols in PERIODS.items():
        present = [c for c in cols if c in occ.columns]
        if len(present) < 2:
            log.warning("period %s: expected 2 columns, found %s", period, present)
            continue
        pct_cols = [c for c in present if is_percent_column(occ[c])]
        cnt_cols = [c for c in present if c not in pct_cols]
        if len(cnt_cols) != 1 or len(pct_cols) != 1:
            log.warning("period %s: could not separate count/percent from %s", period, present)
            continue

        count = as_count(occ[cnt_cols[0]])
        published_pct = as_count(occ[pct_cols[0]]) / 100.0
        recomputed = count / supply.replace(0, np.nan)

        occ[f"occupied_{period}"] = count
        # The City's published percentage is authoritative; the recomputed ratio is kept
        # as a cross-check. They differ slightly on very short segments because Supply is
        # an integer estimate of a capacity that is really continuous.
        occ[f"occupancy_{period}"] = published_pct
        occ[f"occupancy_recomputed_{period}"] = recomputed

        both = recomputed.notna() & published_pct.notna()
        if both.sum():
            diff = (recomputed[both] - published_pct[both]).abs()
            # Allow one vehicle of rounding on the segment's own supply, plus 2 points.
            tol = (1.0 / supply[both].clip(lower=1)) + 0.02
            agree = (diff <= tol).mean()
            checks.append((period, cnt_cols[0], pct_cols[0], both.sum(), 100 * agree, diff.max()))

    log.info("-" * 78)
    log.info("occupancy validation (recomputed count/supply vs the City's published %%,")
    log.info("tolerance = one vehicle on that segment's supply, plus 2 percentage points):")
    log.info("  %-14s %-12s %-12s %6s %8s %8s", "period", "count col", "pct col", "n", "agree%", "maxdiff")
    for period, c, p, n, agree, mx in checks:
        log.info("  %-14s %-12s %-12s %6d %7.1f%% %7.3f", period, c, p, n, agree, mx)
        if agree < 95:
            log.warning("    period %s: only %.1f%% agreement - column pairing may be wrong", period, agree)

    occ_cols = [f"occupancy_{p}" for p in PERIODS if f"occupancy_{p}" in occ.columns]
    if occ_cols:
        occ["occupancy_peak"] = occ[occ_cols].max(axis=1)
        occ["occupancy_mean"] = occ[occ_cols].mean(axis=1)
        occ["peak_period"] = occ[occ_cols].idxmax(axis=1).str.replace("occupancy_", "", regex=False)
        # Segments at or above 85% are conventionally treated as effectively full.
        occ["at_practical_capacity"] = occ["occupancy_peak"] >= 0.85
        occ["over_estimated_supply"] = occ["occupancy_peak"] > 1.0
        log.info("segments where observed parking exceeded the estimated supply at some "
                 "period: %d - Supply is an integer capacity estimate, so values above "
                 "100%% are possible and are retained rather than clipped",
                 int(occ["over_estimated_supply"].sum()))

        log.info("-" * 78)
        log.info("peak occupancy distribution across %d segments:", len(occ))
        for lo, hi in [(0, .5), (.5, .7), (.7, .85), (.85, 1.0), (1.0, 99)]:
            n = ((occ["occupancy_peak"] >= lo) & (occ["occupancy_peak"] < hi)).sum()
            log.info("    %5.0f-%3.0f%%  %4d segments", lo * 100, min(hi, 1) * 100, n)
        log.info("segments at or above 85%% peak occupancy: %d (%.1f%%)",
                 occ["at_practical_capacity"].sum(),
                 100 * occ["at_practical_capacity"].mean())
        busiest = occ["peak_period"].value_counts()
        log.info("most-constrained period by segment count: %s", dict(busiest.head(4)))

    occ = tag_source(occ, "City of North Vancouver ArcGIS - on-street parking occupancy survey",
                     f"{CNV_ARCGIS}/BaseMapServices/TransportMAP/MapServer/55")
    occ["survey_period"] = "2022-12 to 2023-02"
    occ["survey_consultant"] = "Bunt & Associates, for the CNV Curb Access and Parking Plan"
    occ["data_nature"] = (
        "OBSERVED SURVEY COUNTS from a City parking study, aggregated to street segments. "
        "This is NOT a real-time availability feed and must never be presented as live "
        "occupancy. Survey provenance: Curb Access and Parking Plan fieldwork by Bunt & "
        "Associates, conducted December 2022 and January/February 2023."
    )
    occ["occupancy_method"] = (
        "occupancy = occupied vehicles / published Supply, recomputed by this pipeline and "
        "validated against the City's own published percentage for each period."
    )
    occ.to_file(out, layer="parking_occupancy", driver="GPKG")

    # --- other parking layers ----------------------------------------------
    layers = [
        ("parking/cnv_parking_zones.geojson", "parking_restrictions", "Parking Zones / restrictions", 64, "clip"),
        ("parking/cnv_parking_offstreet_lots.geojson", "parking_lots", "Off Street Lots", 62, "within"),
        ("parking/cnv_parking_signs.geojson", "parking_signs", "Parking Signs", 63, "within"),
        ("parking/cnv_loading_zones.geojson", "loading_zones", "Loading Zones", 61, "clip"),
        ("parking/cnv_car_share_parking.geojson", "car_share_parking", "Car Share Parking", 60, "within"),
        ("parking/cnv_accessible_parking.geojson", "accessible_parking", "Accessible parking", 0, "within"),
        ("parking/cnv_pay_stations.geojson", "pay_stations", "Pay Stations", 1, "within"),
        ("parking/cnv_pay_parking_onstreet.geojson", "pay_parking_onstreet", "Pay Parking On Street", 3, "clip"),
        ("parking/cnv_resident_permit_zones.geojson", "resident_permit_zones", "Resident Permit Zones", 1, "clip"),
    ]
    for raw, layer, label, lid, how in layers:
        try:
            g = load_raw_vector(raw, crs)
        except Exception as exc:  # noqa: BLE001
            log.warning("skipping %s: %s", layer, exc)
            continue
        if g.empty:
            log.warning("%s is empty", layer)
            continue
        g = clip_to_cnv(g, boundary, how=how)
        g = g[~g.geometry.is_empty]
        if g.empty:
            log.warning("%s has nothing inside CNV", layer)
            continue
        g = tag_source(g, f"City of North Vancouver ArcGIS - {label}", f"{CNV_ARCGIS}/...")
        g.to_file(out, layer=layer, driver="GPKG")

        extra = ""
        if "SUPPLY" in g.columns:
            extra = f", supply {pd.to_numeric(g['SUPPLY'], errors='coerce').sum():.0f} spaces"
        if "SPACES_WEEKDAY" in g.columns:
            extra = f", {pd.to_numeric(g['SPACES_WEEKDAY'], errors='coerce').sum():.0f} weekday spaces"
        log.info("wrote %-22s %5d features%s", layer, len(g), extra)

    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
