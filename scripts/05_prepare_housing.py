#!/usr/bin/env python3
"""Build the DA-level housing layer and the zoning / OCP land-use context layers.

Output: data/processed/cnv_housing.gpkg
  cnv_housing_da    - dissemination areas with dwelling structure counts and shares
  cnv_zoning        - zoning boundaries clipped to CNV
  cnv_ocp_landuse   - 2014 OCP land use clipped to CNV
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd

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

log = get_logger("05_prepare_housing")

HOUSING_COLS = [
    "DAUID", "population_2021", "total_private_dwellings", "occupied_private_dwellings",
    "dwellings_by_structure_total", "dw_single_detached", "dw_semi_detached", "dw_row_house",
    "dw_apartment_duplex", "dw_apartment_lt5_storeys", "dw_apartment_5plus_storeys",
    "dw_other_single_attached", "dw_movable", "households_1_person", "average_household_size",
    "multiunit_dwellings", "multiunit_share", "apartment_share", "highrise_share",
    "townhouse_share", "single_family_share", "one_person_household_share",
    "housing_density", "land_area_km2",
]


def dominant_type(row) -> str:
    counts = {
        "SINGLE_DETACHED": row.get("dw_single_detached") or 0,
        "SEMI_DETACHED": row.get("dw_semi_detached") or 0,
        "ROW_HOUSE": row.get("dw_row_house") or 0,
        "APARTMENT_DUPLEX": row.get("dw_apartment_duplex") or 0,
        "APARTMENT_LT5": row.get("dw_apartment_lt5_storeys") or 0,
        "APARTMENT_5PLUS": row.get("dw_apartment_5plus_storeys") or 0,
    }
    if not any(counts.values()):
        return "UNKNOWN"
    return max(counts, key=counts.get)


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    boundary = load_boundary()
    out = DATA_PROCESSED / "cnv_housing.gpkg"

    census = gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da")
    cols = [c for c in HOUSING_COLS if c in census.columns]
    housing = census[cols + ["geometry"]].copy()

    housing["dominant_dwelling_type"] = housing.apply(dominant_type, axis=1)
    housing["dwellings_per_km2"] = housing["housing_density"]
    housing["persons_per_dwelling"] = (
        housing["population_2021"] / housing["occupied_private_dwellings"].replace(0, None)
    )

    housing = tag_source(
        housing,
        "Statistics Canada, 2021 Census Profile 98-401-X2021006 (dwelling structure type)",
        "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm",
        "Statistics Canada Open Licence",
    )
    housing.to_file(out, layer="cnv_housing_da", driver="GPKG")
    log.info("wrote cnv_housing_da: %d DAs", len(housing))

    total = housing["dwellings_by_structure_total"].sum()
    log.info("CNV dwelling mix (occupied private dwellings by structure, n=%.0f):", total)
    for label, col in [
        ("single-detached", "dw_single_detached"),
        ("semi-detached", "dw_semi_detached"),
        ("row house", "dw_row_house"),
        ("apartment in duplex", "dw_apartment_duplex"),
        ("apartment <5 storeys", "dw_apartment_lt5_storeys"),
        ("apartment 5+ storeys", "dw_apartment_5plus_storeys"),
    ]:
        v = housing[col].sum()
        log.info("    %-24s %7.0f  (%4.1f%%)", label, v, 100 * v / total)
    log.info("    %-24s %7.1f%%", "multi-unit share", 100 * housing["multiunit_dwellings"].sum() / total)

    log.info("dominant dwelling type by DA count:")
    for k, v in housing["dominant_dwelling_type"].value_counts().items():
        log.info("    %-20s %d DAs", k, v)

    # --- zoning and land use ------------------------------------------------
    for raw, layer, label in [
        ("cnv/cnv_zoning.geojson", "cnv_zoning", "zoning boundaries"),
        ("cnv/cnv_ocp_landuse.geojson", "cnv_ocp_landuse", "2014 OCP land use"),
    ]:
        try:
            gdf = load_raw_vector(raw, crs)
        except Exception as exc:  # noqa: BLE001
            log.warning("could not load %s: %s", raw, exc)
            continue
        if gdf.empty:
            log.warning("%s is empty - skipping", label)
            continue
        gdf = clip_to_cnv(gdf, boundary)
        gdf = gdf[~gdf.geometry.is_empty]
        gdf["area_km2"] = gdf.geometry.area / 1e6
        gdf = tag_source(
            gdf,
            f"City of North Vancouver ArcGIS - {label}",
            "https://gisext2.cnv.org/arcgis/rest/services/BaseMapServices/TransportMAP/MapServer",
        )
        gdf.to_file(out, layer=layer, driver="GPKG")
        log.info("wrote %s: %d features, %.2f km2", layer, len(gdf), gdf["area_km2"].sum())

    log.info("-> %s", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
