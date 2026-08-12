#!/usr/bin/env python3
"""Build the CNV road network and derive the intersection layer.

Intersections are derived from CNV street centreline endpoints: endpoints within
`intersection_snap_tolerance_m` are clustered into a single node, and nodes joining
three or more distinct street *names* (or three or more segment ends) are treated as
intersections. Named cross-street pairs come from the segments meeting at each node.

The independently published DNV GEOweb intersection layer is used as a cross-check,
not as the primary source, because it covers the whole North Shore.

Output: data/processed/cnv_roads.gpkg
  roads              - street centrelines clipped to CNV
  intersections      - derived intersection nodes
  road_designation   - arterial/collector designation and Major Road Network
  bike_routes, speed_zones, one_way, truck_routes, traffic_calming
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union

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

log = get_logger("08_prepare_roads")

CNV_ARCGIS = "https://gisext2.cnv.org/arcgis/rest/services"


def segment_endpoints(geom):
    """Return the first and last coordinate of a (multi)linestring."""
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type == "LineString":
        coords = list(geom.coords)
        return [coords[0], coords[-1]]
    if geom.geom_type == "MultiLineString":
        parts = [g for g in geom.geoms if not g.is_empty]
        if not parts:
            return []
        return [list(parts[0].coords)[0], list(parts[-1].coords)[-1]]
    return []


def build_intersections(roads: gpd.GeoDataFrame, tol: float) -> gpd.GeoDataFrame:
    """Cluster centreline endpoints into intersection nodes."""
    records = []
    for idx, row in roads.iterrows():
        for pt in segment_endpoints(row.geometry):
            records.append((idx, pt[0], pt[1]))

    if not records:
        return gpd.GeoDataFrame(columns=["geometry"], crs=roads.crs)

    ep = pd.DataFrame(records, columns=["seg_idx", "x", "y"])
    log.info("collected %d centreline endpoints from %d segments", len(ep), len(roads))

    # Grid-snap endpoints, then merge grid cells that fall within tolerance.
    ep["cell"] = list(zip((ep["x"] / tol).round().astype(int),
                          (ep["y"] / tol).round().astype(int)))

    # Union-find over neighbouring cells so that near-coincident endpoints merge.
    parent: dict = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    cells = set(ep["cell"])
    for cx, cy in cells:
        find((cx, cy))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nb = (cx + dx, cy + dy)
                if nb in cells:
                    union((cx, cy), nb)

    ep["node"] = [find(c) for c in ep["cell"]]

    node_segments = defaultdict(set)
    node_pts = defaultdict(list)
    for _, r in ep.iterrows():
        node_segments[r["node"]].add(r["seg_idx"])
        node_pts[r["node"]].append((r["x"], r["y"]))

    name_col = "full_street_name" if "full_street_name" in roads.columns else "STREET_NAME"
    rows = []
    for node, segs in node_segments.items():
        pts = np.array(node_pts[node])
        cx, cy = pts[:, 0].mean(), pts[:, 1].mean()

        sub = roads.loc[sorted(segs)]
        names = sorted({str(n).strip() for n in sub[name_col].dropna()}) if name_col else []
        classes = sorted({str(c).strip() for c in sub["ROADCLASS"].dropna()}) if "ROADCLASS" in sub else []

        rows.append({
            "geometry": Point(cx, cy),
            "leg_count": len(segs),
            "distinct_street_names": len(names),
            "street_a": names[0] if len(names) > 0 else None,
            "street_b": names[1] if len(names) > 1 else None,
            "street_names": " / ".join(names) if names else None,
            "road_classes": " / ".join(classes) if classes else None,
            "max_lanes": pd.to_numeric(sub["NOLANES"], errors="coerce").max()
            if "NOLANES" in sub else np.nan,
        })

    nodes = gpd.GeoDataFrame(rows, crs=roads.crs)
    log.info("clustered into %d nodes", len(nodes))

    # A true intersection joins at least two distinct named streets, or is a node where
    # three or more segment ends meet (covers named-street continuations and forks).
    nodes["is_intersection"] = (
        (nodes["distinct_street_names"] >= 2) | (nodes["leg_count"] >= 3)
    )
    return nodes


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    tol = cfg["analysis"]["intersection_snap_tolerance_m"]
    boundary = load_boundary()
    out = DATA_PROCESSED / "cnv_roads.gpkg"

    # --- roads --------------------------------------------------------------
    roads = load_raw_vector("cnv/cnv_street_centreline.geojson", crs)
    roads = clip_to_cnv(roads, boundary)
    roads = roads[~roads.geometry.is_empty].copy()
    roads["length_m"] = roads.geometry.length

    # Build the full posted street name (e.g. "E 3RD ST") so that name-based joins against
    # external sources such as ICBC crash locations can succeed.
    def full_name(r):
        parts = [str(r.get(c) or "").strip() for c in ("SUF_DIR", "STREET_NAME", "STREET_TYPE")]
        parts = [p for p in parts if p and p.lower() != "nan"]
        return " ".join(parts) if parts else None

    roads["full_street_name"] = roads.apply(full_name, axis=1)
    log.info("distinct full street names: %d", roads["full_street_name"].nunique())
    roads = tag_source(roads, "City of North Vancouver ArcGIS - Street Centre Line",
                       f"{CNV_ARCGIS}/BaseMapServices/query_layers/MapServer/7")
    roads.to_file(out, layer="roads", driver="GPKG")
    log.info("roads: %d segments, %.1f km total", len(roads), roads["length_m"].sum() / 1000)

    if "ROADCLASS" in roads.columns:
        log.info("road class distribution:")
        for k, v in roads["ROADCLASS"].value_counts(dropna=False).items():
            km = roads.loc[roads["ROADCLASS"] == k, "length_m"].sum() / 1000
            log.info("    %-22s %4d segments  %6.1f km", str(k), v, km)

    # --- intersections ------------------------------------------------------
    nodes = build_intersections(roads, tol)
    inter = nodes[nodes["is_intersection"]].copy().reset_index(drop=True)
    inter["intersection_id"] = [f"CNV-INT-{i:04d}" for i in range(1, len(inter) + 1)]

    # Keep intersections strictly inside the municipality.
    inter = clip_to_cnv(inter, boundary, how="within")
    log.info("intersections inside CNV: %d (from %d clustered nodes)", len(inter), len(nodes))

    inter = tag_source(
        inter,
        "Derived from City of North Vancouver street centrelines",
        f"{CNV_ARCGIS}/BaseMapServices/query_layers/MapServer/7",
    )
    inter["derivation"] = (
        f"Centreline endpoints clustered at {tol} m tolerance; a node qualifies as an "
        "intersection when it joins 2+ distinct street names or 3+ segment ends."
    )

    # --- cross-check against the DNV GEOweb intersection layer ---------------
    try:
        geoweb = gpd.read_file(f"zip://{Path('data/raw/dnv_geoweb/TrnIntersection_shp.zip').resolve()}")
        if geoweb.crs is None:
            geoweb = geoweb.set_crs(crs)
        geoweb = geoweb.to_crs(crs)
        geoweb_cnv = clip_to_cnv(geoweb, boundary, how="within")
        log.info("GEOweb intersections falling inside CNV: %d", len(geoweb_cnv))

        if len(geoweb_cnv) and len(inter):
            joined = gpd.sjoin_nearest(
                inter[["intersection_id", "geometry"]], geoweb_cnv[["geometry"]],
                how="left", max_distance=25, distance_col="dist_m",
            )
            matched = joined["dist_m"].notna().sum()
            log.info("cross-check: %d of %d derived intersections (%.0f%%) lie within 25 m "
                     "of a GEOweb intersection", matched, len(inter), 100 * matched / len(inter))
            inter = inter.merge(
                joined.groupby("intersection_id")["dist_m"].min().rename("geoweb_match_dist_m"),
                on="intersection_id", how="left",
            )
            geoweb_cnv.to_file(out, layer="geoweb_intersections_reference", driver="GPKG")
    except Exception as exc:  # noqa: BLE001
        log.warning("GEOweb intersection cross-check unavailable: %s", exc)

    inter.to_file(out, layer="intersections", driver="GPKG")
    log.info("wrote intersections layer")

    # --- supporting network layers -----------------------------------------
    extras = [
        ("cnv/cnv_road_designation.geojson", "road_designation", "Road Designation / MRN", 48),
        ("cnv/cnv_bike_routes_existing.geojson", "bike_routes", "Bike Routes (Existing)", 22),
        ("cnv/cnv_speed_zones.geojson", "speed_zones", "Speed Zones", 149),
        ("cnv/cnv_one_way_streets.geojson", "one_way_streets", "One Way Streets", 148),
        ("cnv/cnv_truck_routes.geojson", "truck_routes", "Truck Routes", 154),
        ("cnv/cnv_traffic_calming.geojson", "traffic_calming", "Traffic Calming", 151),
        ("cnv/cnv_walkways.geojson", "walkways", "Walkways", 17),
    ]
    for raw, layer, label, lid in extras:
        try:
            gdf = load_raw_vector(raw, crs)
        except Exception as exc:  # noqa: BLE001
            log.warning("skipping %s: %s", layer, exc)
            continue
        if gdf.empty:
            log.warning("%s is empty", layer)
            continue
        gdf = clip_to_cnv(gdf, boundary)
        gdf = gdf[~gdf.geometry.is_empty]
        if gdf.empty:
            log.warning("%s has nothing inside CNV", layer)
            continue
        gdf = tag_source(gdf, f"City of North Vancouver ArcGIS - {label}",
                         f"{CNV_ARCGIS}/BaseMapServices/TransportMAP/MapServer/{lid}")
        gdf.to_file(out, layer=layer, driver="GPKG")
        log.info("wrote %-18s %5d features", layer, len(gdf))

    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
