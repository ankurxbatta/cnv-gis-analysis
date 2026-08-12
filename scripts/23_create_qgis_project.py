#!/usr/bin/env python3
"""Build a pre-styled QGIS project for the City of North Vancouver analysis.

Written with PyQGIS so QGIS itself serialises the project. An earlier version
hand-wrote the .qgs XML and got coordinate handling subtly wrong — the basemap
rendered in southern France — which is exactly the class of bug you avoid by
letting the application write its own format.

Run through the wrapper, which boots QGIS's bundled Python:

    ./scripts/run_qgis_python.sh scripts/23_create_qgis_project.py

Output: outputs/qgis/CNV_GIS_Analysis.qgz
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
OUT_DIR = ROOT / "outputs" / "qgis"
ANALYSIS_CRS = "EPSG:26910"

# Same palette as the published web map.
PETROL = ["#F2EEE7", "#DDE7E5", "#B9CFCE", "#86ADB0", "#4A848E", "#0F4C5C"]
BRASS = ["#F9F4E9", "#EFE1C4", "#DFC898", "#CBA96D", "#B08D57", "#8A6A3B"]
PURPLE = ["#F5F1F3", "#E4D8DE", "#CBB4C1", "#AC8CA0", "#8A6580", "#5E4258"]
CRIMSON, INK, PETROL_S, PLUM, SAGE, STONE = (
    "#8C2F39", "#1A1917", "#0F4C5C", "#6B4E71", "#2F6B4F", "#8B857C")


BASEMAP_URL = ("type=xyz&url=https://a.basemaps.cartocdn.com/rastertiles/voyager/"
               "%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0")

LAYERS = [
    # --- drawn on TOP: points and outlines -------------------------------
    ("1 Elections", "cnv_elections.gpkg", "voting_places",
     "Voting places 2022", ("single", CRIMSON, 3.6), True),

    ("2 Public space", "cnv_public_space_scores.gpkg", "public_space_scores",
     "Public-space composite score", ("grad", "public_space_composite", BRASS), True),
    ("2 Public space", "cnv_roads.gpkg", "intersections",
     "Intersections (derived, 503)", ("single", STONE, 1.4), False),

    ("3 Transport", "cnv_transit.gpkg", "transit_stops",
     "Transit stops (departures per weekday)", ("grad", "trips_per_weekday", PETROL), False),
    ("3 Transport", "cnv_traffic.gpkg", "signalised_intersections",
     "Signalised locations", ("single", INK, 2.2), False),
    ("3 Transport", "cnv_transit.gpkg", "transit_routes",
     "Transit routes", ("single", PETROL_S, 0.5), False),
    ("3 Transport", "cnv_roads.gpkg", "bike_routes", "Bike routes", ("single", SAGE, 0.8), False),
    ("3 Transport", "cnv_traffic.gpkg", "traffic_volumes",
     "Traffic volumes (38 segments only)", ("single", CRIMSON, 1.6), False),
    ("3 Transport", "cnv_roads.gpkg", "speed_zones", "Speed zones", ("cat", "SPEED_ZONE"), False),
    ("3 Transport", "cnv_roads.gpkg", "road_designation",
     "Road designation (MRN)", ("cat", "DESIGNATION"), False),
    ("3 Transport", "cnv_roads.gpkg", "walkways", "Walkways", ("single", "#B4ADA2", 0.26), False),
    ("3 Transport", "cnv_roads.gpkg", "roads", "Street centrelines", ("cat", "ROADCLASS"), False),

    ("4 Parking", "cnv_parking.gpkg", "parking_lots",
     "Off-street lots", ("single", PETROL_S, 2.6), False),
    ("4 Parking", "cnv_parking.gpkg", "accessible_parking",
     "Accessible parking", ("single", "#3C7C8A", 1.8), False),
    ("4 Parking", "cnv_parking.gpkg", "parking_occupancy",
     "On-street peak occupancy (2022-23 survey)", ("grad", "occupancy_peak", BRASS), False),

    ("5 Safety", "cnv_safety.gpkg", "intersection_crashes",
     "Collisions (ICBC, name-matched)", ("grad", "crash_count", BRASS), False),

    ("6 Boundaries", "cnv_boundary.gpkg", "cnv_boundary",
     "CNV municipal boundary", ("outline", INK, 1.1), True),
    ("6 Boundaries", "cnv_neighbourhoods_stats.gpkg", "cnv_neighbourhoods_stats",
     "Neighbourhoods (with statistics)", ("outline", "#57534E", 0.66), True),

    # --- drawn UNDERNEATH: the filled polygons ----------------------------
    ("7 Housing", "residential_buildings.gpkg", "seniors_housing",
     "Seniors-eligible housing", ("single", PLUM, 0.3), False),
    ("7 Housing", "residential_buildings.gpkg", "buildings",
     "Building footprints (11,833)", ("single", STONE, 0.06), False),
    ("7 Housing", "cnv_housing.gpkg", "cnv_housing_da",
     "Apartment share", ("grad", "apartment_share", PURPLE), False),
    ("7 Housing", "cnv_housing.gpkg", "cnv_housing_da",
     "High-rise share (5+ storeys)", ("grad", "highrise_share", PURPLE), False),
    ("7 Housing", "cnv_housing.gpkg", "cnv_housing_da",
     "Housing density (dwellings per km2)", ("grad", "housing_density", PETROL), False),
    ("7 Housing", "cnv_housing.gpkg", "cnv_zoning", "Zoning", ("cat", "ZONING"), False),
    ("7 Housing", "cnv_housing.gpkg", "cnv_ocp_landuse",
     "OCP land use 2014", ("cat", "OCP2014_LandUse"), False),

    ("8 Population and Census", "cnv_census_2021.gpkg", "cnv_census_da",
     "Population density (persons per km2)", ("grad", "population_density", PETROL), True),
    ("8 Population and Census", "cnv_census_2021.gpkg", "cnv_census_da",
     "Adults 18+ density (PROXY)", ("grad", "adult_population_density", PETROL), False),
    ("8 Population and Census", "cnv_census_2021.gpkg", "cnv_census_da",
     "Canadian citizens 18+ density", ("grad", "citizen_adult_density", PETROL), False),
    ("8 Population and Census", "cnv_census_2021.gpkg", "cnv_census_da",
     "Seniors 65+ density", ("grad", "senior_density", BRASS), False),
]


def main() -> int:
    from qgis.core import (  # noqa: PLC0415
        QgsApplication, QgsCategorizedSymbolRenderer, QgsClassificationQuantile,
        QgsCoordinateReferenceSystem, QgsFillSymbol, QgsGradientColorRamp,
        QgsGraduatedSymbolRenderer, QgsLineSymbol, QgsMarkerSymbol, QgsProject,
        QgsRasterLayer, QgsRectangle, QgsReferencedRectangle, QgsRendererCategory,
        QgsSingleSymbolRenderer, QgsSymbol, QgsVectorLayer,
    )
    from qgis.PyQt.QtGui import QColor  # noqa: PLC0415

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    QgsApplication.setPrefixPath(os.environ.get("QGIS_PREFIX_PATH", ""), True)
    app = QgsApplication([], False)
    app.initQgis()

    project = QgsProject.instance()
    project.clear()
    crs = QgsCoordinateReferenceSystem(ANALYSIS_CRS)
    if not crs.isValid():
        print(f"FATAL: {ANALYSIS_CRS} did not resolve"); return 1
    project.setCrs(crs)
    project.setTitle("City of North Vancouver - GIS Analysis")
    print(f"project CRS: {crs.authid()} - {crs.description()}")

    root = project.layerTreeRoot()
    groups: dict = {}

    def styled(layer, spec):
        gt = layer.geometryType()          # 0 point, 1 line, 2 polygon
        mode = spec[0]

        if mode == "grad":
            _, field, ramp = spec
            base = QgsSymbol.defaultSymbol(gt)
            if gt == 0:
                base.setSize(2.4)
            elif gt == 1:
                base.setWidth(0.9)
            else:
                base.symbolLayer(0).setStrokeColor(QColor("#FFFFFF"))
                base.symbolLayer(0).setStrokeWidth(0.06)
            r = QgsGraduatedSymbolRenderer(field)
            r.setSourceSymbol(base)
            r.setClassificationMethod(QgsClassificationQuantile())
            r.updateClasses(layer, 6)
            r.updateColorRamp(QgsGradientColorRamp(QColor(ramp[0]), QColor(ramp[-1])))
            return r

        if mode == "cat":
            field = spec[1]
            idx = layer.fields().indexFromName(field)
            if idx < 0:
                return None
            vals = sorted({str(v).strip() for v in layer.uniqueValues(idx)
                           if v is not None and str(v).strip()})[:40]
            if not vals:
                return None
            palette = PETROL[1:] + BRASS[1:] + PURPLE[1:]
            cats = []
            for i, v in enumerate(vals):
                sym = QgsSymbol.defaultSymbol(gt)
                sym.setColor(QColor(palette[i % len(palette)]))
                if gt == 1:
                    sym.setWidth(0.7)
                cats.append(QgsRendererCategory(v, sym, v))
            return QgsCategorizedSymbolRenderer(field, cats)

        colour, size = spec[1], spec[2]
        if gt == 0:
            sym = QgsMarkerSymbol.createSimple(
                {"name": "circle", "color": colour, "size": str(size or 2.2),
                 "outline_color": "#FFFFFF", "outline_width": "0.2"})
        elif gt == 1:
            sym = QgsLineSymbol.createSimple({"color": colour, "width": str(size or 0.6)})
        elif mode == "outline":
            sym = QgsFillSymbol.createSimple(
                {"style": "no", "outline_color": colour, "outline_width": str(size or 0.6)})
        else:
            sym = QgsFillSymbol.createSimple(
                {"color": colour, "outline_color": "#FFFFFF", "outline_width": "0.05"})
        return QgsSingleSymbolRenderer(sym)

    added = skipped = 0
    for group, gpkg, layer_name, title, spec, visible in LAYERS:
        path = PROCESSED / gpkg
        if not path.exists():
            print(f"  skip  {gpkg} (missing)"); skipped += 1; continue
        vl = QgsVectorLayer(f"{path}|layername={layer_name}", title, "ogr")
        if not vl.isValid():
            print(f"  skip  {gpkg}:{layer_name} (invalid)"); skipped += 1; continue

        r = styled(vl, spec)
        if r is not None:
            vl.setRenderer(r)
        vl.setOpacity(0.62 if spec[0] == "grad" else 1.0)

        project.addMapLayer(vl, False)
        if group not in groups:
            groups[group] = root.addGroup(group)
        groups[group].addLayer(vl).setItemVisibilityChecked(visible)
        added += 1
        print(f"  {'on ' if visible else 'off'}  {group:<26} {title}")

    # Basemap added last so it sits beneath every vector layer.
    bm = QgsRasterLayer(BASEMAP_URL, "Basemap - CARTO Voyager", "wms")
    if bm.isValid():
        project.addMapLayer(bm, False)
        root.addGroup("9 Basemap").addLayer(bm).setItemVisibilityChecked(True)
        print(f"  on   9 Basemap                  {bm.name()} [{bm.crs().authid()}]")
        added += 1
    else:
        print("  WARNING: basemap layer invalid")

    # Frame the canvas on the municipality.
    bnd = next((l for l in project.mapLayers().values()
                if l.name() == "CNV municipal boundary"), None)
    if bnd is not None:
        e = QgsRectangle(bnd.extent()); e.grow(400)
        project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(e, crs))
        print(f"  canvas framed on {e.width():.0f} x {e.height():.0f} m")

    out = OUT_DIR / "CNV_GIS_Analysis.qgz"
    ok = project.write(str(out))
    project.clear()
    app.exitQgis()

    print(f"\n{added} layers, {skipped} skipped")
    print(f"{'wrote' if ok else 'FAILED'} {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
