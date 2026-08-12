# DATA_GAPS.md — City of North Vancouver GIS Analysis

Every dataset that was sought but could not be obtained, or could only be obtained in a
degraded form. Each entry records what was searched, what was found, why it is
insufficient, and the best defensible proxy actually used in the pipeline.

Last updated: 2026-08-12.

---

## 1. Traffic volumes on CNV municipal streets

**Dataset:** Measured vehicle volumes (AADT or equivalent) for Lonsdale Ave, Marine Dr,
East/West 3rd St, Keith Rd, Esplanade and the rest of the CNV municipal network.

**Desired use:** A `traffic_score` grounded in measured exposure rather than road class.

**Organizations searched:** BC Ministry of Transportation and Infrastructure (Traffic Data
Program), City of North Vancouver, District of North Vancouver GEOweb, TransLink,
Metro Vancouver, BC Data Catalogue.

**URLs searched:**
- `https://www.th.gov.bc.ca/trafficdata/` → `https://twm.th.gov.bc.ca/?c=tdp`
- `https://maps.th.gov.bc.ca/geoV05/ows` (WFS; discovered via the app's `api/url/` resolver)
- `https://prdoas6.pub-apps.th.gov.bc.ca/` (TRADAS report files)
- `https://catalogue.data.gov.bc.ca/api/3/action/package_search`
- `https://gisext2.cnv.org/arcgis/rest/services` (all five folders enumerated)
- `https://geoweb.dnv.org/data/`
- Metro Vancouver ArcGIS org `56eqCzQ5SZhBaDST` (58 public services enumerated)

**What was found:**
- The BC Traffic Data Program covers the **provincial highway network only**. Highway 1 is
  the only provincial facility through CNV.
- 10 count stations lie inside CNV, all on the Highway 1 interchanges (Lonsdale I/C,
  Fern St I/C, Westview Dr I/C). All are classified **Short Core**, and MoTI publishes
  AADT (`AV02` reports) only for **Permanent Core** counters.
- The most recent short counts at CNV stations are **2016** (some ramps 2013).
- The nearest permanent counters are Second Narrows / Ironworkers Memorial Bridge
  (`P-15-2EW`, 1.0 km away) and Lions Gate Bridge (`P-15-1NS`, 2.8 km away).
- CNV's own ArcGIS server publishes a directional volume layer, but it covers only
  **38 street segments** against 941 in the municipality, with no stated survey period or
  units.
- No turning-movement counts are published by any agency.

**Why it is unavailable:** The province does not count municipal streets, and CNV holds
its counts internally — its own Level 1 Transportation Study guidelines confirm that count
data "may be acquired from the City" on request rather than published.

**Best available proxy used:** `traffic_score` is built 70% from road classification
(`ROADCLASS` on the CNV centrelines) and 30% from the sparse published directional volumes
where a segment falls within 150 m of an intersection. Only **40 of 503** intersections
have any measured volume, and `traffic_volume_available` flags which.

**Limitations:** `traffic_score` must not be read as a measured traffic ranking. It is
primarily a road-hierarchy ranking.

**Recommended next action:** Request turning-movement and hose counts from
`transportation@cnv.org`. Retrieved MoTI station data is cached under
`data/raw/traffic/` for the Highway 1 corridor.

---

## 2. Traffic signal cycle and phase timing

**Dataset:** Cycle length, phase splits, offsets, pedestrian walk interval, clearance
interval, coordination plans.

**Desired use:** Estimating dwell/wait time at candidate public-space locations.

**Organizations searched:** City of North Vancouver engineering and transportation pages,
CNV ArcGIS services, CNV council reports, CNV transportation planning documents.

**URLs searched:**
- `https://www.cnv.org/Streets-Transportation/Traffic/Traffic-Signals`
- `https://www.cnv.org/streets-transportation/traffic`
- `TransportMAP/MapServer/153` (Traffic Signals layer — full field list inspected)
- CNV Long-Term Transportation Plan 2008; Mobility Strategy 2022; Safe Mobility Strategy 2020

**What was found:** The traffic signals GIS layer is an **asset inventory only**
(`SIGNAL_TYPE`, `POLE_TYPE`, head counts, `INSTALL_DATE`, `OWNER`) with no timing
attribute. The CNV traffic signals web page describes coordination only qualitatively.
Critically, CNV's *Guidelines for the Submission of a Transportation Study — Level 1*
(p.6) states that "details on signal phasing and cycle lengths **will be provided by the
City**" — so the data exists and is released on request, but is never published.

**Why it is unavailable:** Held internally; released on request for transportation studies.

**Best available proxy used:** **None. No cycle time is estimated anywhere.** The pipeline
records `signal_timing_status = REQUEST_REQUIRED` on every signalised location, and
distinguishes full signals (79 locations) from pedestrian-only signals and special
crosswalks (54 locations) using the `SIGNAL_TYPE` attribute.

**Limitations:** No claim about wait time or "longest light" is made or supportable.

**Recommended next action:** Request timing from `eng@cnv.org` /
`transportation@cnv.org`, or measure in the field using
`outputs/tables/field_audit_checklist.csv`.

---

## 3. Pedestrian counts

**Dataset:** Observed pedestrian volumes at CNV intersections.

**Desired use:** A measured `pedestrian_score` rather than a proxy.

**Organizations searched:** CNV transportation planning, Walk CNV programme, CNV council
reports, TransLink, Metro Vancouver.

**What was found:**
- **Walk CNV (Nov 2017)** — the study the GIS layers reference — is a *perception* survey
  (365 respondents, Jan–Mar 2017) plus walkabouts. It contains **no pedestrian volume
  counts**.
- The **Moodyville Area Transportation Study (Jan 2016)**, Fig. 43, contains the only
  genuine published pedestrian count found: volumes at East 3rd Street intersections from
  Lonsdale to Queensbury, reflecting **2015 field data**. It is a raster figure inside a
  PDF, not machine-readable, and covers one corridor only.
- The **North Shore Transportation Survey (2019/2021/2023)** gives modelled city-wide daily
  walk trips (37,250 in 2023) but **no geography below the municipality**.
- The CNV `Sidewalk Segments` layer carries a `PEDESTRIAN_TRAFFIC` attribute, but it is a
  qualitative asset-management classification, not a count.

**Why it is unavailable:** CNV runs no permanent pedestrian counter programme.

**Best available proxy used:** `pedestrian_proxy_score`, explicitly named a proxy and built
from resident population within 400 m (30%), commercial land-use area within 250 m (25%),
transit departures within 250 m (20%), walkway length within 250 m (15%) and sidewalk ramps
within 100 m (10%).

**Limitations:** This is **not** a pedestrian count and is never presented as one. Observed
counts and proxy values are kept in separate fields throughout.

**Recommended next action:** Manual counts at the top-ranked candidates, using the field
audit checklist.

---

## 4. Polling / voting division boundaries

**Dataset:** Polling-division or voting-division boundary polygons for CNV.

**Desired use:** Mapping results to sub-municipal geography.

**Organizations searched:** City of North Vancouver, CivicInfo BC, Elections BC, CNV
election bylaws and Chief Election Officer materials.

**What was found:** **Nothing — and they almost certainly do not exist.** CNV conducts
"any voting place" elections: an elector may vote at any voting location in the city, so
there are no polling-division catchments to map. CNV publishes **results by voting place**
(which candidate received how many votes at each of the nine locations), but a voting place
is a *service point*, not a *catchment*.

**Why it is unavailable:** Structurally absent from CNV's electoral model.

**Best available proxy used:** Voting-place **point** locations with coordinates, plus
resident and 18+ proxy population within 400/800/1600 m of each place
(`outputs/tables/polling_location_context.csv`). These buffers are catchment *estimates for
context only* and are not electoral divisions.

**Limitations:** Votes cast at a voting place **cannot** be attributed to residents near
that place, because electors may vote anywhere in the city.

**Recommended next action:** None. Documented as structurally unavailable.

---

## 5. Ballots cast per voting place, 2022

**Dataset:** Total ballots issued at each 2022 voting place.

**What was found:** The 2011, 2014 and 2018 results sheets include a "TOTAL VOTERS" row per
voting place. The **2022 sheet does not**. CNV published registered electors (41,325) and
turnout (22.64%) but not total ballots cast.

**Best available proxy used:** Mayoral votes per place (one vote per elector for a
single-winner office) as a **lower bound**, recorded as `mayoral_votes_2022` with an
explicit note. Total mayoral votes = 9,198.

**Limitations:** 41,325 × 22.64% ≈ 9,356 is an arithmetic estimate, not an official figure,
and is not used as one. A third-party figure of "9,351" could not be verified (source URL
now 404) and is not used.

---

## 6. Eligible-elector counts by small geography

**Dataset:** Registered or eligible electors by dissemination area or neighbourhood.

**What was found:** CNV publishes registered electors **city-wide only** (41,325 in 2022).
No sub-municipal elector counts are published, and producing them would raise privacy
concerns.

**Best available proxy used:** `adult_population_18plus_proxy` (49,248 city-wide) from the
2021 Census, and the closer `canadian_citizens_18plus` (41,130 city-wide), which sits
within **0.5%** of the official registered-elector total — a useful consistency check.

**Limitations:** Neither is an elector count. The 18+ proxy apportions the Census 15–19
band (ages 18–19 taken as 2/5 of it) and ignores citizenship and residency requirements.
The citizenship variable is 25% sample data covering private households only. **The term
"eligible voters" is never used for either field**, and a test enforces this.

---

## 7. Real-time parking availability

**Dataset:** Live parking occupancy.

**What was found:** No live feed exists. CNV publishes an **observed survey**: on-street
supply and occupancy across eight time periods for 1,169 segments, collected by
**Bunt & Associates in December 2022 and January/February 2023** for the Curb Access and
Parking Plan.

**Best available proxy used:** The survey itself, labelled `survey_period = 2022-12 to
2023-02` with `data_nature` stating it is not a real-time feed.

**Limitations:** Reflects conditions in the survey window only. Never presented as live
availability. Occupancy above 100% is retained rather than clipped, because `Supply` is an
integer estimate of a continuous capacity.

---

## 8. Building height, unit counts and year built

**Dataset:** Height, dwelling-unit count and construction year for CNV buildings.

**What was found:** The CNV building footprint layer (11,833 polygons inside CNV) carries
only `BUILDING_STATUS` and `BUILDING_NAME`. Only the separate **High Rise Buildings
(>18 m)** layer carries `BUILDING_Z`, `YearBuilt`, `NosUnits` and `Occupancy` — 107
records.

**Coverage achieved:** height known for **109 of 11,833** footprints (0.9%), unit count for
88 (0.7%), year built for 109 (0.9%).

**Best available proxy used:** Dwelling structure type from the 2021 Census at DA level,
which is complete and authoritative for housing mix. Building classification is
evidence-based, and 98.6% of footprints are honestly labelled `UNKNOWN`.

**Limitations:** `UNKNOWN` means the City publishes nothing about that footprint — **not**
that the building is non-residential. No building-level unit-count surface is possible.

---

## 9. Condominium / strata tenure

**Dataset:** Which buildings are strata-titled.

**What was found:** The `Occupancy` attribute on the high-rise layer explicitly contains
`STRATA` for some buildings (e.g. `STRATA APT - HI-RISE`).

**Approach taken:** `condominium_tenure` is set **only** where the City's own attribute
says `STRATA`. It is never inferred from building form, height or apartment status, per the
project rule. Everything else records "tenure unknown, not assumed".

---

## 10. Licensed seniors care facilities inside CNV

**Dataset:** Long-term care and assisted living facilities in the City.

**What was found:** The BC provincial registries (Residential Care Facilities, Assisted
Living Residences — both downloaded to `data/raw/bc_health/`) show **zero** registered
assisted-living residences and **zero** Residential Care Regulation–licensed long-term care
homes inside the City; all North Shore licensed capacity with a "North Vancouver, BC"
address is in the **District**.

**Critical caveat:** **Evergreen House (231 East 15th Street, 284 publicly funded long-term
care beds) is inside the City** but is licensed under the *Hospital Act* rather than the
*Residential Care Regulation*, so it does **not** appear in either provincial registry.
Building a seniors-care layer from those registries alone would under-count the City's
frail-senior capacity by more beds than all its other residential care combined.

**What the pipeline does contain:** 11 seniors-eligible housing sites identified from the
City's own Affordable Housing `Eligibility` (55+) and `Occupancy` (`INDEPENDENT LIVING`)
attributes — subsidised independent seniors housing, which is a different thing from
licensed care.

**Unresolved:** *Sunrise at Lonsdale Square* (2141 Eastern Ave) is confirmed in-City by
parcel lookup but is absent from both provincial registries despite marketing itself as
licensed care. *Summerhill PARC* (135 W 15th) is in-City but publishes no suite count.
Neither has an estimated bed count assigned.

**Recommended next action:** Confirm Evergreen House and Sunrise directly with Vancouver
Coastal Health before publishing any seniors-care capacity figure.

---

## 11. ICBC collision data — geography and municipality

**Dataset:** Georeferenced collision records for CNV.

**What was found:** ICBC publishes crash counts through Tableau Public dashboards. The
CSV export (the dashboard's own sanctioned download) provides **location name strings with
no coordinates**, and ICBC's `NORTH VANCOUVER` municipality value covers **both the City
and the District**.

**Approach taken:** Conservative name matching — a record is attributed to a CNV
intersection only when at least two of its named streets are CNV streets **and** that pair
corresponds to an intersection present in the derived CNV intersection layer. Records that
also name non-CNV streets (typically Highway 1 ramps) are matched but flagged
`match_confidence = medium`.

**Coverage achieved:** 288 of 2,218 ICBC records matched, covering 5,296 crashes, mapped to
288 of 503 intersections (57%). All 1,930 unmatched records are retained with reasons in
`outputs/tables/icbc_unmatched_locations.csv`.

**Limitations:** Intersections without a match are **unknown, not zero collisions** — the
scoring leaves them `NaN` rather than scoring them as safe. Counts are not year-specific in
this export. The BC Data Catalogue record for ICBC Reported Crashes links to Tableau rather
than a data file; no bulk open-data collision file exists.

---

## 12. Municipal land area vs legal boundary

**Not a missing dataset, but a methodological trap worth recording.**

The BC ABMS legal municipal boundary encloses **14.92 km²**, because it extends into
Burrard Inlet. Statistics Canada reports CNV's **land area as 11.83 km²**, and the sum of
the 79 constituent dissemination areas is 11.79 km².

**Approach taken:** All density calculations use **StatCan land area**, never the legal
boundary area. The legal boundary is used only for clipping and display.

---

## 13. Road classification polygons — server-side corruption

Eleven of 518 features in the CNV `Road Classifications` layer (layer 127) cannot be
serialised by the ArcGIS endpoint; any request containing them returns HTTP 400. The
downloader bisects around them and retrieves **507 of 518**, recording the unreadable
OBJECTIDs (499, 522, 532, 543, 2711, 5015 and others) in the download metadata sidecar.
This layer is supplementary — `ROADCLASS` on the street centrelines is the primary source
and is complete.

---

## 14. Zoning regulations (permitted height, FSR) for standard zones

**Dataset:** Maximum building height and floor space ratio per zoning district.

**Desired use:** Permitted built form everywhere, to compensate for actual building height
being published for only 0.9% of footprints.

**What was found:** The CNV zoning GIS layer carries `MAX_BLDG_HT`, `FSR`, setbacks and
`MINIM_OFFSTREET_PKG` fields, but they are populated for only **13%** of zone polygons
(88 of 683) — and mostly for site-specific Comprehensive Development (CD) zones
(71 of 457 CD polygons) rather than the 38 standard zone codes (C-1A, RS-1, LL-1 … ),
where only 17 of 226 polygons carry a height.

`CNV_ZoningBook.pdf` was retrieved and inspected as a candidate source. It is a **42-page
tiled map book with zero regulation text** — a search across all pages for
"maximum height", "floor space ratio" or "FSR" returns **no matches**. It cannot fill this
gap.

**Best available proxy used:** None. Permitted height is not modelled. Built form is
described from the Census dwelling-structure mix, which is complete and authoritative.

**Recommended next action:** Obtain the CNV Zoning Bylaw text (not the map book) and join
its per-zone regulation table to the 38 standard zone codes.

---

## Summary table

| # | Gap | Severity | Proxy used | Coverage achieved |
|---|---|---|---|---|
| 1 | Municipal traffic volumes | **High** | Road classification | 40/503 intersections have measured volume |
| 2 | Signal timing | **High** | None — no estimate made | 0% (REQUEST_REQUIRED) |
| 3 | Pedestrian counts | **High** | Documented composite proxy | 0% measured |
| 4 | Polling division boundaries | Structural | Voting-place points + buffers | n/a — do not exist |
| 5 | 2022 ballots per place | Medium | Mayoral votes as lower bound | 9/9 general places |
| 6 | Electors by small geography | Medium | Census 18+ and citizen 18+ | City-wide only |
| 7 | Real-time parking | Low | Dec 2022–Feb 2023 survey | 1,169 segments |
| 8 | Building height/units/year | **High** | Census dwelling structure type | 0.9% of footprints |
| 9 | Strata tenure | Medium | City `STRATA` attribute only | High-rise layer only |
| 10 | Licensed seniors care | **High** | Affordable-housing 55+ sites | 11 sites; Evergreen House flagged |
| 11 | Collision geography | Medium | Conservative name matching | 288/503 intersections |
| 12 | Land area vs legal area | Resolved | StatCan land area used | 100% |
| 13 | Road class polygons | Low | Centreline `ROADCLASS` | 507/518 |
| 14 | Zoning regulations (height/FSR) | Medium | none — not modelled | 13% of zone polygons |
