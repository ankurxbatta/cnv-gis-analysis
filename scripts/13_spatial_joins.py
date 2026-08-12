#!/usr/bin/env python3
"""Assemble the master intersection table by joining every prepared layer.

For each derived CNV intersection this computes, at 100/250/400 m buffers where relevant:
  transit stop counts and scheduled weekday departures
  on-street parking supply and surveyed peak occupancy
  off-street parking spaces
  signalisation (full signal vs pedestrian-only)
  collision counts (ICBC, name-matched)
  sidewalk and bike-route length, sidewalk ramps
  resident population and the 18+ proxy, by areal interpolation from dissemination areas
  commercial/mixed land-use area

Population figures are areally interpolated from DA polygons, which assumes population is
spread evenly within a DA. That assumption is recorded on the output layer.

Output: data/processed/cnv_intersections_joined.gpkg
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
    get_logger,
    load_boundary,
    load_study_area,
    utc_now,
)

log = get_logger("13_spatial_joins")


def safe_layer(path: Path, layer: str) -> gpd.GeoDataFrame | None:
    try:
        gdf = gpd.read_file(path, layer=layer)
        return gdf if len(gdf) else None
    except Exception:  # noqa: BLE001
        log.warning("layer %s not available in %s", layer, path.name)
        return None


def count_within(points: gpd.GeoDataFrame, targets: gpd.GeoDataFrame, radius: float,
                 value_col: str | None = None) -> pd.Series:
    """Count (or sum a column of) target features within `radius` of each point."""
    buf = points.copy()
    buf["geometry"] = points.geometry.buffer(radius)
    joined = gpd.sjoin(targets, buf[["intersection_id", "geometry"]],
                       predicate="intersects", how="inner")
    if value_col:
        agg = joined.groupby("intersection_id")[value_col].sum()
    else:
        agg = joined.groupby("intersection_id").size()
    return points["intersection_id"].map(agg).fillna(0)


def length_within(points: gpd.GeoDataFrame, lines: gpd.GeoDataFrame, radius: float) -> pd.Series:
    """Total length of line features clipped to each buffer."""
    out = {}
    sindex = lines.sindex
    for iid, geom in zip(points["intersection_id"], points.geometry):
        buf = geom.buffer(radius)
        idx = list(sindex.intersection(buf.bounds))
        if not idx:
            out[iid] = 0.0
            continue
        sub = lines.iloc[idx]
        clipped = sub.geometry.intersection(buf)
        out[iid] = float(clipped.length.sum())
    return points["intersection_id"].map(out).fillna(0.0)


def areal_interpolate(points: gpd.GeoDataFrame, polys: gpd.GeoDataFrame, radius: float,
                      cols: list[str]) -> pd.DataFrame:
    """Areally interpolate polygon counts into circular buffers.

    Assumes each count is distributed uniformly across its polygon.
    """
    results = {c: {} for c in cols}
    sindex = polys.sindex
    poly_area = polys.geometry.area

    for iid, geom in zip(points["intersection_id"], points.geometry):
        buf = geom.buffer(radius)
        idx = list(sindex.intersection(buf.bounds))
        if not idx:
            for c in cols:
                results[c][iid] = 0.0
            continue
        sub = polys.iloc[idx]
        inter = sub.geometry.intersection(buf)
        frac = (inter.area / poly_area.iloc[idx]).clip(0, 1).fillna(0)
        for c in cols:
            results[c][iid] = float((pd.to_numeric(sub[c], errors="coerce").fillna(0) * frac).sum())

    return pd.DataFrame({c: points["intersection_id"].map(results[c]) for c in cols})


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    buffers = cfg["analysis"]["intersection_buffers_m"]
    boundary = load_boundary()

    roads_gpkg = DATA_PROCESSED / "cnv_roads.gpkg"
    inter = gpd.read_file(roads_gpkg, layer="intersections").to_crs(crs)
    log.info("intersections: %d", len(inter))

    out_cols = inter.copy()

    # --- transit ------------------------------------------------------------
    stops = safe_layer(DATA_PROCESSED / "cnv_transit.gpkg", "transit_stops")
    if stops is not None:
        stops = stops.to_crs(crs)
        for r in buffers:
            out_cols[f"transit_stops_{r}m"] = count_within(inter, stops, r).astype(int)
        out_cols["transit_departures_250m"] = count_within(
            inter, stops, 250, value_col="trips_per_weekday")
        out_cols["transit_departures_am_peak_250m"] = count_within(
            inter, stops, 250, value_col="trips_am_peak")
        log.info("transit joined: median stops within 250 m = %.0f",
                 out_cols["transit_stops_250m"].median())

    # --- parking ------------------------------------------------------------
    pk = DATA_PROCESSED / "cnv_parking.gpkg"
    occ = safe_layer(pk, "parking_occupancy")
    if occ is not None:
        occ = occ.to_crs(crs)
        out_cols["onstreet_supply_250m"] = count_within(inter, occ, 250, value_col="supply_spaces")
        # Supply-weighted mean peak occupancy is more meaningful than a plain mean.
        occ_w = occ.copy()
        occ_w["_num"] = occ_w["occupancy_peak"].fillna(0) * occ_w["supply_spaces"].fillna(0)
        num = count_within(inter, occ_w, 250, value_col="_num")
        den = out_cols["onstreet_supply_250m"].replace(0, np.nan)
        out_cols["onstreet_peak_occupancy_250m"] = (num / den).round(3)
        log.info("parking joined: median on-street supply within 250 m = %.0f spaces",
                 out_cols["onstreet_supply_250m"].median())

    lots = safe_layer(pk, "parking_lots")
    if lots is not None:
        lots = lots.to_crs(crs)
        lots["_spaces"] = pd.to_numeric(lots.get("SPACES_WEEKDAY"), errors="coerce").fillna(0)
        out_cols["offstreet_spaces_400m"] = count_within(inter, lots, 400, value_col="_spaces")

    for layer, name, radius in [("pay_stations", "pay_stations_250m", 250),
                                ("accessible_parking", "accessible_parking_250m", 250),
                                ("loading_zones", "loading_zones_250m", 250)]:
        g = safe_layer(pk, layer)
        if g is not None:
            out_cols[name] = count_within(inter, g.to_crs(crs), radius).astype(int)

    # --- signals ------------------------------------------------------------
    tr = DATA_PROCESSED / "cnv_traffic.gpkg"
    sig = safe_layer(tr, "signalised_intersections")
    if sig is not None:
        sig = sig.to_crs(crs)
        dist = cfg["analysis"]["signal_cluster_distance_m"]
        near = gpd.sjoin_nearest(inter[["intersection_id", "geometry"]], sig,
                                 how="left", max_distance=dist, distance_col="_d")
        near = near.sort_values("_d").drop_duplicates("intersection_id")
        out_cols["signalised"] = out_cols["intersection_id"].map(
            near.set_index("intersection_id")["_d"].notna()).fillna(False)
        if "has_full_signal" in near.columns:
            out_cols["full_signal"] = out_cols["intersection_id"].map(
                near.set_index("intersection_id")["has_full_signal"]).fillna(False)
        out_cols["signal_timing_status"] = "REQUEST_REQUIRED"
        log.info("signalised intersections: %d of %d (full signal: %d)",
                 int(out_cols["signalised"].sum()), len(out_cols),
                 int(out_cols.get("full_signal", pd.Series(dtype=bool)).sum()))

    vols = safe_layer(tr, "traffic_volumes")
    if vols is not None:
        vols = vols.to_crs(crs)
        maxd = cfg["analysis"]["traffic_station_association_max_m"]
        nearv = gpd.sjoin_nearest(inter[["intersection_id", "geometry"]],
                                  vols[["volume", "direction", "geometry"]],
                                  how="left", max_distance=maxd, distance_col="_d")
        agg = nearv.dropna(subset=["volume"]).groupby("intersection_id")["volume"].max()
        out_cols["nearest_traffic_volume"] = out_cols["intersection_id"].map(agg)
        out_cols["traffic_volume_available"] = out_cols["nearest_traffic_volume"].notna()
        log.info("intersections with a traffic volume within %d m: %d of %d",
                 maxd, int(out_cols["traffic_volume_available"].sum()), len(out_cols))

    # --- safety -------------------------------------------------------------
    crashes = safe_layer(DATA_PROCESSED / "cnv_safety.gpkg", "intersection_crashes")
    if crashes is not None:
        crashes = crashes.to_crs(crs)
        m = crashes.set_index("intersection_id")["crash_count"]
        out_cols["collision_count"] = out_cols["intersection_id"].map(m).fillna(0)
        out_cols["collision_data_available"] = out_cols["intersection_id"].isin(m.index)
        log.info("intersections with matched collision data: %d of %d",
                 int(out_cols["collision_data_available"].sum()), len(out_cols))

    # --- pedestrian infrastructure -----------------------------------------
    for layer, name in [("walkways", "walkway_length_250m"), ("bike_routes", "bike_route_length_250m")]:
        g = safe_layer(roads_gpkg, layer)
        if g is not None:
            out_cols[name] = length_within(inter, g.to_crs(crs), 250).round(1)

    ramps = None
    try:
        from common import clip_to_cnv, load_raw_vector
        ramps = clip_to_cnv(load_raw_vector("cnv/cnv_sidewalk_ramps.geojson", crs), boundary, how="within")
    except Exception as exc:  # noqa: BLE001
        log.warning("sidewalk ramps unavailable: %s", exc)
    if ramps is not None and len(ramps):
        out_cols["sidewalk_ramps_100m"] = count_within(inter, ramps, 100).astype(int)

    # --- population ---------------------------------------------------------
    census = gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da").to_crs(crs)
    pop_cols = ["population_2021", "adult_population_18plus_proxy", "senior_population_65plus",
                "occupied_private_dwellings", "canadian_citizens_18plus"]
    pop_cols = [c for c in pop_cols if c in census.columns]
    interp = areal_interpolate(inter, census, 400, pop_cols)
    for c in pop_cols:
        out_cols[f"{c}_400m"] = interp[c].round(1)
    log.info("population interpolated into 400 m buffers (median %.0f residents)",
             out_cols["population_2021_400m"].median())

    # --- commercial land use ------------------------------------------------
    lu = safe_layer(DATA_PROCESSED / "cnv_housing.gpkg", "cnv_ocp_landuse")
    if lu is not None:
        lu = lu.to_crs(crs)
        skip = {"geometry", "source", "source_url", "license", "prepared_utc", "GlobalID", "BYLAW"}
        text_col = next(
            (c for c in ("OCP2014_LandUse", "OCP_LU_CODE")
             if c in lu.columns and pd.api.types.is_string_dtype(lu[c])),
            next((c for c in lu.columns
                  if c not in skip and pd.api.types.is_string_dtype(lu[c])), None),
        )
        if text_col:
            comm = lu[lu[text_col].astype(str).str.contains(
                "commercial|mixed|centre|center|retail", case=False, na=False)]
            log.info("commercial/mixed land-use polygons: %d (attribute '%s')", len(comm), text_col)
            if len(comm):
                areas = {}
                sindex = comm.sindex
                for iid, geom in zip(inter["intersection_id"], inter.geometry):
                    buf = geom.buffer(250)
                    idx = list(sindex.intersection(buf.bounds))
                    areas[iid] = float(comm.iloc[idx].geometry.intersection(buf).area.sum()) if idx else 0.0
                out_cols["commercial_area_250m_m2"] = out_cols["intersection_id"].map(areas).round(0)

    # --- neighbourhood ------------------------------------------------------
    nb = safe_layer(DATA_PROCESSED / "cnv_boundary.gpkg", "cnv_neighbourhoods")
    if nb is not None:
        nb = nb.to_crs(crs)
        j = gpd.sjoin(inter[["intersection_id", "geometry"]], nb[["neighbourhood", "geometry"]],
                      predicate="within", how="left").drop_duplicates("intersection_id")
        out_cols["neighbourhood"] = out_cols["intersection_id"].map(
            j.set_index("intersection_id")["neighbourhood"])
        unassigned = out_cols["neighbourhood"].isna().sum()
        log.info("intersections assigned to a neighbourhood: %d (%d unassigned)",
                 len(out_cols) - unassigned, unassigned)

    out_cols["population_method_note"] = (
        "Population within 400 m is areally interpolated from 2021 dissemination areas and "
        "assumes uniform distribution within each DA. It is an estimate, not a count."
    )
    out_cols["prepared_utc"] = utc_now()

    out = DATA_PROCESSED / "cnv_intersections_joined.gpkg"
    out_cols.to_file(out, layer="intersections_joined", driver="GPKG")
    log.info("wrote %d intersections with %d attributes -> %s",
             len(out_cols), len(out_cols.columns), out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
