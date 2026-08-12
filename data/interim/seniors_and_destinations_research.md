# Seniors Residences & Civic Destinations — City of North Vancouver (CNV)

Research date: **2026-08-12**
Study area: **City of North Vancouver (CSD 5915051)** — explicitly NOT the District of North Vancouver.

---

## 0. Method for City-vs-District determination (the "North Vancouver, BC" trap)

Every facility below was classified using **two independent authoritative tests**, not by postal address or
street-name guessing:

1. **Point-in-polygon** against `data/processed/cnv_boundary.gpkg` (layer `cnv_boundary`, BC ABMS
   municipal boundary), using the LATITUDE/LONGITUDE published in the provincial registry CSVs,
   reprojected to EPSG:26910. Distance-to-boundary was computed for every candidate so that
   near-boundary cases are visible rather than silently decided.
2. **CNV legal parcel address lookup** against `data/raw/cnv/cnv_legal_parcels.geojson`
   (fields `ADDRESS` / `ADDR_RNG`). The City's own parcel fabric is the authoritative CNV civic-address
   register: if an address has no CNV parcel, it is not a City address.

Both tests agreed on **every** case. Borderline results are documented in §1.3.

---

## 1. Seniors facilities

### 1.1 Licensed / registered seniors care facilities INSIDE the City of North Vancouver

> **Headline finding:** the provincial registries contain **zero** registered *assisted living* residences
> and **zero** *Residential Care Regulation*–licensed *long-term care* homes inside the City of North Vancouver.
> All North Shore licensed LTC and registered AL capacity in the "North Vancouver" postal area sits in the
> **District**. The City's only large seniors care facility, **Evergreen House**, is hospital-based and
> therefore falls outside the licensing registry (see §1.2).

| Name | Address | Type | Operator | Units / beds | City vs District | Confidence | Source |
|---|---|---|---|---|---|---|---|
| Evergreen House – Lions Gate Hospital | 231 E 15th St | Long-term care (hospital-based, Hospital Act) | Vancouver Coastal Health | **284 publicly funded beds** | **CITY** | High | [OSA Quick Facts 82112](https://www.seniorsadvocatebc.ca/quickfacts/location/82112/); [VCH](https://www.vch.ca/en/lions-gate-hospital-lgh/evergreen-house) |
| Summerhill PARC Retirement Living | 135 W 15th St | Independent living (private pay, unlicensed) | PARC Retirement Living | not published | **CITY** | High (location); Medium (unit count unavailable) | [parcliving.ca](https://parcliving.ca/summerhill-parc/) |
| Sunrise at Lonsdale Square | 2141 Eastern Ave | Private-pay long-term care + memory care | Sunrise Senior Living | not published | **CITY** | High (location); **Low (registry discrepancy — see note)** | [sunriseseniorliving.ca](https://www.sunriseseniorliving.ca/communities/bc/sunrise-at-lonsdale-square); [NV Chamber](https://business.nvchamber.ca/list/member/sunrise-senior-living-lonsdale-square-9789) |
| North Shore Hospice | 319 E 14th St | Hospice (licensed residential care) | Vancouver Coastal Health | 15 (hospice max capacity) | **CITY** | High | BC Residential Care Facilities CSV |

**Notes on the three uncertain entries**

- **Summerhill PARC** — 135 W 15th St is not its own CNV parcel but falls inside CNV parcel
  `133 W 15th St` (`ADDR_RNG` = *133–141 W 15th St*), which is inside the boundary. City status: confirmed.
  Suite count is **not published** by the operator; I did not estimate one.
- **Sunrise at Lonsdale Square** — 2141 Eastern Ave is a confirmed CNV parcel (2,664 m², inside boundary).
  **However it does NOT appear in either provincial registry CSV downloaded 2026-08-12**, despite being
  marketed as "licensed long-term care and memory care". There are two Eastern Avenues in the North
  Vancouver postal area; the CNV one carries civic numbers 1536–2832, and 2141 is present. Location is solid;
  the **licensing/registry status is unresolved** and bed counts are not published. Do not assign a bed count.
- **North Shore Hospice** — licensed under the Residential Care Regulation as hospice, not seniors housing.
  Included because it is a seniors-relevant institutional destination adjacent to the LGH campus.

### 1.2 Why the registries show no LTC/assisted living in the City

Facilities operating **within a hospital** under the *Hospital Act* (Evergreen House, 284 beds) are **not**
licensed under the *Community Care and Assisted Living Act* / *Residential Care Regulation*, so they are
absent from the BC Data Catalogue registries. Relying on those CSVs alone would have produced the false
conclusion that the City has no long-term care capacity at all. This is a documented methodological trap
worth carrying into `DATA_GAPS.md`.

**Independent corroboration** — BC Housing *Non-market Housing (2025)*, local-government level:

| Service allocation subgroup | North Vancouver **City** | North Vancouver **DM** (District) |
|---|---|---|
| Supportive Seniors Housing (assisted living) | **0** | 91 |
| Independent Seniors | **164** | 521 |
| Rent Assist – Seniors (private market supplement) | **465** | (suppressed, "XX") |
| Special Needs | 111 | 92 |
| Low Income Families | 196 | 232 |
| **Local government total** | **1,210** | **1,231** |

The City's **0** BC Housing-administered supportive-seniors-housing units independently confirms the
Assisted Living Registry result. The City's seniors provision is overwhelmingly **independent / subsidized
rental** (164 units) plus **rent supplements** (465), not congregate care.

### 1.3 Licensed residential care facilities in the City (all types, incl. non-seniors)

For completeness — these are all Residential Care Regulation facilities whose registry coordinates fall inside
the CNV boundary. Most are small community-living or mental-health group homes, **not seniors housing**.
All confirmed against CNV parcels.

| Name | Address | Care type | Operator | Max capacity | Confidence |
|---|---|---|---|---|---|
| North Shore Hospice | 319 E 14th St | Hospice | Vancouver Coastal Health | 15 | High |
| Boulevard House | 1053 Grand Blvd | Mental health | Marineview Housing Society | 10 | High |
| Cloverley House | 1057 Cloverley St | Mental health | Marineview Housing Society | 10 | High |
| Magnolia House | 720 E 17th St | Mental health | Vancouver Coastal Health | 7 | High |
| Lillian House | 167 E 27th St | Mental health | CMHA North & West Vancouver | 7 | High |
| C & E Home | 1818 Westview Dr | Mental health | C & E Home Care Inc. | 6 | High |
| Larson House | 1945 Larson Rd | Community living | North Shore Connexions Society | 5 | High |
| Wilding Way | 2412 Wilding Way | Community living | North Shore Disability Resource Society | 4 | High |
| Padwick House | 1924 Jones Ave | Community living | North Shore Connexions Society | 4 | High |
| Bridgit House | 229 W 22nd St | Community living | Helios Learning Point Society | 4 | High |
| Kaspar House | 325 W 19th St | Community living | Cascadia Society for Social Working | 4 | High |
| East Keith Road House | 317 E Keith Rd | Community living | Community Living Society | 3 | High |

### 1.4 Near-boundary facilities correctly excluded (DISTRICT, not City)

These are the real traps — all carry a "North Vancouver, BC" mailing address but are outside the City.
Distance = metres from the CNV boundary.

| Name | Address | Type | Beds/units | Dist. from CNV boundary | Parcel test | Verdict |
|---|---|---|---|---|---|---|
| Churchill House (Chartwell) | 150 W 29th St | Assisted living (seniors) | 31 public + 28 private pay | **54 m outside** | No CNV parcel; CNV has 121 W 29th St only (boundary runs along 29th St) | **DISTRICT** |
| Cedar Garden Assisted Living | 1250 Cedar Village Close | Assisted living (seniors) | 30 public | 70 m outside | No CNV parcels on that street | **DISTRICT** |
| Cedarview Lodge | 1200 Cedar Village Close | Long-term care | 89 | 51 m outside | No CNV parcels on that street | **DISTRICT** |
| Parkview House | 990 E Keith Rd | Mental health | 6 | 26 m outside | CNV E Keith Rd numbers stop in the 300s | **DISTRICT** |
| 1220 East 14th | 1220 E 14th St | Community living | 4 | 41 m outside | CNV E 14th St numbers stop in the 300s | **DISTRICT** |
| Berkley Care Centre | 2444 Burr Pl | Long-term care | 189 | outside | — | **DISTRICT** |
| Creekstone Care Centre | 1526 Oxford St | Long-term care | 180 | 511 m outside | — | **DISTRICT** |
| Lynn Valley Care Centre | 1070 Lynn Valley Rd | Long-term care | 92 | outside | — | **DISTRICT** |
| Lynn Valley House | 1070 Lynn Valley Rd | Assisted living | 4 private pay | outside | — | **DISTRICT** |
| Sunrise of Lynn Valley | 980 Lynn Valley Rd | Long-term care | 114 | 423 m outside | — | **DISTRICT** |
| Amica at Edgemont Village | 3225 Highland Blvd | LTC 40 / AL 98 private pay | 40 + 98 | outside | — | **DISTRICT** |
| Lookout Dovercourt | 1606 Lynn Valley Rd | Supportive recovery | 19 public | outside | — | **DISTRICT** |
| Norgate Xwemélch'stn Elementary | 1295 Sowden St | (school, listed for reference) | — | outside | No "Sowden" street in CNV parcels | **DISTRICT** |

Also excluded (all District, community-living group homes ≤7 beds): Maginnis Ave, Edgemont House,
Coleman St, Carnation House, Windridge House, Walpole House, Plymouth House, Shone House, Barlynn House,
Khyaht Ayahm, Paisley House, Trillium House, Newmarket Dr, Kilmer House, Blueridge House, Lynn Valley House,
Loraine Ave, Frederick Rd, Norwood House, Peters Rd House, Nancy Greene Way, Mt Seymour Pkwy House,
Capilano House, Kerrstead Place, Arborlynn House, Harold House, Turning Point (Burr Pl & Lloyd Ave).

### 1.5 Subsidized seniors-eligible housing already in the CNV Affordable Housing layer

12 of the 59 sites carry **55+** eligibility, totalling **727 units** — see §4.

---

## 2. Civic destinations (pedestrian-activity anchors)

All rows below were derived from the **City of North Vancouver's own GIS**: the `BUILDING_NAME` attribute of
`data/raw/cnv/cnv_buildings.geojson` (107 named buildings), spatially joined to `cnv_legal_parcels.geojson`
for the civic address and tested against the CNV boundary. **Addresses are CNV parcel values, not invented.**
This is a stronger provenance chain than a web-scraped address list.

### 2.1 Civic / government

| Name | Category | Address | Source |
|---|---|---|---|
| City Hall | Municipal government | 141 W 14th St | CNV buildings + parcels |
| North Vancouver City Library | Library | **120 W 14th St** (on CNV parcel 141 W 14th St) | [nvcl.ca](https://www.nvcl.ca/hours-and-locations); CNV GIS |
| Gerry Brewer Building (City offices) | Municipal government | 147 E 14th St | CNV buildings + parcels |
| Court House | Provincial court | 200 E 23rd St | CNV buildings + parcels |
| Fire Hall | Emergency services | 165 E 13th St | CNV buildings + parcels |
| City Operations Centre | Municipal ops | 61 Bewicke Ave | CNV buildings + parcels |
| Armoury | Federal / DND | 1513 Forbes Ave | CNV buildings + parcels |
| ICBC | Provincial crown corp | 151 W Esplanade | CNV buildings + parcels |

### 2.2 Health

| Name | Category | Address | Source |
|---|---|---|---|
| Lions Gate Hospital | Acute hospital | 231 E 15th St | CNV buildings + parcels |
| Evergreen House (LGH campus) | Long-term care | 231 E 15th St | VCH / OSA |
| North Shore Hospice | Hospice | 319 E 14th St | CNV buildings + parcels; BC registry |
| Lonsdale & 19th Medical Centre | Medical offices | 1900 Lonsdale Ave | CNV buildings + parcels |

### 2.3 Recreation, culture & seniors centres

| Name | Category | Address | Source |
|---|---|---|---|
| Harry Jerome Rec Centre / North Vancouver Community Recreation Centre | Recreation centre | 123 E 23rd St | CNV buildings + parcels |
| Memorial Community Recreation Centre | Recreation centre | 123 E 23rd St | CNV buildings + parcels |
| John Braithwaite Community Centre | Community centre | 155 W 1st St | CNV buildings + parcels |
| **Silver Harbour Centre** | **Seniors' activity centre** | **144 E 22nd St** | CNV buildings + parcels |
| Centennial Theatre | Performing arts | 130 E 23rd St | CNV buildings + parcels |
| Presentation House | Arts / theatre | 333 Chesterfield Ave | CNV buildings + parcels |
| The Polygon Gallery | Art gallery | 105 Carrie Cates Crt | CNV buildings + parcels |
| The Pipe Shop | Event venue (Shipyards) | 115 Victory Ship Way | CNV buildings + parcels |
| Shipyards Commons | Public plaza / skating | 125 Victory Ship Way | CNV buildings + parcels |
| McDougall Gym | Recreation | 240 E 23rd St | CNV buildings + parcels |
| Leo Marshall Centre / Lucas Centre | Education / community | 2132 Hamilton Ave | CNV buildings + parcels |

### 2.4 Transit & retail

| Name | Category | Address | Source |
|---|---|---|---|
| **Lonsdale Quay Market** | Public market | **123 Carrie Cates Crt** | CNV buildings + parcels |
| **SeaBus terminal (Lonsdale Quay)** | Rapid transit terminal | **2 Chesterfield Pl** | CNV buildings + parcels |
| Bus Depot | Transit | 502 E 3rd St | CNV buildings + parcels |
| Capilano Mall | Shopping centre | 925 / 935 Marine Dr | CNV buildings + parcels |
| **Park & Tilford** | Shopping centre | **333 Brooksbank Ave** — **CITY, confirmed** | CNV buildings + parcels (inside boundary) |
| Westview Shopping Centre | Shopping centre | 2501 / 2601 Westview Dr | CNV buildings + parcels |

> **Park & Tilford is in the City**, not the District — confirmed by both boundary containment and CNV parcel
> ownership of 333 Brooksbank Ave. All 14 Brooksbank Ave parcels in the CNV register are inside the boundary.

### 2.5 Schools (in the City)

| Name | Category | Address | Source |
|---|---|---|---|
| Carson Graham Secondary | Public secondary | 2145 Jones Ave | CNV buildings + parcels |
| Sutherland Secondary | Public secondary | 1858 Sutherland Ave | CNV buildings + parcels |
| Queen Mary Community Elementary | Public elementary | 230 W Keith Rd | CNV buildings + parcels |
| Ridgeway Elementary | Public elementary | 420 E 8th St | CNV buildings + parcels |
| Queensbury Elementary | Public elementary | 520 E 20th St | CNV buildings + parcels |
| Larson Elementary | Public elementary | 2605 Larson Rd | CNV buildings + parcels |
| **Westview Elementary** | Public elementary | **641 W 17th St** | [sd44.ca](https://www.sd44.ca/); CNV parcel verified in-boundary |
| Bodwell High School | Independent secondary | 955 Harbourside Dr | CNV buildings + parcels |
| St. Thomas Aquinas | Independent secondary | 541 W Keith Rd | CNV buildings + parcels |
| St. Edmund's Elementary | Independent elementary | 535 Mahon Ave | CNV buildings + parcels |
| Holy Trinity School | Independent elementary | 128 W 27th St | CNV buildings + parcels |
| St Alcuin College | Independent | 1046 St. Georges Ave | CNV buildings + parcels |
| BCIT Marine Campus | Post-secondary | 265 W Esplanade | CNV buildings + parcels |
| Eslha7an Learning Centre | Post-secondary / Squamish Nation | (no CNV parcel match) | CNV buildings |

> **Caveat:** the CNV `BUILDING_NAME` layer is **not a complete school inventory** — Westview Elementary
> (641 W 17th St, verified in-City) is missing from it. Treat it as a strong but partial source; SD44's own
> school list should be used if a complete school layer is required.

### 2.6 Named CNV buildings of uncertain seniors relevance — flagged, not classified

`Wellington Manor` (175 E 5th St), `The Woodburn Place` (241 St. Andrews Ave), `Bellevue Court`
(225 W 16th St), `Ventana` (180 Chesterfield Ave), `Queen Mary` (717 Chesterfield Ave). These are named
residential buildings in CNV GIS that are **not** in the Affordable Housing layer and **not** in either
provincial registry. Their names suggest they *may* be seniors-oriented, but **no source confirms this** —
they are listed here so they are not silently lost, and must not be classed as seniors residences without
verification.

---

## 3. Files downloaded

| File | Bytes | SHA256 (first 16) | Source | License |
|---|---|---|---|---|
| `data/raw/bc_health/bc_residential_care_facilities.csv` | 382,883 (1,102 rows) | `c07ca8dae0152a68` | [BC Data Catalogue – Residential Care Facilities](https://catalogue.data.gov.bc.ca/dataset/residential-care-facilities) | Open Government Licence – BC |
| `data/raw/bc_health/bc_assisted_living_residences.csv` | (351 rows) | `2bfe0ca416be9fb9` | [BC Data Catalogue – Assisted Living Residences](https://catalogue.data.gov.bc.ca/dataset/assisted-living-residences) | Open Government Licence – BC |
| `data/raw/bc_housing/bc_housing_non_market_housing_2025.xlsx` | 12,339,574 | `1a95dac6340efb75` | [BC Data Catalogue – Non-market Housing (2025)](https://catalogue.data.gov.bc.ca/dataset/non-market-housing-2025-) | Open Government Licence – BC |

Both CSVs carry `LONGITUDE`/`LATITUDE`, so they can be loaded straight into the pipeline as point layers and
clipped to `cnv_boundary`. Both are refreshed **biweekly** by the Assisted Living Registry & Community Care
Licensing branch. The XLSX is annual (as at 2025-03-31), tabulated by local government (sheet
`Metro Vancouver`, rows 21–22 = North Vancouver City / DM).

Suggested `config/sources.yaml` additions: `bc_residential_care_facilities`,
`bc_assisted_living_residences`, `bc_housing_non_market_2025`.

---

## 4. Overlap with the existing CNV Affordable Housing layer

The existing layer (`data/raw/cnv/cnv_affordable_housing.geojson`, 59 features) covers seniors housing
**only in the subsidized/non-market sense**, via its `Eligibility` field. 12 sites carry `55+`, totalling
**727 units**:

| Name | Address | Units | Operator | Eligibility |
|---|---|---|---|---|
| Twin Towers | 172 E 2nd St | 210 | Affordable Housing Societies | 55+, PWD under 55 |
| Grant McNeil Place | 202–236 W 1st St | 112 | BC Housing | Families, 55+, PWD |
| Kiwanis Towers | 170 W 2nd St | 99 | Kiwanis North Shore Housing Society | 55+ |
| ANAVETS | 245 E 3rd St | 76 | ANAVETS Senior Citizens Housing Society | 55+ |
| Pinewood Place | 850 W 17th St | 50 | Metro Vancouver Housing | Families, 55+, PWD |
| Manor House | 145 W 5th St | 50 | Metro Vancouver Housing | Families, 55+, PWD |
| Chelsea North | 121 W 15th St | 33 | New Chelsea Society | 55+ |
| Kiwanis St Andrews Place | 1480 St. Andrews Ave | 27 | Kiwanis North Shore Housing Society | 55+ |
| Walnut Gardens | 601 W Keith Rd | 26 | Metro Vancouver Housing | Families, 55+, PWD |
| Margaret Heights | 1800 Rufus Dr | 19 | Entre Nous Femmes Housing Society | Families, 55+ |
| St Andrews Place | 95 St. Andrews Ave | 15 | Metro Vancouver Housing | Families, 55+, PWD |
| The Eleanor | 125 E 20th St | 10 | VRS Communities | Individuals, Families, 55+, PWD |

**What the existing layer already covers:** essentially all *subsidized independent* seniors housing in the
City. Its 727 55+-eligible units are broadly consistent with BC Housing's 164 "Independent Seniors" +
196 "Low Income Families" + 111 "Special Needs" City figures (the layer counts whole buildings with mixed
eligibility, BC Housing counts only units it funds — so the two are not directly comparable, and neither
number should be presented as the other).

**What this research adds that the layer does NOT contain:**

1. **Evergreen House, 284 LTC beds** — by far the largest concentration of frail seniors in the City, and
   entirely absent from the affordable-housing layer *and* from both provincial registries.
2. **Two private-pay seniors residences** — Summerhill PARC (135 W 15th St) and Sunrise at Lonsdale Square
   (2141 Eastern Ave). Neither is non-market, so neither could ever appear in the City layer.
3. **12 licensed residential care facilities** (hospice / mental health / community living) with capacities.
4. **The negative finding** that the City has no registered assisted living — analytically important, and
   not derivable from the affordable-housing layer at all.
5. **Authoritative City-vs-District exclusions** for 13+ near-boundary facilities.

**Recommendation:** keep the CNV Affordable Housing layer as the authority for *non-market seniors housing*,
and add a separate `seniors_care_facilities` layer built from the two provincial CSVs plus the manually
verified Evergreen House / Summerhill / Sunrise records, each carrying an explicit `source` and
`confidence` attribute. Do not merge them into one undifferentiated "seniors" layer — subsidized
independent housing and licensed care have very different pedestrian/mobility profiles.

---

## 5. Searched but NOT found

| Sought | Where searched | Outcome |
|---|---|---|
| Bulk download of the OSA Long-Term Care & Assisted Living Directory | `seniorsadvocatebc.ca/long-term-care-directory/`, `/quickfacts/location/`, WP REST API (`/wp-json/wp/v2/types`) | **Not available.** Directory is HTML-only, paginated; the `location` post type is not exposed via REST. Only aggregate PDF summary reports are downloadable. Per-facility pages (e.g. `/quickfacts/location/82112/`) are readable individually. |
| BC Housing Housing Registry / seniors housing directory as data | `housingsearch.bchousing.org/Home/HousingListing` | **No API or export.** 1,401 listings, HTML list/map view only, no documented query parameters. Not scraped. |
| VCH long-term care home directory | `vch.ca/en/service/long-term-care-homes` | **HTTP 403** to automated fetch. Individual facility pages (Evergreen House) are reachable. Not bypassed. |
| CNV GIS layer of civic facilities / POIs / schools | All 5 CNV ArcGIS folders — `BaseMapServices` (37 services, incl. 231-layer `TransportMAP`, `CityMapPro`), `Applications` (19), `FeatureServices`, `BaseMapTools`, `Utilities` | **No dedicated facilities/POI/schools layer exists.** Best available substitute is the `BUILDING_NAME` attribute on the Buildings layer (107 named buildings) — used above. |
| CNV geocoder for address adjudication | `BaseMapTools/cnv_geocoder/GeocodeServer/findAddressCandidates` | Returned zero candidates for all test addresses (single-line field `SingleKey` did not match). **Worked around** using the legal-parcel `ADDRESS`/`ADDR_RNG` register instead, which is authoritative and gave clean results. |
| Bed/suite counts for Summerhill PARC and Sunrise at Lonsdale Square | Operator sites, NV Chamber listing, news releases | **Not published.** No count invented. |
| Registry entry for Sunrise at Lonsdale Square | Both BC registry CSVs (searched by business name, operator, street, and CNV bounding box) | **Absent**, despite being marketed as licensed LTC. Unresolved discrepancy — flag for `DATA_GAPS.md`. |
| BC Care Providers Association member facility list | Not pursued | Trade association, not authoritative for location/licensing; the two provincial registries supersede it. |

### Suggested `DATA_GAPS.md` entries

1. **Hospital-based long-term care is invisible in provincial licensing registries.** Evergreen House
   (284 beds) is licensed under the *Hospital Act*, not the *Residential Care Regulation*. Any pipeline step
   that builds a seniors-care layer purely from `gsr_residential_care.csv` will under-count the City's frail
   seniors population by ~284 beds — more than all other City residential care capacity combined.
2. **Sunrise at Lonsdale Square registry discrepancy** — operating private-pay LTC/memory care at a
   confirmed CNV address (2141 Eastern Ave), absent from both provincial registries as of 2026-08-12.
3. **No machine-readable seniors housing directory** for BC at facility level covering *independent living*
   (private pay). Coverage exists only for licensed residential care and registered assisted living.
4. **No CNV civic facilities/POI GIS layer**; civic destinations were reconstructed from
   `BUILDING_NAME` + parcel join, which is verifiably incomplete (Westview Elementary missing).
