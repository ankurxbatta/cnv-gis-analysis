#!/usr/bin/env python3
"""Process the TransLink GTFS feed into CNV transit layers with service frequencies.

Service frequency is computed from stop_times on a representative WEEKDAY chosen from
calendar/calendar_dates, counting scheduled departures per stop in defined periods.

Output: data/processed/cnv_transit.gpkg
  transit_stops   - stops within the buffered CNV boundary, with trips/day and peak counts
  transit_routes  - route shapes serving CNV
  seabus          - SeaBus terminal(s), flagged separately (very high-capacity service)
"""
from __future__ import annotations

import io
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_PROCESSED,
    DATA_RAW,
    clip_to_cnv,
    get_logger,
    load_boundary,
    load_study_area,
    tag_source,
)

log = get_logger("10_prepare_transit")

GTFS = DATA_RAW / "transit" / "translink_gtfs.zip"

PERIODS = {
    "am_peak": (7 * 3600, 9 * 3600),
    "midday": (11 * 3600, 13 * 3600),
    "pm_peak": (16 * 3600, 18 * 3600),
    "evening": (18 * 3600, 22 * 3600),
}


def read_gtfs(z: zipfile.ZipFile, name: str, **kw) -> pd.DataFrame:
    with z.open(name) as fh:
        return pd.read_csv(io.TextIOWrapper(fh, encoding="utf-8-sig"), **kw)


def gtfs_seconds(value: str) -> int | None:
    """GTFS times can exceed 24:00:00 for trips past midnight."""
    try:
        h, m, s = str(value).split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    except (ValueError, AttributeError):
        return None


def pick_service_ids(z: zipfile.ZipFile) -> tuple[set[str], str]:
    """Choose the service_ids running on a representative weekday."""
    cal = read_gtfs(z, "calendar.txt", dtype={"service_id": str})
    cal["start_date"] = pd.to_datetime(cal["start_date"], format="%Y%m%d")
    cal["end_date"] = pd.to_datetime(cal["end_date"], format="%Y%m%d")

    weekday_mask = cal["wednesday"] == 1
    candidates = cal[weekday_mask]
    if candidates.empty:
        raise SystemExit("no Wednesday services found in GTFS calendar")

    # Use a Wednesday inside the feed's active window.
    start = candidates["start_date"].min()
    end = candidates["end_date"].max()
    probe = start
    while probe.weekday() != 2:  # Wednesday
        probe += pd.Timedelta(days=1)
    if probe > end:
        probe = start

    active = candidates[(candidates["start_date"] <= probe) & (candidates["end_date"] >= probe)]
    service_ids = set(active["service_id"].astype(str))

    # Apply calendar_dates exceptions for that date.
    try:
        cd = read_gtfs(z, "calendar_dates.txt", dtype={"service_id": str})
        stamp = int(probe.strftime("%Y%m%d"))
        added = set(cd[(cd["date"] == stamp) & (cd["exception_type"] == 1)]["service_id"].astype(str))
        removed = set(cd[(cd["date"] == stamp) & (cd["exception_type"] == 2)]["service_id"].astype(str))
        service_ids = (service_ids | added) - removed
    except KeyError:
        log.info("no calendar_dates.txt in feed")

    log.info("representative weekday: %s, %d active service_id(s)",
             probe.date().isoformat(), len(service_ids))
    return service_ids, probe.date().isoformat()


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    boundary = load_boundary()
    buffered = load_boundary("cnv_boundary_buffered")
    out = DATA_PROCESSED / "cnv_transit.gpkg"

    with zipfile.ZipFile(GTFS) as z:
        names = z.namelist()
        log.info("GTFS members: %s", ", ".join(sorted(names)))

        stops = read_gtfs(z, "stops.txt", dtype={"stop_id": str})
        routes = read_gtfs(z, "routes.txt", dtype={"route_id": str})
        trips = read_gtfs(z, "trips.txt", dtype={"route_id": str, "service_id": str,
                                                 "trip_id": str, "shape_id": str})
        service_ids, service_date = pick_service_ids(z)

        log.info("feed totals: %d stops, %d routes, %d trips", len(stops), len(routes), len(trips))

        # Spatially restrict stops first so stop_times parsing stays manageable.
        stops = stops.dropna(subset=["stop_lat", "stop_lon"])
        stops_gdf = gpd.GeoDataFrame(
            stops,
            geometry=[Point(xy) for xy in zip(stops["stop_lon"], stops["stop_lat"])],
            crs="EPSG:4326",
        ).to_crs(crs)

        near = clip_to_cnv(stops_gdf, buffered, how="within")
        log.info("stops within the buffered CNV boundary: %d", len(near))
        keep_stops = set(near["stop_id"].astype(str))

        weekday_trips = trips[trips["service_id"].astype(str).isin(service_ids)]
        keep_trips = set(weekday_trips["trip_id"].astype(str))
        log.info("trips running on the representative weekday: %d", len(keep_trips))

        # Stream stop_times; the file is large and mostly irrelevant to CNV.
        log.info("scanning stop_times.txt ...")
        counts: Counter = Counter()
        period_counts: dict[str, Counter] = {p: Counter() for p in PERIODS}
        stop_routes: dict[str, set] = {}
        trip_to_route = dict(zip(weekday_trips["trip_id"].astype(str),
                                 weekday_trips["route_id"].astype(str)))

        with z.open("stop_times.txt") as fh:
            reader = pd.read_csv(
                io.TextIOWrapper(fh, encoding="utf-8-sig"),
                usecols=["trip_id", "stop_id", "departure_time"],
                dtype={"trip_id": str, "stop_id": str},
                chunksize=1_000_000,
            )
            for chunk in reader:
                chunk = chunk[chunk["stop_id"].isin(keep_stops) & chunk["trip_id"].isin(keep_trips)]
                if chunk.empty:
                    continue
                secs = chunk["departure_time"].map(gtfs_seconds)
                for stop_id, sec, trip_id in zip(chunk["stop_id"], secs, chunk["trip_id"]):
                    counts[stop_id] += 1
                    stop_routes.setdefault(stop_id, set()).add(trip_to_route.get(trip_id))
                    if sec is None:
                        continue
                    for pname, (lo, hi) in PERIODS.items():
                        if lo <= sec < hi:
                            period_counts[pname][stop_id] += 1

        log.info("stop_times scan complete: %d CNV-area stops have scheduled service", len(counts))

        # --- assemble stop layer -------------------------------------------
        near = near.copy()
        near["trips_per_weekday"] = near["stop_id"].astype(str).map(counts).fillna(0).astype(int)
        for pname in PERIODS:
            near[f"trips_{pname}"] = (
                near["stop_id"].astype(str).map(period_counts[pname]).fillna(0).astype(int)
            )
        near["routes_serving"] = near["stop_id"].astype(str).map(
            lambda s: len({r for r in stop_routes.get(s, set()) if r})
        ).fillna(0).astype(int)
        near["service_date_basis"] = service_date
        near["in_cnv"] = near.index.isin(clip_to_cnv(near, boundary, how="within").index)

        # AM peak is a 2-hour window; convert to an average headway for readability.
        near["am_peak_avg_headway_min"] = near["trips_am_peak"].map(
            lambda n: round(120 / n, 1) if n else None
        )

        near = tag_source(
            near, "TransLink GTFS static feed",
            "https://www.translink.ca/about-us/doing-business-with-translink/"
            "app-developer-resources/gtfs/gtfs-data",
            "TransLink Open Data / GTFS terms of use",
        )
        near.to_file(out, layer="transit_stops", driver="GPKG")

        in_cnv = near[near["in_cnv"]]
        log.info("-" * 60)
        log.info("stops inside CNV: %d (plus %d in the %d m edge buffer)",
                 len(in_cnv), len(near) - len(in_cnv), cfg["analysis"]["edge_context_buffer_m"])
        log.info("total scheduled weekday departures at CNV stops: %d",
                 in_cnv["trips_per_weekday"].sum())
        top = in_cnv.nlargest(8, "trips_per_weekday")
        log.info("busiest CNV stops by scheduled weekday departures:")
        for _, r in top.iterrows():
            log.info("    %-42s %5d/day  (AM peak %3d)", str(r.get("stop_name"))[:42],
                     r["trips_per_weekday"], r["trips_am_peak"])

        # --- routes ---------------------------------------------------------
        cnv_trip_ids = set()
        with z.open("stop_times.txt") as fh:
            reader = pd.read_csv(
                io.TextIOWrapper(fh, encoding="utf-8-sig"),
                usecols=["trip_id", "stop_id"], dtype={"trip_id": str, "stop_id": str},
                chunksize=1_000_000,
            )
            cnv_stop_ids = set(in_cnv["stop_id"].astype(str))
            for chunk in reader:
                hit = chunk[chunk["stop_id"].isin(cnv_stop_ids)]
                cnv_trip_ids.update(hit["trip_id"].astype(str))

        cnv_trips = trips[trips["trip_id"].astype(str).isin(cnv_trip_ids)]
        cnv_route_ids = set(cnv_trips["route_id"].astype(str))
        log.info("routes serving CNV: %d", len(cnv_route_ids))

        if "shapes.txt" in names:
            shapes = read_gtfs(z, "shapes.txt", dtype={"shape_id": str})
            want_shapes = set(cnv_trips["shape_id"].dropna().astype(str))
            shapes = shapes[shapes["shape_id"].astype(str).isin(want_shapes)]
            lines = []
            for sid, grp in shapes.sort_values("shape_pt_sequence").groupby("shape_id"):
                if len(grp) < 2:
                    continue
                lines.append({
                    "shape_id": sid,
                    "geometry": LineString(zip(grp["shape_pt_lon"], grp["shape_pt_lat"])),
                })
            if lines:
                shp = gpd.GeoDataFrame(lines, crs="EPSG:4326").to_crs(crs)
                shape_route = cnv_trips.dropna(subset=["shape_id"]).drop_duplicates("shape_id")
                shp = shp.merge(
                    shape_route[["shape_id", "route_id"]].astype(str), on="shape_id", how="left"
                ).merge(
                    routes[["route_id", "route_short_name", "route_long_name", "route_type"]]
                    .astype({"route_id": str}), on="route_id", how="left",
                )
                shp = gpd.clip(shp, buffered.to_crs(crs))
                shp = shp[~shp.geometry.is_empty]
                shp = tag_source(
                    shp, "TransLink GTFS static feed (shapes.txt)",
                    "https://www.translink.ca/about-us/doing-business-with-translink/"
                    "app-developer-resources/gtfs/gtfs-data",
                    "TransLink Open Data / GTFS terms of use",
                )
                shp.to_file(out, layer="transit_routes", driver="GPKG")
                log.info("wrote transit_routes: %d shapes", len(shp))

        # --- SeaBus ---------------------------------------------------------
        seabus = near[near["stop_name"].astype(str).str.contains("seabus|quay", case=False, na=False)]
        if len(seabus):
            seabus.to_file(out, layer="seabus", driver="GPKG")
            log.info("wrote seabus: %d stop(s)", len(seabus))

    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
