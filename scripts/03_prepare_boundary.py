#!/usr/bin/env python3
"""Build the authoritative City of North Vancouver study-area boundary.

Outputs data/processed/cnv_boundary.gpkg with layers:
    cnv_boundary          - the legal municipal boundary (BC ABMS), analysis CRS
    cnv_boundary_buffered - boundary + edge_context_buffer_m, for pulling regional data
    cnv_neighbourhoods    - the 10 official CNV neighbourhoods, clipped to the boundary

Validates that the CNV feature is genuinely distinct from the District of North
Vancouver, and that CNV neighbourhoods cover the municipal area.
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_PROCESSED,
    DATA_RAW,
    get_logger,
    load_study_area,
    utc_now,
)

log = get_logger("03_prepare_boundary")


def main() -> int:
    cfg = load_study_area()
    analysis_crs = cfg["crs"]["analysis"]
    buffer_m = cfg["analysis"]["edge_context_buffer_m"]

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    out = DATA_PROCESSED / "cnv_boundary.gpkg"

    # --- municipal boundary -------------------------------------------------
    src = DATA_RAW / "bcdata" / "cnv_municipal_boundary_abms.geojson"
    boundary = gpd.read_file(src)
    log.info("loaded %d feature(s) from %s (crs=%s)", len(boundary), src.name, boundary.crs)

    if len(boundary) != 1:
        log.error("expected exactly 1 CNV boundary feature, got %d", len(boundary))
        return 1

    name = boundary.iloc[0].get("ADMIN_AREA_NAME", "")
    if name != cfg["study_area"]["bc_abms"]["admin_area_name"]:
        log.error("boundary is '%s', expected '%s'", name,
                  cfg["study_area"]["bc_abms"]["admin_area_name"])
        return 1
    if "District" in name:
        log.error("refusing to proceed: boundary appears to be the District, not the City")
        return 1
    log.info("confirmed study area: %s", name)

    boundary = boundary.to_crs(analysis_crs)
    boundary["geometry"] = boundary.geometry.make_valid()

    area_km2 = float(boundary.geometry.area.sum()) / 1e6
    log.info("CNV area = %.3f km2 (published municipal area is approximately 11.9 km2)", area_km2)
    if not 8.0 < area_km2 < 16.0:
        log.error("area %.2f km2 is outside the plausible range for CNV - wrong feature?", area_km2)
        return 1

    boundary = boundary[["ADMIN_AREA_NAME", "LGL_ADMIN_AREA_ID", "geometry"]].copy()
    boundary["area_km2"] = area_km2
    boundary["source"] = "BC ABMS (WHSE_LEGAL_ADMIN_BOUNDARIES.ABMS_MUNICIPALITIES_SP)"
    boundary["source_url"] = (
        "https://catalogue.data.gov.bc.ca/dataset/"
        "municipalities-legally-defined-administrative-areas-of-bc"
    )
    boundary["license"] = "Open Government Licence - British Columbia"
    boundary["prepared_utc"] = utc_now()
    boundary.to_file(out, layer="cnv_boundary", driver="GPKG")
    log.info("wrote cnv_boundary (%s)", analysis_crs)

    # --- separation check against the District ------------------------------
    ns_path = DATA_RAW / "bcdata" / "northshore_municipalities_abms.geojson"
    if ns_path.exists():
        ns = gpd.read_file(ns_path).to_crs(analysis_crs)
        ns["geometry"] = ns.geometry.make_valid()
        dnv = ns[ns["ADMIN_AREA_NAME"].str.contains("District of North Vancouver", na=False)]
        if not dnv.empty:
            overlap = gpd.overlay(
                boundary[["geometry"]], dnv[["geometry"]], how="intersection"
            )
            overlap_km2 = float(overlap.geometry.area.sum()) / 1e6 if not overlap.empty else 0.0
            pct = 100 * overlap_km2 / area_km2
            log.info("City/District overlap = %.4f km2 (%.3f%% of CNV)", overlap_km2, pct)
            if pct > 1.0:
                log.error("City and District overlap by more than 1%% - boundaries are wrong")
                return 1

    # --- buffered boundary for regional data --------------------------------
    buffered = boundary.copy()
    buffered["geometry"] = buffered.geometry.buffer(buffer_m)
    buffered["buffer_m"] = buffer_m
    buffered["purpose"] = (
        "Edge context only. Regional layers (TransLink, DNV GEOweb) are pulled within this "
        "buffer so that intersections near the municipal edge are not starved of nearby "
        "features. All reported statistics remain clipped to cnv_boundary."
    )
    buffered.to_file(out, layer="cnv_boundary_buffered", driver="GPKG")
    log.info("wrote cnv_boundary_buffered (+%d m)", buffer_m)

    # --- neighbourhoods -----------------------------------------------------
    nb_path = DATA_RAW / "cnv" / "cnv_neighbourhoods.geojson"
    nb = gpd.read_file(nb_path)
    if nb.crs is None:
        nb = nb.set_crs(analysis_crs)
    nb = nb.to_crs(analysis_crs)
    nb["geometry"] = nb.geometry.make_valid()

    nb = nb.rename(columns={"NHOOD": "neighbourhood"})
    keep = [c for c in ("neighbourhood", "NHOOD_ID") if c in nb.columns]
    nb = nb[keep + ["geometry"]].copy()

    nb_clipped = gpd.clip(nb, boundary)
    nb_clipped["area_km2"] = nb_clipped.geometry.area / 1e6
    nb_clipped["source"] = "City of North Vancouver ArcGIS (query_layers/MapServer/8)"
    nb_clipped["source_url"] = (
        "https://gisext2.cnv.org/arcgis/rest/services/BaseMapServices/query_layers/MapServer/8"
    )
    nb_clipped["prepared_utc"] = utc_now()

    coverage = 100 * nb_clipped.geometry.area.sum() / boundary.geometry.area.sum()
    log.info("%d neighbourhoods covering %.1f%% of the municipal area",
             len(nb_clipped), coverage)
    for _, r in nb_clipped.sort_values("area_km2", ascending=False).iterrows():
        log.info("    %-28s %6.3f km2", r["neighbourhood"], r["area_km2"])
    if coverage < 90:
        log.warning("neighbourhoods cover only %.1f%% of CNV - gaps will be reported as "
                    "'unassigned' in neighbourhood analysis", coverage)

    nb_clipped.to_file(out, layer="cnv_neighbourhoods", driver="GPKG")
    log.info("wrote cnv_neighbourhoods -> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
