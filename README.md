# City of North Vancouver — GIS Data Research & Mapping

A reproducible, research-grade geospatial analysis of the **City of North Vancouver,
British Columbia** (Statistics Canada `CSDUID 5915051`; BC ABMS `LGL_ADMIN_AREA_ID 114`).

The project has two analytically separate components:

- **Civic demography** — population, age structure, housing stock, dwelling types, and
  aggregate electoral information (turnout, registered electors, voting places).
- **Public space & transportation** — roads, intersections, traffic, transit, parking,
  pedestrian infrastructure, safety and visibility.

> **Scope constraints.** No individual-level data is collected or derived. Population aged
> 18+ is reported as `adult_population_18plus_proxy`, a demographic proxy for potential
> electorate size — never as eligible or registered electors. The public-space score
> contains no political variable and makes no inference from demographics to political
> preference. These constraints are enforced by automated tests.

---

## What it produces

| Output | Location |
|---|---|
| 13 processed GeoPackages | `data/processed/` |
| 14 static maps | `outputs/maps/` |
| Interactive web map | `outputs/interactive/index.html` |
| 18 CSV tables (rankings, inventories, gaps) | `outputs/tables/` |
| Final report (HTML + PDF) | `outputs/report/` |

### Headline figures

| Measure | Value |
|---|---|
| Population (2021) | 58,120 — reconciles **exactly** with the published CSD total |
| Land area | 11.79 km² (StatCan) vs 14.92 km² legal boundary incl. foreshore |
| Population density | 4,930 / km² |
| Adults 18+ (proxy) | 49,248 |
| Canadian citizens 18+ | 41,130 — within **0.5%** of the 41,325 registered electors in 2022 |
| Multi-unit dwelling share | 85.8% |
| Dissemination areas | 79 |
| Street network | 941 segments, 139 km |
| Intersections derived | 503 (91% validated against an independent layer) |
| Transit stops in city | 172, with 15,961 scheduled weekday departures |
| On-street parking surveyed | 1,169 segments, 29,606 spaces |

---

## Installation

Requires **Python 3.11+**.

```bash
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Or with conda:

```bash
conda env create -f environment.yml
conda activate cnv-gis
```

`weasyprint` is optional and only needed for PDF output.

---

## Running the pipeline

```bash
python run_pipeline.py --all        # everything
python run_pipeline.py --download   # acquisition + validation
python run_pipeline.py --process    # boundary → census → … → scoring
python run_pipeline.py --maps       # static + interactive maps
python run_pipeline.py --report     # QA tests + final report
```

Stages run in order and **stop at the first failure**, so a broken stage never silently
feeds bad data downstream. Individual scripts also run standalone:

```bash
python scripts/01_download.py [--force] [--only SOURCE_ID ...] [--group statcan]
python scripts/04_prepare_census.py
...
python scripts/20_generate_report.py
```

First full run takes roughly 20 minutes, dominated by ~1.2 GB of Statistics Canada
downloads. Subsequent runs reuse the cache and complete in about a minute.

### QGIS desktop project (optional)

If QGIS is installed, regenerate the pre-styled desktop project:

```bash
./scripts/run_qgis_python.sh scripts/23_create_qgis_project.py
open outputs/qgis/CNV_GIS_Analysis.qgz
```

30 layers in 9 themed groups, a CARTO basemap underneath, and the same palette as
the web map. The wrapper boots QGIS's bundled Python — the macOS bundle needs
`PYTHONHOME`, `PROJ_DATA`, `GDAL_DATA` and a corrected prefix path before PyQGIS
will import and load its provider libraries.

No QGIS plugins are required: XYZ basemaps and every format used here are core.

### Viewing the interactive map

```bash
python -m http.server --directory outputs/interactive 8000
# then open http://localhost:8000
```

---

## Repository layout

```
config/          study_area.yaml, sources.yaml (72 audited sources), scoring.yaml
data/raw/        original downloads, never modified, each with a .meta.json sidecar
data/interim/    intermediate extracts and the research audit trails
data/processed/  analysis-ready GeoPackages (EPSG:26910)
scripts/         01–20, run in numeric order
outputs/         maps, interactive, tables, report
tests/           110 automated QA checks
logs/            per-script run logs
```

Raw data is **never overwritten** without `--force`. Every download is SHA256-hashed and
accompanied by a sidecar recording source URL, licence, retrieval time and record count.

---

## Where the data comes from

72 sources were audited live. Full details with endpoints and licences are in
[`DATA_SOURCES.md`](DATA_SOURCES.md).

- **Statistics Canada** — 2021 Census Profile `98-401-X2021006` (British Columbia
  dissemination-area file, 293 MB, preferred over the 2.2 GB national file) plus DA, DB and
  CSD boundary files.
- **City of North Vancouver** — the public ArcGIS REST server at `gisext2.cnv.org`, whose
  `TransportMAP` service alone exposes **230 layers** (roads, signals, parking supply and
  observed occupancy, sidewalks, zoning, OCP land use, affordable housing).
- **Province of BC** — ABMS municipal boundaries (WFS); MoTI traffic count stations
  (GeoServer WFS); residential care and assisted living registries; BC Housing data.
- **TransLink** — GTFS static feed.
- **ICBC** — Lower Mainland crash counts via the Tableau dashboard's own CSV export.

**Everything downloads automatically.** No dataset requires manual retrieval.

### Updating the data

```bash
python run_pipeline.py --download --force   # re-fetch everything
python scripts/01_download.py --only translink_gtfs --force   # refresh one source
```

Then re-run `--process`, `--maps` and `--report`. Compare the new SHA256 values in
`outputs/tables/data_inventory.csv` against the previous run to see exactly what changed.

---

## What is *not* available

Thirteen gaps are documented in full in [`DATA_GAPS.md`](DATA_GAPS.md), each with the
organizations searched, the URLs tried, the proxy used and the coverage achieved. The three
that most constrain interpretation:

- **No traffic counts on CNV municipal streets.** The BC Traffic Data Program covers
  provincial highways only, and its ten in-city stations are all on Highway 1 with counts no
  newer than 2016. The City publishes directional volumes for 38 of 941 segments. Only 40 of
  503 intersections have a measured volume, so `traffic_score` is primarily a road-hierarchy
  measure.
- **No published signal timing.** CNV holds cycle lengths and phasing and releases them on
  request, but publishes nothing. Every signalised location is marked `REQUEST_REQUIRED` and
  **no timing is estimated**.
- **No pedestrian counts.** Walk CNV (2017) is a perception survey. The only published count
  is a raster figure in the 2016 Moodyville study covering one corridor. The pedestrian
  measure is therefore an explicit *proxy*.

Two structural findings worth knowing:

- **Polling-division boundaries do not exist.** CNV runs "any voting place" elections — an
  elector may vote anywhere in the city — so there are no catchments to map. Votes at a
  place therefore cannot be attributed to nearby residents.
- **Evergreen House** (231 E 15th St, 284 long-term care beds) *is* in the City but is
  licensed under the *Hospital Act*, so it is absent from both provincial care registries.
  Building a seniors-care layer from those registries alone would badly undercount the City.

---

## Quality assurance

```bash
python -m pytest          # 110 checks
```

Covers CRS consistency, geometry validity, duplicate identifiers, population plausibility
(including that DA sums reconcile with published CSD totals), spatial containment, source
metadata presence, and the project's privacy and terminology rules — including that no
output uses the term "eligible voters", that no political field exists in the public-space
score, and that intersections without collision data are never scored as safe.

---

## Documentation

| File | Contents |
|---|---|
| [`DATA_SOURCES.md`](DATA_SOURCES.md) | All 72 sources with endpoints, licences and status |
| [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) | Every layer and field in `data/processed/` |
| [`METHODOLOGY.md`](METHODOLOGY.md) | Every formula, assumption and limitation |
| [`DATA_GAPS.md`](DATA_GAPS.md) | 13 documented gaps with proxies and coverage |
| [`LICENSES_AND_ATTRIBUTION.md`](LICENSES_AND_ATTRIBUTION.md) | Licence terms and required attribution |

---

## Licensing note

City of North Vancouver ArcGIS layers are served publicly without an explicit open-data
licence on the endpoints. This project treats them as publicly readable for research, which
is how they are served, but that is **not** the same as an open-data grant. Verify with
`gis@cnv.org` before redistributing those layers or publishing derived products
commercially. See [`LICENSES_AND_ATTRIBUTION.md`](LICENSES_AND_ATTRIBUTION.md).
