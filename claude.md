# CLAUDE.md — City of North Vancouver GIS Data Research & Mapping Project

## 0. Project objective

Build a reproducible, research-grade GIS/data-analysis pipeline for the **City of North Vancouver (CNV), British Columbia**.

The project has two related but analytically separate components:

### A. Voter Density & Polling Place Analysis
Identify geographic concentrations of population/adult population, housing units and housing types, age groups, polling/voting locations, and—only where legitimately available—aggregated electoral information.

### B. Public-Space / Sign-Waving Visibility Analysis
Build a neutral transportation/public-space analysis of roads, intersections, traffic, transit, parking, pedestrian/cycling proxies, safety, and visibility constraints.

**Important:** Do not obtain, infer, expose, or create individual-level voter identities, voter addresses, political preferences, or other personal political data. Use aggregated geographic data only. Treat Census adults 18+ as a **proxy for potential electorate**, not as exact eligible voters. Clearly document this limitation.

Do not make unsupported claims. If a dataset cannot be obtained, record it in `DATA_GAPS.md` and continue with the best defensible proxy.

---

# 1. Operating principles

1. Prefer official government sources.
2. Prefer machine-readable data over PDFs.
3. Prefer vector GIS formats: GeoPackage, GeoJSON, SHP, FGDB, GeoParquet.
4. Preserve raw downloads unchanged.
5. Never overwrite raw data.
6. Record source URL, download date, dataset name, license, geographic level, and processing steps.
7. Cache downloads so the pipeline is reproducible.
8. Use the smallest useful geographic unit available, but respect privacy.
9. Do not fabricate missing attributes.
10. Do not equate population age 18+ with legal voter eligibility.
11. Do not rank locations based on inferred political preferences.
12. Separate descriptive civic geography from campaign persuasion/targeting.
13. All map layers must have metadata and source attribution.
14. If an official endpoint fails, search the official portal for an equivalent downloadable/API endpoint before using a third-party source.
15. If a source is unavailable, create a clear `DATA_GAPS.md` entry rather than silently substituting unreliable data.

---

# 2. Study area

Primary study area:

**City of North Vancouver, BC, Canada**

Use the official municipal boundary wherever possible.

Do NOT confuse:
- City of North Vancouver
- District of North Vancouver
- North Vancouver electoral district
- Metro Vancouver
- North Shore

The final analysis must be clipped to the **City of North Vancouver municipal boundary**, unless a layer is explicitly regional (e.g., TransLink).

Coordinate reference:
- Use a projected CRS appropriate for local distance/area calculations.
- Prefer **EPSG:3005 (NAD83 / BC Albers)** for provincial/regional analysis.
- Use WGS84/EPSG:4326 for web mapping exports.
- Do not calculate area/distance in latitude/longitude degrees.

---

# 3. Official starting sources

Use these sources first.

## City of North Vancouver

Community Facts & Statistics:
https://www.cnv.org/City-Hall/About/community-statistics

Previous Elections:
https://www.cnv.org/City-Hall/General-Local-Election/Past-Election-Results

2022 Official Election Results:
https://www.cnv.org/City-Hall/News-Room/Whats-New/2022/10/19/Official-Results-of-2022-City-Election-Announced

CNV General Zoning Map:
https://gisext2.cnv.org/PDFMaps/CNV_GenZoning48x36.pdf

CNV Regional Context Map:
https://gisext2.cnv.org/PDFMaps/Schedule%20E%20RegionalContextMap_11x17.pdf

CNV Land Use Map:
https://gisext2.cnv.org/PDFMaps/Schedule%20A%20Land%20Use_11x17.pdf

CNV City Map:
https://gisext2.cnv.org/PDFMaps/CNV_CityMap.pdf

CNV Neighbourhoods:
https://gisext2.cnv.org/PDFMaps/CNV_Neighbourhoods.pdf

CNV Traffic Signals:
https://www.cnv.org/Streets-Transportation/Traffic/Traffic-Signals

CNV Pay Parking:
https://www.cnv.org/Streets-Transportation/Parking/Pay-Parking

## North Vancouver GEOweb

https://geoweb.dnv.org/data/

Use it for regional GIS datasets where the dataset explicitly covers the City of North Vancouver.

Potentially useful layers include:
- Streets
- Intersections
- Building outlines
- Parking lots
- Parking restrictions
- Other transportation/foundation GIS layers

Do not assume a District of North Vancouver layer is City-only. Inspect metadata and clip it to CNV.

## Statistics Canada

### 2021 Census geography / boundaries

2021 Census Dissemination Areas:
https://www150.statcan.gc.ca/n1/en/catalogue/92-169-X2021001

2021 Census Dissemination Blocks:
https://www150.statcan.gc.ca/n1/en/catalogue/92-163-X2021001

2021 Census geography/boundary resources:
https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/index.cfm

### 2021 Census population / age / housing data — PRIMARY SOURCE

Census Profile Downloads, 2021:
https://www150.statcan.gc.ca/n1/en/catalogue/98-401-X

Use the entry:
**Census Profile, 2021: Canada, Provinces, Territories, Census Divisions, Census Subdivisions and Dissemination Areas**
(December 15, 2022).

This is the primary source for the project's population, age, dwelling and housing statistics. Statistics Canada provides machine-readable CSV/TAB downloads and the profile is available at the Dissemination Area level.

**Do not use screenshots, PDFs, or manually copied Census Viewer results as the primary data source.**

### Recommended download strategy

The full Canada-level DA Census Profile CSV is very large. Prefer the **British Columbia-only comprehensive Census Profile CSV** from the official download page when available.

Official download page:
https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm

The official download page lists a British Columbia-only comprehensive file for the hierarchy containing Census Divisions, Census Subdivisions and Dissemination Areas.

If the BC-only file is unavailable, use the Canada/provinces/territories/CDs/CSDs/DAs comprehensive CSV and filter it to British Columbia.

### Population and dwelling counts

Statistics Canada table 98-10-0015-01:
https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810001501

Use this as a supplemental source for population, dwelling counts, land area and population density.

### Census Profile Web Data Service

For small, targeted Census requests, investigate the official Statistics Canada Census Profile Web Data Service. Verify the current 2021 endpoint/documentation from Statistics Canada before coding against it.

### Required Census variables

Population:
- Population, 2021
- Population density
- Age groups
- Population aged 18+ or a clearly documented 18+ proxy constructed from published age bands
- Population aged 65+
- Population aged 75+
- Population aged 85+

Housing:
- Total private dwellings
- Occupied private dwellings
- Type of dwelling
- Single-detached house
- Semi-detached house
- Row house / townhouse
- Apartment in a building that has fewer than five storeys
- Apartment in a building that has five or more storeys
- Other attached dwelling types where available

### Census geography join

Use `DAUID` as the primary geographic join key.

Join Census Profile records to the 2021 Dissemination Area boundary layer using `DAUID`.

Do not join by area name alone.

### CNV filtering

Identify the official **City of North Vancouver Census Subdivision (CSD) identifier** from Statistics Canada geography.

Then:
1. Load the relevant BC Census Profile records.
2. Identify the DAs belonging to the CNV CSD.
3. Join those DA records to the 2021 DA boundary polygons.
4. Validate against the official CNV municipal boundary.
5. Save the CNV-only Census dataset to:
   `data/processed/cnv_census_2021.gpkg`

### Required derived fields

Calculate:

`population_density = population / area_km2`

`adult_population_18plus_proxy`

`adult_population_density`

`senior_population_65plus`

`senior_density`

`housing_density = occupied_private_dwellings / area_km2`

`multiunit_share`

IMPORTANT:
Do NOT label Census population aged 18+ as “eligible voters”.
Use:
`adult_population_18plus_proxy`

This is a demographic proxy for potential electorate size, not an official elector count.

## BC traffic

BC Traffic Data Program:
https://www.th.gov.bc.ca/trafficdata/

## TransLink

GTFS:
https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources/gtfs/gtfs-data

## Additional authoritative sources to investigate

- BC Data Catalogue: https://catalogue.data.gov.bc.ca/
- Elections BC: https://elections.bc.ca/
- CivicInfo BC: https://www.civicinfo.bc.ca/
- Metro Vancouver Open Data: https://open-data-portal-metrovancouver.hub.arcgis.com/
- ICBC statistics/data: https://www.icbc.com/
- OpenStreetMap/Overpass as a secondary source only where authoritative municipal data is unavailable.

---

# 4. Required project structure

Create:

```text
cnv_gis_analysis/
├── CLAUDE.md
├── README.md
├── DATA_SOURCES.md
├── DATA_DICTIONARY.md
├── DATA_GAPS.md
├── METHODOLOGY.md
├── LICENSES_AND_ATTRIBUTION.md
├── requirements.txt
├── environment.yml
├── .gitignore
│
├── config/
│   ├── study_area.yaml
│   ├── sources.yaml
│   └── scoring.yaml
│
├── data/
│   ├── raw/
│   │   ├── cnv/
│   │   ├── dnv_geoweb/
│   │   ├── statcan/
│   │   ├── elections/
│   │   ├── traffic/
│   │   ├── transit/
│   │   ├── parking/
│   │   └── safety/
│   ├── interim/
│   └── processed/
│
├── scripts/
│   ├── 01_download.py
│   ├── 02_validate_sources.py
│   ├── 03_prepare_boundary.py
│   ├── 04_prepare_census.py
│   ├── 05_prepare_housing.py
│   ├── 06_prepare_buildings.py
│   ├── 07_prepare_elections.py
│   ├── 08_prepare_roads.py
│   ├── 09_prepare_traffic.py
│   ├── 10_prepare_transit.py
│   ├── 11_prepare_parking.py
│   ├── 12_prepare_safety.py
│   ├── 13_spatial_joins.py
│   ├── 14_analysis_population.py
│   ├── 15_analysis_housing.py
│   ├── 16_analysis_polling.py
│   ├── 17_analysis_intersections.py
│   ├── 18_create_maps.py
│   ├── 19_create_interactive_map.py
│   └── 20_generate_report.py
│
├── outputs/
│   ├── maps/
│   ├── interactive/
│   ├── tables/
│   ├── figures/
│   └── report/
│
├── notebooks/
└── tests/
```

---

# 5. Data acquisition requirements

Build `scripts/01_download.py`.

It should:

1. Read source definitions from `config/sources.yaml`.
2. Download official datasets.
3. Save original files under `data/raw/`.
4. Calculate SHA256 hashes.
5. Store download metadata.
6. Never overwrite an existing raw file unless `--force` is specified.
7. Retry failed downloads.
8. Log failures.
9. Validate that downloaded files are not HTML error pages masquerading as ZIP/CSV/GIS files.

Create a source inventory table with:

- source_id
- organization
- dataset
- URL
- download_url
- format
- geographic_level
- coverage
- date/version
- license
- download_date
- local_path
- status
- notes

---

# 6. CNV boundary

Find the best authoritative municipal boundary.

If CNV does not publish a machine-readable boundary:
- search BC/Metro Vancouver authoritative GIS sources;
- document the source used;
- clip all analysis layers to the boundary.

Output:

`data/processed/cnv_boundary.gpkg`

Layer:
`cnv_boundary`

---

# 7. Census analysis

Acquire 2021 Census geography and variables using the PRIMARY SOURCE specified above.

Preferred workflow:
1. Download the official British Columbia comprehensive Census Profile CSV when available.
2. Otherwise download the official Canada/provinces/territories/CDs/CSDs/DAs comprehensive CSV.
3. Identify the City of North Vancouver CSD.
4. Filter Census Profile records to the CNV CSD and its Dissemination Areas.
5. Join to 2021 DA polygons using DAUID.
6. Save the CNV-only result as a GeoPackage.
7. Record the exact Statistics Canada source, filename, release/version and download date in DATA_SOURCES.md.

Acquire 2021 Census geography and variables.

At minimum collect:

## Population

- total population
- population density
- population by age group
- population 18+
- population 65+
- population 75+
- population 85+

## Housing

- total private dwellings
- occupied private dwellings
- dwelling structure type
- apartments in high-rise buildings
- apartments in low-rise buildings
- row houses/townhouses
- semi-detached
- single-detached
- other attached dwellings

## Useful additional variables

- average household size
- one-person households
- seniors living alone if available at a sufficiently safe aggregate level
- population change where comparable data exists

Use DA and/or DB geography.

Calculate:

```text
population_density = population / area_km2

adult_population_density = population_18_plus / area_km2

senior_density = population_65_plus / area_km2

housing_density = occupied_dwellings / area_km2

multiunit_share =
(apartments + rowhouses + other multiunit) /
occupied_private_dwellings
```

Do not call `population_18_plus` `eligible_voters`.

Use the field name:

`adult_population_18plus_proxy`

---

# 8. Housing/building analysis

Find authoritative CNV or North Shore GIS building data.

Required attributes where available:

- geometry
- address
- building type
- number of units
- number of floors
- year built
- residential/non-residential
- institutional
- seniors housing/residence
- condominium indicator if available
- townhouse/rowhouse indicator

If condo ownership information is unavailable, do NOT infer that every apartment building is a condo.

Create classifications:

```text
SINGLE_FAMILY
TOWNHOUSE_ROW
LOW_RISE_APARTMENT
HIGH_RISE_APARTMENT
MIXED_USE
SENIORS_RESIDENCE
INSTITUTIONAL
OTHER
UNKNOWN
```

For seniors residences:
- search official municipal planning/open-data layers;
- search BC government facility/housing datasets;
- search publicly available municipal facility lists;
- use OpenStreetMap only as a supplementary source;
- preserve the source of every feature.

Create:
`data/processed/residential_buildings.gpkg`

---

# 9. Neighbourhood analysis

Obtain CNV official neighbourhood boundaries.

If only PDF exists:
- search for the underlying GIS service;
- otherwise digitize carefully or georeference the PDF;
- document that it was derived from a PDF.

Output:
`cnv_neighbourhoods`

Calculate for every neighbourhood:

- area
- population
- population density
- adult population 18+ proxy
- adult density
- seniors 65+
- senior density
- dwellings
- housing density
- apartment share
- townhouse share
- single-family share
- building count
- average/median building height where available

---

# 10. Election/polling data

Search official CNV election pages and CivicInfo BC.

Collect:

- election year
- registered voters
- voter turnout
- ballots cast
- voting locations
- voting place addresses
- advance voting locations
- special voting locations where public
- poll/polling division identifiers where public
- candidate results

Do not collect:
- individual voter names
- individual voter addresses
- political preference by person
- personal contact information

### Polling divisions

Search for actual polling division polygons or official maps.

Possible sources:
- CNV election office
- CivicInfo BC
- Elections BC
- municipal election reports
- official PDF election maps

If boundaries are unavailable:
- create a `polling_boundary_status` entry in `DATA_GAPS.md`;
- do not fabricate them.

Geocode voting-place addresses using an appropriate service or official GIS layer.

---

# 11. Important voter-data methodology

The analysis must distinguish:

### Actual electoral data
Only use aggregated registered-voter/elector numbers if an official source publishes them.

### Census proxy
Use:

`adult_population_18plus_proxy`

for spatial population analysis.

Do not claim:

"this area contains X eligible voters"

unless the source actually provides eligible-voter counts.

Instead say:

"this area contains an estimated X residents aged 18+, used as a demographic proxy for potential electorate."

Include a methodology note in every voter-related report/map.

---

# 12. Roads and intersections

Acquire:

- street centerlines
- intersection points
- road classification
- road names
- traffic-load attributes
- signalized intersection locations if available
- pedestrian crossings if available
- bike routes if available

Clip to CNV.

Create an intersection table:

```text
intersection_id
street_a
street_b
geometry
road_class_a
road_class_b
signalized
traffic_volume_a
traffic_volume_b
transit_stop_count_250m
parking_count_250m
collision_count
pedestrian_proxy
visibility_flags
```

---

# 13. Traffic volumes

Use BC Traffic Data Program.

Find all count stations within or immediately adjacent to CNV.

Collect where available:

- count station ID
- latitude/longitude
- road
- direction
- date
- AADT
- hourly counts
- daily counts
- vehicle class if available

Calculate:

- average daily traffic
- morning peak
- afternoon peak
- evening peak
- weekday/weekend differences

Do not assume a count station represents every nearby intersection.

Use distance-based association and document the distance threshold.

---

# 14. Transit

Download TransLink GTFS.

Use:

- stops.txt
- routes.txt
- trips.txt
- stop_times.txt
- shapes.txt
- calendar.txt/calendar_dates.txt

Create:

- transit stop points
- route lines
- service frequency estimates
- stops per intersection buffer
- service during morning/evening periods

Calculate transit accessibility within:

- 100 m
- 250 m
- 400 m

of each candidate intersection.

---

# 15. Pedestrian data

Search official sources first.

Look for:

- pedestrian counts
- sidewalk counts
- intersection counts
- pedestrian/cyclist counters
- transportation studies
- pedestrian plans
- walkability studies
- safe-routes studies

If direct pedestrian counts are unavailable, create a clearly labelled **pedestrian activity proxy**, NOT "pedestrian traffic."

Possible proxy components:

- transit stops/service
- commercial land use
- population density
- employment density if available
- intersection density
- pedestrian infrastructure
- proximity to major civic destinations

Keep actual counts and proxies in separate fields.

---

# 16. Parking

Search CNV CityMap and GIS services.

Find:

- public parking lots
- pay parking
- street parking
- parking restrictions
- time limits
- accessible parking
- loading zones
- no-parking zones
- parking capacity if public

If CityMap is backed by ArcGIS REST services, discover the service endpoint and download the underlying feature layer instead of scraping the rendered map.

Create:

`parking_points`
`parking_lots`
`parking_restrictions`

Calculate parking availability/proximity around intersections.

Do NOT claim real-time availability unless a live availability feed exists.

---

# 17. Traffic signal timing

Search CNV engineering documents and public GIS.

Try to find:

- signal locations
- signal plans
- cycle length
- phase timing
- pedestrian walk interval
- clearance interval
- coordination plans
- time-of-day signal plans

If signal timing is not publicly downloadable:

1. record it as unavailable;
2. search official documents;
3. do not estimate exact cycle times;
4. do not state that an intersection has the "longest light" without actual timing data.

If useful, create:

`signal_timing_status = PUBLIC / REQUEST_REQUIRED / NOT_FOUND`

You may create a separate list of intersections where field observation is recommended.

---

# 18. Safety / visibility

Search official:

- ICBC collision data/statistics
- CNV transportation studies
- CNV traffic safety reports
- BC crash datasets where available

Create collision indicators such as:

- total collisions
- pedestrian-involved collisions
- cyclist-involved collisions
- serious collisions
- collision density

For "poor visibility", do NOT invent a GIS variable.

Instead identify objective proxies:

- sightline obstructions
- sharp curves
- intersection geometry
- vegetation
- grade/slope
- parked vehicles
- building setbacks
- road curvature
- collision history

If these cannot be obtained from GIS, create a **field-audit checklist**.

---

# 19. Maps to produce

Create separate maps.

## Map 1 — Population density
DA/DB polygons shaded by population density.

## Map 2 — Adult population proxy
DA/DB polygons shaded by 18+ population density.

## Map 3 — Age distribution
Separate layers/maps for:
- 18–34
- 35–49
- 50–64
- 65+
- 75+

## Map 4 — Housing structure
Show:
- apartments
- townhouses
- detached
- mixed/multi-unit

## Map 5 — Building density
Buildings/unit counts where available.

## Map 6 — Seniors residences
Point/polygon layer with source attribution.

## Map 7 — Polling/voting locations
Voting-place points and official boundaries if available.

## Map 8 — Roads
Road hierarchy and traffic-load classification.

## Map 9 — Traffic
Traffic-count locations and volumes.

## Map 10 — Transit
Routes and stops.

## Map 11 — Parking
Parking locations/restrictions.

## Map 12 — Safety
Collision/safety indicators.

## Map 13 — Combined civic geography
Combine:
- population
- adult proxy
- housing
- age
- polling locations
- transit
- roads
- parking

Do not create a political persuasion score.

---

# 20. Intersection/public-space scoring

Because the intended use involves public visibility, create a **neutral public-space suitability score**, not a voter-targeting score.

Suggested dimensions:

- vehicle exposure
- transit activity
- pedestrian activity proxy
- intersection prominence
- parking access
- safety
- visibility constraints
- public-space feasibility

Keep each component separate.

Example normalized fields:

```text
traffic_score
transit_score
pedestrian_proxy_score
parking_access_score
intersection_prominence_score
safety_score
visibility_score
```

Do not include:
- political affiliation
- voting history
- candidate support
- demographic political assumptions

Do not infer that age, housing type, income, ethnicity, or other demographics predict political preference.

---

# 21. Combined map

Build an interactive map using one of:

1. Leaflet
2. MapLibre GL JS
3. Folium
4. Kepler.gl
5. ArcGIS-compatible web layers

Prefer **MapLibre/Leaflet** for a portable static web project.

Requirements:

- layer toggle
- legend
- search
- popup
- source attribution
- opacity control
- filtering
- scale bar
- North arrow if appropriate
- metadata panel
- downloadable GeoJSON/CSV links where licensing permits

Do not load huge raw layers directly into the browser.

Simplify/generalize geometry for web display.

---

# 22. Tables to produce

Create CSV files:

```text
neighbourhood_rankings.csv
census_area_rankings.csv
housing_rankings.csv
polling_location_summary.csv
traffic_intersection_summary.csv
transit_intersection_summary.csv
parking_intersection_summary.csv
safety_intersection_summary.csv
public_space_summary.csv
data_inventory.csv
data_gaps.csv
```

Every ranking must contain:
- rank
- feature ID
- name/address if appropriate
- metric
- value
- source
- methodology note

---

# 23. Statistical analysis

Perform:

- descriptive statistics
- quantiles
- percentiles
- spatial density
- nearest-neighbour distances where useful
- spatial joins
- buffer analysis
- correlation analysis where appropriate

Do not imply causation from spatial correlation.

For every calculated metric, record its formula.

---

# 24. Quality assurance

Build automated tests.

Check:

- CRS
- invalid geometries
- duplicate IDs
- missing values
- impossible population values
- polygons outside CNV
- duplicate buildings
- duplicate intersections
- missing source metadata
- incorrect date ranges

Run:

```bash
python -m pytest
```

before generating the final report.

---

# 25. Reproducibility

The entire pipeline should be runnable with:

```bash
python scripts/01_download.py
python scripts/02_validate_sources.py
python scripts/03_prepare_boundary.py
python scripts/04_prepare_census.py
python scripts/05_prepare_housing.py
python scripts/06_prepare_buildings.py
python scripts/07_prepare_elections.py
python scripts/08_prepare_roads.py
python scripts/09_prepare_traffic.py
python scripts/10_prepare_transit.py
python scripts/11_prepare_parking.py
python scripts/12_prepare_safety.py
python scripts/13_spatial_joins.py
python scripts/14_analysis_population.py
python scripts/15_analysis_housing.py
python scripts/16_analysis_polling.py
python scripts/17_analysis_intersections.py
python scripts/18_create_maps.py
python scripts/19_create_interactive_map.py
python scripts/20_generate_report.py
```

Also create:

```bash
python run_pipeline.py
```

which runs the full workflow.

Support:

```bash
python run_pipeline.py --download
python run_pipeline.py --process
python run_pipeline.py --maps
python run_pipeline.py --report
python run_pipeline.py --all
```

---

# 26. Technology stack

Prefer:

- Python 3.11+
- pandas
- geopandas
- shapely
- pyproj
- fiona/pyogrio
- requests
- beautifulsoup4
- openpyxl
- numpy
- scipy
- matplotlib
- folium or Leaflet/MapLibre
- osmnx only as a supplementary source
- networkx if network analysis is needed
- rasterio if raster data becomes necessary

Use GeoPackage as the main processed GIS format.

Use GeoParquet where performance is important.

---

# 27. Source discovery

If a provided page is a map portal rather than a downloadable file:

1. inspect HTML;
2. inspect embedded ArcGIS/GeoServer URLs;
3. search for REST FeatureServer/MapServer;
4. inspect network/API metadata if technically accessible;
5. identify the underlying layer;
6. download using the official API;
7. record the endpoint in `DATA_SOURCES.md`.

Do not scrape data behind authentication or access controls.

Do not bypass CAPTCHAs, rate limits, authentication, robots restrictions, or technical controls.

---

# 28. PDFs

For supplied CNV PDFs:

- preserve original PDFs;
- extract text/metadata where useful;
- georeference only if necessary;
- prefer underlying GIS layers;
- never treat a visually interpreted PDF as equivalent to an authoritative vector dataset without documenting the transformation.

---

# 29. Missing-data protocol

Create `DATA_GAPS.md`.

For every unavailable dataset:

```text
Dataset:
Desired use:
Organizations searched:
URLs searched:
What was found:
Why it is unavailable:
Best available proxy:
Limitations:
Recommended next action:
```

Examples likely to require a gap entry:

- exact polling-division polygons
- exact eligible-voter counts by small geography
- individual voter locations
- real-time parking occupancy
- exact pedestrian counts at every intersection
- traffic-signal cycle timing

---

# 30. Final report

Generate:

`outputs/report/CNV_GIS_Data_Analysis_Report.html`

and, if dependencies permit:

`outputs/report/CNV_GIS_Data_Analysis_Report.pdf`

Report sections:

1. Executive summary
2. Study area
3. Data sources
4. Data acquisition
5. Data cleaning
6. Census/population methodology
7. Housing methodology
8. Electoral/polling methodology
9. Transportation methodology
10. Traffic methodology
11. Transit methodology
12. Parking methodology
13. Safety/visibility methodology
14. GIS methods
15. Results
16. Ranked tables
17. Maps
18. Data limitations
19. Privacy/ethical considerations
20. Reproducibility instructions
21. Full source list

---

# 31. Final README

README must explain:

- what the project does
- how to install dependencies
- how to run the pipeline
- where raw data goes
- where processed data goes
- where maps are produced
- where reports are produced
- which datasets require manual download
- which datasets are unavailable
- how to update the data

---

# 32. First execution instructions for Claude Code

When starting this project:

### Phase 1
Do not immediately write all processing scripts.

First:
1. inspect every official source;
2. discover actual downloadable endpoints;
3. build `DATA_SOURCES.md`;
4. build `config/sources.yaml`;
5. test each source;
6. identify missing datasets.

Then implement downloaders.

### Phase 2
Download and validate raw data.

### Phase 3
Process geography and Census.

### Phase 4
Process housing/buildings/elections.

### Phase 5
Process roads/traffic/transit/parking/safety.

### Phase 6
Perform spatial joins and analysis.

### Phase 7
Generate static and interactive maps.

### Phase 8
Generate tables/report.

### Phase 9
Run QA and produce a final completion report.

---

# 33. Completion criteria

The project is complete only when:

- [ ] CNV boundary exists
- [ ] Census geography exists
- [ ] population data exists
- [ ] age data exists
- [ ] housing data exists
- [ ] neighbourhood layer exists
- [ ] building layer exists or documented as unavailable
- [ ] election results are documented
- [ ] voting locations are mapped where available
- [ ] polling boundaries are mapped or documented unavailable
- [ ] road layer exists
- [ ] intersection layer exists
- [ ] traffic data exists or documented unavailable
- [ ] transit GTFS processed
- [ ] parking layer exists or documented unavailable
- [ ] safety data exists or documented unavailable
- [ ] every processed layer has source metadata
- [ ] separate maps generated
- [ ] combined interactive map generated
- [ ] CSV rankings generated
- [ ] data gaps documented
- [ ] methodology documented
- [ ] privacy limitations documented
- [ ] automated QA passes
- [ ] final report generated

---

# 34. Important interpretation rule

The project is a **geospatial civic-data research project**.

Do not turn demographic variables into assumptions about political beliefs.

For example, never produce statements such as:

"High-rise residents are likely to vote for X."

Instead use factual descriptions such as:

"Area X has a high concentration of multi-unit dwellings and a high adult-population density."

Likewise, never identify or infer individual voters.

The output should remain aggregate, reproducible, transparent, and suitable for legitimate civic/geographic analysis.

---

# 35. Start now

Begin by auditing the official sources.

Do not ask me to manually provide datasets that are publicly downloadable.

If a source is accessible, download it automatically.

If a source is inaccessible, document the exact reason and continue.

At the end of the first run, print a concise status table:

| Dataset | Status | Source | Local file | Notes |
|---|---|---|---|---|

Then continue through the pipeline until all feasible outputs are generated.
