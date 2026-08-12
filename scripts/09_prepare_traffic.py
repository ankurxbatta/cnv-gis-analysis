#!/usr/bin/env python3
"""Prepare CNV traffic layers: signal assets grouped into signalised intersections,
directional traffic volumes, and traffic signs.

Two honesty constraints are enforced here:
  * The signal layer is a POLE/asset inventory, so assets are grouped by the City's own
    INT_UNITID intersection key (falling back to spatial clustering) before being counted.
  * No signal CYCLE or PHASE TIMING is PUBLISHED by CNV, though the City holds it and
    releases it on request, so signal_timing_status is REQUEST_REQUIRED. No timing is
    estimated anywhere in this pipeline.

Output: data/processed/cnv_traffic.gpkg
"""
from __future__ import annotations

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

log = get_logger("09_prepare_traffic")
CNV_ARCGIS = "https://gisext2.cnv.org/arcgis/rest/services"


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    boundary = load_boundary()
    out = DATA_PROCESSED / "cnv_traffic.gpkg"

    # --- traffic signal assets ---------------------------------------------
    sig = load_raw_vector("cnv/cnv_traffic_signals.geojson", crs)
    sig = clip_to_cnv(sig, boundary, how="within")
    log.info("traffic signal assets inside CNV: %d", len(sig))

    if "STATUS" in sig.columns:
        log.info("signal asset status: %s", dict(sig["STATUS"].value_counts(dropna=False)))

    sig = tag_source(sig, "City of North Vancouver ArcGIS - Traffic Signals (asset inventory)",
                     f"{CNV_ARCGIS}/BaseMapServices/TransportMAP/MapServer/153")
    sig["asset_note"] = (
        "One record per signal pole/asset, not per intersection. Cycle length, phase timing "
        "and pedestrian walk intervals are NOT published in this or any other public CNV "
        "source - see DATA_GAPS.md."
    )
    sig.to_file(out, layer="traffic_signal_assets", driver="GPKG")

    # --- group assets into signalised intersections -------------------------
    key = "INT_UNITID" if "INT_UNITID" in sig.columns else None
    if key and sig[key].notna().sum() > 0.5 * len(sig):
        grouped = []
        for uid, grp in sig[sig[key].notna()].groupby(key):
            geom = grp.geometry.union_all().centroid
            grouped.append({
                "signal_group_id": str(uid),
                "asset_count": len(grp),
                "pedestrian_heads": pd.to_numeric(grp.get("PEDESTRIAN_HEADS"), errors="coerce").sum(),
                "primary_heads": pd.to_numeric(grp.get("NUM_PRIMARY_HEADS"), errors="coerce").sum(),
                "signal_types": " / ".join(sorted({str(v) for v in grp.get("SIGNAL_TYPE", []) if pd.notna(v)})),
                "address": grp["ADDRESS"].dropna().iloc[0] if grp["ADDRESS"].notna().any() else None,
                "grouping_basis": f"City INT_UNITID = {uid}",
                "geometry": geom,
            })
        sig_int = gpd.GeoDataFrame(grouped, crs=crs)
        log.info("signalised locations grouped by City INT_UNITID: %d (from %d assets)",
                 len(sig_int), len(sig))
    else:
        dist = cfg["analysis"]["signal_cluster_distance_m"]
        log.warning("INT_UNITID is empty for all %d assets; grouping spatially at %.0f m",
                    len(sig), dist)
        buf = sig.geometry.buffer(dist / 2)
        clusters = gpd.GeoDataFrame(geometry=[buf.union_all()], crs=crs).explode(index_parts=False)
        clusters = clusters.reset_index(drop=True)
        clusters["signal_group_id"] = [f"SIGCL-{i:03d}" for i in range(1, len(clusters) + 1)]

        joined = gpd.sjoin(sig, clusters[["signal_group_id", "geometry"]],
                           predicate="within", how="left")

        def agg_group(grp):
            types = grp["SIGNAL_TYPE"].dropna()
            counts = types.value_counts()
            return pd.Series({
                "asset_count": len(grp),
                "signal_types": " / ".join(f"{k} x{v}" for k, v in counts.items()),
                "has_full_signal": bool((types == "Full Signal").any()),
                "full_signal_assets": int((types == "Full Signal").sum()),
                "pedestrian_signal_assets": int((types == "Pedestrian Signal").sum()),
                "special_crosswalk_assets": int((types == "Special Crosswalk").sum()),
                "rrfb_assets": int((types == "Rectangular Rapid Flashing Beacon").sum()),
                "pedestrian_heads": pd.to_numeric(
                    grp.get("PEDESTRIAN_HEADS"), errors="coerce").sum(),
                "address": grp["ADDRESS"].dropna().iloc[0] if grp["ADDRESS"].notna().any() else None,
            })

        grouped = joined.groupby("signal_group_id").apply(agg_group, include_groups=False)
        cent = clusters.set_index("signal_group_id").geometry.centroid
        sig_int = gpd.GeoDataFrame(
            grouped.join(cent.rename("geometry")).reset_index(), geometry="geometry", crs=crs
        )
        sig_int["grouping_basis"] = (
            f"spatial cluster of signal assets within {dist} m (the City publishes no "
            "intersection key: INT_UNITID is empty for every asset)"
        )
        log.info("signalised locations by spatial clustering: %d", len(sig_int))
        log.info("    with at least one Full Signal asset: %d", int(sig_int["has_full_signal"].sum()))
        log.info("    pedestrian-signal / crosswalk only:  %d",
                 int((~sig_int["has_full_signal"]).sum()))

    sig_int["signal_timing_status"] = "REQUEST_REQUIRED"
    sig_int["signal_timing_note"] = (
        "The City holds signal phasing and cycle-length data and supplies it on request for "
        "transportation studies (Guidelines for the Submission of a Transportation Study - "
        "Level 1, p.6: 'details on signal phasing and cycle lengths will be provided by the "
        "City'), but publishes NO timing values anywhere public. The CNV traffic signals GIS "
        "layer carries asset attributes only. Contacts: eng@cnv.org, transportation@cnv.org. "
        "No cycle time is estimated by this pipeline."
    )
    sig_int = tag_source(sig_int, "Derived from City of North Vancouver Traffic Signals asset layer",
                         f"{CNV_ARCGIS}/BaseMapServices/TransportMAP/MapServer/153")
    sig_int.to_file(out, layer="signalised_intersections", driver="GPKG")

    # --- directional traffic volumes ---------------------------------------
    frames = []
    for direction in ("northbound", "southbound", "eastbound", "westbound"):
        try:
            g = load_raw_vector(f"traffic/cnv_traffic_volume_{direction}.geojson", crs)
        except Exception as exc:  # noqa: BLE001
            log.warning("no %s volume layer: %s", direction, exc)
            continue
        if g.empty:
            continue
        col = direction.capitalize()
        g["direction"] = direction
        g["volume"] = pd.to_numeric(g[col], errors="coerce") if col in g.columns else np.nan
        frames.append(g[["direction", "volume", "geometry"]])

    if frames:
        vol = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=crs)
        vol = clip_to_cnv(vol, boundary)
        vol = vol[~vol.geometry.is_empty]
        vol = tag_source(vol, "City of North Vancouver ArcGIS - Traffic Volumes by direction",
                         f"{CNV_ARCGIS}/BaseMapServices/TransportMAP/MapServer/226-229")
        vol["coverage_warning"] = (
            "Directional volumes are published for a very small number of street segments "
            "only. They must NOT be generalised to the wider network, and no volume is "
            "attributed to an intersection without a segment within the documented "
            "association distance."
        )
        vol["units_note"] = (
            "Units are as published by the City and are not labelled as AADT in the source "
            "layer; treat as a directional segment count of unspecified period."
        )
        vol.to_file(out, layer="traffic_volumes", driver="GPKG")
        log.info("traffic volume segments: %d across %d directions",
                 len(vol), vol["direction"].nunique())
        log.info("    volume range: %.0f - %.0f (median %.0f)",
                 vol["volume"].min(), vol["volume"].max(), vol["volume"].median())
        log.warning("traffic volume coverage is %d segments against %d road segments in CNV - "
                    "this is a headline limitation", len(vol), 941)

    # --- traffic signs -----------------------------------------------------
    for raw, layer, label, lid in [
        ("cnv/cnv_traffic_signs.geojson", "traffic_signs", "Traffic Signs", 152),
        ("traffic/cnv_cyclist_volume.geojson", "cyclist_volume", "Cyclist Volume", 26),
    ]:
        try:
            g = load_raw_vector(raw, crs)
        except Exception as exc:  # noqa: BLE001
            log.warning("skipping %s: %s", layer, exc)
            continue
        if g.empty:
            log.warning("%s is empty", layer)
            continue
        g = clip_to_cnv(g, boundary, how="within" if g.geom_type.iloc[0] == "Point" else "clip")
        g = g[~g.geometry.is_empty]
        if g.empty:
            continue
        g = tag_source(g, f"City of North Vancouver ArcGIS - {label}",
                       f"{CNV_ARCGIS}/BaseMapServices/TransportMAP/MapServer/{lid}")
        g.to_file(out, layer=layer, driver="GPKG")
        log.info("wrote %-18s %5d features", layer, len(g))

    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
