#!/usr/bin/env python3
"""Build a pre-styled QGIS project for every processed layer.

A .qgz is a zip containing a .qgs XML document, so the project is written directly
rather than through PyQGIS — the macOS QGIS bundle ships a Python that will not
bootstrap standalone, and writing the XML keeps this runnable from the project venv.

Output: outputs/qgis/CNV_GIS_Analysis.qgz

Layers are grouped by theme, styled with the same palette as the web map, and the
heavy ones are switched off by default so the project opens quickly.
"""
from __future__ import annotations

import sys
import uuid
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import warnings

import geopandas as gpd
import numpy as np
import pyogrio
from pyproj import CRS

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA_PROCESSED, OUTPUTS, get_logger  # noqa: E402

log = get_logger("23_create_qgis_project")

# to_proj4 warns about lossy conversion; QGIS reads the WKT, the proj4 is a fallback.
warnings.filterwarnings("ignore", message=".*lose important projection information.*")

OUT_DIR = OUTPUTS / "qgis"
ANALYSIS_EPSG = 26910

# Same palette as the published web map.
PETROL = ["#F2EEE7", "#DDE7E5", "#B9CFCE", "#86ADB0", "#4A848E", "#0F4C5C"]
BRASS = ["#F9F4E9", "#EFE1C4", "#DFC898", "#CBA96D", "#B08D57", "#8A6A3B"]
PURPLE = ["#F5F1F3", "#E4D8DE", "#CBB4C1", "#AC8CA0", "#8A6580", "#5E4258"]
CRIMSON, INK, PETROL_S, PLUM, SAGE, STONE = (
    "#8C2F39", "#1A1917", "#0F4C5C", "#6B4E71", "#2F6B4F", "#8B857C")

# (group, gpkg, layer, title, style, visible)
#   style: ("grad", field, ramp) | ("cat", field) | ("single", colour, size) | ("outline", colour, w)
LAYERS = [
    ("1 Population and Census", "cnv_census_2021.gpkg", "cnv_census_da",
     "Population density (persons per km2)", ("grad", "population_density", PETROL), True),
    ("1 Population and Census", "cnv_census_2021.gpkg", "cnv_census_da",
     "Adults 18+ density (PROXY)", ("grad", "adult_population_density", PETROL), False),
    ("1 Population and Census", "cnv_census_2021.gpkg", "cnv_census_da",
     "Canadian citizens 18+ density", ("grad", "citizen_adult_density", PETROL), False),
    ("1 Population and Census", "cnv_census_2021.gpkg", "cnv_census_da",
     "Seniors 65+ density", ("grad", "senior_density", BRASS), False),
    ("1 Population and Census", "cnv_neighbourhoods_stats.gpkg", "cnv_neighbourhoods_stats",
     "Neighbourhoods (with statistics)", ("outline", "#57534E", 0.66), True),

    ("2 Housing", "cnv_housing.gpkg", "cnv_housing_da",
     "Apartment share", ("grad", "apartment_share", PURPLE), False),
    ("2 Housing", "cnv_housing.gpkg", "cnv_housing_da",
     "High-rise share (5+ storeys)", ("grad", "highrise_share", PURPLE), False),
    ("2 Housing", "cnv_housing.gpkg", "cnv_housing_da",
     "Housing density (dwellings per km2)", ("grad", "housing_density", PETROL), False),
    ("2 Housing", "residential_buildings.gpkg", "buildings",
     "Building footprints (11,833)", ("single", STONE, 0.06), False),
    ("2 Housing", "residential_buildings.gpkg", "seniors_housing",
     "Seniors-eligible housing", ("single", PLUM, 0.3), True),
    ("2 Housing", "cnv_housing.gpkg", "cnv_zoning", "Zoning", ("cat", "ZONING"), False),
    ("2 Housing", "cnv_housing.gpkg", "cnv_ocp_landuse",
     "OCP land use 2014", ("cat", "OCP2014_LandUse"), False),

    ("3 Elections", "cnv_elections.gpkg", "voting_places",
     "Voting places 2022", ("single", CRIMSON, 3.6), True),

    ("4 Public space", "cnv_public_space_scores.gpkg", "public_space_scores",
     "Public-space composite score", ("grad", "public_space_composite", BRASS), True),
    ("4 Public space", "cnv_roads.gpkg", "intersections",
     "Intersections (derived, 503)", ("single", STONE, 1.4), False),

    ("5 Transport", "cnv_roads.gpkg", "roads", "Street centrelines", ("cat", "ROADCLASS"), True),
    ("5 Transport", "cnv_roads.gpkg", "road_designation",
     "Road designation (MRN)", ("cat", "DESIGNATION"), False),
    ("5 Transport", "cnv_roads.gpkg", "bike_routes", "Bike routes", ("single", SAGE, 0.8), False),
    ("5 Transport", "cnv_roads.gpkg", "speed_zones", "Speed zones", ("cat", "SPEED_ZONE"), False),
    ("5 Transport", "cnv_roads.gpkg", "walkways", "Walkways", ("single", "#B4ADA2", 0.26), False),
    ("5 Transport", "cnv_transit.gpkg", "transit_routes",
     "Transit routes", ("single", PETROL_S, 0.5), False),
    ("5 Transport", "cnv_transit.gpkg", "transit_stops",
     "Transit stops (departures per weekday)", ("grad", "trips_per_weekday", PETROL), True),
    ("5 Transport", "cnv_traffic.gpkg", "signalised_intersections",
     "Signalised locations", ("single", INK, 2.2), False),
    ("5 Transport", "cnv_traffic.gpkg", "traffic_volumes",
     "Traffic volumes (38 segments only)", ("single", CRIMSON, 1.6), False),

    ("6 Parking", "cnv_parking.gpkg", "parking_occupancy",
     "On-street peak occupancy (2022-23 survey)", ("grad", "occupancy_peak", BRASS), False),
    ("6 Parking", "cnv_parking.gpkg", "parking_lots",
     "Off-street lots", ("single", PETROL_S, 2.6), False),
    ("6 Parking", "cnv_parking.gpkg", "accessible_parking",
     "Accessible parking", ("single", "#3C7C8A", 1.8), False),

    ("7 Safety", "cnv_safety.gpkg", "intersection_crashes",
     "Collisions (ICBC, name-matched)", ("grad", "crash_count", BRASS), False),

    ("8 Reference", "cnv_boundary.gpkg", "cnv_boundary",
     "CNV municipal boundary", ("outline", INK, 1.1), True),
]

GEOM_KIND = {"Point": "Point", "MultiPoint": "Point", "LineString": "Line",
             "MultiLineString": "Line", "Polygon": "Polygon", "MultiPolygon": "Polygon"}
SYMBOL_TYPE = {"Point": "marker", "Line": "line", "Polygon": "fill"}


def rgba(hex_colour: str, alpha: int = 255) -> str:
    h = hex_colour.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{alpha}"


def opt(parent, name, value, typ="QString"):
    ET.SubElement(parent, "Option", {"name": name, "type": typ, "value": str(value)})


def make_symbol(parent, idx, kind, style, colour=None, size=None):
    """Build one <symbol> element for a marker, line or fill."""
    sym = ET.SubElement(parent, "symbol", {
        "name": str(idx), "type": SYMBOL_TYPE[kind], "alpha": "1",
        "clip_to_extent": "1", "force_rhr": "0", "frame_rate": "10", "is_animated": "0"})
    ET.SubElement(sym, "data_defined_properties")
    layer = ET.SubElement(sym, "layer", {
        "class": {"marker": "SimpleMarker", "line": "SimpleLine",
                  "fill": "SimpleFill"}[SYMBOL_TYPE[kind]],
        "enabled": "1", "locked": "0", "pass": "0"})
    props = ET.SubElement(layer, "Option", {"type": "Map"})

    if SYMBOL_TYPE[kind] == "marker":
        opt(props, "name", "circle")
        opt(props, "color", rgba(colour))
        opt(props, "outline_color", rgba("#FFFFFF"))
        opt(props, "outline_width", "0.2")
        opt(props, "size", str(size or 2.2))
        opt(props, "size_unit", "MM")
        opt(props, "outline_width_unit", "MM")
        opt(props, "joinstyle", "bevel")
        opt(props, "angle", "0")
        opt(props, "offset", "0,0")
        opt(props, "scale_method", "diameter")
        opt(props, "horizontal_anchor_point", "1")
        opt(props, "vertical_anchor_point", "1")
    elif SYMBOL_TYPE[kind] == "line":
        opt(props, "line_color", rgba(colour))
        opt(props, "line_width", str(size or 0.6))
        opt(props, "line_width_unit", "MM")
        opt(props, "line_style", "solid")
        opt(props, "capstyle", "round")
        opt(props, "joinstyle", "round")
        opt(props, "offset", "0")
        opt(props, "offset_unit", "MM")
        opt(props, "use_custom_dash", "0")
    else:
        if style == "outline":
            opt(props, "color", "0,0,0,0")
            opt(props, "outline_color", rgba(colour))
            opt(props, "outline_width", str(size or 0.6))
            opt(props, "style", "no")
        else:
            opt(props, "color", rgba(colour))
            opt(props, "outline_color", rgba("#FFFFFF"))
            opt(props, "outline_width", "0.06")
            opt(props, "style", "solid")
        opt(props, "outline_style", "solid")
        opt(props, "outline_width_unit", "MM")
        opt(props, "joinstyle", "bevel")
        opt(props, "offset", "0,0")
    ET.SubElement(layer, "data_defined_properties")
    return sym


def build_renderer(maplayer, kind, style, gdf):
    mode = style[0]

    if mode == "grad":
        _, field, ramp = style
        vals = gdf[field].replace([np.inf, -np.inf], np.nan).dropna() if field in gdf else None
        if vals is None or len(vals) < 2 or vals.nunique() < 2:
            mode = "single"
        else:
            n = min(6, max(2, vals.nunique()))
            qs = sorted(set(np.quantile(vals, np.linspace(0, 1, n + 1))))
            if len(qs) < 3:
                mode = "single"
            else:
                r = ET.SubElement(maplayer, "renderer-v2", {
                    "type": "graduatedSymbol", "attr": field,
                    "graduatedMethod": "GraduatedColor",
                    "forceraster": "0", "enableorderby": "0", "symbollevels": "0"})
                ranges = ET.SubElement(r, "ranges")
                for i in range(len(qs) - 1):
                    ET.SubElement(ranges, "range", {
                        "lower": f"{qs[i]:.6f}", "upper": f"{qs[i+1]:.6f}",
                        "symbol": str(i), "render": "true",
                        "label": f"{qs[i]:,.1f} – {qs[i+1]:,.1f}"})
                syms = ET.SubElement(r, "symbols")
                step = max(1, (len(ramp) - 1) // max(1, len(qs) - 2))
                for i in range(len(qs) - 1):
                    make_symbol(syms, i, kind, "fillcolour",
                                ramp[min(len(ramp) - 1, i * step)], 2.4 if kind == "Point" else 0.9)
                src = ET.SubElement(r, "source-symbol")
                make_symbol(src, 0, kind, "fillcolour", ramp[-1], 2.4)
                return

    if mode == "cat":
        field = style[1]
        if field not in gdf:
            mode = "single"
        else:
            vals = sorted({str(v).strip() for v in gdf[field].dropna() if str(v).strip()})[:40]
            if not vals:
                mode = "single"
            else:
                r = ET.SubElement(maplayer, "renderer-v2", {
                    "type": "categorizedSymbol", "attr": field,
                    "forceraster": "0", "enableorderby": "0", "symbollevels": "0"})
                cats = ET.SubElement(r, "categories")
                for i, v in enumerate(vals):
                    ET.SubElement(cats, "category", {
                        "value": v, "symbol": str(i), "label": v, "render": "true"})
                syms = ET.SubElement(r, "symbols")
                palette = PETROL[1:] + BRASS[1:] + PURPLE[1:]
                for i, _ in enumerate(vals):
                    make_symbol(syms, i, kind, "fillcolour",
                                palette[i % len(palette)], 2.2 if kind == "Point" else 0.8)
                return

    colour = style[1] if mode in ("single", "outline") else PETROL_S
    size = style[2] if len(style) > 2 and mode in ("single", "outline") else None
    r = ET.SubElement(maplayer, "renderer-v2", {
        "type": "singleSymbol", "forceraster": "0", "enableorderby": "0", "symbollevels": "0"})
    syms = ET.SubElement(r, "symbols")
    make_symbol(syms, 0, kind, mode, colour, size)


def crs_element(parent, tag="srs"):
    crs = CRS.from_epsg(ANALYSIS_EPSG)
    holder = ET.SubElement(parent, tag)
    s = ET.SubElement(holder, "spatialrefsys")
    ET.SubElement(s, "wkt").text = crs.to_wkt()
    ET.SubElement(s, "proj4").text = crs.to_proj4()
    ET.SubElement(s, "srsid").text = "3155"
    ET.SubElement(s, "srid").text = str(ANALYSIS_EPSG)
    ET.SubElement(s, "authid").text = f"EPSG:{ANALYSIS_EPSG}"
    ET.SubElement(s, "description").text = "NAD83 / UTM zone 10N"
    ET.SubElement(s, "projectionacronym").text = "utm"
    ET.SubElement(s, "ellipsoidacronym").text = "EPSG:7019"
    ET.SubElement(s, "geographicflag").text = "false"
    return holder


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    qgis = ET.Element("qgis", {
        "projectname": "City of North Vancouver - GIS Analysis",
        "version": "3.34.0-Prizren", "saveDateTime": ""})
    ET.SubElement(qgis, "homePath", {"path": ""})
    ET.SubElement(qgis, "title").text = "City of North Vancouver - GIS Analysis"
    ET.SubElement(qgis, "autotransaction", {"active": "0"})
    ET.SubElement(qgis, "evaluateDefaultValues", {"active": "0"})
    ET.SubElement(qgis, "trust", {"active": "0"})
    crs_element(qgis, "projectCrs")

    tree = ET.SubElement(qgis, "layer-tree-group")
    projectlayers = ET.SubElement(qgis, "projectlayers")
    groups: dict[str, ET.Element] = {}

    added = skipped = 0
    for group, gpkg, layer, title, style, visible in LAYERS:
        path = DATA_PROCESSED / gpkg
        if not path.exists():
            log.warning("missing file %s", gpkg); skipped += 1; continue
        try:
            names = [n for n, _ in pyogrio.list_layers(path)]
            if layer not in names:
                log.warning("missing layer %s:%s", gpkg, layer); skipped += 1; continue
            gdf = gpd.read_file(path, layer=layer)
        except Exception as exc:  # noqa: BLE001
            log.warning("unreadable %s:%s (%s)", gpkg, layer, exc); skipped += 1; continue

        geom_name = str(gdf.geom_type.dropna().iloc[0]) if len(gdf) else "Polygon"
        kind = GEOM_KIND.get(geom_name, "Polygon")
        lid = f"{layer}_{uuid.uuid4().hex[:12]}"
        source = f"{path}|layername={layer}"

        if group not in groups:
            groups[group] = ET.SubElement(tree, "layer-tree-group", {
                "name": group, "checked": "Qt::Checked", "expanded": "1"})
        ET.SubElement(groups[group], "layer-tree-layer", {
            "id": lid, "name": title, "source": source, "providerKey": "ogr",
            "checked": "Qt::Checked" if visible else "Qt::Unchecked", "expanded": "0"})

        ml = ET.SubElement(projectlayers, "maplayer", {
            "type": "vector", "geometry": kind, "hasScaleBasedVisibilityFlag": "0",
            "minScale": "1e+08", "maxScale": "0", "simplifyDrawingHints": "1",
            "simplifyDrawingTol": "1", "simplifyMaxScale": "1",
            "simplifyLocal": "1", "simplifyAlgorithm": "0", "readOnly": "0",
            "refreshOnNotify": "0", "autoRefreshTime": "0", "autoRefreshEnabled": "0",
            "styleCategories": "AllStyleCategories"})
        ET.SubElement(ml, "id").text = lid
        ET.SubElement(ml, "datasource").text = source
        ET.SubElement(ml, "layername").text = title
        crs_element(ml, "srs")
        ET.SubElement(ml, "provider", {"encoding": "UTF-8"}).text = "ogr"
        build_renderer(ml, kind, style, gdf)
        ET.SubElement(ml, "blendMode").text = "0"
        ET.SubElement(ml, "layerOpacity").text = "0.9" if style[0] == "grad" else "1"

        added += 1
        log.info("  %-3s %-26s %s", "on" if visible else "off", group, title)

    ET.SubElement(tree, "custom-order", {"enabled": "0"})

    # Canvas framed on the municipality.
    bnd = gpd.read_file(DATA_PROCESSED / "cnv_boundary.gpkg", layer="cnv_boundary")
    x0, y0, x1, y1 = bnd.total_bounds
    pad = 400
    canvas = ET.SubElement(qgis, "mapcanvas", {"name": "theMapCanvas", "annotationsVisible": "1"})
    ET.SubElement(canvas, "units").text = "meters"
    ext = ET.SubElement(canvas, "extent")
    for tag, v in (("xmin", x0 - pad), ("ymin", y0 - pad), ("xmax", x1 + pad), ("ymax", y1 + pad)):
        ET.SubElement(ext, tag).text = f"{v:.4f}"
    ET.SubElement(canvas, "rotation").text = "0"
    crs_element(canvas, "destinationsrs")

    qgs_name = "CNV_GIS_Analysis.qgs"
    xml = ET.tostring(qgis, encoding="unicode")
    doc = ("<?xml version='1.0' encoding='UTF-8'?>\n"
           "<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>\n" + xml)

    out = OUT_DIR / "CNV_GIS_Analysis.qgz"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(qgs_name, doc)

    # Sanity check: the XML must re-parse.
    ET.fromstring(xml)

    log.info("-" * 62)
    log.info("%d layers added, %d skipped", added, skipped)
    log.info("wrote %s (%.0f KB)", out, out.stat().st_size / 1024)
    log.info("open with:  open -a QGIS-final-4_2_1 %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
