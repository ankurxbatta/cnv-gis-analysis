#!/usr/bin/env python3
"""Generate the static map series into outputs/maps/.

Every map carries a title, legend, scale bar, north arrow and source attribution.
Maps whose underlying data is a proxy or has partial coverage say so on the figure.
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA_PROCESSED, OUTPUTS, get_logger, load_boundary  # noqa: E402

log = get_logger("18_create_maps")
MAPS = OUTPUTS / "maps"

ATTRIB = ("Sources: Statistics Canada 2021 Census (98-401-X2021006); City of North Vancouver "
          "ArcGIS; BC ABMS; TransLink GTFS; ICBC.\nAnalysis CRS EPSG:26910. "
          "Prepared by the CNV GIS analysis pipeline.")


def scale_bar(ax, length_m=1000, location=(0.07, 0.04)):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    sx = x0 + (x1 - x0) * location[0]
    sy = y0 + (y1 - y0) * location[1]
    ax.plot([sx, sx + length_m], [sy, sy], color="black", lw=3, solid_capstyle="butt", zorder=10)
    ax.text(sx + length_m / 2, sy + (y1 - y0) * 0.012, f"{length_m/1000:.0f} km",
            ha="center", va="bottom", fontsize=8, zorder=10)


def north_arrow(ax, location=(0.95, 0.10)):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    nx = x0 + (x1 - x0) * location[0]
    ny = y0 + (y1 - y0) * location[1]
    ax.annotate("N", xy=(nx, ny), xytext=(nx, ny - (y1 - y0) * 0.05),
                arrowprops=dict(facecolor="black", width=3, headwidth=9),
                ha="center", va="center", fontsize=11, fontweight="bold", zorder=10)


def finish(ax, fig, title, subtitle, outfile, note=None):
    ax.set_title(title, fontsize=15, fontweight="bold", loc="left", pad=14)
    ax.text(0.0, 1.008, subtitle, transform=ax.transAxes, fontsize=9.5,
            color="#333", va="bottom")
    ax.set_axis_off()
    scale_bar(ax)
    north_arrow(ax)
    footer = ATTRIB if not note else f"{note}\n{ATTRIB}"
    fig.text(0.01, 0.012, footer, fontsize=7, color="#444", va="bottom")
    fig.subplots_adjust(bottom=0.13)
    fig.savefig(MAPS / outfile, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    log.info("wrote %s", outfile)


def choropleth(gdf, column, title, subtitle, outfile, cmap="viridis", legend_label="",
               note=None, boundary=None, scheme="quantiles", k=6):
    fig, ax = plt.subplots(figsize=(11, 9))
    if boundary is not None:
        boundary.plot(ax=ax, facecolor="#f2f2f2", edgecolor="none", zorder=0)
    data = gdf[gdf[column].notna()]
    data.plot(column=column, ax=ax, cmap=cmap, scheme=scheme, k=k,
              legend=True, edgecolor="white", linewidth=0.3,
              legend_kwds={"title": legend_label or column, "loc": "upper right",
                           "fontsize": 8, "title_fontsize": 9, "frameon": True})
    missing = gdf[gdf[column].isna()]
    if len(missing):
        missing.plot(ax=ax, facecolor="#dddddd", edgecolor="white", linewidth=0.3, hatch="///")
    if boundary is not None:
        boundary.boundary.plot(ax=ax, color="black", linewidth=1.2, zorder=5)
    finish(ax, fig, title, subtitle, outfile, note)


def main() -> int:
    MAPS.mkdir(parents=True, exist_ok=True)
    boundary = load_boundary()
    census = gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da")
    housing = gpd.read_file(DATA_PROCESSED / "cnv_housing.gpkg", layer="cnv_housing_da")
    roads = gpd.read_file(DATA_PROCESSED / "cnv_roads.gpkg", layer="roads")
    nbs = load_boundary("cnv_neighbourhoods")

    # 1 population density
    choropleth(census, "population_density",
               "Map 1 - Population density, City of North Vancouver",
               "Residents per square kilometre by dissemination area, 2021 Census",
               "map_01_population_density.png", "YlOrRd", "persons / km²", boundary=boundary)

    # 2 adult proxy
    choropleth(census, "adult_population_density",
               "Map 2 - Adult population density (18+ proxy)",
               "Residents aged 18+ per km² by dissemination area, 2021 Census",
               "map_02_adult_population_proxy.png", "PuBuGn", "18+ persons / km²",
               note="PROXY: population aged 18+ is a demographic proxy for potential "
                    "electorate size. It is NOT a count of eligible or registered electors.",
               boundary=boundary)

    # 3 age distribution panels
    age_cols = [("age_18_34_proxy", "Aged 18-34 (proxy)"), ("age_35_49", "Aged 35-49"),
                ("age_50_64", "Aged 50-64"), ("senior_population_65plus", "Aged 65+"),
                ("senior_population_75plus", "Aged 75+"), ("senior_population_85plus", "Aged 85+")]
    fig, axes = plt.subplots(2, 3, figsize=(17, 11))
    for ax, (col, label) in zip(axes.ravel(), age_cols):
        d = census.copy()
        d["_v"] = d[col] / d["land_area_km2"]
        d.plot(column="_v", ax=ax, cmap="magma_r", scheme="quantiles", k=5,
               edgecolor="white", linewidth=0.2, legend=True,
               legend_kwds={"fontsize": 6, "loc": "upper right"})
        boundary.boundary.plot(ax=ax, color="black", linewidth=0.8)
        ax.set_title(f"{label} - persons/km²", fontsize=10, fontweight="bold")
        ax.set_axis_off()
    fig.suptitle("Map 3 - Age distribution by dissemination area, 2021 Census",
                 fontsize=15, fontweight="bold", x=0.02, ha="left")
    fig.text(0.01, 0.01, "The 18-34 band is a proxy: the Census publishes 15-19 as one band, "
                         "so ages 18-19 are apportioned as 2/5 of it.\n" + ATTRIB,
             fontsize=7, color="#444")
    fig.savefig(MAPS / "map_03_age_distribution.png", dpi=170, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    log.info("wrote map_03_age_distribution.png")

    # 4 housing structure
    choropleth(housing, "multiunit_share",
               "Map 4 - Multi-unit dwelling share",
               "Share of occupied private dwellings that are apartments, row houses or duplexes",
               "map_04_housing_structure.png", "BuPu", "multi-unit share", boundary=boundary)
    choropleth(housing, "highrise_share",
               "Map 4b - High-rise apartment share (5+ storeys)",
               "Share of occupied private dwellings in buildings of five or more storeys",
               "map_04b_highrise_share.png", "RdPu", "high-rise share", boundary=boundary)

    # 5 building density
    try:
        blds = gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg", layer="buildings")
        fig, ax = plt.subplots(figsize=(11, 9))
        boundary.plot(ax=ax, facecolor="#f7f7f7", edgecolor="black", linewidth=1.2)
        blds.plot(ax=ax, facecolor="#4a5b6b", edgecolor="none", linewidth=0)
        finish(ax, fig, "Map 5 - Building footprints",
               f"{len(blds):,} building footprints, City of North Vancouver",
               "map_05_building_density.png",
               note="The City publishes height, unit counts or year built for under 1% of "
                    "footprints, so no unit-count surface can be mapped.")
    except Exception as exc:  # noqa: BLE001
        log.warning("map 5 skipped: %s", exc)

    # 6 seniors residences
    try:
        sen = gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg", layer="seniors_housing")
        fig, ax = plt.subplots(figsize=(11, 9))
        boundary.plot(ax=ax, facecolor="#f7f7f7", edgecolor="black", linewidth=1.2)
        roads.plot(ax=ax, color="#cccccc", linewidth=0.4)
        census.plot(column="senior_density", ax=ax, cmap="Oranges", alpha=0.75,
                    scheme="quantiles", k=5, edgecolor="white", linewidth=0.2,
                    legend=True, legend_kwds={"title": "65+ per km²", "fontsize": 8,
                                              "loc": "upper right"})
        sen.geometry.representative_point().plot(ax=ax, color="#111", markersize=55,
                                                 marker="*", zorder=6)
        finish(ax, fig, "Map 6 - Seniors housing and senior population density",
               f"{len(sen)} municipally identified seniors-eligible housing sites over "
               "65+ population density",
               "map_06_seniors_residences.png",
               note="Seniors sites are identified from the City's Affordable Housing "
                    "eligibility and occupancy attributes. Licensed care facilities are "
                    "held separately - see DATA_GAPS.md.")
    except Exception as exc:  # noqa: BLE001
        log.warning("map 6 skipped: %s", exc)

    # 7 voting locations
    try:
        vp = gpd.read_file(DATA_PROCESSED / "cnv_elections.gpkg", layer="voting_places")
        fig, ax = plt.subplots(figsize=(11, 9))
        census.plot(column="adult_population_density", ax=ax, cmap="Blues", scheme="quantiles",
                    k=5, edgecolor="white", linewidth=0.2, alpha=0.85, legend=True,
                    legend_kwds={"title": "18+ per km² (proxy)", "fontsize": 8,
                                 "loc": "upper right"})
        boundary.boundary.plot(ax=ax, color="black", linewidth=1.2)
        gen = vp[vp["place_type"] == "General"]
        adv = vp[vp["place_type"] == "Advance"]
        gen.plot(ax=ax, color="#c1121f", markersize=90, marker="o", edgecolor="white", zorder=6)
        adv.plot(ax=ax, color="#003049", markersize=120, marker="s", edgecolor="white", zorder=6)
        for _, r in vp.iterrows():
            ax.annotate(r["place_name"][:26], xy=(r.geometry.x, r.geometry.y),
                        xytext=(6, 5), textcoords="offset points", fontsize=6.5,
                        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
        ax.legend(handles=[
            Line2D([], [], marker="o", color="w", markerfacecolor="#c1121f", markersize=9,
                   label="General voting place (2022)"),
            Line2D([], [], marker="s", color="w", markerfacecolor="#003049", markersize=9,
                   label="Advance voting place (2022)")],
            loc="lower right", fontsize=8, frameon=True)
        finish(ax, fig, "Map 7 - 2022 voting places and adult population proxy",
               "Nine general voting places plus advance voting at City Hall",
               "map_07_voting_locations.png",
               note="CNV runs 'any voting place' elections, so there are NO polling-division "
                    "catchments. No polling-division boundary dataset exists.")
    except Exception as exc:  # noqa: BLE001
        log.warning("map 7 skipped: %s", exc)

    # 8 road hierarchy
    fig, ax = plt.subplots(figsize=(11, 9))
    boundary.plot(ax=ax, facecolor="#fafafa", edgecolor="black", linewidth=1.2)
    colours = {"freeway": "#8b0000", "arterial": "#d1495b", "Major": "#e07a5f",
               "collector": "#f2cc8f", "Minor": "#a8b8a0", "local": "#c9c9c9",
               "ramp": "#6d597a", "lane": "#dddddd", "strata": "#dddddd"}
    widths = {"freeway": 3.2, "arterial": 2.6, "Major": 2.2, "collector": 1.6,
              "Minor": 1.0, "local": 0.6, "ramp": 1.4, "lane": 0.4, "strata": 0.4}
    for cls, grp in roads.groupby("ROADCLASS"):
        grp.plot(ax=ax, color=colours.get(cls, "#bbbbbb"), linewidth=widths.get(cls, 0.6))
    ax.legend(handles=[Line2D([], [], color=colours.get(c, "#bbb"), lw=widths.get(c, 1),
                              label=f"{c}") for c in colours if c in set(roads["ROADCLASS"])],
              loc="lower right", fontsize=8, title="Road class", frameon=True)
    finish(ax, fig, "Map 8 - Road hierarchy",
           f"{len(roads)} street centreline segments, {roads['length_m'].sum()/1000:.0f} km",
           "map_08_roads.png")

    # 9 traffic
    try:
        tv = gpd.read_file(DATA_PROCESSED / "cnv_traffic.gpkg", layer="traffic_volumes")
        sig = gpd.read_file(DATA_PROCESSED / "cnv_traffic.gpkg", layer="signalised_intersections")
        fig, ax = plt.subplots(figsize=(11, 9))
        boundary.plot(ax=ax, facecolor="#fafafa", edgecolor="black", linewidth=1.2)
        roads.plot(ax=ax, color="#dddddd", linewidth=0.5)
        tv.plot(ax=ax, column="volume", cmap="plasma", linewidth=3.4, legend=True,
                legend_kwds={"label": "directional volume (as published)", "shrink": 0.5})
        full = sig[sig["has_full_signal"]] if "has_full_signal" in sig else sig
        full.plot(ax=ax, color="#111", markersize=22, marker="^", zorder=6)
        finish(ax, fig, "Map 9 - Traffic volumes and signalised intersections",
               f"{len(tv)} segments with published directional volumes; "
               f"{len(full)} locations with a full traffic signal",
               "map_09_traffic.png",
               note="COVERAGE WARNING: directional volumes are published for only "
                    f"{len(tv)} of {len(roads)} street segments. No AADT is published for any "
                    "CNV municipal street, and no signal timing is published anywhere.")
    except Exception as exc:  # noqa: BLE001
        log.warning("map 9 skipped: %s", exc)

    # 10 transit
    try:
        stops = gpd.read_file(DATA_PROCESSED / "cnv_transit.gpkg", layer="transit_stops")
        rts = gpd.read_file(DATA_PROCESSED / "cnv_transit.gpkg", layer="transit_routes")
        fig, ax = plt.subplots(figsize=(11, 9))
        boundary.plot(ax=ax, facecolor="#fafafa", edgecolor="black", linewidth=1.2)
        roads.plot(ax=ax, color="#e8e8e8", linewidth=0.4)
        rts.plot(ax=ax, color="#2a9d8f", linewidth=1.1, alpha=0.7)
        s = stops[stops["in_cnv"]] if "in_cnv" in stops else stops
        s.plot(ax=ax, markersize=s["trips_per_weekday"].clip(1, 400) / 3 + 6,
               color="#264653", alpha=0.8, edgecolor="white", linewidth=0.4)
        finish(ax, fig, "Map 10 - Transit routes and stops",
               f"{len(s)} stops in CNV, {int(s['trips_per_weekday'].sum()):,} scheduled "
               "weekday departures; marker size is departures per weekday",
               "map_10_transit.png",
               note="Frequency from the TransLink GTFS feed for a representative weekday.")
    except Exception as exc:  # noqa: BLE001
        log.warning("map 10 skipped: %s", exc)

    # 11 parking
    try:
        occ = gpd.read_file(DATA_PROCESSED / "cnv_parking.gpkg", layer="parking_occupancy")
        lots = gpd.read_file(DATA_PROCESSED / "cnv_parking.gpkg", layer="parking_lots")
        fig, ax = plt.subplots(figsize=(11, 9))
        boundary.plot(ax=ax, facecolor="#fafafa", edgecolor="black", linewidth=1.2)
        roads.plot(ax=ax, color="#eeeeee", linewidth=0.4)
        occ.plot(ax=ax, column="occupancy_peak", cmap="RdYlGn_r", linewidth=2.4, legend=True,
                 vmin=0, vmax=1.2,
                 legend_kwds={"label": "peak surveyed occupancy", "shrink": 0.5})
        lots.plot(ax=ax, color="#003049", markersize=45, marker="P", zorder=6)
        finish(ax, fig, "Map 11 - On-street parking occupancy and off-street lots",
               f"{len(occ)} surveyed segments; {len(lots)} off-street lots",
               "map_11_parking.png",
               note="SURVEY DATA, NOT REAL TIME. Peak of eight surveyed periods. Values above "
                    "100% occur because Supply is an integer capacity estimate.")
    except Exception as exc:  # noqa: BLE001
        log.warning("map 11 skipped: %s", exc)

    # 12 safety
    try:
        cr = gpd.read_file(DATA_PROCESSED / "cnv_safety.gpkg", layer="intersection_crashes")
        fig, ax = plt.subplots(figsize=(11, 9))
        boundary.plot(ax=ax, facecolor="#fafafa", edgecolor="black", linewidth=1.2)
        roads.plot(ax=ax, color="#e4e4e4", linewidth=0.5)
        cr.plot(ax=ax, markersize=cr["crash_count"].clip(1, 700) / 2.2 + 8, color="#9d0208",
                alpha=0.6, edgecolor="white", linewidth=0.4)
        finish(ax, fig, "Map 12 - Recorded collisions by intersection",
               f"{len(cr)} intersections matched to ICBC crash records "
               f"({int(cr['crash_count'].sum()):,} crashes); marker size is crash count",
               "map_12_safety.png",
               note="ICBC reports 'NORTH VANCOUVER' for both the City and the District and "
                    "publishes no coordinates; matching is name-based. Intersections without "
                    "a match are unknown, NOT zero.")
    except Exception as exc:  # noqa: BLE001
        log.warning("map 12 skipped: %s", exc)

    # 13 combined civic geography
    try:
        scores = gpd.read_file(DATA_PROCESSED / "cnv_public_space_scores.gpkg",
                               layer="public_space_scores")
        vp = gpd.read_file(DATA_PROCESSED / "cnv_elections.gpkg", layer="voting_places")
        stops = gpd.read_file(DATA_PROCESSED / "cnv_transit.gpkg", layer="transit_stops")
        fig, ax = plt.subplots(figsize=(12.5, 10))
        census.plot(column="population_density", ax=ax, cmap="Greys", scheme="quantiles", k=5,
                    alpha=0.55, edgecolor="white", linewidth=0.2)
        roads.plot(ax=ax, color="#d7d7d7", linewidth=0.5)
        nbs.boundary.plot(ax=ax, color="#5a5a5a", linewidth=0.9, linestyle="--")
        stops[stops.get("in_cnv", True)].plot(ax=ax, color="#2a9d8f", markersize=5, alpha=0.6)
        sc = scores.plot(ax=ax, column="public_space_composite", cmap="viridis",
                         markersize=scores["public_space_composite"].fillna(0) / 2.2 + 5,
                         legend=True, alpha=0.9, edgecolor="none",
                         legend_kwds={"label": "public-space composite score (0-100)",
                                      "shrink": 0.5})
        vp.plot(ax=ax, color="#c1121f", markersize=110, marker="*", edgecolor="white", zorder=8)
        boundary.boundary.plot(ax=ax, color="black", linewidth=1.4)
        for _, r in nbs.iterrows():
            c = r.geometry.representative_point()
            ax.annotate(r["neighbourhood"][:22], xy=(c.x, c.y), fontsize=7.5, ha="center",
                        color="#222", path_effects=[pe.withStroke(linewidth=2.5,
                                                                  foreground="white")])
        finish(ax, fig, "Map 13 - Combined civic geography",
               "Population density, neighbourhoods, transit stops, voting places and the "
               "neutral public-space score",
               "map_13_combined.png",
               note="The public-space score is a NEUTRAL measure of visibility and "
                    "feasibility. It contains no political variable and makes no inference "
                    "from demographics to political preference.")
    except Exception as exc:  # noqa: BLE001
        log.warning("map 13 skipped: %s", exc)

    log.info("maps written to %s", MAPS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
