#!/usr/bin/env python3
"""Build the DATA REVIEW map: everything excluded, flagged or unverified.

The main analysis deliberately drops or downgrades several things. Rather than have those
decisions be invisible, this builds a separate page that shows exactly what was set aside
and where, so the decisions can be checked independently.

Output: outputs/interactive/review.html (+ data/review_*.geojson)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA_PROCESSED, OUTPUTS, get_logger, load_boundary  # noqa: E402

log = get_logger("21_create_review_map")

OUT = OUTPUTS / "interactive"
DATA = OUT / "data"


def dump(gdf: gpd.GeoDataFrame, name: str, cols: list[str]) -> int:
    keep = [c for c in cols if c in gdf.columns]
    g = gdf[keep + ["geometry"]].copy()
    g = g[~g.geometry.is_empty & g.geometry.notna()].to_crs("EPSG:4326")
    (DATA / f"{name}.geojson").write_text(
        json.dumps(json.loads(g.to_json()), separators=(",", ":")), encoding="utf-8")
    log.info("  %-34s %5d features", name, len(g))
    return len(g)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    counts = {}

    log.info("exporting review layers:")
    dump(load_boundary(), "review_boundary", ["ADMIN_AREA_NAME"])

    # 1. ICBC records excluded as unattributable (Highway 1 interchanges).
    try:
        exc = gpd.read_file(DATA_PROCESSED / "cnv_safety.gpkg", layer="excluded_crashes_review")
        counts["excluded_crashes"] = dump(
            exc, "review_excluded_crashes",
            ["icbc_location", "crash_count", "non_cnv_streets_in_record", "exclusion_reason"])
        counts["excluded_crash_total"] = int(exc["crash_count"].sum())
    except Exception as exc_err:  # noqa: BLE001
        log.warning("excluded crashes unavailable: %s", exc_err)

    # 2. Kept collision records, for side-by-side comparison.
    kept = gpd.read_file(DATA_PROCESSED / "cnv_safety.gpkg", layer="intersection_crashes")
    counts["kept_crashes"] = dump(kept, "review_kept_crashes",
                                  ["icbc_locations", "crash_count"])
    counts["kept_crash_total"] = int(kept["crash_count"].sum())

    # 3. Where safety is UNKNOWN rather than good.
    scores = gpd.read_file(DATA_PROCESSED / "cnv_public_space_scores.gpkg",
                           layer="public_space_scores")
    no_safety = scores[~scores["collision_data_available"].fillna(False).astype(bool)]
    counts["no_collision_data"] = dump(
        no_safety, "review_no_collision_data",
        ["intersection_id", "street_names", "neighbourhood", "public_space_composite"])

    # 4. Where measured traffic volume exists at all.
    has_vol = scores[scores["traffic_volume_available"].fillna(False).astype(bool)]
    counts["has_traffic_volume"] = dump(
        has_vol, "review_has_traffic_volume",
        ["intersection_id", "street_names", "nearest_traffic_volume"])
    counts["no_traffic_volume"] = len(scores) - len(has_vol)

    # 5. Seniors: evidence-based versus name-only candidates.
    try:
        sen = gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg",
                            layer="seniors_housing")
        counts["seniors_verified"] = dump(
            sen, "review_seniors_verified",
            ["ah_name", "BUILDING_NAME", "ah_address", "ah_total_units", "ah_eligibility",
             "classification_basis"])
    except Exception:  # noqa: BLE001
        counts["seniors_verified"] = 0
    try:
        cand = gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg",
                             layer="seniors_name_candidates")
        counts["seniors_candidates"] = dump(
            cand, "review_seniors_candidates",
            ["BUILDING_NAME", "review_status", "review_note"])
    except Exception:  # noqa: BLE001
        counts["seniors_candidates"] = 0

    # 6. Buildings the City publishes nothing about.
    blds = gpd.read_file(DATA_PROCESSED / "residential_buildings.gpkg", layer="buildings")
    known = blds[blds["classification"] != "UNKNOWN"]
    counts["buildings_total"] = len(blds)
    counts["buildings_known"] = dump(
        known, "review_buildings_classified",
        ["classification", "classification_basis", "BUILDING_NAME", "height_m", "year_built"])

    stats = {
        "counts": counts,
        "unmatched_icbc": int(len(pd.read_csv(OUTPUTS / "tables" / "icbc_unmatched_locations.csv"))),
        "intersections_total": int(len(scores)),
    }
    (DATA / "review_stats.json").write_text(json.dumps(stats), encoding="utf-8")

    (OUT / "review.html").write_text(HTML, encoding="utf-8")
    log.info("wrote %s", OUT / "review.html")
    return 0


HTML = r"""<!doctype html>
<html lang="en" data-theme="light"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CNV GIS — Data Review: what was excluded and why</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root{
  /* sophisticated bright: warm ivory ground, deep petrol ink, brass accent */
  --petrol-900:#0B3A46; --petrol-700:#0F4C5C; --petrol-500:#3C7C8A; --petrol-200:#B9CFCE;
  --brass:#B08D57; --brass-dark:#8A6A3B; --crimson:#8C2F39;
  --bg:#FBFAF8; --surface:#FFFFFF; --surface-2:#F5F2EC;
  --fg:#1A1917; --muted:#57534E; --faint:#8B857C;
  --line:#E8E3DA; --line-strong:#D6CFC3;
  --ok:#2F6B4F; --bad:#8C2F39;
  --shadow:0 1px 2px rgba(26,25,23,.04),0 8px 28px rgba(26,25,23,.07);
  --radius:12px; --z-panel:20; --z-float:30; --z-modal:50;
}
:root[data-theme="dark"]{
  --bg:#14100C; --surface:#1C1813; --surface-2:#241F19;
  --fg:#F2EDE4; --muted:#BDB4A6; --faint:#948B7D;
  --line:#332C24; --line-strong:#463D31;
  --petrol-700:#7FB3BE; --brass:#D9B579;
  --ok:#7DBF9B; --bad:#E08A92;
  --shadow:0 1px 2px rgba(0,0,0,.5),0 8px 28px rgba(0,0,0,.55);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{
  font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  font-size:15px;line-height:1.6;color:var(--fg);background:var(--bg);
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
.mono,.tile .v,.layer .ct,.slider .val,.pop-b td:last-child,.legend .lb,.num{
  font-variant-numeric:tabular-nums;font-feature-settings:"tnum" 1;
}
#app{display:flex;height:100%;overflow:hidden}

/* ---------- sidebar ---------- */
#side{
  width:380px;flex:0 0 380px;display:flex;flex-direction:column;
  background:var(--surface);border-right:1px solid var(--line);z-index:var(--z-panel);
}
.head{padding:16px 18px 14px;border-bottom:1px solid var(--line);background:var(--surface)}
.brandrow{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.brand h1{margin:0;font-family:"Playfair Display",Georgia,serif;font-size:20px;font-weight:600;letter-spacing:-.015em;line-height:1.2}
.brand p{margin:3px 0 0;font-size:12px;color:var(--faint);letter-spacing:.02em}
.iconbtn{
  display:inline-flex;align-items:center;justify-content:center;
  width:36px;height:36px;flex:0 0 36px;border:1px solid var(--line);border-radius:8px;
  background:var(--surface);color:var(--muted);cursor:pointer;
  transition:background .18s ease,color .18s ease,border-color .18s ease;
}
.iconbtn:hover{background:var(--surface-2);color:var(--fg);border-color:var(--line-strong)}
.iconbtn:focus-visible{outline:2px solid var(--petrol-500);outline-offset:2px}
.iconbtn svg{width:18px;height:18px}

/* ---------- stat tiles ---------- */
.tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:14px 18px;border-bottom:1px solid var(--line)}
.tile{background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius);padding:9px 10px}
.tile .v{font-variant-numeric:tabular-nums;font-size:16px;font-weight:600;letter-spacing:-.02em;line-height:1.25}
.tile .k{font-size:10.5px;color:var(--faint);text-transform:uppercase;letter-spacing:.05em;margin-top:2px}

/* ---------- scroll body ---------- */
.body{flex:1;overflow-y:auto;padding:0 18px 40px;scrollbar-width:thin}
.body::-webkit-scrollbar{width:9px}
.body::-webkit-scrollbar-thumb{background:var(--line-strong);border-radius:6px;border:3px solid var(--surface)}

.searchwrap{position:relative;margin:14px 0 4px}
.searchwrap svg{position:absolute;left:11px;top:50%;transform:translateY(-50%);width:16px;height:16px;color:var(--faint);pointer-events:none}
#search{
  width:100%;padding:10px 12px 10px 34px;font:inherit;font-size:14px;
  border:1px solid var(--line-strong);border-radius:8px;background:var(--surface);color:var(--fg);
  transition:border-color .18s ease,box-shadow .18s ease;
}
#search::placeholder{color:var(--faint)}
#search:focus{outline:none;border-color:var(--petrol-500);box-shadow:0 0 0 3px rgba(60,124,138,.20)}
#results{margin:6px 0 0;display:flex;flex-direction:column;gap:1px}
#results button{
  text-align:left;font:inherit;font-size:13px;padding:7px 10px;border:0;border-radius:6px;
  background:transparent;color:var(--fg);cursor:pointer;transition:background .15s ease;
}
#results button:hover{background:var(--surface-2)}
#results button:focus-visible{outline:2px solid var(--petrol-500);outline-offset:-2px}

h2.sec{
  display:flex;align-items:center;gap:7px;margin:20px 0 8px;
  font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:var(--faint);
}
h2.sec::after{content:"";flex:1;height:1px;background:var(--line)}

.layer{
  display:flex;align-items:center;gap:10px;padding:7px 8px;margin:0 -8px;border-radius:7px;
  font-size:13.5px;cursor:pointer;transition:background .15s ease;
}
.layer:hover{background:var(--surface-2)}
.layer input{width:15px;height:15px;accent-color:var(--petrol-700);cursor:pointer;flex:0 0 15px}
.layer input:focus-visible{outline:2px solid var(--petrol-500);outline-offset:2px}
.sw{width:14px;height:14px;flex:0 0 14px;border-radius:4px;border:1px solid rgba(26,25,23,.16)}
.layer .nm{flex:1;min-width:0}
.layer .ct{font-variant-numeric:tabular-nums;font-size:10.5px;color:var(--faint)}

.slider{display:flex;align-items:center;gap:10px;font-size:12.5px;color:var(--muted);padding:4px 0}
.slider input[type=range]{flex:1;accent-color:var(--petrol-700);cursor:pointer}
.slider .val{font-variant-numeric:tabular-nums;font-size:11.5px;min-width:34px;text-align:right}

.callout{
  border:1px solid var(--line);border-left:3px solid var(--petrol-700);background:var(--surface-2);
  border-radius:0 8px 8px 0;padding:10px 12px;margin:10px 0;font-size:12.5px;color:var(--muted);
}
.callout.warn{border-left-color:var(--brass-dark)}
.callout strong{color:var(--fg)}
.callout a{color:var(--petrol-700);font-weight:600}

.linkrow{
  display:flex;align-items:center;gap:8px;padding:9px 11px;margin:8px 0;
  border:1px solid var(--line);border-radius:8px;background:var(--surface);
  color:var(--fg);text-decoration:none;font-size:13px;font-weight:500;
  transition:background .18s ease,border-color .18s ease;
}
.linkrow:hover{background:var(--surface-2);border-color:var(--petrol-500)}
.linkrow svg{width:16px;height:16px;color:var(--petrol-700);flex:0 0 16px}
.linkrow .arrow{margin-left:auto;color:var(--faint)}

.dl{display:grid;gap:2px}
.dl a{
  display:flex;align-items:center;gap:7px;font-size:12px;padding:5px 7px;margin:0 -7px;
  border-radius:6px;color:var(--muted);text-decoration:none;transition:background .15s ease,color .15s ease;
}
.dl a:hover{background:var(--surface-2);color:var(--fg)}
.dl svg{width:13px;height:13px;flex:0 0 13px;color:var(--faint)}
.meta{font-size:11.5px;color:var(--faint);line-height:1.6}

/* ---------- map ---------- */
#map{flex:1;background:var(--bg)}
.leaflet-container{font-family:"Inter",sans-serif;background:var(--bg)}
.leaflet-popup-content-wrapper{
  border-radius:var(--radius);box-shadow:var(--shadow);background:var(--surface);color:var(--fg);
  border:1px solid var(--line);
}
.leaflet-popup-tip{background:var(--surface);border:1px solid var(--line)}
.leaflet-popup-content{margin:0;font-size:13px;min-width:250px;max-width:330px}
.pop-h{padding:11px 13px 9px;border-bottom:1px solid var(--line)}
.pop-h .t{font-weight:600;font-size:13.5px;line-height:1.35}
.pop-h .s{font-size:11px;color:var(--faint);text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
.pop-b{padding:9px 13px 12px;max-height:270px;overflow-y:auto}
.pop-b table{width:100%;border-collapse:collapse}
.pop-b td{padding:3px 0;vertical-align:top;font-size:12.5px}
.pop-b td:first-child{color:var(--muted);padding-right:12px;white-space:nowrap}
.pop-b td:last-child{text-align:right;font-variant-numeric:tabular-nums;font-weight:500}
.pop-n{padding:8px 13px;background:var(--surface-2);border-top:1px solid var(--line);font-size:11.5px;color:var(--muted)}
.leaflet-bar a{background:var(--surface);color:var(--fg);border-color:var(--line)}
.leaflet-bar a:hover{background:var(--surface-2)}

.legend{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:11px 13px;font-size:12px;min-width:150px;
}
.legend h4{margin:0 0 6px;font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--faint);font-weight:600}
.legend .row{display:flex;align-items:center;gap:8px;padding:2px 0}
.legend i{width:13px;height:13px;border-radius:3px;flex:0 0 13px}
.legend .lb{font-variant-numeric:tabular-nums;font-size:11px;color:var(--muted)}
.legend + .legend{margin-top:8px}
.leaflet-control-scale-line{background:var(--surface);color:var(--fg);border-color:var(--line-strong)}

#toggleSide{position:absolute;top:12px;left:12px;z-index:var(--z-float);display:none}


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

@media (prefers-reduced-motion:reduce){
  *{transition-duration:.01ms !important;animation-duration:.01ms !important}
}
/* ---------- review-page specifics ---------- */
.card{border:1px solid var(--line);border-left:3px solid var(--bad);border-radius:0 10px 10px 0;
  padding:12px 14px;margin:12px 0;background:var(--surface);box-shadow:var(--shadow)}
.card.kept{border-left-color:var(--ok)}
.card.flag{border-left-color:var(--brass)}
.card h3{margin:6px 0 5px;font-family:"Playfair Display",Georgia,serif;font-size:15px;font-weight:600}
.card p{margin:5px 0;font-size:12.5px;color:var(--muted)}
.tag{display:inline-block;font-size:9.5px;font-weight:600;letter-spacing:.08em;padding:3px 8px;
  border-radius:20px;text-transform:uppercase}
.t-removed{background:#F6E7E8;color:#7A2830}
.t-kept{background:#E4EFE8;color:#265842}
.t-flag{background:#F6EEDF;color:#7A5C2E}
.t-verified{background:#E2ECEE;color:#0B3A46}
:root[data-theme="dark"] .t-removed{background:#3A1A1D;color:#E8A6AC}
:root[data-theme="dark"] .t-kept{background:#16301F;color:#9DD4B6}
:root[data-theme="dark"] .t-flag{background:#33260F;color:#E3C489}
:root[data-theme="dark"] .t-verified{background:#152B31;color:#9FC9D2}
.num{font-weight:600;color:var(--fg);font-variant-numeric:tabular-nums}
code{background:var(--surface-2);padding:1.5px 6px;border-radius:5px;font-size:11.5px;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace}

.leaflet-control-attribution{background:transparent!important;color:var(--faint)!important;
  font-size:9.5px!important;padding:1px 5px!important;box-shadow:none!important}
.leaflet-control-attribution a{color:var(--faint)!important;text-decoration:none}
</style></head><body>
<div id="app"><aside id="side">
<button class="sheet-grab" id="grab" aria-label="Expand panel" aria-expanded="false"><span></span></button>
<div class="head"><div class="brandrow">
  <div class="brand"><h1>Data Review</h1>
  <p>What was excluded, downgraded or unverified</p></div>
  <button class="iconbtn" id="theme" aria-label="Toggle dark mode" title="Toggle dark mode">
   <svg id="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
   <svg id="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:none"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg>
  </button></div></div>
<div class="body">
<a class="linkrow" href="index.html">
 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
 <span>Back to the main map</span></a>
<div class="callout">Layers showing data that was excluded, downgraded or left unverified in the main analysis, so each decision can be checked on the map. Full write-up in <code>DATA_GAPS.md</code>.</div>

<h2 class="sec">Toggle layers</h2><div id="layers"></div>



</div></aside><div id="map"></div></div>

<script>
const root=document.documentElement;
const saved=localStorage.getItem('cnv-theme');
if(saved) root.setAttribute('data-theme',saved);
function syncThemeIcon(){const d=root.getAttribute('data-theme')==='dark';
 document.getElementById('icon-sun').style.display=d?'none':'block';
 document.getElementById('icon-moon').style.display=d?'block':'none';}
syncThemeIcon();
const map=window.map=L.map('map',{preferCanvas:true,zoomControl:false,
  attributionControl:false}).setView([49.322,-123.075],14);
L.control.attribution({prefix:false,position:'bottomright'})
  .addAttribution('&copy; OpenStreetMap &copy; CARTO').addTo(map);
L.control.zoom({position:'topright'}).addTo(map);
L.control.scale({imperial:false,position:'bottomleft'}).addTo(map);
const TILES={light:'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png',
             dark:'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png'};
let base=null;
function swapBasemap(){const d=root.getAttribute('data-theme')==='dark';
 if(base) map.removeLayer(base);
 base=L.tileLayer(d?TILES.dark:TILES.light,
  {maxZoom:19}).addTo(map);
 base.setZIndex(0);}
swapBasemap();
document.getElementById('theme').onclick=()=>{const d=root.getAttribute('data-theme')==='dark';
 root.setAttribute('data-theme',d?'light':'dark');
 localStorage.setItem('cnv-theme',d?'light':'dark'); syncThemeIcon(); swapBasemap();};

function tbl(p,f){let h='<table>';for(const[k,l]of f){if(p[k]==null||p[k]==='')continue;
 let v=p[k];if(typeof v==='number')v=Number.isInteger(v)?v.toLocaleString():v.toFixed(2);
 h+=`<tr><td>${l}</td><td><strong>${v}</strong></td></tr>`;}return h+'</table>';}

const CONF=[
 {f:'review_boundary',label:'Municipal boundary',sw:'#1A1917',on:true,
  style:()=>({color:'#1A1917',weight:2,fill:false})},

 {f:'review_kept_crashes',label:'Collisions KEPT (high confidence)',sw:'#2F6B4F',on:true,
  point:(x,ll)=>L.circleMarker(ll,{radius:3+Math.sqrt(x.properties.crash_count||0)/1.5,
    fillColor:'#2F6B4F',color:'#fff',weight:.7,fillOpacity:.65}),
  title:x=>'KEPT — every named street is a CNV street',
  fields:[['crash_count','Crashes'],['icbc_locations','ICBC location']]},

 {f:'review_excluded_crashes',label:'Collisions EXCLUDED (Hwy 1 interchanges)',sw:'#8C2F39',on:true,
  point:(x,ll)=>L.circleMarker(ll,{radius:5+Math.sqrt(x.properties.crash_count||0)/1.4,
    fillColor:'#8C2F39',color:'#fff',weight:1.4,fillOpacity:.8}),
  title:x=>'EXCLUDED — not attributable to a CNV intersection',
  fields:[['crash_count','Crashes excluded'],['non_cnv_streets_in_record','Non-CNV streets named'],
          ['icbc_location','ICBC location'],['exclusion_reason','Reason']]},

 {f:'review_no_collision_data',label:'Safety UNKNOWN (no ICBC match)',sw:'#B4ADA2',on:false,
  point:(x,ll)=>L.circleMarker(ll,{radius:4,fillColor:'#B4ADA2',color:'#fff',weight:.6,fillOpacity:.75}),
  title:x=>x.properties.street_names||'Intersection',
  fields:[['neighbourhood','Neighbourhood'],['public_space_composite','Composite score']],
  note:'These are UNKNOWN, not zero collisions. They receive no safety score.'},

 {f:'review_has_traffic_volume',label:'Has a measured traffic volume',sw:'#0F4C5C',on:false,
  point:(x,ll)=>L.circleMarker(ll,{radius:6,fillColor:'#0F4C5C',color:'#fff',weight:1.2,fillOpacity:.9}),
  title:x=>x.properties.street_names||'Intersection',
  fields:[['nearest_traffic_volume','Volume (as published)']]},

 {f:'review_seniors_verified',label:'Seniors housing — evidence based',sw:'#6B4E71',on:true,
  style:()=>({color:'#6B4E71',weight:1.5,fillOpacity:.65}),
  point:(x,ll)=>L.circleMarker(ll,{radius:7,fillColor:'#6B4E71',color:'#fff',weight:1.5,fillOpacity:.9}),
  title:x=>x.properties.ah_name||x.properties.BUILDING_NAME||'Seniors housing',
  fields:[['ah_address','Address'],['ah_total_units','Units'],['ah_eligibility','Eligibility'],
          ['classification_basis','Evidence']]},

 {f:'review_seniors_candidates',label:'Seniors — NAME ONLY, unverified',sw:'#B08D57',on:true,
  style:()=>({color:'#B08D57',weight:2,fillOpacity:.55,dashArray:'4,3'}),
  point:(x,ll)=>L.circleMarker(ll,{radius:8,fillColor:'#B08D57',color:'#fff',weight:1.6,fillOpacity:.9}),
  title:x=>(x.properties.BUILDING_NAME||'Building')+' — NOT classified',
  fields:[['review_status','Status'],['review_note','Why it was not classified']]},

 {f:'review_buildings_classified',label:'Buildings with any published attribute',sw:'#3C7C8A',on:false,
  style:()=>({color:'#3C7C8A',weight:.6,fillColor:'#3C7C8A',fillOpacity:.65}),
  title:x=>x.properties.BUILDING_NAME||x.properties.classification,
  fields:[['classification','Class'],['classification_basis','Basis'],
          ['height_m','Height (m)'],['year_built','Year built']]}
];

(async()=>{
 const stats=await (await fetch('data/review_stats.json')).json();
 const c=stats.counts;

 for(const cfg of CONF){
   let gj; try{ gj=await (await fetch('data/'+cfg.f+'.geojson')).json(); }catch(e){ continue; }
   const layer=L.geoJSON(gj,{style:cfg.style?cfg.style:()=>({}),
     pointToLayer:(x,ll)=>cfg.point?cfg.point(x,ll):L.circleMarker(ll,{radius:5}),
     onEachFeature:(x,l)=>{ if(cfg.fields)
       l.bindPopup('<strong>'+(cfg.title?cfg.title(x):'')+'</strong>'+tbl(x.properties,cfg.fields)
         +(cfg.note?`<p style="margin:7px 0 0;color:#5c6670">${cfg.note}</p>`:'')); }});
   if(cfg.on) layer.addTo(map);
   const row=document.createElement('label'); row.className='layer';
   row.innerHTML=`<input type="checkbox" ${cfg.on?'checked':''}>
     <span class="sw" style="background:${cfg.sw}"></span><span>${cfg.label}</span>`;
   row.querySelector('input').onchange=e=>e.target.checked?layer.addTo(map):map.removeLayer(layer);
   document.getElementById('layers').appendChild(row);
 }


 const lg=L.control({position:'bottomright'});
 lg.onAdd=()=>{const d=L.DomUtil.create('div','legend');
  d.innerHTML='<strong>Review map</strong><br>'+
   [['#2F6B4F','collisions kept'],['#8C2F39','collisions excluded'],
    ['#B4ADA2','safety unknown'],['#0F4C5C','has traffic volume'],
    ['#6B4E71','seniors: evidence'],['#B08D57','seniors: name only']]
   .map(([c,l])=>`<i style="background:${c}"></i>${l}`).join('<br>');
  return d;};
 lg.addTo(map);
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
