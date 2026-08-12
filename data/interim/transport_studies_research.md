# CNV Transportation / Engineering Document Research

Research date: 2026-08-12
Scope: City of North Vancouver (CNV, cnv.org) ONLY — not the District of North Vancouver.
All downloads: `/Users/ankurbatta/Desktop/GIS/data/raw/cnv/reports/`
Method: WebSearch + WebFetch + `curl` of public cnv.org URLs + public ArcGIS REST metadata on `gisext2.cnv.org`.
No authentication, paywalls, or technical controls were bypassed. All figures quoted below were read directly
in the cited document/endpoint.

---

## 1. Documents found and downloaded

| # | Title | Year | URL | Local file | Useful data | Page refs (PDF pages) |
|---|---|---|---|---|---|---|
| 1 | Curb Access and Parking Plan | Apr 2025 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/CNV-Curb-Access-and-Parking-Plan.pdf | `cnv_curb_access_and_parking_plan_2025.pdf` (22 p) | **Definitive parking-survey methodology + dates**; 85%/60% occupancy management thresholds; curb space management areas; occupancy observation protocol | p.21 Appendix 1 curb space allocation; **p.22 Appendix 2 "On-Street Parking Occupancy Observations"** (survey dates, method, Figure 8 peak occupancy map); p.19 occupancy observation rules |
| 2 | Curb Access & Parking Plan — Proposed Policy Changes | May 2024 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Proposed-Policy-Changes-Report.pdf | `cnv_curb_parking_proposed_policy_changes_2024.pdf` (16 p) | Occupancy concepts, pricing policy rationale; no dated count tables | p.8 "Curb Space Occupancy" |
| 3 | Council Report — Curb Access & Parking Plan (project initiation) | 11 Oct 2023 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Council-Report-–-Curb-Access-,-a-,-Parking-Plan-(Oct,-d-,-11-2023).pdf | `cnv_council_report_curb_parking_2023-10-11.pdf` (12 p) | States ">90% of curb space is dedicated to vehicle parking"; "Parking data collected across the City … near full occupancy throughout the day, both on weekdays and weekends" (this is the pre-2024 dataset, i.e. the GIS layer) | p.2–3 |
| 4 | Council Report — Curb Access & Parking Plan | 1 May 2024 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Council-Report-Curb-Access-and-Parking-Plan-May-1-2024.pdf | `cnv_council_report_curb_parking_2024-05-01.pdf` (7 p) | Phase 2 process, budget incl. "data collection" | — |
| 5 | Council Report — Curb Access & Parking Plan | 1 Apr 2025 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Council-Report-Curb-Access-and-Parking-Plan-(April-1-2025).pdf | `cnv_council_report_curb_parking_2025-04-01.pdf` (11 p) | Council endorsement of final plan | — |
| 6 | Curb Access & Parking Plan FAQ | Last updated Dec 2025 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Curb-Access-and-Parking-Plan-Frequently-Asked-Questions.pdf | `cnv_curb_parking_plan_faq.pdf` (9 p) | Rates, monitoring cadence ("occupancy will be monitored through 2026 and adjusted in 2027") | p.4–6 |
| 7 | Curb Access & Parking Plan — Phase 1 Engagement Summary | 2023/24 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Curb-Access-and-Parking-Plan-Phase-1-Engagement-Summary-Report.pdf | `cnv_curb_parking_phase1_engagement_summary.pdf` (33 p) | Stated-preference survey results, not counts | — |
| 8 | Curb Access & Parking Implementation Phases Map | 2025 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Curb-Access-,-a-,-Parking-Implementation-Phases-Map-2025.pdf | `cnv_curb_parking_implementation_phases_map_2025.pdf` (1 p) | Implementation phase geography | — |
| 9 | Mobility Strategy | Apr 2022 (Council approved 11 Apr 2022) | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Transportation-Resources/Mobility-Strategy-2022.pdf | `cnv_mobility_strategy_2022.pdf` (80 p) | City mobility policy to 2035; street-type framework. **Contains NO count tables** (grep for count/volume/AADT/screenline/signal timing returns nothing substantive) | — |
| 10 | Walk CNV — The Current State of Walking in the City of North Vancouver | **November 2017** | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Walk-CNV-The-Current-State-of-Walking-in-the-City-of-North-Vancouver.pdf | `cnv_walk_cnv_current_state_of_walking.pdf` (54 p) | This IS the "Walk CNV 2017" study the GIS layers reference. Contains: online/hardcopy interactive survey (**365 respondents, open 25 Jan – 6 Mar 2017**); walkabouts (Mar 2017); mapped survey responses (great places to walk, frequent destinations, infrastructure/accessibility issues); traffic-signal & special-crosswalk inventory map; mode share from 2011 NHS. **No pedestrian volume counts.** | Fig. 10 "Traffic Signals and Special Crosswalks" p.22 (report numbering); survey figures pp.27–44; signals narrative near p.22–23 |
| 11 | Walk CNV Pedestrian Plan Framework | Dec 2019 (PDF built Dec 2019, modified Jan 2020) | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Walk-CNV-Pedestrian-Plan-Framework.pdf | `cnv_walk_cnv_pedestrian_plan_framework.pdf` (22 p) | Four action areas; policy framework only, no counts | — |
| 12 | Safe Mobility Strategy | July 2020 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Safety-Mobility-Strategy-Report-Final.pdf | `cnv_safe_mobility_strategy_2020.pdf` (20 p) | Safety policy. Cites two **unpublished** sources: "City of North Vancouver **Network Screening Study (2016)**" and "ICBC Collision and Claim Data (2011–2017)" / "(2016–2017)". Commits to a city-wide road safety (network screening) study **at least every 5 years** and an **annual safe mobility status report to Council and the public** | Footnotes on the "Be Evidence-Based & Accountable" and speed/safety pages |
| 13 | Safe Mobility Strategy — Council presentation | July 2020 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Safety-Mobility-Strategy-Council-Presentation.pdf | `cnv_safe_mobility_strategy_council_presentation.pdf` (9 p) | Slide summary | — |
| 14 | **Moodyville Area Transportation Study — Technical Report (FINAL)** | **January 2016** | https://www.cnv.org/-/media/city-of-north-vancouver/documents/official-community-plan/moodyville-area-transportation-study-technical-report-final.pdf | `cnv_moodyville_area_transportation_study_technical_report.pdf` (68 p) | **Richest count document found.** Screenline hose counts + 7-day averages on East 3rd St; turning movement counts at every intersection Lonsdale→Queensbury; **pedestrian volumes at intersections**; parking occupancy/turnover by block; ICBC collision counts 2002–2013 | **p.21** Fig.14 weekday hourly volume profile E 3rd St; **p.22** Fig.15 current operations & signalization, Fig.16 observed peak-hour intersection volumes; **p.23** Fig.17 directional peak-hour volumes; **p.24** Table 6 intersection performance (PM peak, LOS/vc); **p.25** §2.4.2 Parking (Fig.18 parking demand & supply by block) + Tables 7 & 8 collisions; **p.35** Fig.28 current on-street parking; **p.64** Fig.42 E 3rd St 2015 hourly volumes and **Fig.43 Pedestrian Volumes at Intersections on East 3rd Street – Lonsdale to Queensbury** |
| 15 | Guidelines for the Submission of a Transportation Study — Level 1 | undated (references 2010 HCM, 2008 TransLink) | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Development-Application-Resources/Transportation-Study-Level-1-Guidelines.pdf | `cnv_transportation_study_level1_guidelines.pdf` (16 p) | **Key evidence for the signal-timing verdict** and for what count data the City holds internally | **p.6**: "Intersections and accesses (geometric layout, intersection control devices ‐ **details on signal phasing and cycle lengths will be provided by the City**)"; **p.7** §3.2 "Traffic count data (such as manual turning movement counts, hose counts or **count data uploaded from the traffic signals**) may be acquired from the City. In many cases the City's data may not be current or available…"; counts must cover vehicles, bicycles and **"pedestrian crossing volumes (differentiating children, seniors and adults)"**; **p.8** Synchro required, LOS D / v/c 0.9 thresholds |
| 16 | North Vancouver Bicycle Master Plan | Council-approved 5 Nov 2012 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Cycling/North-Vancouver-Bicycle-Master-Plan-2012.pdf | `cnv_bicycle_master_plan_2012.pdf` (66 p) | Joint City+District plan; 107 km of facilities; route network that the GIS `Bike Routes (BMP)` layer encodes | — |
| 17 | Bicycle Master Plan map (on-street/off-street) | — | https://gisext2.cnv.org/PDFMaps/CNV_BikeMasterPlanOffStOnSt.pdf | `cnv_bike_master_plan_map.pdf` (1 p) | Network map | — |
| 18 | Council Report — Priority Corridors for AAA Mobility Lanes | 23 Oct 2019 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Streets-and-Transportation/Council-Report-Priority-Corridors-for-All-Ages-and-Abilities-AAA-Mobility-Lanes-Report-of-October-23-2019.pdf | `cnv_council_report_aaa_priority_corridors_2019.pdf` (30 p) | Corridor prioritisation; Attachment 4 is a **Strava "heat map"** of tracked cyclists; Attachment 5 maps cyclist collisions. Strava is a biased sample, not a count program | Attachments 4–5 |
| 19 | Long-Term Transportation Plan | April 2008 | https://www.cnv.org/-/media/city-of-north-vancouver/documents/transportation-plan/long-term-transportation-plan.pdf | `cnv_long_term_transportation_plan_2008.pdf` (135 p) | Historic plan; mentions refining Lonsdale signal coordination and adjusting signal timing at specific locations, but publishes **no timing values** | — |
| 20 | LTTP Implementation & Monitoring Strategy | Jan 2009 | https://www.cnv.org/-/media/city-of-north-vancouver/documents/transportation-plan/implementation-and-monitoring-strategy-for-the-long-term-transportation-plan.ashx | `cnv_lttp_implementation_monitoring_strategy.pdf` (24 p) | Monitoring indicator framework | — |
| 21 | Traffic Calming Program | Sept 2004 (PDF creation date) | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Traffic-Calming/TrafficCalmingProgram.pdf | `cnv_traffic_calming_program.pdf` (35 p) | Warrant/petition process and device catalogue. No neighbourhood-specific counts | — |
| 22 | 2023 North Shore Transportation Survey — Report | June 2024 (PDF creation date); survey fielded 2023 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Transportation-Plan/2023-North-Shore-Transportation-Survey-Report.pdf | `cnv_north_shore_transportation_survey_2023.pdf` (107 p) | **Trip volumes and mode share for CNV specifically.** Table E3 (p.8): CNV daily trips 2023 — Auto driver 87,760; Auto passenger 8,570; Transit 16,930; Walk 37,250; Bicycle 4,440; Other 2,300; Total 157,250. Mode shares 2023: auto driver 55.8%, transit 10.8%, walk 23.7%, bike 2.8%. Trip-diary survey (modelled/expanded), **not** intersection counts | p.8 Table E3 / Fig. E5 |
| 23 | 2021 North Shore Transportation Survey — Report | 2021 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Transportation-Plan/2021-North-Shore-Transportation-Survey-Report.pdf | `cnv_north_shore_transportation_survey_2021.pdf` (134 p) | Comparable 2021 wave | — |
| 24 | 2019 North Shore Transportation Survey — Report | 2019 | https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Transportation-Plan/2019-North-Shore-Transportation-Survey-Report.pdf | `cnv_north_shore_transportation_survey_2019.pdf` (152 p) | Baseline 2019 wave | — |

Not downloaded but noted (available if needed):
- 2020 North Shore Transportation Survey — https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Transportation-Plan/2020-North-Shore-Transportation-Survey.pdf
- Mobility Strategy council reports (Feb 2021, Nov 2021, Apr 2022) and Phase 1 engagement summary — all under `.../Documents/Transportation-Resources/`
- Harbourside Waterfront OCP "Attachment 2 – Traffic Assessment" — https://www.cnv.org/-/media/city-of-north-vancouver/documents/major-development/harbourside-waterfront-ocp/attachment-2---traffic-assessment.PDF (developer-submitted study; likely contains TMCs for the Harbourside area)
- Transportation Study – Mini Study Guidelines — `.../Development-Application-Resources/Transportation-Study-Mini-Study-Guidelines.pdf`
- Schedule B Transportation Network Road Classification map — https://gisext2.cnv.org/PDFMaps/Schedule%20B%20TransportationNetworkRdClassification_11x17.pdf

---

## 2. THE PARKING SURVEY DATE

**There are TWO distinct CNV on-street parking occupancy datasets. They must not be conflated.**

### 2a. The dataset behind the GIS layer we already have (weekday/weekend 7am/11am/4pm/9pm + `Supply`)

**Answer: collected by Bunt & Associates in December 2022 and January/February 2023.**

Evidence — ArcGIS ISO metadata abstract (`idAbs`) on the parent group layer, read verbatim:

- Endpoint: `https://gisext2.cnv.org/arcgis/rest/services/BaseMapServices/TransportMAP/MapServer/50/metadata`
- `<resTitle>` = `Parking-Occupancy`
- `<idAbs>` = **"Parking inventory collected by Bunt & Associates in December 2022 and January/February 2023"**
- `<CreaDate>` = `20231004` (2023-10-04) on layer 50 and on every child layer 51–58.

Child layers (each a polyline feature layer, fields `Supply`, `Weekday_07/08/11/12/16/17/21/22`, `Weekend_07/09/11/12/16/17/21/22`, `Peak_Perio`, `Neighbourh`, `Street_Sid`, `BLOCK_STRE`, `SIGNTYPE`, `PARKING_TI`, `RESTRICTIO`, `Unit_Type`):

| Layer id | Name |
|---|---|
| 51 | Weekday: 7am to 9am |
| 52 | Weekday: 11am to 1pm |
| 53 | Weekday: 4pm to 6pm |
| 54 | Weekday: 9pm to 11pm |
| 55 | Weekend: 7am to 9am |
| 56 | Weekend: 11am to 1pm |
| 57 | Weekend: 4pm to 6pm |
| 58 | Weekend: 9pm to 11pm |

Field aliases confirm the four periods: `Weekday_AM`, `Weekday_MD`, `Weekday_PM`, `Weekday_EVE` (and weekend equivalents).

**Recommended citation for this layer:** "On-street parking supply and occupancy observations, City of North Vancouver; parking inventory collected by Bunt & Associates, December 2022 and January/February 2023; published via CNV TransportMAP ArcGIS service (layer group created 2023-10-04)."
Winter (Dec–Feb) collection is a real seasonal caveat worth stating.

### 2b. The dataset behind the Apr 2025 Curb Access and Parking Plan (a LATER, separate survey)

**June and July 2024** — quoted verbatim from `cnv_curb_access_and_parking_plan_2025.pdf`, p.22:

> "staff undertook city-wide curb space data collection in **June and July 2024**. The purpose of parking occupancy counts is to determine the peak occupancy… At least one midday count (11 am to 3 pm) was undertaken for all usable curb space in the City. In areas with known high parking occupancy (Central and Lower Lonsdale), up to four counts were undertaken: during the midday and afternoon, both on weekdays and weekends."
> "Figure 8: Peak on-street parking occupancy, from **summer 2024** observations."

Same document also says the 2024 results "were benchmarked against existing years of occupancy data" — consistent with the 2022/23 Bunt inventory being an earlier wave.

Note the time-of-day periods differ (2024: midday 11am–3pm + afternoon; the GIS layer: 7–9am / 11am–1pm / 4–6pm / 9–11pm), which independently confirms the GIS layer is **not** the 2024 survey. The 2024 results are published only as a categorical map (Figure 8, three classes: >85%, 60–85%, <60%) — no machine-readable table was found.

---

## 3. VERDICT — Traffic signal timing data

## **REQUEST_REQUIRED**

CNV holds signal phasing and cycle-length data and will supply it on request to parties doing transportation studies, but does **not** publish any timing values anywhere public.

Direct evidence (quoted verbatim, `cnv_transportation_study_level1_guidelines.pdf`, p.6):
> "Intersections and accesses (geometric layout, intersection control devices ‐ **details on signal phasing and cycle lengths will be provided by the City**);"

And p.7:
> "Traffic count data (such as manual turning movement counts, hose counts or **count data uploaded from the traffic signals**) may be acquired from the City. In many cases the City's data may not be current or available…"

Supporting evidence that nothing numeric is published:
- **https://www.cnv.org/streets-transportation/traffic/traffic-signals** — describes coordination qualitatively only: "Coordination of traffic signals means that they all run the same cycle length, and each signal assigns a 'window' for each direction of travel… During peak periods such as the morning and evening rush hours, we try to keep this wait to a maximum of about a minute." **No cycle length, split, offset, walk interval or clearance interval is published.** Page also lists the 5 new right-turn-on-red restriction locations effective April 2025 (Westview SB at Larson; Bewicke SB at Marine; Forbes SB at 3rd; 3rd WB at Forbes; 13th WB at Lonsdale) and says the City "may adjust signal timing" at Westview/Larson.
- **GIS layer `TransportMAP/153 Traffic Signals`** (point layer) — full field list is asset-management only: `SIGNAL_TYPE, POLE_TYPE, NUM_PRIMARY_HEADS, NUM_SECONDARY_HEADS, NUM_TERTIARY_HEADS, PEDESTRIAN_HEADS, STREET_LIGHT, INSTALL_DATE, OWNER, FIRE_PRE_EMPTIVE, ADDRESS, …`. **No cycle length, phase, walk-interval or coordination-plan attribute exists.**
- https://www.cnv.org/streets-transportation/traffic — index page, no timing data.
- https://www.cnv.org/streets-transportation/traffic/traffic-calming — speed hump/speed bump petition policy only.
- No CNV signal-timing guideline document exists (the "Traffic Signal Timing Guidelines" and "Synchro Modelling Guidelines" that surface in search are the **City of Vancouver**'s, at vancouver.ca — a different municipality; do not use them for CNV).
- Contacts for a request: `eng@cnv.org` (signals/signs maintenance) and `transportation@cnv.org`.

**Recommended field for the pipeline:** `signal_timing_status = REQUEST_REQUIRED`.

---

## 4. VERDICT — Published pedestrian counts

**Verdict: essentially NOT_FOUND as a city-wide, dated, machine-readable dataset. What exists is fragmentary.**

What exists, in order of usefulness:

1. **Moodyville Area Transportation Study (Jan 2016), Fig. 43, PDF p.64 — "Pedestrian Volumes at Intersections on East 3rd Street – Lonsdale to Queensbury."** This is the only genuine published pedestrian count in CNV found. It is a **raster figure inside a PDF** — not machine-readable, would require manual transcription, covers only the East 3rd corridor, and reflects **2015 field data**. Companion vehicle TMCs, hourly profiles and LOS are on pp.21–24; block-level parking occupancy on p.25; ICBC 2002–2013 collision tables (624 collisions on E 3rd St, 150 of them within Moodyville; 279 of the 624 at Lonsdale Ave) on p.25.
2. **Walk CNV 2017** — has **no** pedestrian volume counts. Its "pedestrian" content is a **stated-preference/crowdsourced mapping survey** (365 respondents, 25 Jan–6 Mar 2017). The GIS layers named `…(Walk CNV 2017)` (ids 156, 160–166 in TransportMAP) are that survey's point/heatmap responses — "Great Places to Walk", "Infrastructure Issues", "Accessibility Issues", "Frequent Work/Shopping/Grocery/Restaurant/Recreation Destinations" — with fields `VisitID, Date_, MarkerType, Response1, Response2, Comment_, Question1, Question2, Latitude, Longitude`. **These are opinions, not counts.** They are machine-readable via ArcGIS REST query, and are legitimate as a *pedestrian-interest / destination proxy* if labelled as such.
3. **Cyclist counts (not pedestrian)** — `TransportMAP/26 VolumeOfCyclists Street Segment` and group `23 Cyclist Volume`: **10 street segments only**, fields `Street_Segment_Start_End, BMP_Type, Northbound_Southbound, Eastbound_Westbound` with values such as West 1st St (Hanes→Fell) 40,980 and West 3rd St (Mission→Forbes) 46,805. **No year/date attribute and no matching figure found in any CNV PDF — the period these totals represent is undocumented.** Treat as undated.
4. **Vehicle counts** — `TransportMAP/225 Traffic Volumes` with children `226 Northbound / 227 Southbound / 228 Eastbound / 229 Westbound`: **11 segments only**, single value field (e.g. Northbound = 613, 720, 602, 306, 272). Again **no date attribute** and no source document found. Treat as undated and inadequate for city-wide traffic analysis.
5. **Transit activity (a strong pedestrian proxy)** — `TransportMAP/121 Bus Stops` (under the "Transit Ridership" group) carries `Average_Passenger_LLS, trip_count, Trips_per_Hour, Riders_per_hour, Rideship_per_hour_factored` per stop. Undated but machine-readable and stop-level; the best available boarding-activity proxy inside CNV data.
6. **Sidewalk network / gaps** — `TransportMAP/69 Missing Sidewalks` (and 68 "Natural Barriers"), abstract: "Data originally provided by **Urban Systems** consultants… to enable update of a sidewalk priority layer." Plus `130 Sidewalk Segments`, `129 Sidewalk Ramps`, `70 Pedestrian Areas`, `71 School Routes`. Infrastructure, not counts.
7. **North Shore Transportation Survey (2019/2020/2021/2023)** — modelled daily trip volumes by mode for CNV as a whole (e.g. 37,250 daily walk trips in 2023). City-wide totals only; **no geography below the municipality**, so unusable for intersection-level analysis.

**Bottom line:** CNV publishes **no** pedestrian count program, no counter feed, no intersection count database, and no open-data traffic/pedestrian count downloads. Per the Level 1 TS Guidelines, pedestrian crossing volumes are collected **by developers' consultants** case-by-case and submitted to the City — meaning the counts exist inside individual development-application transportation studies, not in any central public dataset. A pedestrian-activity **proxy** is therefore required, and must be labelled as a proxy.

---

## 5. GIS / open data findings (task 4)

CNV has **no** ArcGIS Hub / Socrata / CKAN open-data portal. Its public GIS is an ArcGIS Server at
**`https://gisext2.cnv.org/arcgis/rest/services`** (ArcGIS Server 10.81), folders: `Applications`, `BaseMapServices`, `BaseMapTools`, `FeatureServices`, `Utilities`.

**`BaseMapServices/TransportMAP/MapServer` is the single most valuable endpoint for this project — 230 layers + 1 table.** Transportation-relevant layers not previously enumerated:

- Roads/streets: `123 Streets` group → `124 Bridges`, `125 CNV Streetlights`, `126 Lane Segments`, **`127 Road Classifications`**, `128 Road Markings`, `129 Sidewalk Ramps`, `130 Sidewalk Segments`, **`131 Street Segments`**, `132 Streetscape Guideline Areas`, `133 Street Trees`
- Traffic: `147 Traffic` group → `148 One Way Streets`, **`149 Speed Zones`**, **`150 Traffic Calming Pts`** (fields incl. `FEATURE_SUBTYPE, INSTALL_DATE, RAISED_FEATURE, BLOCK_STREET`), `151 Traffic Calming`, `152 Traffic Signs`, **`153 Traffic Signals`**, `154 Truck Routes`
- OCP transport: `47 OCP Transportation Network` → `48 Road Designation`, `49 Major Road Network`
- Parking: `50 Parking - Occupancy` (51–58 as above); `59 Parking - Streets` → `60 Car Share Parking`, **`61 Loading Zones`**, **`62 Off Street Lots`**, **`63 Parking Signs`**, **`64 Parking Zones`**, `65 Resident Parking Street`, `66 Resident Parking Zone`
- Pedestrians: `67 Pedestrians` → `69 Missing Sidewalks`, `70 Pedestrian Areas`, `71 School Routes`
- Cycling: `18 Cycling` → `19 Bike Racks`, `20 Bike Routes (AAA)`, `21 Bike Routes (BMP)`, `22 Bike Routes (Existing)`, `23–26 Cyclist Volume`
- Transit: `105 Public Transit` → `106 Bus Routes`, `107 Bus Shelters`, `108 Bus Stops`, `109 Rapid Transit`, `110 Transit Ridership` → `121 Bus Stops` (ridership fields), `122 Bus Stop Segment`, `157 B-Line Rapid Bus`
- Vehicles: `222 Vehicles` → `223 Passenger Vehicles per 2021 Capita`, `224 Passenger Vehicles per 2021 Private Dwelling`, table `230 PASSENGER_PERC_BY_DBUID_2021`
- Census (already partly known): `8–17` DB-level 2016/2021 population, `11 2021 Population By Parcel`, `12 2021 vs 2016 Pop Change(DB)`, `89 Neighbourhoods`, `91 Transport Oriented Area`
- Buildings: `4 Buildings`, `6 High Rise Buildings(>18m)`, `85 Heritage Register Buildings`
- Policy: `167 Mobility Strategy - Street Types`, `155 Transportation Projects`

Other services: `Applications/curbaccessparking` and `curbaccessparking2` (layers `Extent`, `ParkingZones`, `ParkingZones_25K` — the *proposed/implemented* curb management zones, distinct from the occupancy layers); `Applications/accessibleparking`, `pparking` (pay parking), `ResidentPermitParking`, `ResidentExemptParking`, `Taxi_Ridehailing`, `TransitPM`, `TransitPM_L2`, `RoadworksAndConstruction`, `SnowRemoval`. `BaseMapServices/CityMapPro` and `StaffMap` are the general basemaps; `BaseMapTools/cnv_geocoder` and `street_CentreLine_Locator` are **GeocodeServers usable for geocoding voting-place addresses** (relevant to the elections component of this project).

Caveats: several layers are labelled "(Placeholder)" and are empty/incomplete (`5 Building Age`, `7 Number building units`, `68 Natural Barriers`, `90 Pivotal Development Sites`, `158 CNV Transport Ideas`, `159 Dominant Travel Patterns`, `168 Transportation Study Areas`). Most layers carry empty ISO abstracts, so provenance/date is unknown for the majority — the parking-occupancy abstract is the exception, not the rule.

---

## 6. Searched and NOT found

- **A standalone CNV parking study/technical report by Bunt & Associates.** The report itself is not published on cnv.org. Only the derived GIS layer and the summarised Curb Access & Parking Plan are public. The Bunt attribution survives only in the ArcGIS layer metadata. → Gap entry recommended.
- **City of North Vancouver Network Screening Study (2016)** — cited twice as a footnote in the Safe Mobility Strategy (2020); the document itself is not published anywhere on cnv.org. → Gap entry recommended (this is the City's road-safety collision analysis).
- **Any "annual safe mobility status report"** promised by the 2020 Safe Mobility Strategy. No such published report was found on cnv.org.
- **Traffic signal timing values of any kind** — cycle length, splits, offsets, walk interval, flashing don't walk / clearance interval, time-of-day plans, coordination plans. Checked: `/streets-transportation/traffic`, `/streets-transportation/traffic/traffic-signals`, `/streets-transportation/traffic/traffic-calming`, `/streets-transportation/transportation-planning`, `/streets-transportation/mobility-strategy`, the ArcGIS `Traffic Signals` layer schema, LTTP 2008, Mobility Strategy 2022, Walk CNV 2017, Safe Mobility Strategy 2020. Nothing numeric anywhere.
- **A published CNV pedestrian or cyclist count program** (permanent counters, annual screenline counts, intersection count database). None exists. The `Cyclist Volume` and `Traffic Volumes` GIS layers are tiny (10 and 11 segments) and undated.
- **Machine-readable traffic/pedestrian count downloads (CSV/JSON) on cnv.org.** None. CNV has no open-data catalogue.
- **`letstalk.cnv.org/curb` documents widget** — returns HTTP 403 to automated fetching and the documents listing could not be enumerated; a direct document-id URL returned 404. Not pursued further (no attempt to circumvent). Its content appears to be duplicated on the cnv.org Curb Access & Parking page, which was fully enumerated.
- **A "Walk CNV" final Pedestrian Plan** distinct from the 2019 Framework. The 2017 report said the process would "be completed in Fall 2017 with the development of the final Plan"; what was actually published is the Dec 2019 *Framework*. No fuller plan document was found.
- **A neighbourhood traffic calming plan with counts.** Only the 2004 program/petition policy document exists; the "Cloverley Neighbourhood Traffic Calming" and other named projects have project webpages but no posted technical reports with count data.
- **Waterfront Transportation Network Study documents** — the project page (now under Past Projects) contains no document links.
- **CNV council agenda/minutes full-text search** — `cnvapps.cnv.org` hosts a Council Minutes search (minutes back to 1907); agenda *packages* are individual PDFs under `.../Documents/Council-Meeting-Agenda/<year>/`. No index of transportation staff reports containing count data was found via search engines; only the individual reports linked from topic pages (all captured above) were retrievable. Exhaustively mining agenda packages was out of reach for this pass and would be the next step if more count data is needed.

---

## 7. Suggested DATA_GAPS.md entries arising from this research

1. `signal_timing_status = REQUEST_REQUIRED` — CNV holds phasing/cycle lengths and releases them to transportation-study consultants (Level 1 TS Guidelines p.6); nothing is published. Next action: written request to `transportation@cnv.org` / `eng@cnv.org`. Do **not** estimate cycle times; do **not** claim any intersection has the "longest light".
2. `pedestrian_counts = NOT_FOUND (city-wide)` — only source is Moodyville 2016 Fig.43 (E 3rd St corridor, 2015 data, raster figure in PDF). Best available proxy: transit ridership per stop (TransportMAP/121) + Walk CNV 2017 crowdsourced destination/issue points + population/employment density + intersection density. Label as `pedestrian_activity_proxy`, never `pedestrian_counts`.
3. `parking_occupancy_vintage` — GIS layer = Bunt & Associates, **Dec 2022 + Jan/Feb 2023** (winter); the Apr 2025 Curb Access and Parking Plan is based on a **different, later June–July 2024** survey published only as a 3-class map. Do not present the GIS layer as current or as the Plan's data.
4. `network_screening_study_2016 = NOT_PUBLISHED` — cited in Safe Mobility Strategy 2020; request from City or fall back to ICBC published crash data.
5. `traffic_volumes_cnv_gis = UNDATED` — the 11-segment `Traffic Volumes` and 10-segment `Cyclist Volume` layers carry no date attribute and no traceable source document. Use only with an explicit "vintage unknown" flag, or prefer BC MoTI traffic data program stations.
