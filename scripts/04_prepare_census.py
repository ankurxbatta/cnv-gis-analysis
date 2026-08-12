#!/usr/bin/env python3
"""Build the CNV 2021 Census dissemination-area dataset.

Steps:
  1. Identify the CNV census subdivision (CSDUID 5915051) from the StatCan CSD file.
  2. Select the dissemination areas that nest inside it.
  3. Extract those DAs' Census Profile records from the 3.6 GB British Columbia CSV,
     seeking by StatCan's own line-number index rather than parsing the whole file.
  4. Pivot the long-format profile to one row per DA.
  5. Join to DA geometry and compute derived density/share fields.

Output: data/processed/cnv_census_2021.gpkg
  layers: cnv_census_da, cnv_csd_reference

Terminology note enforced here: the 18+ measure is named adult_population_18plus_proxy
and is never called an elector or eligible-voter count.
"""
from __future__ import annotations

import csv
import io
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_INTERIM,
    DATA_PROCESSED,
    DATA_RAW,
    get_logger,
    load_study_area,
    utc_now,
)

log = get_logger("04_prepare_census")

PROFILE_ZIP = DATA_RAW / "statcan" / "98-401-X2021006_BC_CB_eng_CSV.zip"
DA_ZIP = DATA_RAW / "statcan" / "lda_000b21a_e.zip"
CSD_ZIP = DATA_RAW / "statcan" / "lcsd000b21a_e.zip"

# Characteristic IDs from the 2021 Census Profile (98-401-X2021006).
CHARS = {
    1: "population_2021",
    2: "population_2016",
    3: "population_pct_change_2016_2021",
    4: "total_private_dwellings",
    5: "occupied_private_dwellings",
    6: "statcan_population_density_km2",
    7: "land_area_km2",
    8: "age_total",
    9: "age_0_14",
    13: "age_15_64",
    14: "age_15_19",
    15: "age_20_24",
    16: "age_25_29",
    17: "age_30_34",
    18: "age_35_39",
    19: "age_40_44",
    20: "age_45_49",
    21: "age_50_54",
    22: "age_55_59",
    23: "age_60_64",
    24: "age_65_plus",
    25: "age_65_69",
    26: "age_70_74",
    27: "age_75_79",
    28: "age_80_84",
    29: "age_85_plus",
    39: "average_age",
    40: "median_age",
    41: "dwellings_by_structure_total",
    42: "dw_single_detached",
    43: "dw_semi_detached",
    44: "dw_row_house",
    45: "dw_apartment_duplex",
    46: "dw_apartment_lt5_storeys",
    47: "dw_apartment_5plus_storeys",
    48: "dw_other_single_attached",
    49: "dw_movable",
    51: "households_1_person",
    57: "average_household_size",
    1522: "citizenship_total",
    1523: "canadian_citizens",
    1524: "canadian_citizens_under_18",
    1525: "canadian_citizens_18plus",
    1526: "not_canadian_citizens",
}

ROWS_PER_GEOGRAPHY = 2631


def to_num(value: str):
    """Census counts use '...', 'F', 'x' etc. for suppressed/unavailable values."""
    v = (value or "").strip()
    if not v or v in {"...", "..", ".", "F", "x", "X", "n/a", "N/A", "-"}:
        return None
    try:
        return float(v.replace(",", ""))
    except ValueError:
        return None


def select_cnv_das(cfg: dict) -> gpd.GeoDataFrame:
    analysis_crs = cfg["crs"]["analysis"]
    csduid = cfg["study_area"]["statcan"]["csduid_expected"]

    csd = gpd.read_file(CSD_ZIP, engine="pyogrio", where=f"CSDUID = '{csduid}'")
    if len(csd) != 1:
        raise SystemExit(f"expected 1 CSD for {csduid}, got {len(csd)}")
    row = csd.iloc[0]
    log.info("CSD %s = %s (%s), StatCan land area %.4f km2",
             csduid, row["CSDNAME"], row["CSDTYPE"], row["LANDAREA"])
    if row["CSDTYPE"] != cfg["study_area"]["statcan"]["csd_type"]:
        raise SystemExit(f"CSD type is {row['CSDTYPE']}, expected CY (City) - wrong municipality")

    csd = csd.to_crs(analysis_crs)
    csd["geometry"] = csd.geometry.make_valid()

    das = gpd.read_file(DA_ZIP, engine="pyogrio", where="PRUID = '59'").to_crs(analysis_crs)
    das["geometry"] = das.geometry.make_valid()
    log.info("loaded %d British Columbia dissemination areas", len(das))

    # DAs nest exactly inside CSDs, so a representative point is an exact test.
    pts = das.copy()
    pts["geometry"] = das.geometry.representative_point()
    inside = gpd.sjoin(pts, csd[["geometry"]], predicate="within", how="inner")
    cnv = das.loc[das.index.isin(inside.index)].copy()
    log.info("selected %d dissemination areas inside the CNV CSD", len(cnv))
    return cnv, csd


def extract_profile(dauids: set[str]) -> pd.DataFrame:
    """Pull the Census Profile rows for the given DAUIDs out of the BC CSV."""
    with zipfile.ZipFile(PROFILE_ZIP) as z:
        index_name = next(n for n in z.namelist() if "Geo_starting_row" in n)
        data_name = next(n for n in z.namelist() if "_data_" in n and n.endswith(".csv"))

        # DGUID for a dissemination area is 2021S0512 + DAUID.
        wanted = {f"2021S0512{d}": d for d in dauids}
        starts: dict[int, str] = {}
        with z.open(index_name) as fh:
            for rec in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1")):
                code = rec["Geo Code"].strip().strip('"')
                if code in wanted:
                    starts[int(rec["Line Number"])] = wanted[code]

        log.info("located %d of %d DAs in the profile line index", len(starts), len(dauids))
        missing = set(dauids) - set(starts.values())
        if missing:
            log.warning("%d DAs absent from the profile index: %s",
                        len(missing), sorted(missing)[:10])

        # Build the set of line numbers to keep, then stream once.
        keep_from = sorted(starts)
        ranges = [(s, s + ROWS_PER_GEOGRAPHY) for s in keep_from]
        line_to_da = {}
        for s in keep_from:
            line_to_da[s] = starts[s]

        records = []
        wanted_chars = set(CHARS)
        ri = 0
        cur_end = -1
        cur_da = None

        log.info("streaming the British Columbia profile CSV (this reads ~3.6 GB compressed)...")
        with z.open(data_name) as fh:
            text = io.TextIOWrapper(fh, encoding="latin-1", newline="")
            header = next(text).rstrip("\n").split(",")
            # Column positions are stable in this product; resolve by name.
            idx_char = header.index("CHARACTERISTIC_ID")
            idx_val = header.index("C1_COUNT_TOTAL")
            idx_geo = header.index("ALT_GEO_CODE")

            for lineno, line in enumerate(text, start=2):
                if lineno >= cur_end:
                    while ri < len(ranges) and ranges[ri][1] <= lineno:
                        ri += 1
                    if ri >= len(ranges):
                        break
                    start, end = ranges[ri]
                    if lineno < start:
                        continue
                    cur_end = end
                    cur_da = line_to_da[start]

                parts = next(csv.reader([line]))
                try:
                    cid = int(parts[idx_char])
                except (ValueError, IndexError):
                    continue
                if cid in wanted_chars:
                    records.append((cur_da, parts[idx_geo].strip('"'), cid, parts[idx_val]))

    log.info("extracted %d profile records", len(records))
    df = pd.DataFrame(records, columns=["DAUID", "ALT_GEO_CODE", "char_id", "value"])
    if df.empty:
        raise SystemExit("no census profile records extracted - aborting rather than guessing")

    mismatch = df[df["DAUID"] != df["ALT_GEO_CODE"]]
    if not mismatch.empty:
        raise SystemExit(
            f"line-index alignment error: {len(mismatch)} rows landed on the wrong geography"
        )
    log.info("line-index alignment verified against ALT_GEO_CODE for all extracted rows")

    df["value"] = df["value"].map(to_num)
    wide = df.pivot_table(index="DAUID", columns="char_id", values="value", aggfunc="first")
    wide.columns = [CHARS[c] for c in wide.columns]
    return wide.reset_index()


def derive(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the density, proxy and share fields required by the project brief."""
    out = df.copy()

    # 18+ proxy. The Census publishes 15-19 as a single band, so the 18-19 portion is
    # apportioned as 2/5 of that band (uniform-age assumption within the band).
    out["age_18_19_estimated"] = out["age_15_19"] * (2 / 5)
    out["adult_population_18plus_proxy"] = (
        out["population_2021"] - out["age_0_14"] - out["age_15_19"] + out["age_18_19_estimated"]
    )
    out["adult_proxy_method"] = "population_2021 - age_0_14 - (3/5 * age_15_19)"

    out["senior_population_65plus"] = out["age_65_plus"]
    out["senior_population_75plus"] = (
        out[["age_75_79", "age_80_84", "age_85_plus"]].sum(axis=1, min_count=1)
    )
    out["senior_population_85plus"] = out["age_85_plus"]

    out["age_18_34_proxy"] = (
        out["age_18_19_estimated"] + out["age_20_24"] + out["age_25_29"] + out["age_30_34"]
    )
    out["age_35_49"] = out[["age_35_39", "age_40_44", "age_45_49"]].sum(axis=1, min_count=1)
    out["age_50_64"] = out[["age_50_54", "age_55_59", "age_60_64"]].sum(axis=1, min_count=1)

    area = out["land_area_km2"].where(out["land_area_km2"] > 0)
    out["population_density"] = out["population_2021"] / area
    out["adult_population_density"] = out["adult_population_18plus_proxy"] / area
    out["senior_density"] = out["senior_population_65plus"] / area
    out["housing_density"] = out["occupied_private_dwellings"] / area

    multi = out[["dw_row_house", "dw_apartment_duplex",
                 "dw_apartment_lt5_storeys", "dw_apartment_5plus_storeys"]].sum(axis=1, min_count=1)
    out["multiunit_dwellings"] = multi
    denom = out["dwellings_by_structure_total"].where(out["dwellings_by_structure_total"] > 0)
    out["multiunit_share"] = multi / denom
    out["apartment_share"] = (
        out[["dw_apartment_lt5_storeys", "dw_apartment_5plus_storeys"]].sum(axis=1, min_count=1)
        / denom
    )
    out["highrise_share"] = out["dw_apartment_5plus_storeys"] / denom
    out["townhouse_share"] = out["dw_row_house"] / denom
    out["single_family_share"] = out["dw_single_detached"] / denom
    out["one_person_household_share"] = out["households_1_person"] / denom

    # Secondary, citizenship-aware proxy. Closer to municipal elector eligibility than a
    # raw 18+ count, but 25% sample data covering private households only.
    out["canadian_citizens_18plus_proxy"] = out["canadian_citizens_18plus"]
    out["citizen_adult_density"] = out["canadian_citizens_18plus"] / area

    return out


def main() -> int:
    cfg = load_study_area()
    analysis_crs = cfg["crs"]["analysis"]
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    DATA_INTERIM.mkdir(parents=True, exist_ok=True)

    das, csd = select_cnv_das(cfg)
    dauids = set(das["DAUID"].astype(str))

    cache = DATA_INTERIM / "cnv_census_profile_wide.csv"
    if cache.exists():
        log.info("reusing cached profile extract %s", cache)
        wide = pd.read_csv(cache, dtype={"DAUID": str})
    else:
        wide = extract_profile(dauids)
        wide.to_csv(cache, index=False)
        log.info("cached profile extract -> %s", cache)

    log.info("profile coverage: %d of %d DAs returned records", len(wide), len(dauids))

    suppressed = wide["canadian_citizens_18plus"].isna().sum()
    log.info("canadian_citizens_18plus available for %d/%d DAs (%d suppressed)",
             len(wide) - suppressed, len(wide), suppressed)

    derived = derive(wide)

    gdf = das.merge(derived, on="DAUID", how="left", validate="one_to_one")
    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=analysis_crs)

    gdf["source"] = "Statistics Canada, 2021 Census Profile 98-401-X2021006 (British Columbia, DA)"
    gdf["source_url"] = (
        "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm"
    )
    gdf["boundary_source"] = "Statistics Canada 2021 DA cartographic boundary file (92-169-X)"
    gdf["license"] = "Statistics Canada Open Licence"
    gdf["adult_proxy_disclaimer"] = cfg["privacy"]["adult_population_disclaimer"].strip()
    gdf["prepared_utc"] = utc_now()

    # --- validation ---------------------------------------------------------
    pop_sum = gdf["population_2021"].sum()
    dwell_sum = gdf["occupied_private_dwellings"].sum()
    land_sum = gdf["land_area_km2"].sum()
    log.info("-" * 70)
    log.info("CNV DA totals: population=%.0f  occupied dwellings=%.0f  land area=%.3f km2",
             pop_sum, dwell_sum, land_sum)
    log.info("CSD published:  population=58120   occupied dwellings=27293  land area=11.830 km2")
    log.info("population difference vs CSD: %+.0f (%.2f%%)",
             pop_sum - 58120, 100 * (pop_sum - 58120) / 58120)
    log.info("adult_population_18plus_proxy total = %.0f", gdf["adult_population_18plus_proxy"].sum())
    log.info("canadian_citizens_18plus total      = %.0f (CSD published 41125)",
             gdf["canadian_citizens_18plus"].sum())
    log.info("seniors 65+ total                   = %.0f (CSD published 10190)",
             gdf["senior_population_65plus"].sum())

    if abs(pop_sum - 58120) / 58120 > 0.02:
        log.error("DA population sum deviates from the CSD total by more than 2%%")
        return 1

    out = DATA_PROCESSED / "cnv_census_2021.gpkg"
    gdf.to_file(out, layer="cnv_census_da", driver="GPKG")
    csd.to_file(out, layer="cnv_csd_reference", driver="GPKG")
    log.info("wrote %d DAs -> %s", len(gdf), out)

    gdf.drop(columns="geometry").to_csv(
        DATA_INTERIM / "cnv_census_da_attributes.csv", index=False
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
