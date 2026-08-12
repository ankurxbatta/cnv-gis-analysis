#!/usr/bin/env python3
"""Population and age analysis at dissemination-area and neighbourhood level.

Neighbourhood figures are areally interpolated from DAs, because CNV neighbourhood
boundaries and StatCan DA boundaries do not align. The interpolation assumes uniform
population distribution within each DA and is labelled as an estimate throughout.

Outputs:
  data/processed/cnv_neighbourhoods_stats.gpkg
  outputs/tables/census_area_rankings.csv
  outputs/tables/neighbourhood_rankings.csv
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
    OUTPUTS,
    get_logger,
    load_boundary,
    load_study_area,
    utc_now,
)

log = get_logger("14_analysis_population")

COUNT_COLS = [
    "population_2021", "adult_population_18plus_proxy", "senior_population_65plus",
    "senior_population_75plus", "senior_population_85plus", "age_0_14", "age_18_34_proxy",
    "age_35_49", "age_50_64", "occupied_private_dwellings", "total_private_dwellings",
    "canadian_citizens_18plus", "multiunit_dwellings", "dw_single_detached", "dw_row_house",
    "dw_apartment_lt5_storeys", "dw_apartment_5plus_storeys", "households_1_person",
    "dwellings_by_structure_total",
]

SOURCE = "Statistics Canada, 2021 Census Profile 98-401-X2021006, dissemination areas"
METHOD_DA = "Directly from the 2021 Census Profile for that dissemination area."
METHOD_NB = ("Areally interpolated from 2021 dissemination areas into CNV neighbourhood "
             "boundaries, assuming uniform distribution within each DA. Estimate, not a count.")


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    tables = OUTPUTS / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    da = gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da").to_crs(crs)
    nb = load_boundary("cnv_neighbourhoods").to_crs(crs)
    boundary = load_boundary().to_crs(crs)

    # ------------------------------------------------------------------ DA level
    log.info("=" * 74)
    log.info("CITY TOTALS (2021 Census)")
    total_pop = da["population_2021"].sum()
    log.info("  population                     %8.0f", total_pop)
    log.info("  adult 18+ proxy                %8.0f  (%.1f%% of population)",
             da["adult_population_18plus_proxy"].sum(),
             100 * da["adult_population_18plus_proxy"].sum() / total_pop)
    log.info("  Canadian citizens 18+          %8.0f  (%.1f%% of population)",
             da["canadian_citizens_18plus"].sum(),
             100 * da["canadian_citizens_18plus"].sum() / total_pop)
    log.info("  seniors 65+                    %8.0f  (%.1f%%)",
             da["senior_population_65plus"].sum(),
             100 * da["senior_population_65plus"].sum() / total_pop)
    log.info("  seniors 85+                    %8.0f  (%.1f%%)",
             da["senior_population_85plus"].sum(),
             100 * da["senior_population_85plus"].sum() / total_pop)
    log.info("  occupied private dwellings     %8.0f", da["occupied_private_dwellings"].sum())
    log.info("  land area (km2)                %8.3f", da["land_area_km2"].sum())
    log.info("  overall population density     %8.0f /km2", total_pop / da["land_area_km2"].sum())

    log.info("-" * 74)
    log.info("DA-level density distribution (persons/km2):")
    q = da["population_density"].describe(percentiles=[.1, .25, .5, .75, .9])
    for k in ("min", "10%", "25%", "50%", "75%", "90%", "max"):
        log.info("    %-6s %10.0f", k, q[k])

    da_out = da.drop(columns="geometry").copy()
    da_out["source"] = SOURCE
    da_out["methodology_note"] = METHOD_DA
    da_out["adult_proxy_disclaimer"] = cfg["privacy"]["adult_population_disclaimer"].strip()

    rank_rows = []
    for metric in ["population_density", "adult_population_density", "senior_density",
                   "housing_density", "population_2021", "adult_population_18plus_proxy"]:
        sub = da[["DAUID", metric]].dropna().sort_values(metric, ascending=False).reset_index(drop=True)
        for i, r in sub.iterrows():
            rank_rows.append({
                "rank": i + 1,
                "feature_id": r["DAUID"],
                "feature_name": f"DA {r['DAUID']}",
                "metric": metric,
                "value": round(float(r[metric]), 2),
                "source": SOURCE,
                "methodology_note": METHOD_DA,
            })
    pd.DataFrame(rank_rows).to_csv(tables / "census_area_rankings.csv", index=False)
    log.info("wrote census_area_rankings.csv (%d rows)", len(rank_rows))

    log.info("-" * 74)
    log.info("Top 10 DAs by population density:")
    for i, r in da.nlargest(10, "population_density").iterrows():
        log.info("    DA %s  %7.0f /km2  (pop %5.0f, 18+ proxy %5.0f, %.2f km2)",
                 r["DAUID"], r["population_density"], r["population_2021"],
                 r["adult_population_18plus_proxy"], r["land_area_km2"])

    # ---------------------------------------------------- neighbourhood level
    da_area = da.geometry.area
    rows = []
    for _, n in nb.iterrows():
        inter = da.geometry.intersection(n.geometry)
        frac = (inter.area / da_area).clip(0, 1).fillna(0)
        rec = {"neighbourhood": n["neighbourhood"], "area_km2": n.geometry.area / 1e6}
        for c in COUNT_COLS:
            if c in da.columns:
                rec[c] = float((pd.to_numeric(da[c], errors="coerce").fillna(0) * frac).sum())
        rec["land_area_km2_from_da"] = float((da["land_area_km2"] * frac).sum())
        rec["geometry"] = n.geometry
        rows.append(rec)

    nbs = gpd.GeoDataFrame(rows, crs=crs)
    land = nbs["land_area_km2_from_da"].replace(0, np.nan)
    nbs["population_density"] = nbs["population_2021"] / land
    nbs["adult_population_density"] = nbs["adult_population_18plus_proxy"] / land
    nbs["senior_density"] = nbs["senior_population_65plus"] / land
    nbs["housing_density"] = nbs["occupied_private_dwellings"] / land
    denom = nbs["dwellings_by_structure_total"].replace(0, np.nan)
    nbs["apartment_share"] = (nbs["dw_apartment_lt5_storeys"] + nbs["dw_apartment_5plus_storeys"]) / denom
    nbs["townhouse_share"] = nbs["dw_row_house"] / denom
    nbs["single_family_share"] = nbs["dw_single_detached"] / denom
    nbs["multiunit_share"] = nbs["multiunit_dwellings"] / denom

    # Building counts per neighbourhood.
    try:
        bld = gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg", layer="buildings").to_crs(crs)
        bpts = bld.copy()
        bpts["geometry"] = bld.geometry.representative_point()
        j = gpd.sjoin(bpts, nbs[["neighbourhood", "geometry"]], predicate="within", how="inner")
        counts = j.groupby("neighbourhood").size()
        nbs["building_count"] = nbs["neighbourhood"].map(counts).fillna(0).astype(int)
        hts = j[j["height_m"].notna()].groupby("neighbourhood")["height_m"]
        nbs["mean_building_height_m"] = nbs["neighbourhood"].map(hts.mean()).round(1)
        nbs["max_building_height_m"] = nbs["neighbourhood"].map(hts.max()).round(1)
        nbs["buildings_with_height_known"] = nbs["neighbourhood"].map(hts.size()).fillna(0).astype(int)
    except Exception as exc:  # noqa: BLE001
        log.warning("building counts unavailable: %s", exc)

    nbs["source"] = SOURCE
    nbs["methodology_note"] = METHOD_NB
    nbs["adult_proxy_disclaimer"] = cfg["privacy"]["adult_population_disclaimer"].strip()
    nbs["prepared_utc"] = utc_now()
    nbs.to_file(DATA_PROCESSED / "cnv_neighbourhoods_stats.gpkg",
                layer="cnv_neighbourhoods_stats", driver="GPKG")

    log.info("-" * 74)
    log.info("NEIGHBOURHOOD ESTIMATES (areally interpolated from DAs)")
    log.info("  %-26s %7s %7s %8s %8s %7s", "neighbourhood", "pop", "18+", "pop/km2", "dwell", "apt%")
    for _, r in nbs.sort_values("population_2021", ascending=False).iterrows():
        log.info("  %-26s %7.0f %7.0f %8.0f %8.0f %6.0f%%",
                 r["neighbourhood"][:26], r["population_2021"],
                 r["adult_population_18plus_proxy"], r["population_density"],
                 r["occupied_private_dwellings"], 100 * (r["apartment_share"] or 0))

    interpolated_total = nbs["population_2021"].sum()
    log.info("  interpolated neighbourhood total = %.0f vs city total %.0f (%.1f%% covered)",
             interpolated_total, total_pop, 100 * interpolated_total / total_pop)

    nb_rank_rows = []
    for metric in ["population_density", "adult_population_density", "senior_density",
                   "housing_density", "apartment_share", "population_2021"]:
        sub = nbs[["neighbourhood", metric]].dropna().sort_values(metric, ascending=False).reset_index(drop=True)
        for i, r in sub.iterrows():
            nb_rank_rows.append({
                "rank": i + 1,
                "feature_id": r["neighbourhood"],
                "feature_name": r["neighbourhood"],
                "metric": metric,
                "value": round(float(r[metric]), 4),
                "source": SOURCE,
                "methodology_note": METHOD_NB,
            })
    pd.DataFrame(nb_rank_rows).to_csv(tables / "neighbourhood_rankings.csv", index=False)
    log.info("wrote neighbourhood_rankings.csv (%d rows)", len(nb_rank_rows))

    da_out.to_csv(tables / "census_da_full.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
