# LICENSES_AND_ATTRIBUTION.md

This project redistributes and derives from public data published by several agencies.
Each is credited below with its licence. **No dataset was obtained by bypassing
authentication, CAPTCHAs, rate limits or robots restrictions.**

---

## Statistics Canada

**Datasets:** Census Profile 2021 (98-401-X2021006); 2021 Census boundary files for
dissemination areas (92-169-X), dissemination blocks (92-163-X) and census subdivisions.

**Licence:** Statistics Canada Open Licence — <https://www.statcan.gc.ca/en/reference/licence>

**Required attribution:**
> Adapted from Statistics Canada, 2021 Census of Population, Census Profile
> (98-401-X2021006) and 2021 Census boundary files. This does not constitute an endorsement
> by Statistics Canada of this product.

**Note on random rounding:** Statistics Canada applies random rounding to base 5 to protect
confidentiality. Component values may therefore not sum exactly to their totals, and small
discrepancies against published figures are expected rather than errors.

---

## Province of British Columbia

**Datasets:** ABMS Legally Defined Administrative Areas (municipal boundaries) via the BC
Data Catalogue WFS; BC Ministry of Transportation and Infrastructure traffic count station
geometry via the GeoServer WFS at `maps.th.gov.bc.ca/geoV05/ows`; BC residential care and
assisted living facility registries; BC Housing non-market housing data.

**Licence:** Open Government Licence – British Columbia —
<https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc>

**Required attribution:**
> Contains information licensed under the Open Government Licence – British Columbia.

**Important restriction:** the BC Data Catalogue record for the **Traffic Data Program** is
licensed **"Access Only"**, not open data. Its station geometry and static TRADAS report
files are publicly retrievable, but that licence should be cited and checked before
redistributing the report files themselves.

---

## City of North Vancouver

**Datasets:** all layers retrieved from the public ArcGIS REST server at
`gisext2.cnv.org/arcgis/rest/services` — street centrelines, building footprints,
neighbourhoods, zoning, OCP land use, traffic signals and signs, speed zones, parking
supply/occupancy/restrictions, sidewalks, bike routes, affordable housing, bus stops, parks
— plus published PDF maps, election results and transportation planning reports.

**Licence:** City of North Vancouver open data terms. The ArcGIS services are publicly
served without an access control or a stated open-data licence on the endpoints themselves.

> **Verify licensing with the City before redistributing these layers or publishing derived
> products commercially.** Contact: `gis@cnv.org`. This project treats the data as publicly
> readable for research, which is how it is served, but that is not the same as an explicit
> open-data grant.

**Attribution used:**
> Contains data from the City of North Vancouver.

---

## District of North Vancouver — GEOweb

**Datasets:** street centrelines, street intersections, parking restrictions, parking lots,
sidewalks, Metro Vancouver municipal boundaries, from <https://geoweb.dnv.org/data/>.

**Licence:** District of North Vancouver GEOweb terms of use. Used here as a **cross-check**
on CNV-derived layers, never as the primary source for City geography.

**Attribution used:**
> Contains data from the District of North Vancouver (GEOweb).

---

## TransLink

**Dataset:** GTFS static feed —
<https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources/gtfs/gtfs-data>

**Licence:** TransLink open data / GTFS terms of use.

**Required attribution:**
> Transit data provided by TransLink (South Coast British Columbia Transportation
> Authority). TransLink does not warrant the accuracy of this data and is not responsible
> for any use of it.

---

## Insurance Corporation of British Columbia (ICBC)

**Dataset:** Lower Mainland Crashes, retrieved through the Tableau Public dashboard's own
built-in CSV export (the sanctioned download path for a publicly published visualisation).

**Licence:** Open Data Licence for ICBC Information.

**Required attribution:**
> Contains information licensed under the Open Data Licence for ICBC Information.

**Limitations to state wherever these figures appear:** ICBC's `NORTH VANCOUVER`
municipality value covers **both the City and the District**; records carry location name
strings with **no coordinates**; and crash maps exclude collisions in parking lots and those
involving only parked vehicles.

---

## Base map tiles (interactive map only)

**CARTO Positron** basemap over OpenStreetMap data.

**Required attribution** (displayed in the map):
> © OpenStreetMap contributors, © CARTO

OpenStreetMap data is licensed under the Open Database Licence (ODbL). OSM was **not** used
as a data source anywhere in the analysis — only as a visual basemap.

---

## Software

Python 3.11 with pandas, GeoPandas, Shapely, PyProj, pyogrio, NumPy, SciPy, Matplotlib,
mapclassify, Requests, PyYAML, WeasyPrint and pytest — each under its own open-source
licence. Leaflet (BSD-2-Clause) is used for the interactive map.

---

## Combined attribution statement

For any published output derived from this project:

> Contains information licensed under the Statistics Canada Open Licence; the Open
> Government Licence – British Columbia; and the Open Data Licence for ICBC Information.
> Contains data from the City of North Vancouver and the District of North Vancouver
> (GEOweb). Transit data provided by TransLink. Basemap © OpenStreetMap contributors,
> © CARTO. Analysis by the CNV GIS analysis pipeline; source agencies do not endorse this
> product.
