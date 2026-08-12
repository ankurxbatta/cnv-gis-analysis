# ADDING_DATA.md — How to find data and add it as a layer

A practical guide to finding a new dataset, checking it's usable, and wiring it into this
project so it flows through to the maps and the website.

Every command below was run against the live services and works as written.

---

## The short version

```bash
# 1. find it (see §1 for the search recipes)
# 2. add ~10 lines to config/sources.yaml
# 3. download and check it
python scripts/01_download.py --only my_new_source
python scripts/02_validate_sources.py
# 4. use it — clip to CNV in a prepare script, or add it to a map
```

---

## 1. Where to search, and how

### 1a. BC Data Catalogue — the province's open data

Search from the command line rather than the website; it's faster and shows the formats:

```bash
curl -sS "https://catalogue.data.gov.bc.ca/api/3/action/package_search?q=parks&rows=5" \
 | python3 -c "
import sys, json
for p in json.load(sys.stdin)['result']['results']:
    fmts = sorted({r['format'] for r in p.get('resources', [])})
    print(f\"{p['title']}\n   name: {p['name']}\n   formats: {fmts}\")"
```

Swap `q=parks` for anything: `q=traffic`, `q=schools`, `q=zoning`.

> Watch the **licence**. Look for "Open Government Licence – British Columbia". Some
> records are `Access Only`, which means you may read but not redistribute — the BC
> Traffic Data Program is one, and it's noted in `DATA_GAPS.md`.

### 1b. BC WFS — 895 live provincial layers

The catalogue's spatial layers are served as WFS. List everything once, then grep it:

```bash
curl -sS "https://openmaps.gov.bc.ca/geo/pub/wfs?service=WFS&version=2.0.0&request=GetCapabilities" \
  -o /tmp/wfs.xml

grep -o '<Name>pub:' /tmp/wfs.xml | wc -l          # 895 layers

# find layers matching a keyword
grep -oE "<Name>pub:[A-Z_.]*PARK[A-Z_.]*</Name>" /tmp/wfs.xml | sed 's/<[^>]*>//g' | sort -u
```

The part after `pub:` is the `typename` you put in `sources.yaml`.

### 1c. City of North Vancouver ArcGIS — the richest source for this project

The City runs a public ArcGIS REST server. Browse it as JSON:

```bash
S=https://gisext2.cnv.org/arcgis/rest/services

curl -sS "$S?f=json"                      # folders: Applications, BaseMapServices, ...
curl -sS "$S/Applications?f=json"         # 19 services in that folder
curl -sS "$S/Applications/Parks/MapServer?f=json" \
 | python3 -c "import sys,json;[print(l['id'], l['name']) for l in json.load(sys.stdin)['layers']]"
```

Then inspect a single layer before committing to it — check the fields and the count:

```bash
L=$S/Applications/Parks/MapServer/1
curl -sS "$L?f=json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('geometry :', d.get('geometryType'))
print('fields   :', [f['name'] for f in d['fields']])"

curl -sS "$L/query?where=1%3D1&returnCountOnly=true&f=json"
```

`TransportMAP` alone has **230 layers** — worth browsing:

```bash
curl -sS "$S/BaseMapServices/TransportMAP/MapServer?f=json" \
 | python3 -c "import sys,json;[print(l['id'], l['name']) for l in json.load(sys.stdin)['layers']]"
```

### 1d. Other portals worth knowing

| Source | URL | Notes |
|---|---|---|
| Statistics Canada | `www12.statcan.gc.ca/census-recensement/2021/` | Census profiles, boundary files |
| District of North Vancouver | `geoweb.dnv.org/data/` | 121 shapefiles; covers DNV, some include CNV |
| Metro Vancouver | `open-data-portal-metrovancouver.hub.arcgis.com` | 58 services; regional, no traffic data |
| TransLink | `translink.ca/.../gtfs` | GTFS only — no traffic or screenline counts |

---

## 2. Decide whether it's usable

Three questions, in order:

**Is it data or a picture?** A **WMS** endpoint returns rendered images you cannot query
or analyse. You want **WFS**, **Esri REST**, or a downloadable file. See `DATA_SOURCES.md`
for the formats already in use.

**Does it actually cover the City?** The commonest trap here. "North Vancouver" usually
means the **District**, a separate municipality. Always clip to the CNV boundary and count
what survives:

```python
from common import load_raw_vector, clip_to_cnv, load_boundary
g = load_raw_vector("cnv/my_layer.geojson")
inside = clip_to_cnv(g, load_boundary(), how="within")
print(f"{len(inside)} of {len(g)} features are inside CNV")
```

If that prints `0 of 400`, the dataset is District-only.

**What's the licence?** Record it in `sources.yaml`; it flows into
`LICENSES_AND_ATTRIBUTION.md`.

---

## 3. Add it to `config/sources.yaml`

Pick the handler that matches how the data is served.

### Esri REST layer (most CNV data)

```yaml
  - source_id: cnv_playgrounds
    organization: "City of North Vancouver"
    dataset: "Playgrounds"
    handler: arcgis_layer
    service: "Applications/Parks/MapServer"
    layer_id: 2
    url: "https://gisext2.cnv.org/arcgis/rest/services/Applications/Parks/MapServer/2"
    out_dir: cnv
    filename: cnv_playgrounds.geojson
    format: GeoJSON
    geographic_level: point
    coverage: "City of North Vancouver"
    license: "City of North Vancouver open data terms - verify"
    expected_count: 24          # optional; the downloader warns if it differs
    notes: "Playground points from the Parks application."
```

### WFS layer (provincial data)

```yaml
  - source_id: bc_schools
    organization: "Province of BC"
    dataset: "Public schools"
    handler: wfs
    url: "https://catalogue.data.gov.bc.ca/dataset/..."
    typename: "WHSE_IMAGERY_AND_BASE_MAPS.GSR_SCHOOLS_K_TO_12_SVW"
    cql_filter: "SCHOOL_DISTRICT_NAME LIKE '%North Vancouver%'"
    out_dir: bcdata
    filename: bc_schools_north_van.geojson
    format: GeoJSON
    license: "Open Government Licence - British Columbia"
```

`cql_filter` is optional but filters server-side, which is far faster than downloading the
province and discarding 99% of it.

### A file (zip, CSV, PDF)

```yaml
  - source_id: geoweb_sidewalk_centreline
    organization: "District of North Vancouver - GEOweb"
    dataset: "Sidewalk centrelines"
    handler: http_file
    url: "https://geoweb.dnv.org/data/"
    download_url: "https://geoweb.dnv.org/Products/Data/SHP/RodSidewalkCenterline_shp.zip"
    out_dir: dnv_geoweb
    filename: RodSidewalkCenterline_shp.zip
    format: "Shapefile (zip)"
    expect_magic: zip          # rejects an HTML error page saved as .zip
    license: "District of North Vancouver GEOweb terms"
```

### An HTML page to scrape later

```yaml
  - source_id: cnv_some_page
    handler: html_page
    url: "https://www.cnv.org/..."
    out_dir: cnv
    filename: cnv_some_page.html
    format: HTML
```

---

## 4. Download and check it

```bash
python scripts/01_download.py --only cnv_playgrounds
python scripts/02_validate_sources.py
```

The downloader writes the file to `data/raw/<out_dir>/`, never overwrites without
`--force`, computes a SHA256, and writes a `.meta.json` sidecar recording the URL, licence,
retrieval time and feature count. Validation then confirms the file parses and carries a
CRS.

If a layer has awkward geometry the endpoint can't serialise, add `page_size: 100` or
`paging: oid` — the downloader bisects around unreadable features rather than failing.

---

## 5. Turn it into a processed layer

Add a few lines to whichever `scripts/0*_prepare_*.py` fits the theme:

```python
g = load_raw_vector("cnv/cnv_playgrounds.geojson", crs)
g = clip_to_cnv(g, boundary, how="within")     # "within" for points, "clip" for lines/polygons
g = tag_source(g, "City of North Vancouver ArcGIS - Playgrounds",
               "https://gisext2.cnv.org/arcgis/rest/services/Applications/Parks/MapServer/2")
g.to_file(out, layer="playgrounds", driver="GPKG")
log.info("playgrounds inside CNV: %d", len(g))
```

`tag_source` attaches `source`, `source_url`, `licence` and `prepared_utc` — a QA test
fails the build if a processed layer has no source.

Then re-run:

```bash
python run_pipeline.py --process --maps
python -m pytest
```

---

## 6. Show it on the website

Export it in `scripts/19_create_interactive_map.py`:

```python
export(gpd.read_file(DATA_PROCESSED / "cnv_parks.gpkg", layer="playgrounds"),
       "playgrounds", ["NAME", "ADDRESS"], 0, simplify=False)
```

Add it to the `CONF` array in `scripts/web_template.py`:

```javascript
 {file:'playgrounds', group:'grp-base', label:'Playgrounds', swatch:'#2F6B4F', on:false,
  point:(f,ll)=>L.circleMarker(ll,{radius:5,fillColor:'#2F6B4F',color:'#fff',weight:1}),
  title:f=>f.properties.NAME, sub:'Playground',
  fields:[['ADDRESS','Address']]},
```

Then `./publish.sh` — the site rebuilds, CI validates it, Vercel redeploys.

---

## 7. Or just look at it in QGIS first

For a quick look before committing to any of the above:

- **A local file** — drag the `.gpkg`, `.shp` or `.geojson` straight onto the QGIS canvas.
- **An Esri REST service** — Browser panel → right-click **ArcGIS REST Servers** → **New
  Connection** → paste `https://gisext2.cnv.org/arcgis/rest/services`.
- **A WFS layer** — Browser panel → right-click **WFS / OGC API - Features** → **New
  Connection** → `https://openmaps.gov.bc.ca/geo/pub/wfs`.
- **An XYZ basemap** — Browser panel → **XYZ Tiles** → **New Connection**.

Nothing needs a plugin; all four are core QGIS.

> If you add layers by hand in QGIS, they live only in that project. Anything that should
> survive a rebuild has to go through `sources.yaml`, or the next
> `python scripts/23_create_qgis_project.py` will overwrite the project without them.
> Close QGIS before regenerating.

---

## Checklist for any new layer

- [ ] Licence recorded, and redistribution allowed if the site is public
- [ ] Coverage confirmed — **City**, not District
- [ ] Clipped to the CNV boundary
- [ ] `tag_source()` applied so provenance survives
- [ ] Reprojected to EPSG:26910 (`load_raw_vector` does this)
- [ ] Counts logged, so a silent change is visible on the next run
- [ ] If it's a proxy or partial, said so in the field name and in `DATA_GAPS.md`
- [ ] `python -m pytest` passes
