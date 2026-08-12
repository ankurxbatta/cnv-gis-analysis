"""HTML template for the interactive civic geography explorer.

Kept separate from the export logic so the markup stays readable.
Design: data-dense dashboard — blue data with amber highlights, Fira Sans/Fira Code,
light and dark themes, SVG icons throughout (no emoji), WCAG AA contrast.
"""

INDEX_HTML = r"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>City of North Vancouver — Civic Geography Explorer</title>
<meta name="description" content="Population, housing, transport and public-space analysis for the City of North Vancouver, BC.">
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

@media (max-width:860px){
  #app{flex-direction:column}
  #side{width:100%;flex:0 0 auto;max-height:52vh;border-right:0;border-bottom:1px solid var(--line)}
  .tiles{grid-template-columns:repeat(2,1fr)}
  body{font-size:16px}
}
@media (prefers-reduced-motion:reduce){
  *{transition-duration:.01ms !important;animation-duration:.01ms !important}
}
</style>
</head>
<body>
<div id="app">
  <aside id="side">
    <div class="head">
      <div class="brandrow">
        <div class="brand">
          <h1>City of North Vancouver</h1>
          <p>Civic Geography Explorer &middot; 2021 Census</p>
        </div>
        <button class="iconbtn" id="theme" aria-label="Toggle dark mode" title="Toggle dark mode">
          <svg id="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
          <svg id="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="display:none"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg>
        </button>
      </div>
    </div>

    <div class="tiles" id="tiles"></div>

    <div class="body">
      <div class="searchwrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
        <label for="search" class="visually-hidden" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Search intersections and places</label>
        <input id="search" placeholder="Search an intersection or place" autocomplete="off">
      </div>
      <div id="results"></div>

      <h2 class="sec">Base geography</h2><div id="grp-base"></div>
      <h2 class="sec">Population &amp; housing</h2><div id="grp-pop"></div>
      <h2 class="sec">Transport</h2><div id="grp-transport"></div>
      <h2 class="sec">Civic</h2><div id="grp-civic"></div>

      <h2 class="sec">Display</h2>
      <div class="slider">
        <span>Fill</span><input id="op" type="range" min="10" max="100" value="75" aria-label="Layer fill opacity">
        <span class="val mono" id="opv">75%</span>
      </div>

      <h2 class="sec">Read this first</h2>
      <div class="callout warn">
        <strong>Adults 18+ is a proxy.</strong> A demographic proxy for potential electorate
        size from the 2021 Census &mdash; not a count of eligible or registered electors.
      </div>
      <div class="callout">
        <strong>The public-space score is politically neutral.</strong> It measures
        visibility, access and feasibility only. No party, candidate or voting variable, and
        no inference from demographics to political preference.
      </div>
      <div class="callout warn">
        <strong>Coverage varies by layer.</strong> Collision data covers about half of
        intersections &mdash; the rest are unknown, not zero. Measured traffic volumes exist
        for 40 of 503. Parking occupancy is a 2022&ndash;23 survey, not live data.
      </div>

      <a class="linkrow" href="review.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9L1.8 18a2 2 0 001.7 3h17a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z"/></svg>
        <span>Data review &mdash; what was excluded</span>
        <span class="arrow">&rarr;</span>
      </a>

      <h2 class="sec">Metadata</h2>
      <div class="meta" id="meta"></div>

      <h2 class="sec">Download tables</h2>
      <div class="dl" id="downloads"></div>
    </div>
  </aside>
  <div id="map"></div>
</div>

<script>
const ICON_FILE='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>';

/* ---------- theme ---------- */
const root=document.documentElement;
const saved=localStorage.getItem('cnv-theme');
if(saved) root.setAttribute('data-theme',saved);   // light is the default presentation
function syncThemeIcon(){
  const dark=root.getAttribute('data-theme')==='dark';
  document.getElementById('icon-sun').style.display=dark?'none':'block';
  document.getElementById('icon-moon').style.display=dark?'block':'none';
}
syncThemeIcon();
document.getElementById('theme').onclick=()=>{
  const dark=root.getAttribute('data-theme')==='dark';
  root.setAttribute('data-theme',dark?'light':'dark');
  localStorage.setItem('cnv-theme',dark?'light':'dark');
  syncThemeIcon(); swapBasemap();
};

/* ---------- map ---------- */
const map=L.map('map',{preferCanvas:true,zoomControl:false}).setView([49.322,-123.075],14);
L.control.zoom({position:'topright'}).addTo(map);
L.control.scale({imperial:false,position:'bottomleft'}).addTo(map);
const TILES={
  light:'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png',
  dark :'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png'
};
let base=null;
function swapBasemap(){
  const dark=root.getAttribute('data-theme')==='dark';
  if(base) map.removeLayer(base);
  base=L.tileLayer(dark?TILES.dark:TILES.light,
    {attribution:'&copy; OpenStreetMap contributors &copy; CARTO',maxZoom:19}).addTo(map);
  base.setZIndex(0);
}
swapBasemap();

/* ---------- helpers ---------- */
const BLUES=['#F2EEE7','#DDE7E5','#B9CFCE','#86ADB0','#4A848E','#0F4C5C'];
const VIRIDIS=['#F6F0E4','#EADCC2','#DBC49B','#C7A671','#B08D57','#8A6A3B'];
const HEAT=['#2F6B4F','#7C9A6B','#C7A671','#B08D57','#A8555E','#8C2F39'];
function ramp(v,stops,cols){ if(v==null||isNaN(v))return '#B4ADA2';
  for(let i=stops.length-1;i>=0;i--) if(v>=stops[i]) return cols[i]; return cols[0]; }
const fmt=v=>typeof v!=='number'?v:(Number.isInteger(v)?v.toLocaleString():v.toFixed(2));

function popup(title,sub,props,fields,note){
  let rows='';
  for(const [k,label] of fields){
    const v=props[k]; if(v===undefined||v===null||v==='')continue;
    rows+=`<tr><td>${label}</td><td>${fmt(v)}</td></tr>`;
  }
  return `<div class="pop-h"><div class="t">${title||'&mdash;'}</div>`+
         (sub?`<div class="s">${sub}</div>`:'')+`</div>`+
         `<div class="pop-b"><table>${rows}</table></div>`+
         (note?`<div class="pop-n">${note}</div>`:'');
}

let fillOpacity=0.75;
const layers={}, registry=[];

async function addLayer(c){
  let gj; try{ const r=await fetch('data/'+c.file+'.geojson'); if(!r.ok)return; gj=await r.json(); }
  catch(e){ return; }
  const layer=L.geoJSON(gj,{
    style:f=>c.style?c.style(f):{},
    pointToLayer:(f,ll)=>c.point?c.point(f,ll):L.circleMarker(ll,{radius:5}),
    onEachFeature:(f,l)=>{
      if(c.fields) l.bindPopup(popup(c.title(f),c.sub||'',f.properties,c.fields,c.note),
                               {maxWidth:340,closeButton:true});
      if(c.searchable) registry.push({name:c.title(f)||'',layer:l});
    }
  });
  layers[c.file]=layer;
  if(c.on) layer.addTo(map);

  const el=document.createElement('label');
  el.className='layer';
  el.innerHTML=`<input type="checkbox" ${c.on?'checked':''} aria-label="${c.label}">
    <span class="sw" style="background:${c.swatch}"></span>
    <span class="nm">${c.label}</span>
    <span class="ct">${gj.features.length.toLocaleString()}</span>`;
  el.querySelector('input').addEventListener('change',e=>{
    e.target.checked?layer.addTo(map):map.removeLayer(layer);
  });
  document.getElementById(c.group).appendChild(el);
}

const CONF=[
 {file:'boundary',group:'grp-base',label:'Municipal boundary',swatch:'#1A1917',on:true,
  style:()=>({color:'#1A1917',weight:2.2,fill:false}),
  title:f=>f.properties.ADMIN_AREA_NAME,sub:'BC ABMS legal boundary',
  fields:[['area_km2','Legal area (km²)']],
  note:'The legal boundary includes foreshore. Densities use StatCan land area (11.79 km²).'},

 {file:'neighbourhoods',group:'grp-base',label:'Neighbourhoods',swatch:'#8B857C',on:true,
  style:()=>({color:'#8B857C',weight:1.4,dashArray:'5 4',fill:false}),
  title:f=>f.properties.neighbourhood,sub:'CNV neighbourhood',
  fields:[['population_2021','Population (est.)'],['adult_population_18plus_proxy','Adults 18+ (proxy)'],
   ['senior_population_65plus','Seniors 65+'],['population_density','Persons / km²'],
   ['housing_density','Dwellings / km²'],['apartment_share','Apartment share'],
   ['building_count','Buildings']],
  note:'Areally interpolated from dissemination areas — an estimate, not a count.'},

 {file:'census_da',group:'grp-pop',label:'Population density',swatch:'#0F4C5C',on:true,
  style:f=>({fillColor:ramp(f.properties.population_density,[0,3000,6000,10000,15000,20000],BLUES),
             color:'#fff',weight:.5,fillOpacity:fillOpacity}),
  title:f=>'DA '+f.properties.DAUID,sub:'Dissemination area',
  fields:[['population_2021','Population'],['population_density','Persons / km²'],
   ['adult_population_18plus_proxy','Adults 18+ (proxy)'],['canadian_citizens_18plus','Citizens 18+'],
   ['senior_population_65plus','Seniors 65+'],['occupied_private_dwellings','Occupied dwellings'],
   ['multiunit_share','Multi-unit share'],['highrise_share','High-rise share'],
   ['land_area_km2','Land area (km²)']],
  note:'Statistics Canada 2021 Census Profile 98-401-X2021006.'},

 {file:'intersections',group:'grp-transport',label:'Public-space score',swatch:'#B08D57',on:true,
  point:(f,ll)=>L.circleMarker(ll,{radius:3+(f.properties.public_space_composite||0)/13,
    fillColor:ramp(f.properties.public_space_composite,[0,40,52,62,72,80],VIRIDIS),
    color:'#fff',weight:.8,fillOpacity:.92}),
  title:f=>f.properties.street_names||f.properties.intersection_id,
  sub:'Intersection',searchable:true,
  fields:[['composite_rank','Rank'],['public_space_composite','Composite'],
   ['neighbourhood','Neighbourhood'],['road_hierarchy_score','Road hierarchy'],
   ['transit_score','Transit'],['pedestrian_proxy_score','Pedestrian (proxy)'],
   ['parking_access_score','Parking access'],['intersection_prominence_score','Prominence'],
   ['safety_score','Safety (separate)'],['signalised','Signalised'],
   ['collision_count','Collisions'],['transit_departures_250m','Departures 250 m'],
   ['onstreet_supply_250m','On-street spaces 250 m'],['population_2021_400m','Residents 400 m']],
  note:'Composite = mean of five full-coverage components. Safety is reported separately, not inside it.'},

 {file:'roads',group:'grp-transport',label:'Street centrelines',swatch:'#B4ADA2',on:false,
  style:f=>({color:{freeway:'#7F1D1D',arterial:'#8C2F39',Major:'#B08D57',collector:'#EAB308',
    Minor:'#B4ADA2',local:'#CBD5E1'}[f.properties.ROADCLASS]||'#CBD5E1',
    weight:{freeway:3,arterial:2.4,Major:2,collector:1.5}[f.properties.ROADCLASS]||.8}),
  title:f=>f.properties.full_street_name,sub:'Street segment',
  fields:[['ROADCLASS','Class'],['NOLANES','Lanes'],['ONEWAY','One way']]},

 {file:'transit_stops',group:'grp-transport',label:'Transit stops',swatch:'#3C7C8A',on:false,
  point:(f,ll)=>L.circleMarker(ll,{radius:2.5+Math.sqrt(f.properties.trips_per_weekday||0)/3.2,
    fillColor:'#3C7C8A',color:'#fff',weight:.7,fillOpacity:.88}),
  title:f=>f.properties.stop_name,sub:'TransLink stop',
  fields:[['trips_per_weekday','Departures / weekday'],['trips_am_peak','AM peak departures'],
   ['am_peak_avg_headway_min','AM peak headway (min)'],['routes_serving','Routes']],
  note:'Scheduled service from the TransLink GTFS feed for a representative weekday.'},

 {file:'parking_occupancy',group:'grp-transport',label:'Parking occupancy',swatch:'#B08D57',on:false,
  style:f=>({color:ramp(f.properties.occupancy_peak,[0,.4,.6,.75,.85,1.0],HEAT),weight:3,opacity:.9}),
  title:()=>'On-street segment',sub:'Surveyed parking',
  fields:[['supply_spaces','Supply (spaces)'],['occupancy_peak','Peak occupancy'],
   ['occupancy_mean','Mean occupancy'],['peak_period','Busiest period'],
   ['at_practical_capacity','At/above 85%']],
  note:'Survey by Bunt &amp; Associates, Dec 2022 – Feb 2023. Not a real-time feed.'},

 {file:'parking_lots',group:'grp-transport',label:'Off-street lots',swatch:'#0B3A46',on:false,
  point:(f,ll)=>L.circleMarker(ll,{radius:6,fillColor:'#0B3A46',color:'#fff',weight:1.4,fillOpacity:.95}),
  title:f=>f.properties.LOT_NAME,sub:'Parking lot',
  fields:[['ADDRESS','Address'],['Operator','Operator'],['SPACES_WEEKDAY','Weekday spaces'],
   ['ACCESSIBLE_PARKING_SPACES','Accessible spaces'],['PAY_PARKING','Pay parking']]},

 {file:'collisions',group:'grp-transport',label:'Collisions (ICBC)',swatch:'#8C2F39',on:false,
  point:(f,ll)=>L.circleMarker(ll,{radius:3+Math.sqrt(f.properties.crash_count||0)/1.5,
    fillColor:'#8C2F39',color:'#fff',weight:.7,fillOpacity:.7}),
  title:()=>'Recorded collisions',sub:'ICBC, name-matched',
  fields:[['crash_count','Crashes'],['icbc_locations','ICBC location']],
  note:'Only high-confidence matches. Intersections without data are unknown, not zero.'},

 {file:'voting_places',group:'grp-civic',label:'Voting places (2022)',swatch:'#8C2F39',on:true,
  point:(f,ll)=>L.circleMarker(ll,{radius:8,fillColor:'#8C2F39',color:'#fff',weight:2.2,fillOpacity:.97}),
  title:f=>f.properties.place_name,sub:'2022 voting place',searchable:true,
  fields:[['address','Address'],['place_type','Type'],['mayoral_votes_2022','Mayoral votes 2022']],
  note:'CNV runs any-voting-place elections, so there are no polling-division catchments.'},

 {file:'seniors_housing',group:'grp-civic',label:'Seniors-eligible housing',swatch:'#6B4E71',on:false,
  style:()=>({color:'#6B4E71',weight:1.5,fillOpacity:.6}),
  point:(f,ll)=>L.circleMarker(ll,{radius:6,fillColor:'#6B4E71',color:'#fff',weight:1.4,fillOpacity:.95}),
  title:f=>f.properties.ah_name||f.properties.BUILDING_NAME||'Seniors housing',
  sub:'Municipal eligibility record',
  fields:[['ah_address','Address'],['ah_total_units','Units'],['ah_eligibility','Eligibility'],
   ['classification_basis','Evidence']]}
];

(async()=>{
  const st=await (await fetch('data/stats.json')).json();
  const tiles=[
    [st.population.toLocaleString(),'Population'],
    [st.density.toLocaleString(),'Persons / km²'],
    [st.multiunit_pct+'%','Multi-unit'],
    [st.adults.toLocaleString(),'Adults 18+*'],
    [st.intersections.toLocaleString(),'Intersections'],
    [st.transit_stops.toLocaleString(),'Transit stops'],
  ];
  document.getElementById('tiles').innerHTML=tiles.map(([v,k])=>
    `<div class="tile"><div class="v">${v}</div><div class="k">${k}</div></div>`).join('');

  for(const c of CONF) await addLayer(c);

  document.getElementById('op').addEventListener('input',e=>{
    fillOpacity=e.target.value/100;
    document.getElementById('opv').textContent=e.target.value+'%';
    if(layers['census_da']) layers['census_da'].setStyle(f=>({
      fillColor:ramp(f.properties.population_density,[0,3000,6000,10000,15000,20000],BLUES),
      color:'#fff',weight:.5,fillOpacity}));
  });

  const box=document.getElementById('search'),out=document.getElementById('results');
  box.addEventListener('input',()=>{
    const q=box.value.trim().toLowerCase(); out.innerHTML='';
    if(q.length<2)return;
    registry.filter(r=>r.name.toLowerCase().includes(q)).slice(0,7).forEach(r=>{
      const b=document.createElement('button'); b.textContent=r.name;
      b.onclick=()=>{const ll=r.layer.getLatLng?r.layer.getLatLng():r.layer.getBounds().getCenter();
        map.setView(ll,17); r.layer.openPopup();};
      out.appendChild(b);
    });
    if(!out.children.length) out.innerHTML='<button disabled style="color:var(--faint)">No match</button>';
  });

  const legend=L.control({position:'bottomright'});
  legend.onAdd=()=>{const d=L.DomUtil.create('div','legend');
    d.innerHTML='<h4>Population density</h4>'+
      [['#EFF6FF','< 3k'],['#BFDBFE','3–6k'],['#93C5FD','6–10k'],
       ['#60A5FA','10–15k'],['#0F4C5C','15–20k'],['#1D4ED8','20k+ /km²']]
      .map(([c,l])=>`<div class="row"><i style="background:${c}"></i><span class="lb">${l}</span></div>`).join('')+
      '<h4 style="margin-top:9px">Public-space score</h4>'+
      [['#F6F0E4','low'],['#DBC49B','mid'],['#8A6A3B','high']]
      .map(([c,l])=>`<div class="row"><i style="background:${c}"></i><span class="lb">${l}</span></div>`).join('');
    return d;};
  legend.addTo(map);

  document.getElementById('meta').innerHTML=
    `Analysis CRS EPSG:26910 (NAD83 / UTM 10N); displayed in EPSG:4326.<br>
     Census: Statistics Canada 2021, ${st.das} dissemination areas, land area ${st.land_km2} km².<br>
     Boundary: BC ABMS. Transport &amp; parking: City of North Vancouver ArcGIS.<br>
     Transit: TransLink GTFS (${st.departures.toLocaleString()} weekday departures).<br>
     Collisions: ICBC. Geometry generalised for display only.<br>
     <em>*Adults 18+ is a demographic proxy, not an elector count.</em>`;

  const files=['public_space_summary.csv','census_area_rankings.csv','neighbourhood_rankings.csv',
   'housing_rankings.csv','polling_location_summary.csv','election_turnout_series.csv',
   'traffic_intersection_summary.csv','transit_intersection_summary.csv',
   'parking_intersection_summary.csv','safety_intersection_summary.csv',
   'field_audit_checklist.csv','data_inventory.csv','data_gaps.csv'];
  document.getElementById('downloads').innerHTML=
    files.map(f=>`<a href="tables/${f}" download>${ICON_FILE}<span>${f}</span></a>`).join('');
})();
</script>
</body>
</html>
"""
