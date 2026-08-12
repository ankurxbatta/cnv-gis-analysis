#!/usr/bin/env python3
"""Build CNV election layers and tables from official published results.

All figures are AGGREGATE and officially published. No individual-level voter data is
collected, stored or derived anywhere in this pipeline.

Data transcribed from (see data/interim/elections_research.md for the full audit trail):
  * CNV "Past Election Results" - turnout and registered-elector series
  * CNV 2022 official results PDF - votes by candidate by voting place
  * CNV 2022 news release - the nine general voting locations
  * CNV election GeoRSS feed - voting place coordinates only

Output:
  data/processed/cnv_elections.gpkg  (voting_places)
  outputs/tables/polling_location_summary.csv
  outputs/tables/election_turnout_series.csv
  outputs/tables/election_results_2022_by_voting_place.csv
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_PROCESSED,
    OUTPUTS,
    get_logger,
    load_boundary,
    load_study_area,
    utc_now,
)

log = get_logger("07_prepare_elections")

SRC_PAST = "https://www.cnv.org/City-Hall/General-Local-Election/Past-Election-Results"
SRC_2022 = ("https://www.cnv.org/City-Hall/News-Room/Whats-New/2022/10/19/"
            "Official-Results-of-2022-City-Election-Announced")
SRC_PLACES = ("https://www.cnv.org/City-Hall/News-Room/Whats-New/2022/9/26/"
              "Get-Out-and-Vote-in-the-2022-Local-Election")

# --- turnout series, verbatim from the CNV "Voter Turnout by Year" table ------
TURNOUT = """year,registered_voters,turnout_pct,note
2022,41325,22.64,CNV labels this "Total Registered Voters"
2018,38163,34.0,
2014,34127,30.0,
2011,33415,21.2,
2008,31352,17.67,Mayor elected by acclamation
2005,30327,22.37,
2002,24983,26.13,
1999,23193,25.99,
1996,,18.79,registered electors not published by CNV for this year
1993,,18.89,registered electors not published by CNV for this year
1990,,21.69,registered electors not published by CNV for this year
1987,,13.33,registered electors not published by CNV for this year
1985,,18.06,registered electors not published by CNV for this year
1983,,13.50,registered electors not published by CNV for this year
1981,,23.00,registered electors not published by CNV for this year
1979,,15.42,registered electors not published by CNV for this year
1978,,7.96,registered electors not published by CNV for this year
1977,,21.80,registered electors not published by CNV for this year
1976,,14.97,registered electors not published by CNV for this year
1975,,22.90,registered electors not published by CNV for this year
1974,,13.43,registered electors not published by CNV for this year
"""

# --- 2022 voting places; coordinates from the CNV election GeoRSS feed --------
PLACES = """year,place_name,address,place_type,lat,lon
2022,Carson Graham Secondary School,2145 Jones Ave,General,49.3289347,-123.0819935
2022,Larson Elementary School,2605 Larson Rd,General,49.333373,-123.085181
2022,Memorial Recreation Centre,125 East 23rd St,General,49.3298602,-123.0694833
2022,North Shore Neighbourhood House,225 East 2nd St,General,49.3108177,-123.0743436
2022,Queen Mary Elementary School,230 West Keith Rd,General,49.3194466,-123.0781481
2022,Ridgeway Elementary School,420 East 8th St,General,49.3152172,-123.0613468
2022,Sutherland Secondary School,1860 Sutherland Ave,General,49.326000,-123.052950
2022,The Pipe Shop,115 Victory Ship Way,General,49.310256,-123.079550
2022,Westview Elementary School,641 West 17th St,General,49.323816,-123.089478
2022,North Vancouver City Hall (Conference Room A),141 West 14th St,Advance,49.320679,-123.073799
"""

# --- 2022 votes by candidate by voting place, from the official results PDF ---
# Columns: candidate, office, then the nine general places, advance, mail, special, total.
RESULTS_2022 = """candidate,office,carson_graham,larson,memorial_rec,nsn_house,queen_mary,ridgeway,sutherland,pipe_shop,westview,advance,mail,special,total,elected
"BUCHANAN, Linda",Mayor,434,252,314,418,591,625,351,610,294,1221,132,33,5275,yes
"HEYWOOD, Guy",Mayor,269,124,280,324,430,492,374,336,185,987,100,22,3923,no
"VALENTE, Tony",Councillor,350,230,319,420,563,721,427,576,244,1266,142,14,5272,yes
"BELL, Don",Councillor,383,212,353,422,588,642,424,499,254,1277,132,35,5221,yes
"GIRARD, Angela",Councillor,380,226,312,430,551,677,382,513,289,1211,150,19,5140,yes
"SHAHRIARI, Shervin",Councillor,397,187,310,343,540,560,408,406,244,1084,110,7,4596,yes
"McILROY, Jessica",Councillor,283,183,233,318,435,487,279,403,195,972,107,18,3913,yes
"BACK, Holly",Councillor,312,166,231,313,399,452,312,415,169,988,115,20,3892,yes
"McGRENERA, Kathy",Councillor,271,128,223,325,459,456,254,342,217,935,101,15,3726,no
"CATO, Jeremy",Councillor,239,109,229,294,393,407,292,351,168,848,94,10,3434,no
"BOLTENKO, Anna",Councillor,226,128,217,294,363,361,233,360,173,815,75,11,3256,no
"LACESTE, Me-An",Councillor,189,107,150,247,279,297,228,237,165,566,50,11,2526,no
"POLLY, Ron",Councillor,138,67,149,174,222,260,212,193,101,487,60,8,2071,no
"LAI, Max",Councillor,148,79,146,155,223,177,162,229,96,464,57,7,1943,no
"ANDERSON, Daniel",School Trustee,418,235,357,487,628,648,461,545,304,1336,149,25,5593,yes
"TUMANENG, Lailani",School Trustee,352,201,272,403,532,527,343,421,254,1082,128,16,4531,yes
"WILSON, Antje",School Trustee,301,178,273,348,446,586,382,429,202,1136,111,22,4414,yes
"KOLSTEE, Jullian",School Trustee,272,167,237,341,425,420,278,392,216,950,90,15,3803,no
"""

PLACE_COLS = ["carson_graham", "larson", "memorial_rec", "nsn_house", "queen_mary",
              "ridgeway", "sutherland", "pipe_shop", "westview"]
PLACE_TO_NAME = {
    "carson_graham": "Carson Graham Secondary School",
    "larson": "Larson Elementary School",
    "memorial_rec": "Memorial Recreation Centre",
    "nsn_house": "North Shore Neighbourhood House",
    "queen_mary": "Queen Mary Elementary School",
    "ridgeway": "Ridgeway Elementary School",
    "sutherland": "Sutherland Secondary School",
    "pipe_shop": "The Pipe Shop",
    "westview": "Westview Elementary School",
}


def main() -> int:
    cfg = load_study_area()
    crs = cfg["crs"]["analysis"]
    tables = OUTPUTS / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    # --- turnout -----------------------------------------------------------
    turnout = pd.read_csv(io.StringIO(TURNOUT))
    turnout["source"] = SRC_PAST
    turnout["definition_note"] = (
        "Registered electors are those on the municipal voters list, NOT the census-eligible "
        "population. CNV labels 2022 'Total Registered Voters' and earlier years 'Total "
        "Eligible Voters'; both mean electors on the list."
    )
    turnout.to_csv(tables / "election_turnout_series.csv", index=False)
    log.info("turnout series: %d elections (%d-%d)", len(turnout),
             turnout["year"].min(), turnout["year"].max())
    recent = turnout.head(5)
    for _, r in recent.iterrows():
        reg = f"{r['registered_voters']:,.0f}" if pd.notna(r["registered_voters"]) else "not published"
        log.info("    %d  registered %-12s turnout %5.2f%%", r["year"], reg, r["turnout_pct"])

    # --- results by voting place -------------------------------------------
    res = pd.read_csv(io.StringIO(RESULTS_2022))
    res["source"] = SRC_2022
    res.to_csv(tables / "election_results_2022_by_voting_place.csv", index=False)
    log.info("2022 results: %d candidates across %d offices",
             len(res), res["office"].nunique())
    for office in res["office"].unique():
        sub = res[res["office"] == office]
        won = sub[sub["elected"] == "yes"]
        log.info("    %-14s %2d candidates, %d elected, top: %s (%d votes)",
                 office, len(sub), len(won), sub.iloc[0]["candidate"], sub.iloc[0]["total"])

    # --- voting places -----------------------------------------------------
    places = pd.read_csv(io.StringIO(PLACES))
    gdf = gpd.GeoDataFrame(
        places,
        geometry=[Point(xy) for xy in zip(places["lon"], places["lat"])],
        crs="EPSG:4326",
    ).to_crs(crs)

    boundary = load_boundary().to_crs(crs)
    inside = gpd.sjoin(gdf, boundary[["geometry"]], predicate="within", how="left")
    gdf["inside_cnv_boundary"] = inside["index_right"].notna().values
    log.info("voting places: %d (%d inside the CNV boundary)",
             len(gdf), int(gdf["inside_cnv_boundary"].sum()))
    if not gdf["inside_cnv_boundary"].all():
        for _, r in gdf[~gdf["inside_cnv_boundary"]].iterrows():
            log.warning("    voting place outside the boundary: %s (%s)",
                        r["place_name"], r["address"])

    # Total ballots recorded at each general voting place, summed across offices.
    # Mayor is the cleanest per-place ballot proxy: one vote per elector.
    mayor = res[res["office"] == "Mayor"]
    mayor_by_place = {PLACE_TO_NAME[c]: int(mayor[c].sum()) for c in PLACE_COLS}
    gdf["mayoral_votes_2022"] = gdf["place_name"].map(mayor_by_place)
    gdf["mayoral_votes_note"] = (
        "Sum of mayoral votes cast at this place in 2022. CNV did not publish a 'total "
        "voters' row for 2022, so this is a lower bound on ballots cast at the place, not "
        "a ballot count."
    )

    gdf["source"] = SRC_PLACES
    gdf["coordinate_source"] = (
        "CNV election GeoRSS feed (https://gisext2.cnv.org/election/), used for coordinates "
        "only. The feed's 2022 file contains stale 2018 place/date content, so place lists "
        "come from the official 2022 news release and results PDF instead."
    )
    gdf["polling_boundary_status"] = "NOT_AVAILABLE"
    gdf["polling_boundary_note"] = (
        "CNV operates 'any voting place' elections: an elector may vote at any location in "
        "the city, so there are no polling-division catchments. No polling-division polygon "
        "dataset exists in any format. See DATA_GAPS.md."
    )
    gdf["prepared_utc"] = utc_now()

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    gdf.to_file(DATA_PROCESSED / "cnv_elections.gpkg", layer="voting_places", driver="GPKG")

    summary = gdf.drop(columns="geometry").copy()
    summary = summary.sort_values("mayoral_votes_2022", ascending=False, na_position="last")
    summary.insert(0, "rank", range(1, len(summary) + 1))
    summary["metric"] = "mayoral_votes_2022"
    summary["value"] = summary["mayoral_votes_2022"]
    summary["methodology_note"] = (
        "Ranked by mayoral votes recorded at each voting place in 2022, a lower bound on "
        "ballots cast there. CNV published no per-place ballot total for 2022. Voting places "
        "are service points, NOT catchments: electors may vote at any location in the city."
    )
    summary.to_csv(tables / "polling_location_summary.csv", index=False)

    log.info("-" * 66)
    log.info("2022 mayoral votes by voting place:")
    for _, r in summary[summary["place_type"] == "General"].iterrows():
        log.info("    %-38s %5d", r["place_name"][:38], r["mayoral_votes_2022"])
    log.info("    %-38s %5d", "(advance, mail and special polls)",
             int(mayor[["advance", "mail", "special"]].sum().sum()))
    log.info("total mayoral votes 2022 = %d", int(mayor["total"].sum()))
    log.info("-> %s", DATA_PROCESSED / "cnv_elections.gpkg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
