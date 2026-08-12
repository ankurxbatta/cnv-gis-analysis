# DATA_DICTIONARY.md — City of North Vancouver GIS Analysis

Every layer in `data/processed/` with its fields. Generated from the actual GeoPackages by
`scripts/` output, so it reflects what the pipeline really produced.

**Analysis CRS for every layer: EPSG:26910 (NAD83 / UTM zone 10N).**

## Critical terminology

| Field | Meaning |
|---|---|
| `adult_population_18plus_proxy` | A demographic **proxy** for potential electorate size. **Never** an elector count. The term "eligible voters" is prohibited and enforced by a test. |
| `canadian_citizens_18plus` | Census citizens aged 18+. Closer to municipal elector eligibility, but still not an elector count. |
| `pedestrian_proxy_score` | A **proxy**. No pedestrian counts are published for CNV. |
| `collision_count` = NaN | **Unknown**, not zero. 43% of intersections have no ICBC match. |
| `signal_timing_status` | Always `REQUEST_REQUIRED`. No cycle or phase timing is ever estimated. |
| `classification` = UNKNOWN | The City publishes no attributes for that footprint — not a statement that it is non-residential. |

## `cnv_boundary.gpkg`

### `cnv_boundary`

1 features · geometry: Polygon

| field | type | description |
|---|---|---|
| `ADMIN_AREA_NAME` | object | — |
| `LGL_ADMIN_AREA_ID` | int32 | — |
| `area_km2` | float64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `cnv_neighbourhoods`

10 features · geometry: Polygon

| field | type | description |
|---|---|---|
| `neighbourhood` | object | CNV official neighbourhood containing the feature |
| `area_km2` | float64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `prepared_utc` | object | Pipeline run timestamp |

## `cnv_census_2021.gpkg`

### `cnv_census_da`

79 features · geometry: MultiPolygon

| field | type | description |
|---|---|---|
| `DAUID` | object | Statistics Canada dissemination area identifier (8-digit); primary census join key |
| `DGUID` | object | — |
| `LANDAREA` | float64 | — |
| `PRUID` | object | — |
| `population_2021` | float64 | Total population, 2021 Census |
| `total_private_dwellings` | float64 | All private dwellings including unoccupied |
| `occupied_private_dwellings` | float64 | Private dwellings occupied by usual residents |
| `statcan_population_density_km2` | float64 | — |
| `land_area_km2` | float64 | StatCan land area in km2 (excludes water); density denominator |
| `age_total` | float64 | — |
| `age_0_14` | float64 | — |
| `age_15_64` | float64 | — |
| `age_15_19` | float64 | — |
| `age_20_24` | float64 | — |
| `age_25_29` | float64 | — |
| `age_30_34` | float64 | — |
| `age_35_39` | float64 | — |
| `age_40_44` | float64 | — |
| `age_45_49` | float64 | — |
| `age_50_54` | float64 | — |
| `age_55_59` | float64 | — |
| `age_60_64` | float64 | — |
| `age_65_plus` | float64 | — |
| `age_65_69` | float64 | — |
| `age_70_74` | float64 | — |
| `age_75_79` | float64 | — |
| `age_80_84` | float64 | — |
| `age_85_plus` | float64 | — |
| `average_age` | float64 | — |
| `median_age` | float64 | — |
| `dwellings_by_structure_total` | float64 | Denominator for all dwelling structure shares |
| `dw_single_detached` | float64 | Single-detached houses |
| `dw_semi_detached` | float64 | — |
| `dw_row_house` | float64 | Row houses / townhouses |
| `dw_apartment_duplex` | float64 | — |
| `dw_apartment_lt5_storeys` | float64 | Apartments in buildings of fewer than five storeys |
| `dw_apartment_5plus_storeys` | float64 | Apartments in buildings of five or more storeys |
| `dw_other_single_attached` | float64 | — |
| `dw_movable` | float64 | — |
| `households_1_person` | float64 | — |
| `average_household_size` | float64 | — |
| `citizenship_total` | float64 | — |
| `canadian_citizens` | float64 | — |
| `canadian_citizens_under_18` | float64 | — |
| `canadian_citizens_18plus` | float64 | Canadian citizens aged 18+ (Census characteristic 1525); closer to municipal elector eligibility; 25% sample data |
| `not_canadian_citizens` | float64 | — |
| `age_18_19_estimated` | float64 | — |
| `adult_population_18plus_proxy` | float64 | PROXY for potential electorate size: population_2021 - age_0_14 - (3/5 x age_15_19). NOT an elector count |
| `adult_proxy_method` | object | — |
| `senior_population_65plus` | float64 | Population aged 65 and over |
| `senior_population_75plus` | float64 | Population aged 75 and over (75-79 + 80-84 + 85+) |
| `senior_population_85plus` | float64 | Population aged 85 and over |
| `age_18_34_proxy` | float64 | Estimated population 18-34; uses the apportioned 18-19 estimate |
| `age_35_49` | float64 | — |
| `age_50_64` | float64 | — |
| `population_density` | float64 | population_2021 / land_area_km2 |
| `adult_population_density` | float64 | adult_population_18plus_proxy / land_area_km2 |
| `senior_density` | float64 | senior_population_65plus / land_area_km2 |
| `housing_density` | float64 | occupied_private_dwellings / land_area_km2 |
| `multiunit_dwellings` | float64 | — |
| `multiunit_share` | float64 | (row + duplex + apartments) / dwellings_by_structure_total |
| `apartment_share` | float64 | — |
| `highrise_share` | float64 | dw_apartment_5plus_storeys / dwellings_by_structure_total |
| `townhouse_share` | float64 | — |
| `single_family_share` | float64 | — |
| `one_person_household_share` | float64 | — |
| `canadian_citizens_18plus_proxy` | float64 | — |
| `citizen_adult_density` | float64 | canadian_citizens_18plus / land_area_km2 |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `boundary_source` | object | — |
| `license` | object | Licence of the originating dataset |
| `adult_proxy_disclaimer` | object | — |
| `prepared_utc` | object | Pipeline run timestamp |

## `cnv_housing.gpkg`

### `cnv_housing_da`

79 features · geometry: MultiPolygon

| field | type | description |
|---|---|---|
| `DAUID` | object | Statistics Canada dissemination area identifier (8-digit); primary census join key |
| `population_2021` | float64 | Total population, 2021 Census |
| `total_private_dwellings` | float64 | All private dwellings including unoccupied |
| `occupied_private_dwellings` | float64 | Private dwellings occupied by usual residents |
| `dwellings_by_structure_total` | float64 | Denominator for all dwelling structure shares |
| `dw_single_detached` | float64 | Single-detached houses |
| `dw_semi_detached` | float64 | — |
| `dw_row_house` | float64 | Row houses / townhouses |
| `dw_apartment_duplex` | float64 | — |
| `dw_apartment_lt5_storeys` | float64 | Apartments in buildings of fewer than five storeys |
| `dw_apartment_5plus_storeys` | float64 | Apartments in buildings of five or more storeys |
| `dw_other_single_attached` | float64 | — |
| `dw_movable` | float64 | — |
| `households_1_person` | float64 | — |
| `average_household_size` | float64 | — |
| `multiunit_dwellings` | float64 | — |
| `multiunit_share` | float64 | (row + duplex + apartments) / dwellings_by_structure_total |
| `apartment_share` | float64 | — |
| `highrise_share` | float64 | dw_apartment_5plus_storeys / dwellings_by_structure_total |
| `townhouse_share` | float64 | — |
| `single_family_share` | float64 | — |
| `one_person_household_share` | float64 | — |
| `housing_density` | float64 | occupied_private_dwellings / land_area_km2 |
| `land_area_km2` | float64 | StatCan land area in km2 (excludes water); density denominator |
| `dominant_dwelling_type` | object | — |
| `dwellings_per_km2` | float64 | — |
| `persons_per_dwelling` | float64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `cnv_zoning`

683 features · geometry: MultiPolygon

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `AREA_` | float64 | — |
| `PERIMETER` | float64 | — |
| `ZONING_CNTR_` | float64 | — |
| `ZONING_CNTR_ID` | float64 | — |
| `TEXTANGLE` | float64 | — |
| `ZONING` | object | — |
| `CHECKED` | object | — |
| `BASE_ZONING2` | object | — |
| `GIS_EDITOR` | object | — |
| `GIS_EDIT_DATE` | float64 | — |
| `GLOBALID` | object | — |
| `TEXTSIZE_` | float64 | — |
| `ADOPTED` | float64 | — |
| `BYLAW_NO` | object | — |
| `ENERGUIDE_STD` | object | — |
| `MAX_BLDG_HT` | float64 | — |
| `MAX_BLDG_HT_45DEG` | float64 | — |
| `NUM_PRINCIP_BLDGS` | float64 | — |
| `PRINCIP_USE` | object | — |
| `XREF_ZONE_REGS` | object | — |
| `GFA` | float64 | — |
| `GFA_EXCEPTION` | object | — |
| `FSR` | object | — |
| `FRONT_SETBACK` | float64 | — |
| `REAR_SETBACK` | float64 | — |
| `EAST_SETBACK` | float64 | — |
| `WEST_SETBACK` | float64 | — |
| `MINIM_OFFSTREET_PKG` | float64 | — |
| `COMMENTS` | object | — |
| `CITYDOCS_NO` | object | — |
| `FORMER_ZONE` | object | — |
| `SHAPE.STArea()` | float64 | — |
| `SHAPE.STLength()` | float64 | — |
| `area_km2` | float64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `cnv_ocp_landuse`

609 features · geometry: MultiPolygon

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `OCP2014_LandUse` | object | — |
| `BYLAW` | object | — |
| `OCP_LU_CODE` | object | — |
| `Shape.STArea()` | float64 | — |
| `Shape.STLength()` | float64 | — |
| `GlobalID` | object | — |
| `area_km2` | float64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

## `residential_buildings.gpkg`

### `buildings`

11,833 features · geometry: MultiPolygon

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `BUILDING_STATUS` | object | — |
| `BUILDING_NAME` | object | — |
| `WEBLINK` | object | — |
| `SHAPE.STArea()` | float64 | — |
| `SHAPE.STLength()` | float64 | — |
| `building_id` | int64 | — |
| `footprint_area_m2` | float64 | — |
| `BUILDING_Z` | float64 | — |
| `YearBuilt` | object | — |
| `NosUnits` | object | — |
| `Occupancy` | object | — |
| `CivicAddress` | object | — |
| `SUBTYPE_DESCRIPTION` | object | — |
| `StrataUnitArea` | object | — |
| `ah_type` | object | — |
| `ah_tenure` | object | — |
| `ah_eligibility` | object | — |
| `ah_name` | object | — |
| `ah_operator` | object | — |
| `ah_total_units` | float64 | — |
| `ah_address` | object | — |
| `ah_status` | object | — |
| `classification` | object | Building class from published evidence; UNKNOWN = City publishes nothing |
| `classification_basis` | object | The specific evidence used for that classification |
| `units_known` | bool | — |
| `height_m` | float64 | — |
| `year_built` | object | — |
| `condominium_tenure` | bool | True only where the City's Occupancy attribute says STRATA; never inferred |
| `condominium_basis` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `classification_note` | object | — |

### `residential_buildings`

123 features · geometry: Polygon

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `BUILDING_STATUS` | object | — |
| `BUILDING_NAME` | object | — |
| `WEBLINK` | object | — |
| `SHAPE.STArea()` | float64 | — |
| `SHAPE.STLength()` | float64 | — |
| `building_id` | int64 | — |
| `footprint_area_m2` | float64 | — |
| `BUILDING_Z` | float64 | — |
| `YearBuilt` | object | — |
| `NosUnits` | object | — |
| `Occupancy` | object | — |
| `CivicAddress` | object | — |
| `SUBTYPE_DESCRIPTION` | object | — |
| `StrataUnitArea` | object | — |
| `ah_type` | object | — |
| `ah_tenure` | object | — |
| `ah_eligibility` | object | — |
| `ah_name` | object | — |
| `ah_operator` | object | — |
| `ah_total_units` | float64 | — |
| `ah_address` | object | — |
| `ah_status` | object | — |
| `classification` | object | Building class from published evidence; UNKNOWN = City publishes nothing |
| `classification_basis` | object | The specific evidence used for that classification |
| `units_known` | bool | — |
| `height_m` | float64 | — |
| `year_built` | object | — |
| `condominium_tenure` | bool | True only where the City's Occupancy attribute says STRATA; never inferred |
| `condominium_basis` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `classification_note` | object | — |

### `seniors_housing`

11 features · geometry: Polygon

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `BUILDING_STATUS` | object | — |
| `BUILDING_NAME` | object | — |
| `WEBLINK` | object | — |
| `SHAPE.STArea()` | float64 | — |
| `SHAPE.STLength()` | float64 | — |
| `building_id` | int64 | — |
| `footprint_area_m2` | float64 | — |
| `BUILDING_Z` | float64 | — |
| `YearBuilt` | object | — |
| `NosUnits` | object | — |
| `Occupancy` | object | — |
| `CivicAddress` | object | — |
| `SUBTYPE_DESCRIPTION` | object | — |
| `StrataUnitArea` | object | — |
| `ah_type` | object | — |
| `ah_tenure` | object | — |
| `ah_eligibility` | object | — |
| `ah_name` | object | — |
| `ah_operator` | object | — |
| `ah_total_units` | float64 | — |
| `ah_address` | object | — |
| `ah_status` | object | — |
| `classification` | object | Building class from published evidence; UNKNOWN = City publishes nothing |
| `classification_basis` | object | The specific evidence used for that classification |
| `units_known` | bool | — |
| `height_m` | float64 | — |
| `year_built` | object | — |
| `condominium_tenure` | bool | True only where the City's Occupancy attribute says STRATA; never inferred |
| `condominium_basis` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `classification_note` | object | — |

## `cnv_elections.gpkg`

### `voting_places`

10 features · geometry: Point

| field | type | description |
|---|---|---|
| `year` | int64 | — |
| `place_name` | object | — |
| `address` | object | — |
| `place_type` | object | — |
| `lat` | float64 | — |
| `lon` | float64 | — |
| `inside_cnv_boundary` | bool | — |
| `mayoral_votes_2022` | float64 | Mayoral votes recorded at this voting place; a LOWER BOUND on ballots cast |
| `mayoral_votes_note` | object | — |
| `source` | object | Originating dataset |
| `coordinate_source` | object | — |
| `polling_boundary_status` | object | NOT_AVAILABLE - CNV runs any-voting-place elections; no catchments exist |
| `polling_boundary_note` | object | — |
| `prepared_utc` | object | Pipeline run timestamp |

## `cnv_roads.gpkg`

### `roads`

941 features · geometry: LineString

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `STREET_NAME` | object | — |
| `STREET_TYPE` | object | — |
| `SUF_DIR` | object | — |
| `LF_ADD` | float64 | — |
| `LT_ADD` | float64 | — |
| `RF_ADD` | float64 | — |
| `RT_ADD` | float64 | — |
| `F_ADD` | float64 | — |
| `T_ADD` | float64 | — |
| `NEWSTREET` | object | — |
| `GIS_EDITOR` | object | — |
| `GIS_EDIT_DATE` | float64 | — |
| `GLOBALID` | object | — |
| `NOLANES` | float64 | — |
| `ROADCLASS` | object | — |
| `ROADLEVEL` | object | — |
| `OWNER` | object | — |
| `SHAPE_1_Length` | object | — |
| `ONEWAY` | float64 | — |
| `FIRELANE` | float64 | — |
| `GlobalID_1` | object | — |
| `Shape.STLength()` | float64 | — |
| `length_m` | float64 | — |
| `full_street_name` | object | SUF_DIR + STREET_NAME + STREET_TYPE, e.g. 'E 3RD ST' |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `intersections`

503 features · geometry: Point

| field | type | description |
|---|---|---|
| `leg_count` | int64 | Number of centreline segment ends meeting at the node |
| `distinct_street_names` | int64 | — |
| `street_a` | object | — |
| `street_b` | object | — |
| `street_names` | object | Distinct street names meeting at the intersection |
| `road_classes` | object | — |
| `max_lanes` | float64 | — |
| `is_intersection` | bool | — |
| `intersection_id` | object | Derived CNV intersection identifier (CNV-INT-nnnn) |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `derivation` | object | — |
| `geoweb_match_dist_m` | float64 | — |

### `road_designation`

178 features · geometry: MultiLineString

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `DESIGNATION` | object | — |
| `MRN` | object | — |
| `Shape_Length` | float64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `bike_routes`

198 features · geometry: MultiLineString

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `BMP_Designation` | object | — |
| `BMP_Type` | object | — |
| `BMP` | object | — |
| `ROUTE_NAME` | object | — |
| `BMP_STATUS` | object | — |
| `REFERENCE` | object | — |
| `OWNER` | object | — |
| `COMMENTS` | object | — |
| `GlobalID` | object | — |
| `Shape.STLength()` | float64 | — |
| `ALTERNATE_ROUTE` | object | — |
| `TRAVEL_DIRECTION` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `speed_zones`

120 features · geometry: LineString

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `STATUS` | object | — |
| `SPEED_ZONE` | int32 | — |
| `BYLAW_NO` | object | — |
| `INSTALL_DATE` | float64 | — |
| `SHAPE.STLength()` | float64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `walkways`

2,693 features · geometry: MultiLineString

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `MINOR` | float64 | — |
| `MAJOR` | float64 | — |
| `FNODE` | float64 | — |
| `TNODE` | float64 | — |
| `UPDATED` | float64 | — |
| `ASBUILT` | float64 | — |
| `GIS_EDITOR` | object | — |
| `GIS_EDIT_DATE` | float64 | — |
| `SHAPE.STLength()` | float64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

## `cnv_traffic.gpkg`

### `traffic_signal_assets`

569 features · geometry: Point

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `UNITTYPE` | object | — |
| `ASSET_TYPE` | object | — |
| `STATUS` | object | — |
| `UNITID` | object | — |
| `OWNER` | object | — |
| `INSTALL_DATE` | float64 | — |
| `ADDRESS` | object | — |
| `ADDRKEY` | float64 | — |
| `BASE_TYPE` | object | — |
| `POLE_TYPE` | object | — |
| `POLE_COLOUR` | object | — |
| `POLE_CONDITION` | object | — |
| `POLE_CONDITION_DATE` | float64 | — |
| `NUM_PRIMARY_HEADS` | object | — |
| `NUM_SECONDARY_HEADS` | object | — |
| `NUM_TERTIARY_HEADS` | object | — |
| `PEDESTRIAN_HEADS` | object | — |
| `STREET_LIGHT` | object | — |
| `COMMENTS` | object | — |
| `MAPNO` | object | — |
| `COMPTYPE` | object | — |
| `COMPKEY` | object | — |
| `XCOORD` | float64 | — |
| `YCOORD` | float64 | — |
| `GEOM_SOURCE` | object | — |
| `GEOM_REFERENCE` | object | — |
| `GIS_GEOM_DATE` | float64 | — |
| `ATTR_SOURCE` | object | — |
| `ATTR_REFERENCE` | object | — |
| `GIS_ATTR_DATE` | float64 | — |
| `GIS_EDIT_DATE` | int64 | — |
| `CREATE_SOURCE` | object | — |
| `CREATE_REFERENCE` | object | — |
| `GIS_CREATION_DATE` | float64 | — |
| `GIS_CREATION_EDITOR` | object | — |
| `DESCRIPTION` | object | — |
| `SIGNAL_TYPE` | object | — |
| `INT_UNITID` | object | — |
| `INT_ADDRKEY` | object | — |
| `COMPASS_DIR` | object | — |
| `FIRE_PRE_EMPTIVE` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `asset_note` | object | — |

### `signalised_intersections`

133 features · geometry: Point

| field | type | description |
|---|---|---|
| `signal_group_id` | object | — |
| `asset_count` | int64 | — |
| `signal_types` | object | — |
| `has_full_signal` | bool | — |
| `full_signal_assets` | int64 | — |
| `pedestrian_signal_assets` | int64 | — |
| `special_crosswalk_assets` | int64 | — |
| `rrfb_assets` | int64 | — |
| `pedestrian_heads` | float64 | — |
| `address` | object | — |
| `grouping_basis` | object | — |
| `signal_timing_status` | object | REQUEST_REQUIRED - CNV holds timing but publishes none; never estimated |
| `signal_timing_note` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `traffic_volumes`

38 features · geometry: LineString

| field | type | description |
|---|---|---|
| `direction` | object | — |
| `volume` | int64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `coverage_warning` | object | — |
| `units_note` | object | — |

### `traffic_signs`

1,088 features · geometry: Point

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `STATUS` | object | — |
| `UNITID` | object | — |
| `UNITTYPE` | object | — |
| `SIGN_SUBTYPE` | float64 | — |
| `OWNER` | object | — |
| `SIZE_` | object | — |
| `GRADE` | object | — |
| `CONDITION` | float64 | — |
| `REFLECTIVITY` | float64 | — |
| `ANNOTATION` | object | — |
| `COMMENTS` | object | — |
| `GEOM_SOURCE` | object | — |
| `GEOM_REFERENCE` | object | — |
| `ATTR_SOURCE` | object | — |
| `ATTR_REFERENCE` | object | — |
| `MAPNO` | object | — |
| `BLOCK_STREET` | object | — |
| `CREATE_SOURCE` | object | — |
| `CREATE_REFERENCE` | object | — |
| `ZONE_` | object | — |
| `INTERSECTION` | object | — |
| `LOCATION` | object | — |
| `CNVZONE` | float64 | — |
| `COMMENTS1` | object | — |
| `REMOVAL_DATE` | float64 | — |
| `INSTALL_DATE` | float64 | — |
| `INSPECTION_DATE` | float64 | — |
| `PREVIOUS_INSPECTION` | float64 | — |
| `INSPECTION_HISTORY` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

## `cnv_transit.gpkg`

### `transit_stops`

244 features · geometry: Point

| field | type | description |
|---|---|---|
| `stop_id` | object | — |
| `stop_code` | float64 | — |
| `stop_name` | object | — |
| `stop_desc` | float64 | — |
| `stop_lat` | float64 | — |
| `stop_lon` | float64 | — |
| `zone_id` | object | — |
| `stop_url` | object | — |
| `location_type` | int64 | — |
| `parent_station` | float64 | — |
| `wheelchair_boarding` | int64 | — |
| `trips_per_weekday` | int64 | Scheduled GTFS departures at the stop on a representative weekday |
| `trips_am_peak` | int64 | — |
| `trips_midday` | int64 | — |
| `trips_pm_peak` | int64 | — |
| `trips_evening` | int64 | — |
| `routes_serving` | int64 | — |
| `service_date_basis` | object | — |
| `in_cnv` | bool | — |
| `am_peak_avg_headway_min` | float64 | 120 / trips_am_peak |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `transit_routes`

61 features · geometry: MultiLineString

| field | type | description |
|---|---|---|
| `shape_id` | object | — |
| `route_id` | object | — |
| `route_short_name` | object | — |
| `route_long_name` | object | — |
| `route_type` | int64 | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

## `cnv_parking.gpkg`

### `parking_occupancy`

1,169 features · geometry: MultiLineString

| field | type | description |
|---|---|---|
| `OBJECTID_1` | int32 | — |
| `ObjectID` | int32 | — |
| `Supply` | int32 | — |
| `Weekday_07` | int32 | — |
| `Weekday_08` | object | — |
| `Weekday_11` | int32 | — |
| `Weekday_12` | object | — |
| `Weekday_16` | int32 | — |
| `Weekday_17` | object | — |
| `Weekday_21` | int32 | — |
| `Weekday_22` | object | — |
| `Weekend_09` | int32 | — |
| `Weekend_07` | object | — |
| `Weekend_11` | int32 | — |
| `Weekend_12` | object | — |
| `Weekend_16` | int32 | — |
| `Weekend_17` | object | — |
| `Weekend_21` | int32 | — |
| `Weekend_22` | object | — |
| `supply_spaces` | int64 | Published on-street parking capacity estimate for the segment (integer) |
| `occupied_weekday_0709` | int64 | — |
| `occupancy_weekday_0709` | float64 | — |
| `occupancy_recomputed_weekday_0709` | float64 | — |
| `occupied_weekday_1113` | int64 | — |
| `occupancy_weekday_1113` | float64 | — |
| `occupancy_recomputed_weekday_1113` | float64 | — |
| `occupied_weekday_1618` | int64 | — |
| `occupancy_weekday_1618` | float64 | — |
| `occupancy_recomputed_weekday_1618` | float64 | — |
| `occupied_weekday_2123` | int64 | — |
| `occupancy_weekday_2123` | float64 | — |
| `occupancy_recomputed_weekday_2123` | float64 | — |
| `occupied_weekend_0709` | int64 | — |
| `occupancy_weekend_0709` | float64 | — |
| `occupancy_recomputed_weekend_0709` | float64 | — |
| `occupied_weekend_1113` | int64 | — |
| `occupancy_weekend_1113` | float64 | — |
| `occupancy_recomputed_weekend_1113` | float64 | — |
| `occupied_weekend_1618` | int64 | — |
| `occupancy_weekend_1618` | float64 | — |
| `occupancy_recomputed_weekend_1618` | float64 | — |
| `occupied_weekend_2123` | int64 | — |
| `occupancy_weekend_2123` | float64 | — |
| `occupancy_recomputed_weekend_2123` | float64 | — |
| `occupancy_peak` | float64 | Maximum occupancy across the eight surveyed periods; >1.0 possible and retained |
| `occupancy_mean` | float64 | — |
| `peak_period` | object | — |
| `at_practical_capacity` | bool | occupancy_peak >= 0.85 |
| `over_estimated_supply` | bool | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `survey_period` | object | Parking survey window: 2022-12 to 2023-02 (Bunt & Associates) |
| `survey_consultant` | object | — |
| `data_nature` | object | — |
| `occupancy_method` | object | — |

### `parking_restrictions`

5,971 features · geometry: MultiLineString

| field | type | description |
|---|---|---|
| `Shape.STLength()` | float64 | — |
| `OBJECTID` | int32 | — |
| `SIGNTYPE` | object | — |
| `PARKING_TYPE` | object | — |
| `SUPPLY` | float64 | — |
| `PARKING_TIME` | object | — |
| `RESTRICTIONS` | object | — |
| `STATUS` | object | — |
| `ZONE_ID` | object | — |
| `EXEMPT_PARKING` | object | — |
| `BLOCK_STREET` | object | — |
| `NEIGHBOURHOOD` | object | — |
| `COMMENTS` | object | — |
| `DESCRIPTION` | object | — |
| `IMPLEMENTATION_AREA` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `parking_lots`

28 features · geometry: Point

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `LOT_NAME` | object | — |
| `ADDRESS` | object | — |
| `Operator` | object | — |
| `PAY_PARKING` | object | — |
| `RESTRICTION` | object | — |
| `SPACES_WEEKDAY` | int32 | — |
| `SPACES_WEEKNIGHT_WKND` | int32 | — |
| `ACCESSIBLE_PARKING_SPACES` | int32 | — |
| `EV_PARKING_SPACES` | int32 | — |
| `IMAGE` | object | — |
| `STATUS` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

### `parking_signs`

2,578 features · geometry: Point

| field | type | description |
|---|---|---|
| `OBJECTID` | int32 | — |
| `UNITID` | object | — |
| `STATUS` | object | — |
| `SIGNTYPE` | object | — |
| `PARKING_TIME` | object | — |
| `SIGN_ORDER` | object | — |
| `CREATE_REFERENCE` | object | — |
| `RESTRICTIONS` | object | — |
| `EXEMPT_PARKING` | object | — |
| `BLOCK_STREET` | object | — |
| `COMMENTS` | object | — |
| `ATTR_REFERENCE` | object | — |
| `Shape` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |

## `cnv_safety.gpkg`

### `intersection_crashes`

288 features · geometry: Point

| field | type | description |
|---|---|---|
| `intersection_id` | object | Derived CNV intersection identifier (CNV-INT-nnnn) |
| `crash_count` | int64 | — |
| `icbc_locations` | object | — |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `matching_limitation` | object | — |

## `cnv_neighbourhoods_stats.gpkg`

### `cnv_neighbourhoods_stats`

10 features · geometry: Polygon

| field | type | description |
|---|---|---|
| `neighbourhood` | object | CNV official neighbourhood containing the feature |
| `area_km2` | float64 | — |
| `population_2021` | float64 | Total population, 2021 Census |
| `adult_population_18plus_proxy` | float64 | PROXY for potential electorate size: population_2021 - age_0_14 - (3/5 x age_15_19). NOT an elector count |
| `senior_population_65plus` | float64 | Population aged 65 and over |
| `senior_population_75plus` | float64 | Population aged 75 and over (75-79 + 80-84 + 85+) |
| `senior_population_85plus` | float64 | Population aged 85 and over |
| `age_0_14` | float64 | — |
| `age_18_34_proxy` | float64 | Estimated population 18-34; uses the apportioned 18-19 estimate |
| `age_35_49` | float64 | — |
| `age_50_64` | float64 | — |
| `occupied_private_dwellings` | float64 | Private dwellings occupied by usual residents |
| `total_private_dwellings` | float64 | All private dwellings including unoccupied |
| `canadian_citizens_18plus` | float64 | Canadian citizens aged 18+ (Census characteristic 1525); closer to municipal elector eligibility; 25% sample data |
| `multiunit_dwellings` | float64 | — |
| `dw_single_detached` | float64 | Single-detached houses |
| `dw_row_house` | float64 | Row houses / townhouses |
| `dw_apartment_lt5_storeys` | float64 | Apartments in buildings of fewer than five storeys |
| `dw_apartment_5plus_storeys` | float64 | Apartments in buildings of five or more storeys |
| `households_1_person` | float64 | — |
| `dwellings_by_structure_total` | float64 | Denominator for all dwelling structure shares |
| `land_area_km2_from_da` | float64 | — |
| `population_density` | float64 | population_2021 / land_area_km2 |
| `adult_population_density` | float64 | adult_population_18plus_proxy / land_area_km2 |
| `senior_density` | float64 | senior_population_65plus / land_area_km2 |
| `housing_density` | float64 | occupied_private_dwellings / land_area_km2 |
| `apartment_share` | float64 | — |
| `townhouse_share` | float64 | — |
| `single_family_share` | float64 | — |
| `multiunit_share` | float64 | (row + duplex + apartments) / dwellings_by_structure_total |
| `building_count` | int64 | — |
| `mean_building_height_m` | float64 | — |
| `max_building_height_m` | float64 | — |
| `buildings_with_height_known` | int64 | — |
| `source` | object | Originating dataset |
| `methodology_note` | object | — |
| `adult_proxy_disclaimer` | object | — |
| `prepared_utc` | object | Pipeline run timestamp |

## `cnv_intersections_joined.gpkg`

### `intersections_joined`

503 features · geometry: Point

| field | type | description |
|---|---|---|
| `leg_count` | int64 | Number of centreline segment ends meeting at the node |
| `distinct_street_names` | int64 | — |
| `street_a` | object | — |
| `street_b` | object | — |
| `street_names` | object | Distinct street names meeting at the intersection |
| `road_classes` | object | — |
| `max_lanes` | float64 | — |
| `is_intersection` | bool | — |
| `intersection_id` | object | Derived CNV intersection identifier (CNV-INT-nnnn) |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `derivation` | object | — |
| `geoweb_match_dist_m` | float64 | — |
| `transit_stops_100m` | int64 | — |
| `transit_stops_250m` | int64 | — |
| `transit_stops_400m` | int64 | — |
| `transit_departures_250m` | float64 | — |
| `transit_departures_am_peak_250m` | float64 | — |
| `onstreet_supply_250m` | float64 | — |
| `onstreet_peak_occupancy_250m` | float64 | — |
| `offstreet_spaces_400m` | float64 | — |
| `pay_stations_250m` | int64 | — |
| `accessible_parking_250m` | int64 | — |
| `loading_zones_250m` | int64 | — |
| `signalised` | bool | A signal asset cluster lies within 40 m |
| `full_signal` | object | At least one asset in that cluster is a Full Signal (not pedestrian-only) |
| `signal_timing_status` | object | REQUEST_REQUIRED - CNV holds timing but publishes none; never estimated |
| `nearest_traffic_volume` | float64 | — |
| `traffic_volume_available` | bool | — |
| `collision_count` | float64 | ICBC crashes name-matched to this intersection; NaN means unknown, NOT zero |
| `collision_data_available` | bool | Whether any ICBC record matched this intersection |
| `walkway_length_250m` | float64 | — |
| `bike_route_length_250m` | float64 | — |
| `sidewalk_ramps_100m` | int64 | — |
| `population_2021_400m` | float64 | — |
| `adult_population_18plus_proxy_400m` | float64 | — |
| `senior_population_65plus_400m` | float64 | — |
| `occupied_private_dwellings_400m` | float64 | — |
| `canadian_citizens_18plus_400m` | float64 | — |
| `commercial_area_250m_m2` | float64 | — |
| `neighbourhood` | object | CNV official neighbourhood containing the feature |
| `population_method_note` | object | — |

## `cnv_public_space_scores.gpkg`

### `public_space_scores`

503 features · geometry: Point

| field | type | description |
|---|---|---|
| `leg_count` | int64 | Number of centreline segment ends meeting at the node |
| `distinct_street_names` | int64 | — |
| `street_a` | object | — |
| `street_b` | object | — |
| `street_names` | object | Distinct street names meeting at the intersection |
| `road_classes` | object | — |
| `max_lanes` | float64 | — |
| `is_intersection` | bool | — |
| `intersection_id` | object | Derived CNV intersection identifier (CNV-INT-nnnn) |
| `source` | object | Originating dataset |
| `source_url` | object | Endpoint or landing page |
| `license` | object | Licence of the originating dataset |
| `prepared_utc` | object | Pipeline run timestamp |
| `derivation` | object | — |
| `geoweb_match_dist_m` | float64 | — |
| `transit_stops_100m` | int64 | — |
| `transit_stops_250m` | int64 | — |
| `transit_stops_400m` | int64 | — |
| `transit_departures_250m` | float64 | — |
| `transit_departures_am_peak_250m` | float64 | — |
| `onstreet_supply_250m` | float64 | — |
| `onstreet_peak_occupancy_250m` | float64 | — |
| `offstreet_spaces_400m` | float64 | — |
| `pay_stations_250m` | int64 | — |
| `accessible_parking_250m` | int64 | — |
| `loading_zones_250m` | int64 | — |
| `signalised` | bool | A signal asset cluster lies within 40 m |
| `full_signal` | bool | At least one asset in that cluster is a Full Signal (not pedestrian-only) |
| `signal_timing_status` | object | REQUEST_REQUIRED - CNV holds timing but publishes none; never estimated |
| `nearest_traffic_volume` | float64 | — |
| `traffic_volume_available` | bool | — |
| `collision_count` | float64 | ICBC crashes name-matched to this intersection; NaN means unknown, NOT zero |
| `collision_data_available` | bool | Whether any ICBC record matched this intersection |
| `walkway_length_250m` | float64 | — |
| `bike_route_length_250m` | float64 | — |
| `sidewalk_ramps_100m` | int64 | — |
| `population_2021_400m` | float64 | — |
| `adult_population_18plus_proxy_400m` | float64 | — |
| `senior_population_65plus_400m` | float64 | — |
| `occupied_private_dwellings_400m` | float64 | — |
| `canadian_citizens_18plus_400m` | float64 | — |
| `commercial_area_250m_m2` | float64 | — |
| `neighbourhood` | object | CNV official neighbourhood containing the feature |
| `population_method_note` | object | — |
| `road_class_weight` | float64 | — |
| `traffic_score` | float64 | Vehicle exposure; road class 70% + measured volume 30%. Volume exists for ~8% only |
| `traffic_score_coverage_note` | object | — |
| `transit_score` | float64 | Scheduled transit activity within 250 m (GTFS) |
| `transit_score_coverage_note` | object | — |
| `pedestrian_proxy_score` | float64 | PROXY for pedestrian activity. NOT a count; no CNV pedestrian counts exist |
| `pedestrian_proxy_score_coverage_note` | object | — |
| `parking_access_score` | float64 | On-street supply, off-street spaces, and inverted observed occupancy |
| `parking_access_score_coverage_note` | object | — |
| `intersection_prominence_score` | float64 | — |
| `intersection_prominence_score_coverage_note` | object | — |
| `safety_score` | float64 | Inverted collision count; NaN where no ICBC match (57% coverage) |
| `safety_score_coverage_note` | object | — |
| `visibility_score` | float64 | Proxy from intersection geometry and frontage; no measured sightlines exist |
| `visibility_score_coverage_note` | object | — |
| `public_space_composite` | float64 | Unweighted mean of available 0-100 components; neutral, no political variable |
| `components_available` | int64 | — |
| `composite_method` | object | — |
| `political_neutrality_statement` | object | — |
| `composite_rank` | float64 | Rank by public_space_composite, 1 = highest |
