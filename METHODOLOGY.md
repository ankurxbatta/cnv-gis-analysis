# METHODOLOGY.md — City of North Vancouver GIS Analysis

Every derived metric, its formula, its assumptions and its known limitations.

---

## 1. Study area and coordinate reference systems

| Purpose | CRS | Rationale |
|---|---|---|
| Analysis (all areas, lengths, densities, buffers) | **EPSG:26910** NAD83 / UTM 10N | Native CRS of the CNV ArcGIS server; metre-based, so no reprojection round-trip on the largest layers |
| Provincial/regional joins | EPSG:3005 NAD83 / BC Albers | Standard for province-wide BC data |
| Web export only | EPSG:4326 WGS 84 | Leaflet/web mapping |
| StatCan boundary files as shipped | EPSG:3347 Lambert | Reprojected to the analysis CRS on load |

**No area or distance is ever computed in degrees.** A QA test asserts every processed
layer is in EPSG:26910.

### Land area versus legal boundary

The BC ABMS legal boundary encloses **14.92 km²** because it extends into Burrard Inlet.
Statistics Canada reports CNV's **land area as 11.83 km²**; the 79 constituent dissemination
areas sum to **11.79 km²**.

**All density denominators use StatCan land area.** Using the legal boundary would
understate density by ~26%. The legal boundary is used only for clipping and cartography.
A QA test enforces this.

---

## 2. Census extraction

### Source selection
The BC-only dissemination-area Census Profile (`98-401-X2021006`, `GEONO=006_BC_CB`,
293 MB compressed / 3.6 GB uncompressed) is used in preference to the 2.2 GB national file.

### Cartographic versus Digital boundary files — a decision that changes the maps

Statistics Canada ships every boundary in two variants that cover the same areas with the
same IDs but differ at the water's edge:

| | Digital (DBF) | Cartographic (CBF) |
|---|---|---|
| Filename flag | `lda_000**a**21a_e.zip` | `lda_000**b**21a_e.zip` |
| Coastal edge | extends into water to the territorial limit | clipped to the shoreline |

**This pipeline uses the Cartographic file.** Measured directly for CNV's 79 DAs:

```
Cartographic (CBF) : 11.852 km²
Digital      (DBF) : 17.214 km²
water included     : +5.363 km²  (+45.2%)
```

CNV fronts Burrard Inlet, so the Digital file pushes waterfront DAs out into the harbour —
DA 59153241 grows 0.88 → 3.43 km² (3.9x), DA 59150200 grows 1.31 → 3.75 km² (2.9x).

Because density is population / area, using the Digital file would have understated density
by up to **74%** in exactly the densest places:

| DA | Correct | With Digital | Error |
|---|---|---|---|
| 59153970 | 10,837 /km² | 3,850 /km² | 64% understated |
| 59153241 | 2,846 /km² | 729 /km² | 74% understated |
| 59150200 | 927 /km² | 324 /km² | 65% understated |

DA 59153970 is Lower Lonsdale waterfront, one of the densest blocks in the city; the Digital
file would have rendered it below average and demoted it in every ranking.

Note there are therefore **three** defensible "areas" for CNV — legal 14.92 km² (BC ABMS,
includes foreshore), digital census 17.21 km², cartographic census 11.85 km². Every density
here divides by StatCan's published `LANDAREA` attribute (11.79 km²), enforced by a test.

### Seeking rather than parsing
Statistics Canada ships a `Geo_starting_row` index giving the first line number of each
geography's 2,631-row block. The pipeline reads that index, computes the line ranges for the
79 CNV DAs, and parses only those lines — about 10 seconds instead of a full 3.6 GB parse.

**Verification:** every extracted row's `ALT_GEO_CODE` is compared against the DAUID the
index predicted. Any mismatch aborts the run. This check caught an off-by-one error at the
block boundary (line `start + 2631` belongs to the *next* geography).

### Determining which DAs are in CNV
The cartographic DA file carries no `CSDUID`, so DA membership is determined by
**representative-point containment** within the CNV census subdivision polygon
(`CSDUID = 5915051`). DAs nest exactly within CSDs in StatCan geography, so this is exact
rather than approximate. Result: 79 DAs.

### Reconciliation
| Measure | DA sum | Published CSD | Difference |
|---|---|---|---|
| Population 2021 | 58,120 | 58,120 | **0** |
| Occupied private dwellings | 27,293 | 27,293 | **0** |
| Canadian citizens 18+ | 41,130 | 41,125 | +5 (random rounding) |
| Seniors 65+ | 10,180 | 10,190 | −10 (random rounding) |
| Land area (km²) | 11.79 | 11.83 | −0.04 (cartographic generalisation) |

Statistics Canada applies random rounding to base 5, so small discrepancies are expected
and are not errors.

---

## 3. Derived population measures

### The 18+ proxy

The Census publishes ages 15–19 as a single band. Ages 18–19 are apportioned as two-fifths
of that band under a **uniform-age-within-band assumption**:

```
age_18_19_estimated          = age_15_19 × (2/5)
adult_population_18plus_proxy = population_2021 − age_0_14 − age_15_19 + age_18_19_estimated
                              = population_2021 − age_0_14 − (3/5 × age_15_19)
```

City-wide result: **49,248**.

### The citizenship measure

`canadian_citizens_18plus` is taken directly from Census characteristic 1525 with no
interpolation. City-wide: **41,130**.

Because BC municipal elections require Canadian citizenship, residency and age 18+, this is
materially closer to elector eligibility than the raw 18+ figure. It lands within **0.5%**
of the 41,325 registered electors CNV recorded in 2022.

**This is a consistency check, not an equivalence.** The citizenship variable is 25% sample
data covering population in private households only; the registered-elector count is an
administrative list from a different year. Neither is called "eligible voters" anywhere.

### Densities

```
population_density        = population_2021                   / land_area_km2
adult_population_density  = adult_population_18plus_proxy      / land_area_km2
senior_density            = senior_population_65plus           / land_area_km2
housing_density           = occupied_private_dwellings         / land_area_km2
citizen_adult_density     = canadian_citizens_18plus           / land_area_km2
```

### Housing shares

```
multiunit_dwellings = dw_row_house + dw_apartment_duplex
                    + dw_apartment_lt5_storeys + dw_apartment_5plus_storeys
multiunit_share     = multiunit_dwellings              / dwellings_by_structure_total
apartment_share     = (lt5 + 5plus)                    / dwellings_by_structure_total
highrise_share      = dw_apartment_5plus_storeys       / dwellings_by_structure_total
townhouse_share     = dw_row_house                     / dwellings_by_structure_total
single_family_share = dw_single_detached               / dwellings_by_structure_total
```

---

## 4. Neighbourhood aggregation

CNV neighbourhood boundaries and StatCan DA boundaries do not align, so neighbourhood
figures are **areally interpolated**:

```
for each neighbourhood N and dissemination area D:
    fraction = area(D ∩ N) / area(D)
    contribution = count(D) × fraction
```

This assumes population is **uniformly distributed within each DA**. Results are labelled
estimates, never counts. Interpolated totals recover **99.8%** of the city population
(57,998 of 58,120), the shortfall being DA slivers outside any neighbourhood polygon (the
neighbourhood layer covers 89.7% of the legal municipal area, largely because it excludes
water).

---

## 5. Intersection derivation

1. Extract the first and last coordinate of every street-centreline segment (1,882
   endpoints from 941 segments).
2. Snap endpoints to a grid of `intersection_snap_tolerance_m` = **5 m**, then union
   neighbouring cells so near-coincident endpoints merge into one node (654 nodes).
3. A node qualifies as an intersection when it joins **two or more distinct street names**
   or **three or more segment ends**. The second condition captures forks and
   continuations that a name test alone would miss.
4. Keep only nodes inside the municipal boundary.

Result: **503 intersections**.

### External validation
The District of North Vancouver publishes an independent `TrnIntersection` layer covering
the North Shore; 501 of its points fall inside CNV. **459 of the 503 derived intersections
(91%) lie within 25 m of one of them.** The residual reflects genuine methodological
differences (private/strata roads, ramp treatment) rather than error.

Street names are built as `SUF_DIR + STREET_NAME + STREET_TYPE` (e.g. `E 3RD ST`) so that
name-based joins against external sources such as ICBC can succeed.

---

## 6. Signalised intersections

The CNV traffic signal layer is a **pole/asset inventory** (569 assets inside CNV), not a
list of intersections, and its `INT_UNITID` intersection key is **empty for every record**.
Assets are therefore clustered spatially: each asset is buffered by
`signal_cluster_distance_m / 2` = 20 m, the buffers are unioned, and connected components
become signal groups.

Result: **133 signalised locations**, of which **79** contain at least one `Full Signal`
asset and **54** are pedestrian-signal or special-crosswalk only. Preserving `SIGNAL_TYPE`
matters: treating a pedestrian crossing beacon as a signalised intersection would inflate
the count by 68%.

**Signal timing is never estimated.** `signal_timing_status = REQUEST_REQUIRED` on every
location, because CNV's own transportation-study guidelines confirm the City holds phasing
and cycle lengths and releases them on request but publishes no values.

---

## 7. Parking occupancy

The City's on-street layer pairs an **occupied-vehicle count** with a **published
percentage** for each of eight surveyed periods, but field naming is inconsistent between
weekday and weekend blocks (weekday periods are labelled by start hour, weekend by end
hour). The pipeline detects which column of each pair is numeric (the count) and which is a
`%` string (the percentage), rather than assuming an order.

**Validation.** Recomputed `count / Supply` is compared against the City's published
percentage. Agreement is **99.8–100%** across all eight periods at a tolerance of one
vehicle on that segment's own supply plus two percentage points. The looser tolerance is
necessary because `Supply` is a small integer estimate of a continuous kerb capacity: on a
3-space segment, one vehicle is 33 percentage points.

**The City's published percentage is used as authoritative**; the recomputed ratio is
retained as `occupancy_recomputed_*` for audit.

```
occupancy_peak = max(occupancy over the eight surveyed periods)
at_practical_capacity = occupancy_peak ≥ 0.85
```

Occupancy above 100% is **retained, not clipped** — 314 segments exceed their estimated
supply at some period, which is real information about capacity estimation.

**Provenance:** fieldwork by Bunt & Associates, December 2022 and January–February 2023, for
the CNV Curb Access and Parking Plan. **Not a real-time feed.**

---

## 8. Collision matching

ICBC publishes crash counts against **location name strings with no coordinates**, and its
`NORTH VANCOUVER` municipality value covers **both the City and the District**. Matching is
therefore name-based and deliberately conservative:

1. Split the location string on `&` and normalise each part (suffix and direction
   abbreviations unified: `AVENUE`→`AVE`, `EAST`→`E`, …).
2. Discard non-street tokens (`OFFRAMP`, `ONRAMP`, `BUS LANE`, `TURNING LANE`).
3. Require **at least two** of the named streets to be CNV street names.
4. Require that pair to correspond to an intersection **actually present** in the derived
   CNV intersection layer. This is the decisive test — a coincidental pair of CNV street
   names that do not cross in CNV is rejected.
5. Records that also name non-CNV streets (typically Highway 1 ramps) are matched but
   flagged `match_confidence = medium`.

**Result:** 288 of 2,218 records matched, covering 5,296 crashes across 288 of 503
intersections (57%). All 1,930 unmatched records are retained with reasons in
`outputs/tables/icbc_unmatched_locations.csv`.

**Unmatched intersections are `NaN`, never zero.** Scoring them as zero would rank
data-poor intersections as the safest in the city. A QA test enforces this.

---

## 9. Transit frequency

A representative weekday is chosen from the GTFS `calendar` (a Wednesday inside the feed's
active window), with `calendar_dates` exceptions applied. `stop_times.txt` is streamed in
chunks and filtered to stops within the buffered boundary and trips running that day.

```
trips_per_weekday        = scheduled departures at the stop that day
trips_am_peak            = departures 07:00–09:00
am_peak_avg_headway_min  = 120 / trips_am_peak
```

GTFS times exceeding 24:00:00 (post-midnight trips) are parsed correctly rather than
discarded. Result: 172 stops inside CNV, 15,961 scheduled weekday departures, 15 routes.

An **edge-context buffer** of 500 m is applied when selecting regional data so that
intersections near the municipal boundary are not starved of nearby stops. All reported
statistics remain clipped to the city.

---

## 10. Buffer measures at intersections

Counts and sums within 100 m / 250 m / 400 m of each intersection. Population is areally
interpolated from DA polygons into the buffer using the same fraction-of-area method as
neighbourhood aggregation, with the same uniform-distribution assumption recorded on the
output.

Traffic volumes are associated to an intersection only within
`traffic_station_association_max_m` = **150 m**, and `traffic_volume_available` records
whether any volume was found. Only 40 of 503 intersections qualify.

---

## 11. Public-space suitability score

A **neutral** measure of visibility, access and feasibility. It contains **no political
variable** — no party, candidate, voting history, or inference from demographics to
political preference. Population inputs measure only how many people are physically nearby.
A QA test asserts no political field exists in the output.

### Normalisation
Each input is converted to a **percentile rank scaled 0–100**, not min-max, so a single
extreme value cannot dominate. `NaN` inputs stay `NaN` and are excluded from that row's
weighted mean rather than being treated as zero, and the remaining weights are renormalised
so a row with one missing input is not silently penalised.

### Components

| Component | Inputs (weight) | Coverage |
|---|---|---|
| `traffic_score` | road class (0.70), nearest measured volume (0.30) | 100% (but volume only 8%) |
| `transit_score` | departures 250 m (0.60), stops 250 m (0.25), AM peak departures (0.15) | 100% |
| `pedestrian_proxy_score` | population 400 m (0.30), commercial area 250 m (0.25), transit departures (0.20), walkway length (0.15), ramps 100 m (0.10) | 100% (all proxy) |
| `parking_access_score` | on-street supply (0.45), off-street spaces (0.30), peak occupancy **inverted** (0.25) | 100% |
| `intersection_prominence_score` | leg count (0.40), distinct names (0.20), max lanes (0.20), signalised (0.20) | 100% |
| `safety_score` | collision count **inverted** (1.00) | **57%** |
| `visibility_score` | leg count (0.35), max lanes (0.35), commercial area (0.30) | 100% (proxy) |

Inverted inputs mean "higher is better" consistently: more collisions lowers
`safety_score`; higher observed parking occupancy lowers `parking_access_score`.

### Composite

```
public_space_composite = mean(available components)
```

Unweighted, so no dimension silently dominates. `components_available` records how many
components contributed. **The composite is a convenience summary, not ground truth** — the
components measure different things on different evidence bases and are reported
separately.

### What this score is not
It is **not** a measured traffic ranking (road class dominates), **not** a pedestrian count
(the pedestrian component is entirely proxy), and **not** a complete safety ranking (43% of
intersections have no collision data).

---

## 12. Building classification

Evidence-based, with the evidence recorded in `classification_basis` on every feature.
Order of precedence:

1. **Seniors** — affordable-housing `Eligibility` containing `55+`/`65+`/`senior`, or
   `Occupancy` containing independent/assisted living/care, or a seniors keyword in the
   building name.
2. **Institutional** — school, church, hospital, library, city hall, recreation, fire hall,
   police, arena, museum keywords.
3. **Occupancy attribute** — the City's own statement of use (`STRATA APT - HI-RISE`,
   `APT-CONCRETE HI-RISE`, `CLASS A OFFICE`, `REGIONAL SHOPPING CENTRE`, …).
4. **Published height** ≥ 18 m → high-rise (storeys approximated at 3.0 m/storey, stated
   explicitly wherever used).
5. **Unit counts** — ≥5 low-rise apartment, 2–4 townhouse/row, 1 single-family.
6. Otherwise **UNKNOWN**.

**`UNKNOWN` means the City publishes nothing about that footprint — not that the building
is non-residential.** 98.6% of footprints are UNKNOWN, which is an honest statement about
CNV's published attribute coverage (height 0.9%, units 0.7%, year built 0.9%).

**Condominium tenure is set only where the City's `Occupancy` attribute contains `STRATA`.**
It is never inferred from building form, height or apartment status.

---

## 13. Statistical treatment

- Rankings use quantiles and percentile ranks; choropleths use quantile classification.
- Distributions are reported with min / 10th / 25th / median / 75th / 90th / max.
- **Spatial correlation is never presented as causation.** No causal claim is made anywhere
  in the outputs.
- Where a measure is an estimate (areal interpolation, the 18+ apportionment, storey
  approximation), the output layer carries a field saying so.

---

## 14. Reproducibility

Raw downloads are cached with SHA256 hashes and never overwritten without `--force`, so
re-runs are deterministic given stable upstream sources. The pipeline stops at the first
failing stage rather than feeding bad data downstream. `python -m pytest` runs 110 QA checks
covering CRS, geometry, identifiers, population plausibility, spatial containment,
provenance metadata, and the privacy and terminology constraints.
