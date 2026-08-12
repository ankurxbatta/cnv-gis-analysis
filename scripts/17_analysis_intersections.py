#!/usr/bin/env python3
"""Compute the neutral public-space suitability score for CNV intersections.

Every component is kept separate and carries its own coverage flag. The composite is an
unweighted mean of components and is explicitly a convenience summary.

No political variable of any kind enters this calculation - see config/scoring.yaml.

Outputs:
  data/processed/cnv_public_space_scores.gpkg
  outputs/tables/public_space_summary.csv
  outputs/tables/{traffic,transit,parking,safety}_intersection_summary.csv
  outputs/tables/field_audit_checklist.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    CONFIG_DIR,
    DATA_PROCESSED,
    OUTPUTS,
    get_logger,
    load_yaml,
    utc_now,
)

log = get_logger("17_analysis_intersections")


def pct_rank(s: pd.Series, invert: bool = False) -> pd.Series:
    """Percentile rank scaled 0-100. NaNs stay NaN so missing data never scores as zero."""
    v = pd.to_numeric(s, errors="coerce")
    if v.notna().sum() == 0:
        return pd.Series(np.nan, index=s.index)
    r = v.rank(pct=True, na_option="keep") * 100
    return (100 - r) if invert else r


def road_class_weight(text: str, weights: dict) -> float:
    if not text or str(text) == "nan":
        return 0.0
    best = 0.0
    for cls in str(text).split(" / "):
        best = max(best, float(weights.get(cls.strip(), 0.0)))
    return best


def main() -> int:
    cfg = load_yaml(CONFIG_DIR / "scoring.yaml")
    gdf = gpd.read_file(DATA_PROCESSED / "cnv_intersections_joined.gpkg",
                        layer="intersections_joined")
    log.info("scoring %d intersections", len(gdf))

    gdf["road_class_weight"] = gdf["road_classes"].map(
        lambda t: road_class_weight(t, cfg["road_class_weights"]))

    for boolcol in ("signalised", "full_signal", "traffic_volume_available",
                    "collision_data_available"):
        if boolcol in gdf.columns:
            gdf[boolcol] = gdf[boolcol].fillna(False).astype(bool)

    # Collision counts are only meaningful where ICBC data actually matched. Leave the
    # rest NaN so that "no data" never scores as "perfectly safe".
    if "collision_count" in gdf.columns:
        gdf.loc[~gdf["collision_data_available"], "collision_count"] = np.nan

    component_coverage = {}
    for comp_name, comp in cfg["components"].items():
        parts, weights = [], []
        for inp in comp["inputs"]:
            field = inp["field"]
            if field not in gdf.columns:
                log.warning("%s: input '%s' missing, skipped", comp_name, field)
                continue
            series = gdf[field]
            if series.dtype == bool:
                series = series.astype(float)
            parts.append(pct_rank(series, invert=bool(inp.get("invert"))) * float(inp["weight"]))
            weights.append(float(inp["weight"]))

        if not parts:
            log.warning("%s: no usable inputs", comp_name)
            continue

        stacked = pd.concat(parts, axis=1)
        # Renormalise by the weight actually available per row, so a row with one missing
        # input is not silently penalised.
        wmat = pd.concat(
            [pd.Series(np.where(p.notna(), w, np.nan), index=gdf.index)
             for p, w in zip(parts, weights)], axis=1)
        gdf[comp_name] = (stacked.sum(axis=1, min_count=1) / wmat.sum(axis=1)).round(2)

        cov = 100 * gdf[comp_name].notna().mean()
        component_coverage[comp_name] = cov
        gdf[f"{comp_name}_coverage_note"] = comp.get("coverage_warning", "").strip()
        log.info("  %-32s computed for %.0f%% of intersections", comp_name, cov)

    comps = [c for c in cfg["composite"]["components"] if c in gdf.columns]
    gdf["public_space_composite"] = gdf[comps].mean(axis=1, skipna=True).round(2)
    gdf["components_available"] = gdf[comps].notna().sum(axis=1)
    gdf["composite_method"] = (
        "Unweighted mean of " + str(len(comps)) + " full-coverage components, each a 0-100 "
        "percentile rank. Only components available for every intersection are included, so "
        "all rows are scored on the same basis. safety_score is reported alongside but is "
        "NOT in the composite because its coverage is partial."
    )
    incomplete = int((gdf["components_available"] < len(comps)).sum())
    if incomplete:
        log.warning("%d intersections lack a full component set despite the "
                    "full-coverage rule", incomplete)
    else:
        log.info("all %d intersections scored on the same %d components",
                 len(gdf), len(comps))
    gdf["political_neutrality_statement"] = (
        "This score contains no political variable. It does not use party, candidate, "
        "voting history or any inference from demographics to political preference. "
        "Population inputs measure how many people are physically nearby, nothing more."
    )
    gdf["prepared_utc"] = utc_now()

    gdf["composite_rank"] = gdf["public_space_composite"].rank(ascending=False, method="min")

    out = DATA_PROCESSED / "cnv_public_space_scores.gpkg"
    gdf.to_file(out, layer="public_space_scores", driver="GPKG")

    log.info("-" * 96)
    log.info("TOP 15 INTERSECTIONS BY COMPOSITE PUBLIC-SPACE SCORE")
    log.info("  %-4s %-34s %6s %6s %6s %6s %6s %6s", "rank", "location", "comp",
             "road", "trans", "ped", "park", "safe*")
    top = gdf.nsmallest(15, "composite_rank")
    for _, r in top.iterrows():
        log.info("  %-4.0f %-34s %6.1f %6.1f %6.1f %6.1f %6.1f %6s",
                 r["composite_rank"], str(r.get("street_names"))[:34],
                 r["public_space_composite"], r.get("road_hierarchy_score", np.nan),
                 r.get("transit_score", np.nan), r.get("pedestrian_proxy_score", np.nan),
                 r.get("parking_access_score", np.nan),
                 f"{r['safety_score']:.1f}" if pd.notna(r.get("safety_score")) else "n/a")

    # --- exported tables ----------------------------------------------------
    tables = OUTPUTS / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    base = ["intersection_id", "street_names", "neighbourhood"]

    def export(name: str, cols: list[str], metric: str, note: str) -> None:
        keep = base + [c for c in cols if c in gdf.columns]
        df = gdf[keep].copy()
        df = df.sort_values(metric, ascending=False, na_position="last").reset_index(drop=True)
        df.insert(0, "rank", df.index + 1)
        df["metric"] = metric
        df["value"] = df[metric]
        df["source"] = "Derived; see DATA_SOURCES.md for each contributing layer"
        df["methodology_note"] = note
        df.to_csv(tables / name, index=False)
        log.info("wrote %-42s %d rows", name, len(df))

    export("public_space_summary.csv",
           comps + ["public_space_composite", "components_available", "composite_rank",
                    "safety_score", "collision_count", "collision_data_available",
                    "nearest_traffic_volume", "traffic_volume_available"],
           "public_space_composite",
           "Unweighted mean of full-coverage 0-100 percentile-rank components. Neutral "
           "public-space measure containing no political variable. safety_score and "
           "nearest_traffic_volume are reported as separate columns, NOT folded into the "
           "composite, because their coverage is partial.")

    export("traffic_intersection_summary.csv",
           ["road_classes", "road_class_weight", "nearest_traffic_volume",
            "traffic_volume_available", "signalised", "full_signal", "road_hierarchy_score"],
           "road_hierarchy_score",
           "Road hierarchy only. Measured traffic volumes were removed from this score "
           "because they cover just 40 of 503 intersections; they are reported as the "
           "separate nearest_traffic_volume column. This is NOT a measured traffic ranking.")

    export("transit_intersection_summary.csv",
           ["transit_stops_100m", "transit_stops_250m", "transit_stops_400m",
            "transit_departures_250m", "transit_departures_am_peak_250m", "transit_score"],
           "transit_score",
           "Scheduled weekday departures from the TransLink GTFS feed within 250 m.")

    export("parking_intersection_summary.csv",
           ["onstreet_supply_250m", "onstreet_peak_occupancy_250m", "offstreet_spaces_400m",
            "pay_stations_250m", "accessible_parking_250m", "parking_access_score"],
           "parking_access_score",
           "Supply from City layers; occupancy from a City survey, NOT a real-time feed.")

    log.info("  * safety is reported separately and is NOT part of the composite")

    export("safety_intersection_summary.csv",
           ["collision_count", "collision_data_available", "safety_score"],
           "collision_count",
           "ICBC crash counts name-matched to CNV intersections. Intersections without a "
           "match are unknown, not zero.")

    # --- field audit checklist ---------------------------------------------
    audit = gdf.nsmallest(30, "composite_rank")[
        base + ["public_space_composite", "signalised", "full_signal"]].copy()
    audit["signal_timing_status"] = "REQUEST_REQUIRED"
    for col, prompt in [
        ("check_sightlines", "Obstructions to sightlines on each approach? (vegetation, parked vehicles, signage)"),
        ("check_grade_slope", "Noticeable grade or crest limiting visibility?"),
        ("check_curvature", "Curved approach reducing approach visibility?"),
        ("check_sidewalk_width", "Usable footway width clear of street furniture (m)?"),
        ("check_pedestrian_volume", "Observed pedestrian count, 15 min, with date and time"),
        ("check_signal_cycle_seconds", "Measured signal cycle length (s) - not published by CNV"),
        ("check_pedestrian_walk_interval", "Measured walk interval (s) - not published by CNV"),
        ("check_noise_environment", "Ambient noise limiting conversation?"),
        ("check_lighting", "Lighting adequate after dark?"),
        ("check_public_realm_space", "Space to stand clear of the footway travel path?"),
    ]:
        audit[col] = prompt
    audit["instruction"] = (
        "Field observation is required for these attributes because no public dataset "
        "publishes them for CNV. Record the date, time and observer for each visit."
    )
    audit.to_csv(tables / "field_audit_checklist.csv", index=False)
    log.info("wrote field_audit_checklist.csv (top %d candidates)", len(audit))

    log.info("-" * 96)
    log.info("component coverage summary:")
    for k, v in sorted(component_coverage.items(), key=lambda kv: -kv[1]):
        flag = "" if v > 95 else "   <-- partial coverage, read with its note"
        log.info("    %-32s %5.1f%%%s", k, v, flag)
    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
