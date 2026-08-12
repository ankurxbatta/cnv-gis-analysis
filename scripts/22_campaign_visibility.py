#!/usr/bin/env python3
"""Recommend public locations for lawful in-person campaigning, with reasons.

The recommendation is built ONLY on public-space exposure: how many people pass a
location, how much transit activity there is, how walkable it is, how prominent the
intersection is, and how easy it is to park nearby.

It contains NO political variable. It does not use party, candidate, voting history, or
any inference from demographics to political preference. It tells you where people ARE,
not who they are or how they might vote. Two campaigns of opposing views would get
exactly the same list.

Outputs:
  outputs/tables/campaign_visibility_recommendations.csv
  outputs/maps/map_14_campaign_visibility.png
  outputs/interactive/recommendations.html
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA_PROCESSED, OUTPUTS, get_logger, load_boundary  # noqa: E402

log = get_logger("22_campaign_visibility")

TOP_N = 20


def build_reasons(r: pd.Series, ranks: dict) -> list[str]:
    """Explain, in plain language, why this location scores as it does."""
    out = []
    dep = r.get("transit_departures_250m") or 0
    stops = r.get("transit_stops_250m") or 0
    if dep >= ranks["dep_p90"]:
        out.append(f"Very high transit activity: {dep:,.0f} scheduled weekday bus departures "
                   f"within 250 m across {stops:.0f} stops — a steady stream of people on foot.")
    elif dep >= ranks["dep_p60"]:
        out.append(f"Good transit activity: {dep:,.0f} weekday departures within 250 m.")

    pop = r.get("population_2021_400m") or 0
    if pop >= ranks["pop_p90"]:
        out.append(f"Dense residential catchment: about {pop:,.0f} residents live within a "
                   f"5-minute walk (400 m).")
    elif pop >= ranks["pop_p60"]:
        out.append(f"Solid residential catchment: about {pop:,.0f} residents within 400 m.")

    comm = r.get("commercial_area_250m_m2") or 0
    if comm >= ranks["comm_p75"]:
        out.append(f"Commercial frontage nearby ({comm/10000:.1f} ha of commercial/mixed land "
                   f"use within 250 m), so there is footfall beyond residents.")

    if r.get("full_signal"):
        out.append("Full traffic signal: pedestrians and drivers actually stop here, which "
                   "creates dwell time rather than passing traffic.")
    elif r.get("signalised"):
        out.append("Signalised crossing, so pedestrians pause at the kerb.")

    legs = r.get("leg_count") or 0
    if legs >= 4:
        out.append(f"Prominent junction with {legs:.0f} approaches — visible from several "
                   f"directions at once.")

    sup = r.get("onstreet_supply_250m") or 0
    occ = r.get("onstreet_peak_occupancy_250m")
    if sup >= ranks["park_p60"]:
        if occ is not None and occ == occ and occ >= 0.85:
            out.append(f"{sup:,.0f} on-street spaces within 250 m, but they hit "
                       f"{occ*100:.0f}% occupancy at peak — arrive early or use a lot.")
        else:
            out.append(f"{sup:,.0f} on-street parking spaces within 250 m for loading in and out.")

    col = r.get("collision_count")
    if col is not None and col == col and col >= ranks["col_p90"]:
        out.append(f"CAUTION: {col:,.0f} recorded collisions here — one of the higher-collision "
                   f"junctions in the city. Stand well back from the kerb.")
    elif col is None or col != col:
        out.append("No collision record matched this location, so its safety is unknown "
                   "rather than good.")
    return out


def main() -> int:
    scores = gpd.read_file(DATA_PROCESSED / "cnv_public_space_scores.gpkg",
                           layer="public_space_scores")
    boundary = load_boundary()
    tables = OUTPUTS / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    ranks = {
        "dep_p90": scores["transit_departures_250m"].quantile(.90),
        "dep_p60": scores["transit_departures_250m"].quantile(.60),
        "pop_p90": scores["population_2021_400m"].quantile(.90),
        "pop_p60": scores["population_2021_400m"].quantile(.60),
        "comm_p75": scores["commercial_area_250m_m2"].quantile(.75)
        if "commercial_area_250m_m2" in scores else 0,
        "park_p60": scores["onstreet_supply_250m"].quantile(.60),
        "col_p90": scores["collision_count"].quantile(.90),
    }

    top = scores.nsmallest(TOP_N, "composite_rank").copy().reset_index(drop=True)
    top["recommendation_rank"] = range(1, len(top) + 1)
    top["reasons"] = [build_reasons(r, ranks) for _, r in top.iterrows()]
    top["reason_text"] = top["reasons"].map(lambda xs: " ".join(xs))

    def headline(r):
        bits = []
        if (r.get("transit_score") or 0) >= 85: bits.append("transit hub")
        if (r.get("pedestrian_proxy_score") or 0) >= 85: bits.append("high footfall")
        if r.get("full_signal"): bits.append("signalised")
        if (r.get("parking_access_score") or 0) >= 80: bits.append("easy parking")
        return ", ".join(bits) if bits else "prominent junction"

    top["headline"] = top.apply(headline, axis=1)

    cols = ["recommendation_rank", "street_names", "neighbourhood", "public_space_composite",
            "headline", "transit_departures_250m", "transit_stops_250m",
            "population_2021_400m", "onstreet_supply_250m", "onstreet_peak_occupancy_250m",
            "full_signal", "signalised", "leg_count", "collision_count",
            "collision_data_available", "reason_text"]
    out_df = top[[c for c in cols if c in top.columns]].copy()
    out_df["basis"] = ("Public-space exposure only: transit activity, resident catchment, "
                       "commercial frontage, junction prominence and parking access.")
    out_df["neutrality"] = ("Contains no political variable. Identical for any campaign of "
                            "any viewpoint. Measures where people are, not who they are.")
    out_df["legal_note"] = ("BC's Local Government Act restricts campaigning at and near "
                            "voting places on voting day, and CNV requires permits for some "
                            "activities on City property. Confirm with the CNV Chief Election "
                            "Officer before campaigning at any location.")
    out_df.to_csv(tables / "campaign_visibility_recommendations.csv", index=False)

    log.info("=" * 92)
    log.info("TOP %d PUBLIC LOCATIONS BY VISIBILITY AND FOOTFALL", TOP_N)
    log.info("=" * 92)
    for _, r in top.iterrows():
        log.info("")
        log.info("%2d. %s  [%s]", r["recommendation_rank"],
                 str(r["street_names"])[:56], r["neighbourhood"])
        log.info("    score %.1f/100 — %s", r["public_space_composite"], r["headline"])
        for reason in r["reasons"]:
            log.info("      • %s", reason)

    # ---------------- static map ----------------
    fig, ax = plt.subplots(figsize=(12, 10))
    census = gpd.read_file(DATA_PROCESSED / "cnv_census_2021.gpkg", layer="cnv_census_da")
    roads = gpd.read_file(DATA_PROCESSED / "cnv_roads.gpkg", layer="roads")
    vp = gpd.read_file(DATA_PROCESSED / "cnv_elections.gpkg", layer="voting_places")

    census.plot(column="population_density", ax=ax, cmap="BuPu", scheme="quantiles", k=5,
                alpha=.45, edgecolor="white", linewidth=.25)
    roads.plot(ax=ax, color="#cfcfcf", linewidth=.5)
    boundary.boundary.plot(ax=ax, color="black", linewidth=1.4)
    scores.plot(ax=ax, color="#b8b0a4", markersize=6, alpha=.55)
    top.plot(ax=ax, color="#0F4C5C", markersize=190, marker="o",
             edgecolor="white", linewidth=1.8, zorder=7)
    vp.plot(ax=ax, color="#8C2F39", markersize=95, marker="*",
            edgecolor="white", linewidth=.9, zorder=8)

    for _, r in top.iterrows():
        ax.annotate(str(int(r["recommendation_rank"])),
                    xy=(r.geometry.x, r.geometry.y), ha="center", va="center",
                    fontsize=7.5, fontweight="bold", color="white", zorder=9)
    # The top locations cluster tightly along Lonsdale, so per-point labels collide.
    # A ranked list keyed to the numbered markers reads far better.
    def short(name, n=30):
        parts = [p.strip() for p in str(name).split("/")]
        # "E 15TH ST / LONSDALE AVE / W 15TH ST" -> "Lonsdale Ave & 15th St"
        main = next((p for p in parts if "LONSDALE" in p.upper()), parts[0])
        other = next((p for p in parts if p != main), "")
        label = f"{main.title()} & {other.title()}" if other else main.title()
        return label[:n]

    lines = [f"{int(r['recommendation_rank']):>2}. {short(r['street_names'])}"
             for _, r in top.iterrows()]
    ax.text(0.005, 0.975, "Ranked locations", transform=ax.transAxes, fontsize=9.5,
            fontweight="bold", va="top", ha="left", color="#1A1917")
    ax.text(0.005, 0.945, "\n".join(lines), transform=ax.transAxes, fontsize=7.6,
            va="top", ha="left", color="#3A3733", linespacing=1.62, family="DejaVu Sans",
            bbox=dict(boxstyle="round,pad=0.55", facecolor="white",
                      edgecolor="#D6CFC3", alpha=.95))

    ax.set_title("Map 14 — Public visibility: highest-exposure locations",
                 fontsize=16, fontweight="bold", loc="left", pad=14)
    ax.text(0, 1.008, f"Top {TOP_N} public spaces by footfall, transit activity and junction "
                      "prominence. Red stars are 2022 voting places.",
            transform=ax.transAxes, fontsize=9.5, color="#57534E", va="bottom")
    ax.set_axis_off()
    fig.text(0.01, 0.012,
             "NEUTRAL MEASURE: ranks locations by public exposure only — transit activity, "
             "resident catchment, commercial frontage, junction prominence and parking.\n"
             "Contains no political variable and makes no inference from demographics to "
             "political preference. Identical for any campaign of any viewpoint.\n"
             "Campaigning near voting places is legally restricted on voting day — confirm "
             "with the CNV Chief Election Officer.",
             fontsize=7.3, color="#57534E", va="bottom")
    fig.subplots_adjust(bottom=0.14)
    fig.savefig(OUTPUTS / "maps" / "map_14_campaign_visibility.png", dpi=180,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    log.info("")
    log.info("wrote map_14_campaign_visibility.png")

    # ---------------- interactive layer ----------------
    web = OUTPUTS / "interactive" / "data"
    web.mkdir(parents=True, exist_ok=True)
    g = top[["recommendation_rank", "street_names", "neighbourhood", "public_space_composite",
             "headline", "reason_text", "transit_departures_250m", "population_2021_400m",
             "onstreet_supply_250m", "full_signal", "collision_count", "geometry"]].to_crs(4326)
    (web / "recommendations.geojson").write_text(
        json.dumps(json.loads(g.to_json()), separators=(",", ":")), encoding="utf-8")
    log.info("wrote recommendations.geojson (%d locations)", len(g))

    (OUTPUTS / "interactive" / "recommendations.html").write_text(PAGE, encoding="utf-8")
    log.info("wrote recommendations.html")
    return 0


PAGE = r"""<!doctype html>
<html lang="en" data-theme="light"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CNV — Public visibility recommendations</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root{--petrol-700:#0F4C5C;--petrol-500:#3C7C8A;--brass:#B08D57;--crimson:#8C2F39;
 --bg:#FBFAF8;--surface:#FFFFFF;--surface-2:#F5F2EC;--fg:#1A1917;--muted:#57534E;--faint:#8B857C;
 --line:#E8E3DA;--line-strong:#D6CFC3;--ok:#2F6B4F;
 --shadow:0 1px 2px rgba(26,25,23,.04),0 8px 28px rgba(26,25,23,.07);--radius:12px}
:root[data-theme="dark"]{--bg:#14100C;--surface:#1C1813;--surface-2:#241F19;--fg:#F2EDE4;
 --muted:#BDB4A6;--faint:#948B7D;--line:#332C24;--line-strong:#463D31;--petrol-700:#7FB3BE;--brass:#D9B579}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{font-family:"Inter",system-ui,sans-serif;font-size:15px;line-height:1.6;color:var(--fg);
 background:var(--bg);-webkit-font-smoothing:antialiased}
#app{display:flex;height:100%;overflow:hidden}
#side{width:430px;flex:0 0 430px;display:flex;flex-direction:column;background:var(--surface);
 border-right:1px solid var(--line)}
.head{padding:16px 20px 14px;border-bottom:1px solid var(--line)}
.head h1{margin:0;font-family:"Playfair Display",Georgia,serif;font-size:21px;font-weight:600;letter-spacing:-.015em}
.head p{margin:3px 0 0;font-size:12px;color:var(--faint)}
.body{flex:1;overflow-y:auto;padding:0 20px 44px}
.callout{border:1px solid var(--line);border-left:3px solid var(--petrol-700);background:var(--surface-2);
 border-radius:0 10px 10px 0;padding:11px 13px;margin:14px 0;font-size:12.5px;color:var(--muted)}
.callout.warn{border-left-color:var(--crimson)}
.callout strong{color:var(--fg)}
.rec{border:1px solid var(--line);border-radius:var(--radius);padding:13px 15px;margin:11px 0;
 background:var(--surface);cursor:pointer;transition:border-color .18s ease,box-shadow .18s ease}
.rec:hover{border-color:var(--petrol-500);box-shadow:var(--shadow)}
.rec:focus-visible{outline:2px solid var(--petrol-500);outline-offset:2px}
.rec .top{display:flex;align-items:flex-start;gap:11px}
.rank{width:29px;height:29px;flex:0 0 29px;border-radius:50%;background:var(--petrol-700);color:#fff;
 display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;font-variant-numeric:tabular-nums}
.rec h3{margin:0;font-size:14px;font-weight:600;line-height:1.35}
.rec .sub{font-size:11.5px;color:var(--faint);margin-top:2px}
.pill{display:inline-block;font-size:10px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;
 padding:3px 8px;border-radius:20px;background:var(--surface-2);color:var(--brass);margin-top:7px}
.why{margin:9px 0 0;padding:0 0 0 15px;font-size:12.5px;color:var(--muted)}
.why li{margin:4px 0}
.why li::marker{color:var(--brass)}
.sc{margin-left:auto;text-align:right;font-variant-numeric:tabular-nums}
.sc .n{font-family:"Playfair Display",Georgia,serif;font-size:19px;font-weight:600;color:var(--petrol-700)}
.sc .l{font-size:9.5px;color:var(--faint);text-transform:uppercase;letter-spacing:.05em}
h2.sec{display:flex;align-items:center;gap:7px;margin:20px 0 6px;font-size:11px;font-weight:600;
 text-transform:uppercase;letter-spacing:.07em;color:var(--faint)}
h2.sec::after{content:"";flex:1;height:1px;background:var(--line)}
a.back{display:flex;align-items:center;gap:8px;padding:9px 12px;margin:14px 0 0;border:1px solid var(--line);
 border-radius:9px;color:var(--fg);text-decoration:none;font-size:13px;font-weight:500}
a.back:hover{background:var(--surface-2)}
#map{flex:1}
.leaflet-popup-content-wrapper{border-radius:var(--radius);border:1px solid var(--line);background:var(--surface);color:var(--fg)}
.leaflet-popup-content{margin:0;font-size:13px;min-width:250px;max-width:320px}
.ph{padding:11px 13px 8px;border-bottom:1px solid var(--line);font-weight:600}
.pb{padding:10px 13px 12px;font-size:12.5px;color:var(--muted)}

/* ============================ MOBILE ============================ */
.sheet-grab{display:none}

@media (max-width:860px){
  html,body{overscroll-behavior:none}
  #app{display:block;height:100%}

  /* Map fills the viewport; the sheet floats above it. */
  #map{position:fixed;inset:0;width:100%;height:100%;z-index:1}

  #side{
    position:fixed;left:0;right:0;bottom:0;width:auto;flex:none;
    max-height:88vh;height:88vh;
    border-right:0;border-top:1px solid var(--line);
    border-radius:20px 20px 0 0;
    box-shadow:0 -6px 30px rgba(26,25,23,.16);
    transform:translateY(calc(100% - var(--peek,132px)));
    transition:transform .3s cubic-bezier(.32,.72,0,1);
    z-index:40;will-change:transform;
  }
  #side.open{transform:translateY(0)}
  #side.dragging{transition:none}
  :root[data-theme="dark"] #side{box-shadow:0 -6px 30px rgba(0,0,0,.5)}

  /* Grab handle doubles as the expand/collapse control. */
  .sheet-grab{
    display:flex;align-items:center;justify-content:center;
    width:100%;min-height:34px;border:0;background:transparent;
    cursor:grab;touch-action:none;padding:11px 0 5px;
  }
  .sheet-grab span{
    display:block;width:42px;height:5px;border-radius:3px;background:var(--line-strong);
    transition:background .18s ease;
  }
  .sheet-grab:active{cursor:grabbing}
  .sheet-grab:active span{background:var(--faint)}
  .sheet-grab:focus-visible{outline:2px solid var(--petrol-500);outline-offset:-4px;border-radius:12px}

  .head{padding:2px 18px 12px}
  .brand h1{font-size:18px}

  /* Scroll the sheet body, not the page, and clear the home indicator. */
  .body{-webkit-overflow-scrolling:touch;padding-bottom:calc(48px + env(safe-area-inset-bottom,0px))}
  .tiles{grid-template-columns:repeat(3,1fr);padding:10px 18px;gap:7px}
  .tile{padding:8px 9px}
  .tile .v{font-size:16px}
  .tile .k{font-size:9.5px}

  /* 44px minimum touch targets throughout. */
  .layer{padding:11px 8px;min-height:44px;font-size:14.5px}
  .layer input{width:22px;height:22px;flex:0 0 22px}
  .sw{width:16px;height:16px;flex:0 0 16px}
  .iconbtn{width:44px;height:44px;flex:0 0 44px}
  .linkrow{padding:13px 13px;min-height:48px}
  .dl a{padding:11px 7px;min-height:44px;font-size:13px}
  #results button{padding:12px 10px;min-height:44px;font-size:14px}
  .slider input[type=range]{height:34px}

  /* 16px stops iOS zooming the page when the field is focused. */
  #search{font-size:16px;padding:13px 12px 13px 38px;min-height:48px}
  .searchwrap svg{left:12px;width:18px;height:18px}

  h2.sec{margin:18px 0 6px}

  /* Controls sit clear of the sheet. */
  .leaflet-top.leaflet-right{top:calc(10px + env(safe-area-inset-top,0px))}
  .leaflet-bar a{width:40px!important;height:40px!important;line-height:40px!important;font-size:19px!important}
  .leaflet-bottom.leaflet-left{bottom:calc(var(--peek,132px) + 8px)}
  .leaflet-bottom.leaflet-right{bottom:calc(var(--peek,132px) + 8px)}

  /* Legend collapses to a tappable chip so it never covers the map. */
  .legend{max-width:150px;font-size:11px;padding:9px 10px}
  .legend.collapsed .row,.legend.collapsed h4:not(:first-child){display:none}
  .legend h4{cursor:pointer;margin-bottom:4px}
  .legend h4:first-child::after{content:" ▾";color:var(--faint)}
  .legend.collapsed h4:first-child::after{content:" ▸"}

  .leaflet-popup-content{min-width:0;max-width:78vw;font-size:13.5px}
  .pop-b{max-height:44vh}
  .pop-b td{font-size:13px;padding:5px 0}
  .leaflet-popup-content-wrapper{max-width:82vw}

  .callout{font-size:13px;padding:12px 13px}
  .meta{font-size:12px}
}

@media (max-width:400px){
  .tiles{grid-template-columns:repeat(2,1fr)}
  #side{--peek:126px}
}

@media(prefers-reduced-motion:reduce){*{transition-duration:.01ms!important}}
.leaflet-control-attribution{background:transparent!important;color:var(--faint)!important;
  font-size:9.5px!important;padding:1px 5px!important;box-shadow:none!important}
.leaflet-control-attribution a{color:var(--faint)!important;text-decoration:none}
</style></head><body>
<div id="app"><aside id="side">
<button class="sheet-grab" id="grab" aria-label="Expand panel" aria-expanded="false"><span></span></button>
 <div class="head"><h1>Where people actually are</h1>
 <p>Highest-exposure public locations in the City of North Vancouver</p></div>
 <div class="body">
  <div class="callout"><strong>What this ranks.</strong> Public exposure only: scheduled
  transit activity, residents within a 5-minute walk, commercial frontage, junction
  prominence and parking access. It tells you where people <em>are</em>.</div>
  <div class="callout"><strong>How solid the numbers are.</strong> Transit departures are
  actual scheduled counts from the TransLink feed. Resident counts are estimates,
  interpolated from census areas. Footfall is a <em>proxy</em> &mdash; no pedestrian counts
  are published for this city &mdash; so treat the ordering as indicative and verify on the
  ground.</div>
  <div class="callout warn"><strong>What it does not do.</strong> It contains no political
  variable — no party, candidate or voting history — and makes no inference from
  demographics to political preference. A campaign of any viewpoint would get this exact
  same list.</div>
  <div class="callout warn"><strong>Before you go.</strong> BC's Local Government Act
  restricts campaigning at and near voting places on voting day, and the City requires
  permits for some activities on City property. Confirm with the CNV Chief Election
  Officer.</div>
  <h2 class="sec">Ranked locations</h2>
  <div id="list"></div>
  <a class="back" href="index.html">← Back to the full explorer</a>
 </div>
</aside><div id="map"></div></div>
<script>
const root=document.documentElement;
const saved=localStorage.getItem('cnv-theme'); if(saved) root.setAttribute('data-theme',saved);
const map=window.map=L.map('map',{preferCanvas:true,zoomControl:false,
  attributionControl:false}).setView([49.320,-123.073],14);
L.control.attribution({prefix:false,position:'bottomright'})
  .addAttribution('&copy; OpenStreetMap &copy; CARTO').addTo(map);
L.control.zoom({position:'topright'}).addTo(map);
L.control.scale({imperial:false,position:'bottomleft'}).addTo(map);
const dark=root.getAttribute('data-theme')==='dark';
L.tileLayer(dark?'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png'
                :'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png',
 {maxZoom:19}).addTo(map);

(async()=>{
 try{ const b=await (await fetch('data/boundary.geojson')).json();
   L.geoJSON(b,{style:{color:'#1A1917',weight:2,fill:false}}).addTo(map);}catch(e){}
 try{ const v=await (await fetch('data/voting_places.geojson')).json();
   L.geoJSON(v,{pointToLayer:(f,ll)=>L.circleMarker(ll,{radius:7,fillColor:'#8C2F39',
     color:'#fff',weight:1.8,fillOpacity:.95})
     .bindPopup('<div class="ph">'+f.properties.place_name+'</div><div class="pb">2022 voting place — campaigning nearby is restricted on voting day.</div>')}).addTo(map);}catch(e){}

 const gj=await (await fetch('data/recommendations.geojson')).json();
 const marks={};
 const layer=L.geoJSON(gj,{pointToLayer:(f,ll)=>{
   const m=L.circleMarker(ll,{radius:12,fillColor:'#0F4C5C',color:'#fff',weight:2,fillOpacity:.95});
   marks[f.properties.recommendation_rank]=m;
   const p=f.properties;
   m.bindPopup(`<div class="ph">${p.recommendation_rank}. ${p.street_names}</div>
     <div class="pb"><strong>Score ${p.public_space_composite}/100</strong> — ${p.headline}<br><br>${p.reason_text}</div>`,
     {maxWidth:330});
   return m;}}).addTo(map);
 map.fitBounds(layer.getBounds().pad(.15));

 const feats=gj.features.sort((a,b)=>a.properties.recommendation_rank-b.properties.recommendation_rank);
 document.getElementById('list').innerHTML=feats.map(f=>{const p=f.properties;
  const why=p.reason_text.split(/(?<=\.)\s+(?=[A-Z])/).filter(Boolean);
  return `<article class="rec" tabindex="0" data-rank="${p.recommendation_rank}">
    <div class="top"><div class="rank">${p.recommendation_rank}</div>
     <div style="flex:1;min-width:0"><h3>${p.street_names}</h3>
      <div class="sub">${p.neighbourhood||''}</div>
      <span class="pill">${p.headline}</span></div>
     <div class="sc"><div class="n">${p.public_space_composite}</div><div class="l">score</div></div></div>
    <ul class="why">${why.map(w=>`<li>${w}</li>`).join('')}</ul></article>`;}).join('');

 document.querySelectorAll('.rec').forEach(el=>{
   const go=()=>{const m=marks[el.dataset.rank]; if(m){map.setView(m.getLatLng(),17); m.openPopup();}};
   el.onclick=go; el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}};
 });
})();

/* ---------- mobile bottom sheet ---------- */
(function(){
  const side=document.getElementById('side');
  const grab=document.getElementById('grab');
  if(!side||!grab) return;
  const mq=window.matchMedia('(max-width:860px)');
  let startY=0, startOpen=false, dragging=false, moved=0;

  const setOpen=(open)=>{
    side.classList.toggle('open',open);
    grab.setAttribute('aria-expanded',String(open));
    grab.setAttribute('aria-label',open?'Collapse panel':'Expand panel');
    setTimeout(()=>{ if(window.map) window.map.invalidateSize(); },320);
  };

  grab.addEventListener('click',()=>{ if(!dragging||Math.abs(moved)<6) setOpen(!side.classList.contains('open')); });
  grab.addEventListener('keydown',e=>{
    if(e.key==='Enter'||e.key===' '){e.preventDefault();setOpen(!side.classList.contains('open'));}
  });

  grab.addEventListener('touchstart',e=>{
    if(!mq.matches) return;
    dragging=true; moved=0; startY=e.touches[0].clientY;
    startOpen=side.classList.contains('open');
    side.classList.add('dragging');
  },{passive:true});

  grab.addEventListener('touchmove',e=>{
    if(!dragging) return;
    moved=e.touches[0].clientY-startY;
    const peek=parseInt(getComputedStyle(side).getPropertyValue('--peek'))||132;
    const closedY=side.offsetHeight-peek;
    let y=(startOpen?0:closedY)+moved;
    y=Math.max(0,Math.min(closedY,y));
    side.style.transform=`translateY(${y}px)`;
  },{passive:true});

  const end=()=>{
    if(!dragging) return;
    dragging=false;
    side.classList.remove('dragging');
    side.style.transform='';
    if(Math.abs(moved)>44) setOpen(moved<0);
  };
  grab.addEventListener('touchend',end);
  grab.addEventListener('touchcancel',end);

  // Collapse the legend by default on a phone; tap its title to reopen.
  const collapseLegend=()=>{
    document.querySelectorAll('.legend').forEach(l=>{
      if(mq.matches && !l.dataset.wired){
        l.classList.add('collapsed');
        const h=l.querySelector('h4');
        if(h){ h.style.cursor='pointer';
          h.addEventListener('click',()=>l.classList.toggle('collapsed')); }
        l.dataset.wired='1';
      }
    });
  };
  setTimeout(collapseLegend,700);
  mq.addEventListener('change',()=>{ setOpen(false); collapseLegend();
    setTimeout(()=>{ if(window.map) window.map.invalidateSize(); },80); });
})();

</script></body></html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
