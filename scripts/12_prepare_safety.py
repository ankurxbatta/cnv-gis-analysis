#!/usr/bin/env python3
"""Match ICBC crash records to CNV intersections.

ICBC publishes crash counts against location NAME strings with no coordinates, and its
'NORTH VANCOUVER' municipality value covers BOTH the City and the District. Matching is
therefore name-based and deliberately conservative:

  a record is attributed to a CNV intersection only when every street named in the
  location string is a CNV street AND the named pair corresponds to an intersection
  actually present in the derived CNV intersection layer.

Everything not matched is retained in an unmatched table rather than being discarded or
force-fitted, so the shortfall is visible.

Output: data/processed/cnv_safety.gpkg
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
    DATA_RAW,
    OUTPUTS,
    get_logger,
    load_study_area,
    tag_source,
)

log = get_logger("12_prepare_safety")

# Tokens that appear in ICBC location strings but are not street names.
NON_STREET_TOKENS = {
    "BUS LANE", "TURNING LANE", "OFFRAMP", "ONRAMP", "OFF RAMP", "ON RAMP",
    "PARKING LOT", "ALLEY", "LANE",
}

SUFFIX_NORMALISE = {
    "AVENUE": "AVE", "AV": "AVE", "STREET": "ST", "ROAD": "RD", "DRIVE": "DR",
    "PLACE": "PL", "BOULEVARD": "BLVD", "CRESCENT": "CRES", "COURT": "CRT",
    "HIGHWAY": "HWY", "PARKWAY": "PKWY", "TERRACE": "TERR", "WAY": "WAY",
}
DIR_NORMALISE = {
    "EAST": "E", "WEST": "W", "NORTH": "N", "SOUTH": "S",
}


def normalise_street(name: str) -> str:
    """Reduce a street name to a comparable canonical form."""
    s = str(name).upper().strip()
    s = re.sub(r"[.,]", " ", s)
    s = re.sub(r"\s+", " ", s)
    tokens = [DIR_NORMALISE.get(t, t) for t in s.split()]
    tokens = [SUFFIX_NORMALISE.get(t, t) for t in tokens]
    return " ".join(tokens).strip()


def cnv_street_names(roads: gpd.GeoDataFrame) -> set[str]:
    names = set()
    for _, r in roads.iterrows():
        full = str(r.get("full_street_name") or "").strip()
        if full and full.lower() != "nan":
            names.add(normalise_street(full))
    return {n for n in names if n}


def parse_location(loc: str) -> list[str]:
    parts = [p.strip() for p in str(loc).split("&")]
    out = []
    for p in parts:
        pn = normalise_street(p)
        if not pn or pn in NON_STREET_TOKENS:
            continue
        if any(tok in pn for tok in ("OFFRAMP", "ONRAMP", "BUS LANE", "TURNING LANE")):
            continue
        out.append(pn)
    return out


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    out = DATA_PROCESSED / "cnv_safety.gpkg"

    roads = gpd.read_file(DATA_PROCESSED / "cnv_roads.gpkg", layer="roads")
    inter = gpd.read_file(DATA_PROCESSED / "cnv_roads.gpkg", layer="intersections")
    cnv_names = cnv_street_names(roads)
    log.info("CNV street-name variants for matching: %d", len(cnv_names))

    crashes = pd.read_csv(DATA_RAW / "safety" / "icbc_crashes_north_vancouver.csv",
                          encoding="utf-8-sig")
    crashes.columns = [c.strip() for c in crashes.columns]
    loc_col = crashes.columns[0]
    cnt_col = next((c for c in crashes.columns[1:] if "count" in c.lower().replace(" ", "")),
                   crashes.columns[1])
    crashes["crash_count"] = pd.to_numeric(
        crashes[cnt_col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    crashes = crashes.dropna(subset=["crash_count"])
    log.info("ICBC 'NORTH VANCOUVER' records: %d, total crashes %.0f",
             len(crashes), crashes["crash_count"].sum())

    # --- name matching ------------------------------------------------------
    inter_keys: dict[frozenset, list] = {}
    for _, r in inter.iterrows():
        a, b = r.get("street_a"), r.get("street_b")
        if not a or not b:
            continue
        key = frozenset({normalise_street(a), normalise_street(b)})
        inter_keys.setdefault(key, []).append(r)

    log.info("CNV intersections with two named streets: %d", len(inter_keys))

    matched_rows, unmatched_rows, excluded_rows = [], [], []
    for _, row in crashes.iterrows():
        streets = parse_location(row[loc_col])
        if len(streets) < 2:
            unmatched_rows.append((row[loc_col], row["crash_count"],
                                   "fewer than 2 street names parsed (mid-block record)"))
            continue

        in_cnv = [s for s in streets if s in cnv_names]
        foreign = [s for s in streets if s not in cnv_names]
        if len(in_cnv) < 2:
            unmatched_rows.append((row[loc_col], row["crash_count"],
                                   "fewer than 2 of the named streets are CNV streets"))
            continue

        # The decisive test: a pair of CNV streets that actually cross in CNV.
        hit = None
        for k, v in inter_keys.items():
            if k <= set(in_cnv):
                hit = v
                break
        if not hit:
            unmatched_rows.append((row[loc_col], row["crash_count"],
                                   "CNV street names but no matching CNV intersection"))
            continue

        r = hit[0]
        if foreign:
            # The record also names non-CNV streets, which in practice means a Highway 1
            # interchange. Those crashes are largely provincial-highway collisions, not
            # collisions at a CNV municipal intersection, and 26 such records carried 29%
            # of all matched crashes. They are excluded from the analysis layer and written
            # to a separate review layer instead of being silently folded in.
            excluded_rows.append({
                "intersection_id": r["intersection_id"],
                "icbc_location": row[loc_col],
                "crash_count": row["crash_count"],
                "street_a": r.get("street_a"),
                "street_b": r.get("street_b"),
                "non_cnv_streets_in_record": "; ".join(foreign),
                "exclusion_reason": (
                    "record names non-CNV streets (typically Highway 1 ramps), so the crash "
                    "total cannot be attributed to a CNV municipal intersection"
                ),
                "geometry": r.geometry,
            })
            continue

        confidence = "high"
        matched_rows.append({
            "intersection_id": r["intersection_id"],
            "icbc_location": row[loc_col],
            "crash_count": row["crash_count"],
            "street_a": r.get("street_a"),
            "street_b": r.get("street_b"),
            "match_confidence": confidence,
            "match_basis": (
                "every named street is a CNV street and the pair exists in the CNV "
                "intersection layer"
            ),
            "geometry": r.geometry,
        })

    matched = gpd.GeoDataFrame(matched_rows, crs=crs) if matched_rows else gpd.GeoDataFrame()
    unmatched = pd.DataFrame(unmatched_rows, columns=["icbc_location", "crash_count", "reason"])

    log.info("-" * 70)
    log.info("matched to a CNV intersection: %d records, %.0f crashes",
             len(matched), matched["crash_count"].sum() if len(matched) else 0)
    log.info("unmatched: %d records, %.0f crashes", len(unmatched), unmatched["crash_count"].sum())
    log.info("EXCLUDED as unattributable: %d records, %.0f crashes "
             "(records naming non-CNV streets, e.g. Highway 1 interchanges)",
             len(excluded_rows), sum(r["crash_count"] for r in excluded_rows))
    log.info("unmatched reasons:")
    for reason, grp in unmatched.groupby("reason"):
        log.info("    %-58s %4d records, %6.0f crashes", reason, len(grp), grp["crash_count"].sum())

    if len(matched):
        agg = matched.dissolve(by="intersection_id", aggfunc={"crash_count": "sum"}).reset_index()
        agg = agg.merge(
            matched.groupby("intersection_id")["icbc_location"]
            .apply(lambda s: " | ".join(sorted(set(s)))).rename("icbc_locations"),
            on="intersection_id", how="left",
        )
        agg = tag_source(
            agg, "ICBC Lower Mainland Crashes (Tableau Public CSV export), name-matched to "
                 "CNV intersections",
            "https://public.tableau.com/app/profile/icbc/viz/LowerMainlandCrashes/LMDashboard",
            "Open Data Licence for ICBC Information",
        )
        agg["matching_limitation"] = (
            "ICBC reports 'NORTH VANCOUVER' for both the City and the District and provides "
            "no coordinates. Attribution here required every named street to be a CNV street "
            "and the pair to exist in the CNV intersection layer. Counts cover ICBC's "
            "published reporting period and are not year-specific in this export."
        )
        agg.to_file(out, layer="intersection_crashes", driver="GPKG")
        log.info("wrote intersection_crashes: %d intersections, %.0f crashes",
                 len(agg), agg["crash_count"].sum())
        log.info("highest-crash CNV intersections:")
        for _, r in agg.nlargest(10, "crash_count").iterrows():
            log.info("    %-34s %5.0f", str(r["icbc_locations"])[:34], r["crash_count"])

    if excluded_rows:
        exc = gpd.GeoDataFrame(excluded_rows, crs=crs)
        exc = tag_source(
            exc, "ICBC Lower Mainland Crashes - EXCLUDED from the analysis layer",
            "https://public.tableau.com/app/profile/icbc/viz/LowerMainlandCrashes/LMDashboard",
            "Open Data Licence for ICBC Information",
        )
        exc.to_file(out, layer="excluded_crashes_review", driver="GPKG")
        exc.drop(columns="geometry").to_csv(
            OUTPUTS / "tables" / "icbc_excluded_records.csv", index=False)
        log.info("wrote excluded_crashes_review layer (%d records) for manual review",
                 len(exc))

    OUTPUTS.joinpath("tables").mkdir(parents=True, exist_ok=True)
    unmatched.to_csv(OUTPUTS / "tables" / "icbc_unmatched_locations.csv", index=False)
    log.info("unmatched records written to outputs/tables/icbc_unmatched_locations.csv")
    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
