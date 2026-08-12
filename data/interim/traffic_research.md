# Traffic Count Data Research — City of North Vancouver & North Shore

Research date: **2026-08-12**
Scope: machine-readable vehicle traffic count / volume data covering the City of North
Vancouver (CNV) and the surrounding North Shore corridor (DNV, West Vancouver,
Highway 1 / Upper Levels, Lions Gate Bridge, Ironworkers Memorial / Second Narrows Bridge).

All endpoints below are **public and unauthenticated**. No CAPTCHA, rate-limit,
authentication or robots restriction was bypassed. Where a source required a key or
login, that fact is recorded and the source was abandoned.

---

## 1. API discovery — BC Traffic Data Program

### 1.1 How the endpoints were found

`https://www.th.gov.bc.ca/trafficdata/` has no download links; it points at the
interactive map `https://twm.th.gov.bc.ca/?c=tdp`. That map is **not** ArcGIS — it is a
custom BC MoTI OpenLayers framework ("TWM v2.3"). The discovery chain was:

1. `GET https://twm.th.gov.bc.ca/?c=tdp` — the HTML loads `application/inc/init.js`.
2. `init.js` reveals configs load from `configuration/<name>/app-config.js`, so
   `GET https://twm.th.gov.bc.ca/configuration/tdp/app-config.js`.
3. That config defines the map layers as **OGC WFS** sources against
   `returnEnvironmentUrl("ogs-public")`, plus report links built from
   `returnEnvironmentUrl("pub-oas")` and `returnEnvironmentUrl("tradas")`.
4. `common.js` shows `returnEnvironmentUrl()` resolves via `api/url/<key>`:

```
GET https://twm.th.gov.bc.ca/api/url/ogs-public  -> {"endpointKey":"ogs-public","url":"https://maps.th.gov.bc.ca/geoV05"}
GET https://twm.th.gov.bc.ca/api/url/tradas      -> {"endpointKey":"tradas","url":"https://tradas.th.gov.bc.ca"}
GET https://twm.th.gov.bc.ca/api/url/pub-oas     -> {"endpointKey":"pub-oas","url":"https://prdoas6.pub-apps.th.gov.bc.ca"}
```

Note: the BC Data Catalogue record for the Traffic Data Program still advertises
`https://prdoas3.pub-apps.th.gov.bc.ca/tsg/`; the live application now resolves to
**prdoas6**. Use the `api/url/` resolver rather than hard-coding the host.

### 1.2 Station geometry — GeoServer WFS (primary discovery endpoint)

**Base:** `https://maps.th.gov.bc.ca/geoV05/ows`  (GeoServer, OGC WFS 2.0.0)

| typeName | Contents | Features (BC-wide) |
|---|---|---|
| `tig:TIG_TMS_GEOMETRY_EXT_V` | Traffic count sites, **2004 to present** | 914 |
| `tig:TIG_TMP_GEOM_EXT_V` | Historical count sites, **1994–2003**, includes AADT | 3,229 |
| `tsg:TSG_ARCIMS_SURVEY_V_SQLVIEW` | Survey view referenced by the TDP config | not harvested |

Working example request (whole-province, GeoJSON, WGS84):

```
https://maps.th.gov.bc.ca/geoV05/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=tig:TIG_TMS_GEOMETRY_EXT_V&outputFormat=application/json&srsName=EPSG:4326
```

`count=<n>` limits results; `srsName` accepts EPSG:4326 / 3857 / 3005.

**`TIG_TMS_GEOMETRY_EXT_V` response schema** — GeoJSON `FeatureCollection`, Point
geometry (`geometry_name: "SHAPE"`), properties:

| Field | Type | Meaning |
|---|---|---|
| `OBJECTID` | int | GeoServer row id |
| `TMS_EXT_ID` | int | internal traffic-monitoring-station id |
| `SITE_CODE` | string | **public station code** (e.g. `P-15-2EW`, `15-025E`) — the join key to TRADAS |
| `PDB_SITE_ID` | int | id used by the `tig-public` PDF site-report service |
| `UTV_SEGMENT_EXT_ID` | int/null | Uniform Traffic Volume segment id |
| `TMS_DESCRIPTION` | string | site/interchange name (e.g. `5100; Lonsdale I/C`) |
| `DESCRIPTION` | string | free-text location |
| `STATUS_CODE` / `STATUS_DESCRIPTION` | string | `A` / `Active` |
| `TYPE_CODE` / `TYPE_DESCRIPTION` | string | `P` = `Permanent Core`, `S` = `Short Core` |

**`TIG_TMP_GEOM_EXT_V` (1994–2003)** carries volumes directly in the attributes:
`TMP_ID`, `TMP_GROUP_ID`, `LOCATION_DESCRIPTION`, `ROAD_NAME`, `PERMANENT_FLAG`,
`COMPOSITE_FLAG`, `LANE_COUNT`, `SURVEY_AREA_ID`, **`LAST_YEAR`**, **`AADT`**, `GROUP_TMPS`.

### 1.3 Count data — TRADAS report application

**Base:** `https://tradas.th.gov.bc.ca/tradas.asp?loc=<SITE_CODE>`

This is a stateful classic-ASP app (session cookie `ASPSESSIONID*`). It is **not** a JSON
API, but it exposes **static, directly-downloadable report files** once a selection
cascade is completed. The cascade is a sequence of form POSTs back to the *same URL
including its query string* (posting to bare `/tradas.asp` returns HTTP 500 and drops
back to the province-wide location list):

```
GET  /tradas.asp?loc=P-15-2EW                                        # session + full option lists
POST /tradas.asp?loc=P-15-2EW   loc, stype=AV02, syear=0,  smon=0, sday=0   # -> years that actually have data
POST /tradas.asp?loc=P-15-2EW   loc, stype=AV02, syear=2025, smon=0, sday=0 # -> report links appear
```

Each dropdown is **data-driven**: the returned `<option>` list is exactly the set of
years/months/days for which that station has a report. Submitting a year that is not in
the returned list silently resets the form — so the year list must be read back, not guessed.

Report links in the response have the shape:

```
reports/AllYears/<YYYY>/<MM>/<TYPE>/<TYPE><P|S>_<Site name> <SITE_CODE> - <dir>Y<YYYY>.<csv|pdf|xls>
```

and can then be fetched directly (URL-encode the spaces):

```
https://tradas.th.gov.bc.ca/reports/AllYears/2025/01/AV02/AV02P_Second%20Narrows%20P-15-2EW%20-%20NY2025.csv
```

**Report types** (`stype` values). Availability differs by station class:

| Code | Report | Available at |
|---|---|---|
| `AV02` | Annual Volume — **AADT / AAWDT / AAWET** | permanent stations only |
| `AV03` | Annual Design Hours | permanent stations only |
| `AV04` | Annual by Day of Week | permanent stations only |
| `DV01` | Daily Volume (permanents), full year | permanent stations only |
| `MV02` / `MV03` | Monthly Volume calendar / by hour | permanent stations only |
| `AL01`,`AL02`,`AS01`,`DL01`,`DS01`,`MS01`,`MS02`,`ML01`,`ML02`,`MV04` | length / speed / class breakdowns | `P-15-2EW` only, locally |
| **`DV03S`** | **Short-count Daily Volume — 24 hourly counts + daily total + AM/PM peaks** | **all 48 short-count stations near CNV** |

`DV03S` is *not* listed in the initial `stype` dropdown scraped from a permanent station —
it only appears on short-count sites. This is the report type that actually covers the
City of North Vancouver's own Highway 1 interchanges. `DV03S` is published as **.xls and
.pdf only (no CSV)**; the annual permanent-station reports are published as **.csv, .xls and .pdf**.

### 1.4 Per-site PDF report service

```
https://prdoas6.pub-apps.th.gov.bc.ca/tig-public/Report.do?pdbSiteId=<PDB_SITE_ID>
```

Returns `application/pdf` directly (verified with `pdbSiteId=14072`, Second Narrows). Use
`PDB_SITE_ID` from the WFS layer. Site diagrams are also static:
`https://tradas.th.gov.bc.ca/siteDiagrams/<n>.pdf`.

---

## 2. Count stations in or near the City of North Vancouver

Distances are **exact metres from the CNV legal municipal boundary**
(`data/processed/cnv_boundary.gpkg`, ABMS, computed in EPSG:3005), not centroid
approximations. `0 m` = the station falls inside the CNV boundary.

Full machine-readable tables:
- `data/interim/tms_stations_near_cnv.csv` — 50 stations, 2004-present layer
- `data/interim/tmp_stations_near_cnv_1994_2003.csv` — 202 stations, 1994–2003 layer

### 2.1 Stations INSIDE the City of North Vancouver (10)

All are Highway 1 (Upper Levels) mainline/ramp sites — CNV has **no MoTI count station on
a municipal street**, because the Traffic Data Program only monitors the provincial
highway network.

| station_id | name | lat | lon | road / relation to CNV | years available (DV03S) |
|---|---|---|---|---|---|
| `15-024E` | Lonsdale I/C | 49.33214 | -123.08029 | Hwy 1 EB, W of Lonsdale Ave — **inside CNV** | 2003, 2006, 2009, 2013, 2016 |
| `15-024W` | Lonsdale I/C | 49.33220 | -123.08020 | Hwy 1 WB, W of Lonsdale Ave — **inside CNV** | 2003, 2006, 2009, 2013, 2016 |
| `15-025E` | Lonsdale I/C | 49.33187 | -123.06132 | Hwy 1 EB, Lonsdale↔St. Andrews — **inside CNV** | 2003, 2006, 2009, 2016 |
| `15-025W` | Lonsdale I/C | 49.33210 | -123.06198 | Hwy 1 WB, Lonsdale↔St. Andrews — **inside CNV** | 2003, 2006, 2009, 2013, 2016 |
| `15-0243` | Lonsdale I/C (ramp) | 49.33171 | -123.06531 | Hwy 1 ramp — **inside CNV** | 2003, 2006, 2009, 2013, 2016 |
| `15-0244` | Lonsdale I/C (ramp) | 49.33210 | -123.06609 | Hwy 1 ramp — **inside CNV** | 2003, 2006, 2009, 2013, 2016 |
| `15-026E` | Fern Street I/C | 49.32167 | -123.04264 | Hwy 1 EB, 0.8 km W of Mountain Hwy — **inside CNV** | 2003, 2013, 2016 |
| `15-026W` | Fern Street I/C | 49.32175 | -123.04253 | Hwy 1 WB, 0.8 km W of Mountain Hwy — **inside CNV** | 2003, 2013, 2016 |
| `15-0226` | Westview Drive I/C | 49.33187 | -123.08661 | Hwy 1 ramp — **inside CNV** | 2003, 2006, 2013 |
| `15-0227` | Westview Drive I/C | 49.33222 | -123.08623 | Hwy 1 ramp — **inside CNV** | 2003, 2013 |

### 2.2 Key stations adjacent to CNV (the two bridges + Upper Levels corridor)

| station_id | name | lat | lon | road / relation to CNV | type | dist. to CNV |
|---|---|---|---|---|---|---|
| `P-15-2EW` | Second Narrows | 49.29134 | -123.02637 | Hwy 1, **Ironworkers Memorial Bridge**, east end | **Permanent Core** | 1,025 m |
| `P-15-1NS` | Lions Gate | 49.31268 | -123.14123 | Hwy 99, **Lions Gate Bridge**, south end | **Permanent Core** | 2,812 m |
| `15-960NS` | Fern Street I/C | 49.31530 | -123.03740 | Hwy 1 approach to Second Narrows | Short Core | 231 m |
| `15-0558` | Fern Street I/C | 49.31588 | -123.03680 | Hwy 1 ramp | Short Core | 305 m |
| `15-022W` | Westview Drive I/C | 49.33259 | -123.10581 | Hwy 1, 0.8 km E of Capilano I/C | Short Core | 322 m |
| `15-022E` | Westview Drive I/C | 49.33245 | -123.10598 | Hwy 1, 0.8 km E of Capilano I/C | Short Core | 324 m |
| `15-0553` | Fern Street I/C | 49.31253 | -123.02950 | Hwy 1 ramp | Short Core | 631 m |
| `15-035E` | Fern Street I/C | 49.30902 | -123.02792 | Hwy 1, 0.28 km S of Fern St U/P | Short Core | 754 m |
| `15-035W` | Fern Street I/C | 49.30899 | -123.02780 | Hwy 1, 0.28 km S of Fern St U/P | Short Core | 763 m |
| `15-818E` | Capilano Road I/C | 49.33249 | -123.11528 | Hwy 1 EB at Capilano Rd | Short Core | 973 m |
| `15-0534` | Capilano Road I/C | 49.33237 | -123.11548 | Hwy 1 ramp | Short Core | 985 m |
| `15-0531` | Capilano Road I/C | 49.33287 | -123.11546 | Hwy 1 ramp | Short Core | 994 m |
| `15-819W` | Capilano Road I/C | 49.33261 | -123.11664 | Hwy 1 WB at Capilano Rd | Short Core | 1,073 m |
| `15-021W` / `15-021E` | Taylor Way I/C | 49.33371 / 49.33362 | -123.12237 / -123.12243 | Hwy 1A/99 Taylor Way, West Vancouver | Short Core | ~1,506 m |
| `15-0573` | First Narrows I/C | 49.32581 | -123.12706 | Lions Gate approach | Short Core | 1,807 m |
| `15-0524` / `15-0520` | Taylor Way I/C | 49.33737 / 49.33741 | -123.12855 / -123.13243 | Hwy 1 ramps, West Vancouver | Short Core | 2,050 / 2,318 m |
| `15-006NS` | First Narrows I/C | 49.32715 | -123.13372 | Hwy 1A/99, W end Capilano River Bridge | Short Core | 2,294 m |
| `15-005NS` | Taylor Way I/C | 49.33573 | -123.13488 | Hwy 1A/99 Taylor Way | Short Core | 2,442 m |
| `15-015E` / `15-015W` | Taylor Way I/C | 49.33817 / 49.33832 | -123.14169 / -123.14168 | Hwy 1/99 W of Taylor Way | Short Core | ~2,990 m |
| `15-051W` / `15-051E` | 21 Street I/C | 49.34366 / 49.34364 | -123.16050 / -123.16238 | Hwy 1/99, West Vancouver | Short Core | 4,474 / 4,604 m |
| `16-25xx`, `16-09xx`, `16-0xx`, `16-1xx` (16 sites) | McGill St / Cassiar / Boundary Rd / Lougheed / Willingdon I/Cs | — | — | Hwy 1 **south** of the Second Narrows (Vancouver/Burnaby side) | Short Core | 997–4,826 m |

Full 50-row listing with every field: `data/interim/tms_stations_near_cnv.csv`.

### 2.3 Historical stations (1994–2003 layer)

202 stations within 5 km of CNV, **33 inside CNV**, every one carrying an `AADT` value
and a `LAST_YEAR`. Highest in-CNV values (verbatim from
`tig:TIG_TMP_GEOM_EXT_V`, all Hwy 1):

| TMP_ID | location | AADT | LAST_YEAR |
|---|---|---|---|
| `15-025E` | 0.5 km E of Lonsdale Ave (composite, Lonsdale I/C) | 39,104 | 2001 |
| `15-024W` | 0.5 km W of Lonsdale Ave (composite, Lonsdale I/C) | 37,316 | 2002 |
| `15-026W` | just W of Mountain Hwy (composite, Lynn Valley + Fern St I/C) | 34,972 | 1998 |
| `15-024E` | 0.5 km W of Lonsdale Ave (composite, Lonsdale I/C) | 34,746 | 2002 |
| `15-025W` | 0.5 km E of Lonsdale Ave (composite, Lonsdale I/C) | 34,115 | 1995 |
| `15-026E` | just W of Mountain Hwy (composite) | 32,560 | 2000 |
| `15-823` | Hwy 1 WB through, just E of Lynn Valley Rd | 31,784 | 2000 |
| `15-821` | Hwy 1 WB through, just W of Lonsdale Ave | 29,881 | 2002 |
| `15-820` | Hwy 1 EB through, just W of Lonsdale Ave | 28,432 | 2001 |

These are **legacy 1994–2003 values** and must not be presented as current conditions.

---

## 3. Data actually downloaded

### 3.1 Files

| Path | Content | Format |
|---|---|---|
| `data/raw/traffic/bcmoti_tms_stations_2004_present_bc.geojson` | 914 BC count stations, 2004–present | GeoJSON, EPSG:4326 |
| `data/raw/traffic/bcmoti_tmp_stations_1994_2003_bc.geojson` | 3,229 BC historical stations **with AADT** | GeoJSON, EPSG:4326 |
| `data/raw/traffic/tradas_reports/*.csv` | Annual volume/design-hour/day-of-week reports, permanent stations | CSV |
| `data/raw/traffic/tradas_reports/DV03S_*.xls` | 102 short-count workbooks, 38 stations, **2003–2016**, 24 hourly counts per survey day | XLS (BIFF) |
| `data/raw/traffic/tradas_reports/MV0*_*.xls`, `DV01_*.xls` | Monthly + daily volume series, permanent stations, 2004–2025 | XLS (BIFF) |
| `data/raw/traffic/tradas_reports/_harvest_log.json`, `_shortcount_harvest_log.json` | Per-station provenance: report types found, source URL, bytes | JSON |
| `data/raw/traffic/bcdc_annual_traffic_volumes_2004_2010.xlsx` | BC-wide AADT + SADT by UTVS segment, 1994–2010 | XLSX |
| `data/interim/tms_stations_near_cnv.csv` | 50 stations ≤5 km of CNV boundary + exact distance | CSV |
| `data/interim/tmp_stations_near_cnv_1994_2003.csv` | 202 historical stations ≤5 km + AADT | CSV |
| `data/interim/tradas_shortcount_daily.csv` | Parsed short counts: station-day volume, AM/PM peak volume & hour | CSV |

### 3.2 Most recent AADT actually retrieved (verbatim from source CSVs)

From `AV02` Annual Volume reports, **2025 rows**:

| Station | Facility | AADT 2025 | AAWDT 2025 | AAWET 2025 | Source file |
|---|---|---|---|---|---|
| `P-15-2EW` | Ironworkers Memorial / Second Narrows Bridge (Hwy 1) | **130,664** | 133,737 | 120,712 | `P-15-2EW_AV02_2025.csv` |
| `P-15-1NS` | Lions Gate Bridge (Hwy 99), south end | **56,581** | 57,992 | 52,110 | `P-15-1NS_AV02_2025.csv` |

Each AV02 CSV also contains the full annual back-series (2015–2025) and a monthly
MADT/MAWDT/MAWET table for the reported year, so time-series analysis needs no extra requests.

### 3.3 Units and definitions — do not mix these

| Term | Definition | Where it appears |
|---|---|---|
| **AADT** | Annual Average Daily Traffic — average vehicles/day over the whole year, seasonally and daily factored. Two-way total at the site. | `AV02` CSVs; `TIG_TMP_GEOM_EXT_V.AADT`; BCDC xlsx |
| **AAWDT** | Annual Average **Weekday** Traffic (Mon–Fri) | `AV02` CSVs |
| **AAWET** | Annual Average **Weekend** Traffic (Sat–Sun) | `AV02` CSVs |
| **MADT / MAWDT / MAWET** | Monthly equivalents of the above | `AV02`, `MV02` |
| **SADT** | Summer Average Daily Traffic (Jul–Aug) | BCDC xlsx only |
| **Daily volume (short count)** | **Raw observed** vehicles counted in a 24 h period on a specific date. **Not** annualised, **not** an AADT. | `DV03S` xls |
| **Hourly count** | Raw observed vehicles in a clock hour (`00:00`…`23:00`) | `DV03S` xls |
| **AM/PM Peak Vol** | Raw observed vehicles in the peak hour of that survey day | `DV03S` xls |
| **Seasonal Fct / Daily Fct / Growth Fct** | Expansion factors MoTI applies to convert raw counts to annualised estimates | `DV03S` xls |
| **`% POS`** | Share of volume in the "positive" direction (50 = balanced) | `AV02` |
| **`TYPE_CODE`** | `P` = Permanent Core (continuous counter); `S` = Short Core (periodic manual/tube survey) | WFS |

Worked example of the distinction, from
`DV03S_-_Site_Lonsdale_I-C_-_15-024E_-_N_on_09-23-2009.xls` (Hwy 1 EB, 0.5 km W of
Lonsdale Ave, inside CNV): 24 Sep 2009 daily volume **40,249 veh**, AM peak hour 08:00
with **2,694 veh**, PM peak hour ~16:18 with **3,559 veh**; seasonal factor 0.955.
Those are raw observed counts for one day — **not** an AADT for that location.

---

## 4. What is NOT available, and why

| Missing dataset | Why |
|---|---|
| **AADT for any station inside CNV** | The 10 in-CNV stations are all `Short Core`. MoTI publishes `AV02` (AADT) only for `Permanent Core` counters. The nearest permanent counters are Second Narrows (1.0 km) and Lions Gate (2.8 km). In-CNV volumes exist only as dated raw short counts. |
| **Recent counts at CNV stations** | Latest `DV03S` surveys at the CNV Hwy 1 interchanges are **2016** (Lonsdale I/C, Fern St I/C, Westview Dr I/C 2016; some ramps 2013). No 2017+ short count is published for these sites. |
| **Traffic counts on CNV municipal streets** (Lonsdale Ave, Marine Dr, 3rd St, Keith Rd, Esplanade …) | The BC Traffic Data Program covers the **provincial highway network only**. Hwy 1 is the sole provincial facility through CNV. Municipal counts would have to come from the City of North Vancouver directly and are **not** in `gisext2.cnv.org` ArcGIS services (which carry signals, signs, speed zones, calming, truck routes — no volumes). |
| **Bulk download of the TDP database** | The BC Data Catalogue record `traffic-data-program` is licensed **"Access Only"** and its only resource is a link to the web application — not an open-data file. The WFS station layer and the static TRADAS report files are retrievable, but there is no sanctioned bulk export of the count database, and the "Access Only" licence should be cited before redistributing the report files. |
| **A JSON/REST count API** | TRADAS is classic ASP with server-side session state. There is no JSON endpoint for volumes. The only stable machine-readable artefacts are the static `reports/AllYears/...` csv/xls/pdf files. |
| **BC Data Catalogue AADT beyond 2010** | The only open-licensed volume file is `annual-traffic-volumes-2004-2010` (OGL-BC), AADT+SADT by UTVS segment, **1994–2010**. The three `monthly-traffic-volumes-permanent-counters-*` files stop at **June 2011**. Nothing newer is published there. |
| **TransLink Major Road Network geometry** | Catalogued at BCDC (`translink-major-road-network`, OGL–TransLink) but the download API is **broken**: `https://trp.regionalroads.com/api/?data=GM_MRN&format=geojson&download=true` returns **HTTP 500** for every format (geojson / shapefile / kml / json); the API root answers `{"error": "Invalid Parameters"}`, so the host is alive but the dataset export is failing. `https://trp.regionalroads.com/` itself returns **HTTP 403**. Re-test later or request from TransLink. |
| **TransLink traffic / screenline counts** | TransLink's developer resources page publishes **GTFS schedule + realtime and transit APIs only**. No screenline, cordon or regional traffic count product is offered as open data. Trip Diary / screenline survey results are published as PDF reports, not machine-readable counts. |
| **Metro Vancouver traffic or truck-route data** | The Metro Vancouver open-data ArcGIS org (`56eqCzQ5SZhBaDST`) was enumerated in full: **58 public feature services**, none traffic-related (they are ecology, land use, waste, air quality, parks, hazard layers). No truck route, count station or screenline layer exists there. |
| **District of North Vancouver counts** | `geoweb.dnv.org/data/` publishes traffic **infrastructure** only (`LgtTrafficConduit`, `LgtTrafficFittings`, `LgtTrafficPoles`). No count or volume dataset. |
| **Vehicle classification / speed at CNV stations** | Length/speed report types (`AL01`, `AS01`, `DL01`, `DS01`, `MS01`, `MS02`, `ML01`, `ML02`) are offered **only at `P-15-2EW`** among the stations studied. Not available at any in-CNV station. |
| **Turning-movement counts at intersections** | Not published by MoTI, CNV, DNV, TransLink or Metro Vancouver in any machine-readable form found. |

### Implication for the intersection analysis

No CNV **municipal** intersection can be assigned a measured traffic volume from these
sources. The defensible options are:
1. Use the Hwy 1 station data for the highway corridor and the two bridges only.
2. For municipal streets, use the CNV road-designation / classification layers
   (arterial / collector / local, MRN flag) as an **ordinal exposure proxy** — clearly
   labelled as a proxy, never as a count.
3. Record a `DATA_GAPS.md` entry for CNV municipal traffic volumes and note that a direct
   request to CNV Engineering is the recommended next action.

---

## 5. Ready-to-use `config/sources.yaml` entries

```yaml
  # ---------------------------------------------------------------------------
  # TRAFFIC - BC Ministry of Transportation and Transit, Traffic Data Program
  # Endpoints discovered 2026-08-12 by resolving the TWM webmap config:
  #   https://twm.th.gov.bc.ca/configuration/tdp/app-config.js
  #   https://twm.th.gov.bc.ca/api/url/ogs-public -> https://maps.th.gov.bc.ca/geoV05
  # ---------------------------------------------------------------------------
  - source_id: bcmoti_tms_stations
    organization: "BC Ministry of Transportation and Transit"
    dataset: "Traffic Data Program - count sites, 2004 to present (TIG_TMS_GEOMETRY_EXT_V)"
    handler: wfs
    url: "https://www.th.gov.bc.ca/trafficdata/"
    wfs_base: "https://maps.th.gov.bc.ca/geoV05/ows"
    typename: "tig:TIG_TMS_GEOMETRY_EXT_V"
    out_dir: traffic
    filename: bcmoti_tms_stations_2004_present_bc.geojson
    format: GeoJSON
    geographic_level: point_station
    coverage: "British Columbia (filter to CNV + 5 km locally)"
    expected_count: 914
    license: "Access Only - see BC Data Catalogue record 'traffic-data-program'"
    authoritative: true
    notes: >
      Join key SITE_CODE (also used by TRADAS). PDB_SITE_ID keys the tig-public PDF
      report service. TYPE_CODE P=Permanent Core, S=Short Core. 50 stations lie within
      5 km of the CNV boundary; 10 lie inside it, all on Highway 1.

  - source_id: bcmoti_tmp_stations_historic
    organization: "BC Ministry of Transportation and Transit"
    dataset: "Traffic Data Program - historical count sites 1994-2003 (TIG_TMP_GEOM_EXT_V)"
    handler: wfs
    url: "https://www.th.gov.bc.ca/trafficdata/"
    wfs_base: "https://maps.th.gov.bc.ca/geoV05/ows"
    typename: "tig:TIG_TMP_GEOM_EXT_V"
    out_dir: traffic
    filename: bcmoti_tmp_stations_1994_2003_bc.geojson
    format: GeoJSON
    geographic_level: point_station
    coverage: "British Columbia"
    expected_count: 3229
    license: "Access Only - see BC Data Catalogue record 'traffic-data-program'"
    notes: >
      Carries AADT and LAST_YEAR directly in the attributes - the only source giving
      in-CNV AADT at all, but the values are 1994-2003 vintage. 202 stations within 5 km
      of CNV, 33 inside it. Historical context only; never label as current.

  - source_id: bcmoti_tradas_reports
    organization: "BC Ministry of Transportation and Transit"
    dataset: "TRADAS traffic volume reports (AADT + short counts) for stations near CNV"
    handler: custom
    script: scripts/09_prepare_traffic.py
    url: "https://tradas.th.gov.bc.ca/tradas.asp?loc=P-15-2EW"
    report_base: "https://tradas.th.gov.bc.ca/reports/AllYears"
    out_dir: traffic/tradas_reports
    format: "CSV + XLS (BIFF, needs xlrd>=2.0.1)"
    geographic_level: point_station
    coverage: "50 stations within 5 km of the CNV boundary"
    license: "Access Only - see BC Data Catalogue record 'traffic-data-program'"
    notes: >
      Stateful ASP app, not a JSON API. POST the form back to the URL INCLUDING its
      query string (?loc=<SITE_CODE>); posting to bare /tradas.asp returns HTTP 500.
      Cascade stype -> syear -> smon -> sday, reading each returned <option> list rather
      than guessing values. Permanent stations (P-15-2EW Second Narrows, P-15-1NS Lions
      Gate) expose AV02/AV03/AV04/DV01/MV02/MV03; short-count stations expose DV03S only.
      AV02 is published as csv/xls/pdf; DV03S as xls/pdf only.

  - source_id: bcdc_annual_traffic_volumes
    organization: "Province of BC - BC Data Catalogue"
    dataset: "Annual Traffic Volumes 2004-2010 (AADT and SADT by UTVS segment)"
    handler: http_file
    url: "https://catalogue.data.gov.bc.ca/dataset/annual-traffic-volumes-2004-2010"
    download_url: "https://catalogue.data.gov.bc.ca/dataset/fb64bc6f-4a96-4cc9-a4f4-f84578968ca6/resource/6f821337-1cbb-4b3d-8caf-6cafa2aa472b/download/bctransportannualvolumes.xlsx"
    out_dir: traffic
    filename: bcdc_annual_traffic_volumes_2004_2010.xlsx
    format: XLSX
    geographic_level: highway_segment
    coverage: "British Columbia provincial highways"
    version: "1994-2010 series"
    license: "Open Government Licence - British Columbia"
    expect_magic: zip      # xlsx is a zip container
    notes: >
      Pivot-table layout: header on row 2, AADT columns 1994-2010 then SADT columns
      1994-2010. Site Id column matches SITE_CODE in the WFS layers. The ONLY
      open-licensed (OGL-BC) volume file found; everything newer is 'Access Only'.
```

Optional, only if TransLink fixes the export (currently HTTP 500 — leave commented out):

```yaml
  # - source_id: translink_major_road_network
  #   organization: "TransLink"
  #   dataset: "Major Road Network (MRN)"
  #   handler: http_file
  #   url: "https://catalogue.data.gov.bc.ca/dataset/translink-major-road-network"
  #   download_url: "https://trp.regionalroads.com/api/?data=GM_MRN&format=geojson&download=true"
  #   out_dir: traffic
  #   filename: translink_major_road_network.geojson
  #   format: GeoJSON
  #   license: "Open Government Licence - TransLink"
  #   status: BROKEN_UPSTREAM
  #   notes: "Verified 2026-08-12: HTTP 500 for all formats; host root returns 403. Re-test before enabling."
```

---

## 6. Reproduction

```bash
# 1. Resolve the endpoints (no key required)
curl -s https://twm.th.gov.bc.ca/api/url/ogs-public

# 2. Station geometry
curl -s "https://maps.th.gov.bc.ca/geoV05/ows?service=WFS&version=2.0.0&request=GetFeature\
&typeName=tig:TIG_TMS_GEOMETRY_EXT_V&outputFormat=application/json&srsName=EPSG:4326" \
  -o data/raw/traffic/bcmoti_tms_stations_2004_present_bc.geojson

# 3. A known-good AADT report
curl -s "https://tradas.th.gov.bc.ca/reports/AllYears/2025/01/AV02/\
AV02P_Second%20Narrows%20P-15-2EW%20-%20NY2025.csv" -o second_narrows_aadt_2025.csv
```

Parsing the legacy `.xls` short counts requires `xlrd>=2.0.1` (added to the environment);
add it to `requirements.txt`.

### Accuracy note

Every station ID, coordinate and volume in this document was read directly from the
BC MoTI WFS response or from a downloaded TRADAS report file. Nothing is estimated,
interpolated or fabricated. Where a value is unavailable it is stated as unavailable.
