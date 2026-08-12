"""HTML template for the interactive civic geography explorer.

Kept separate from the export logic so the markup stays readable.
Design: data-dense dashboard — blue data with amber highlights, Fira Sans/Fira Code,
light and dark themes, SVG icons throughout (no emoji), WCAG AA contrast.
"""

INDEX_HTML_RAW = r"""<!doctype html>
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

.theme{display:flex;align-items:flex-start;gap:10px;padding:10px 10px;margin:0 -10px 2px;
  border-radius:9px;cursor:pointer;transition:background .15s ease}
.theme:hover{background:var(--surface-2)}
.theme.active{background:var(--surface-2);box-shadow:inset 3px 0 0 var(--petrol-700)}
.theme input{margin-top:3px;width:16px;height:16px;accent-color:var(--petrol-700);cursor:pointer;flex:0 0 16px}
.theme .tt{font-size:13.5px;font-weight:600;line-height:1.3}
.theme .td{font-size:11.5px;color:var(--faint);margin-top:2px;line-height:1.4}
.sub{display:flex;flex-wrap:wrap;gap:6px;padding:4px 0 2px}
.sub button{font:inherit;font-size:12px;padding:6px 11px;border:1px solid var(--line-strong);
  border-radius:20px;background:var(--surface);color:var(--muted);cursor:pointer;
  transition:all .15s ease;min-height:34px}
.sub button:hover{border-color:var(--petrol-500);color:var(--fg)}
.sub button.on{background:var(--petrol-700);border-color:var(--petrol-700);color:#fff;font-weight:600}
.sub button:focus-visible{outline:2px solid var(--petrol-500);outline-offset:2px}
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
.leaflet-control-attribution{background:transparent!important;color:var(--faint)!important;
  font-size:9.5px!important;padding:1px 5px!important;box-shadow:none!important}
.leaflet-control-attribution a{color:var(--faint)!important;text-decoration:none}

#toggleSide{position:absolute;top:12px;left:12px;z-index:var(--z-float);display:none}

__MOBILE_CSS__
@media (prefers-reduced-motion:reduce){
  *{transition-duration:.01ms !important;animation-duration:.01ms !important}
}
</style>
</head>
<body>
<div id="app">
  <aside id="side">
    <button class="sheet-grab" id="grab" aria-label="Expand panel" aria-expanded="false"><span></span></button>
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

      <h2 class="sec">Show on the map</h2>
      <div id="themes" role="radiogroup" aria-label="Map theme"></div>
      <div id="subthemes"></div>

      <h2 class="sec">Reference layers</h2><div id="grp-base"></div>

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
        visibility, access and feasibility only. It contains no political variable &mdash; no
        party, candidate or voting history &mdash; and makes no inference from demographics
        to political preference.
      </div>
      <div class="callout warn">
        <strong>Coverage varies by layer.</strong> Collision data covers about half of
        intersections &mdash; the rest are unknown, not zero. Measured traffic volumes exist
        for 40 of 503. Parking occupancy is a 2022&ndash;23 survey, not live data.
      </div>

      <a class="linkrow" href="recommendations.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-4.5-7-10a7 7 0 1114 0c0 5.5-7 10-7 10z"/><circle cx="12" cy="11" r="2.5"/></svg>
        <span>Where people are &mdash; top public locations</span>
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
const map=window.map=L.map('map',{preferCanvas:true,zoomControl:false,
  attributionControl:false}).setView([49.322,-123.075],14);
L.control.attribution({prefix:false,position:'bottomright'})
  .addAttribution('&copy; OpenStreetMap &copy; CARTO').addTo(map);
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
    {maxZoom:19}).addTo(map);
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

// Reference layers only. The DA choropleth is driven by the theme selector below.
const CONF=[
 {file:'boundary',group:'grp-base',label:'Municipal boundary',swatch:'#1A1917',on:true,
  style:()=>({color:'#1A1917',weight:2.2,fill:false}),
  title:f=>f.properties.ADMIN_AREA_NAME,sub:'BC ABMS legal boundary',
  fields:[['area_km2','Legal area (km²)']],
  note:'The legal boundary includes foreshore. Densities use StatCan land area (11.79 km²).'},

 {file:'neighbourhoods',group:'grp-base',label:'Neighbourhoods',swatch:'#8B857C',on:true,
  style:()=>({color:'#57534E',weight:1.5,dashArray:'5 4',fill:false}),
  title:f=>f.properties.neighbourhood,sub:'CNV neighbourhood',
  fields:[['population_2021','Population (est.)'],['adult_population_18plus_proxy','Adults 18+ (proxy)'],
   ['senior_population_65plus','Seniors 65+'],['population_density','Persons / km²'],
   ['housing_density','Dwellings / km²'],['apartment_share','Apartment share']],
  note:'Areally interpolated from dissemination areas — an estimate, not a count.'},

 {file:'voting_places',group:'grp-base',label:'Voting places (2022)',swatch:'#8C2F39',on:true,
  point:(f,ll)=>L.circleMarker(ll,{radius:8,fillColor:'#8C2F39',color:'#fff',weight:2.2,fillOpacity:.97}),
  title:f=>f.properties.place_name,sub:'2022 voting place',searchable:true,
  fields:[['address','Address'],['place_type','Type'],['mayoral_votes_2022','Mayoral votes 2022']],
  note:'CNV runs any-voting-place elections, so there are no polling-division catchments.'}
];

// ---------------------------------------------------------------------------
// THEMES — the four questions this map answers.
// ---------------------------------------------------------------------------
const THEMES={
 people:{
   label:'Where the most people are',
   desc:'Residents per km², 2021 Census',
   src:'census_da', field:'population_density', ramp:'BLUES',
   legend:'Residents / km²', fmt:v=>Math.round(v).toLocaleString(),
   breaks:[0,3000,6000,10000,15000,20000],
   labels:['< 3k','3–6k','6–10k','10–15k','15–20k','20k+'],
   fields:[['population_2021','Population'],['population_density','Residents / km²'],
     ['occupied_private_dwellings','Occupied dwellings'],['land_area_km2','Land area (km²)']]},

 adults:{
   label:'Where the most adults 18+ are',
   desc:'A demographic PROXY for potential electorate — not an elector count',
   src:'census_da', field:'adult_population_density', ramp:'PETROL',
   legend:'Adults 18+ / km²', fmt:v=>Math.round(v).toLocaleString(),
   breaks:[0,2500,5000,8500,12500,17000],
   labels:['< 2.5k','2.5–5k','5–8.5k','8.5–12.5k','12.5–17k','17k+'],
   sub:[['adult_population_density','Adults 18+ (proxy)'],
        ['citizen_adult_density','Canadian citizens 18+']],
   fields:[['adult_population_18plus_proxy','Adults 18+ (proxy)'],
     ['adult_population_density','Adults 18+ / km²'],
     ['canadian_citizens_18plus','Canadian citizens 18+'],
     ['population_2021','Total population']],
   note:'PROXY. Population aged 18+ from the 2021 Census, used as a proxy for potential '+
        'electorate size. It is NOT a count of eligible or registered electors — it ignores '+
        'citizenship and residency rules and reflects 2021.'},

 age:{
   label:'Age distribution by area',
   desc:'Choose an age band',
   src:'census_da', field:'age_18_34_proxy', ramp:'AMBER', perArea:true,
   legend:'Persons / km²', fmt:v=>Math.round(v).toLocaleString(),
   breaks:[0,500,1500,3000,5000,8000],
   labels:['< 500','0.5–1.5k','1.5–3k','3–5k','5–8k','8k+'],
   sub:[['age_0_14','Under 15'],['age_18_34_proxy','18–34'],['age_35_49','35–49'],
        ['age_50_64','50–64'],['senior_population_65plus','65+'],
        ['senior_population_75plus','75+'],['senior_population_85plus','85+']],
   fields:[['age_0_14','Under 15'],['age_18_34_proxy','18–34 (proxy)'],['age_35_49','35–49'],
     ['age_50_64','50–64'],['senior_population_65plus','65+'],
     ['senior_population_75plus','75+'],['senior_population_85plus','85+'],
     ['population_2021','Total population']],
   note:'The 18–34 band is a proxy: the Census publishes 15–19 as one band, so ages 18–19 '+
        'are apportioned as two fifths of it.'},

 residence:{
   label:'Residence type',
   desc:'Share of homes by dwelling structure',
   src:'housing_da', field:'apartment_share', ramp:'PURPLE', pct:true,
   legend:'Share of dwellings', fmt:v=>(v*100).toFixed(0)+'%',
   breaks:[0,.2,.4,.6,.8,.95],
   labels:['< 20%','20–40%','40–60%','60–80%','80–95%','95%+'],
   sub:[['apartment_share','Apartments'],['highrise_share','High-rise (5+)'],
        ['townhouse_share','Townhouse / row'],['single_family_share','Single detached'],
        ['multiunit_share','All multi-unit']],
   fields:[['dominant_dwelling_type','Most common type'],
     ['occupied_private_dwellings','Occupied dwellings'],
     ['dw_single_detached','Single detached'],['dw_row_house','Row house'],
     ['dw_apartment_lt5_storeys','Apartment < 5 storeys'],
     ['dw_apartment_5plus_storeys','Apartment 5+ storeys'],
     ['apartment_share','Apartment share'],['single_family_share','Detached share']]}
};

const RAMPS={
 BLUES:['#F2EEE7','#DDE7E5','#B9CFCE','#86ADB0','#4A848E','#0F4C5C'],
 PETROL:['#F4F1EA','#D8E3E2','#A8C6C6','#6FA3A9','#3B7B88','#0B3A46'],
 AMBER:['#F9F4E9','#EFE1C4','#DFC898','#CBA96D','#B08D57','#8A6A3B'],
 PURPLE:['#F5F1F3','#E4D8DE','#CBB4C1','#AC8CA0','#8A6580','#5E4258']
};

(async()=>{
  const st=await (await fetch('data/stats.json')).json();
  document.getElementById('tiles').innerHTML=[
    [st.population.toLocaleString(),'Population'],
    [st.density.toLocaleString(),'Persons / km²'],
    [st.multiunit_pct+'%','Multi-unit'],
    [st.adults.toLocaleString(),'Adults 18+*'],
    [st.seniors.toLocaleString(),'Seniors 65+'],
    [st.das.toLocaleString(),'Census areas'],
  ].map(([v,k])=>`<div class="tile"><div class="v">${v}</div><div class="k">${k}</div></div>`).join('');

  for(const c of CONF) await addLayer(c);

  // --- theme engine -------------------------------------------------------
  const cache={};
  const getData=async src=>cache[src]||(cache[src]=await (await fetch(`data/${src}.geojson`)).json());
  let themeLayer=null, current='people', currentField=null;

  const legend=L.control({position:'bottomright'});
  let legendDiv=null;
  legend.onAdd=()=>{legendDiv=L.DomUtil.create('div','legend');return legendDiv;};
  legend.addTo(map);

  function drawLegend(t,fieldLabel){
    const cols=RAMPS[t.ramp];
    legendDiv.innerHTML=`<h4>${fieldLabel||t.legend}</h4>`+
      cols.map((c,i)=>`<div class="row"><i style="background:${c}"></i>`+
        `<span class="lb">${t.labels[i]}</span></div>`).join('');
  }

  async function showTheme(key,fieldOverride){
    current=key;
    const t=THEMES[key];
    const field=fieldOverride||t.field;
    currentField=field;
    const gj=await getData(t.src);

    // Age bands are stored as counts; show them per km² so areas compare fairly.
    const areaOf=f=>f.properties.land_area_km2||null;
    const valueOf=f=>{
      const raw=f.properties[field];
      if(raw===null||raw===undefined) return null;
      if(t.perArea){const a=areaOf(f); return a?raw/a:null;}
      return raw;
    };

    if(themeLayer) map.removeLayer(themeLayer);
    themeLayer=L.geoJSON(gj,{
      style:f=>({fillColor:ramp(valueOf(f),t.breaks,RAMPS[t.ramp]),
                 color:'#fff',weight:.5,fillOpacity:fillOpacity}),
      onEachFeature:(f,l)=>{
        const v=valueOf(f);
        const sub=(t.sub||[]).find(x=>x[0]===field);
        const head=sub?sub[1]:t.legend;
        l.bindPopup(popup(`DA ${f.properties.DAUID}`,
          `${head} — ${v==null?'no data':t.fmt(v)}`,
          f.properties,t.fields,t.note),{maxWidth:340});
      }
    });
    themeLayer.addTo(map);
    if(themeLayer.bringToBack) themeLayer.bringToBack();

    const sub=(t.sub||[]).find(x=>x[0]===field);
    drawLegend(t,sub?sub[1]:t.legend);

    // sub-theme chips
    const holder=document.getElementById('subthemes');
    if(t.sub&&t.sub.length){
      holder.innerHTML='<div class="sub">'+t.sub.map(([f2,lab])=>
        `<button data-f="${f2}" class="${f2===field?'on':''}">${lab}</button>`).join('')+'</div>';
      holder.querySelectorAll('button').forEach(b=>
        b.onclick=()=>showTheme(key,b.dataset.f));
    } else holder.innerHTML='';

    document.querySelectorAll('.theme').forEach(el=>
      el.classList.toggle('active',el.dataset.k===key));
  }

  document.getElementById('themes').innerHTML=Object.entries(THEMES).map(([k,t])=>
    `<label class="theme ${k===current?'active':''}" data-k="${k}">
       <input type="radio" name="theme" value="${k}" ${k===current?'checked':''}>
       <span><span class="tt">${t.label}</span><span class="td">${t.desc}</span></span>
     </label>`).join('');
  document.querySelectorAll('input[name=theme]').forEach(r=>
    r.onchange=()=>showTheme(r.value));

  await showTheme('people');

  document.getElementById('op').addEventListener('input',e=>{
    fillOpacity=e.target.value/100;
    document.getElementById('opv').textContent=e.target.value+'%';
    if(themeLayer){
      const t=THEMES[current];
      themeLayer.setStyle(f=>{
        const a=f.properties.land_area_km2||null;
        const raw=f.properties[currentField];
        const v=(raw==null)?null:(t.perArea&&a?raw/a:raw);
        return {fillColor:ramp(v,t.breaks,RAMPS[t.ramp]),color:'#fff',weight:.5,fillOpacity};
      });
    }
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

  document.getElementById('meta').innerHTML=
    `Analysis CRS EPSG:26910 (NAD83 / UTM 10N); displayed in EPSG:4326.<br>
     Census: Statistics Canada 2021 Profile 98-401-X2021006, ${st.das} dissemination areas.<br>
     Boundaries: cartographic (shoreline-clipped) files; densities use StatCan land area.<br>
     Voting places: City of North Vancouver official records.<br>
     <em>*Adults 18+ is a demographic proxy, not an elector count.</em>`;

  const files=['census_area_rankings.csv','neighbourhood_rankings.csv','housing_rankings.csv',
   'polling_location_summary.csv','election_turnout_series.csv',
   'campaign_visibility_recommendations.csv','data_inventory.csv','data_gaps.csv'];
  document.getElementById('downloads').innerHTML=
    files.map(f=>`<a href="tables/${f}" download>${ICON_FILE}<span>${f}</span></a>`).join('');
})();
__MOBILE_JS__
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Shared mobile layer. Injected into all three pages so they behave identically
# on a phone: the map goes full-screen and the panel becomes a bottom sheet that
# can be dragged or tapped between a peek and a full state.
# ---------------------------------------------------------------------------

MOBILE_CSS = r"""
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
"""

MOBILE_JS = r"""
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
"""


INDEX_HTML = INDEX_HTML_RAW.replace("__MOBILE_CSS__", MOBILE_CSS).replace("__MOBILE_JS__", MOBILE_JS)
