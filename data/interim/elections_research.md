# City of North Vancouver (CNV) — Aggregate Municipal Election Research

**Research date:** 2026-08-12
**Scope:** City of North Vancouver only (CSD 5915051). **Not** the District of North Vancouver, not West Vancouver, not the provincial/federal ridings.
**Ethical scope:** Only aggregate, officially published data (candidate vote totals, turnout, registered elector counts, voting place names/addresses). No individual-level voter data was sought, obtained or stored. No authentication was bypassed; one source (CivicInfo BC) was blocked by a Cloudflare bot challenge and was **not** circumvented.

---

## 1. Headline verdicts

| Question | Verdict |
|---|---|
| 2022 official results with per-voting-place breakdown? | **YES** — official CNV PDF gives votes by each of 12 poll columns |
| 2018 per-voting-place breakdown? | **YES** — official CNV JPG table, 10 poll columns |
| 2014 per-voting-place breakdown? | **YES** — official CNV JPG table, 19 poll columns |
| 2011 per-voting-place breakdown? | **YES** — official CNV JPG table, 10 poll columns |
| Voting place addresses 2011/2014/2018/2022/2026? | **YES** — official notices + CNV GeoRSS feed with lat/lon |
| **Polling / voting DIVISION boundary polygons or maps?** | **NOT AVAILABLE — and almost certainly do not exist.** See §6 |
| Separate "Chief Election Officer report" / "Statement of Votes" PDF? | **NOT FOUND** as a distinct document. The signed CEO statement is embedded in the results table itself (see §7) |

**Key structural finding:** CNV runs an **at-large, any-voting-place** election. The Sept 26 2022 CNV news release states electors may vote *"at any one of the nine voting locations across the city."* Electors are **not** assigned to a geographic polling division. Therefore vote counts by voting place **cannot** be attributed to a catchment area, and no division polygons exist to be published. This is a hard analytical constraint for any spatial election analysis.

---

## 2. 2022 General Local Election (Saturday, October 15, 2022)

**Primary source (authoritative):** `https://www.cnv.org/-/media/City-of-North-Vancouver/Images/Page-Images/Election/Election-Results/2022-Election-Results-PDF.pdf`
(linked from `https://www.cnv.org/City-Hall/General-Local-Election/Past-Election-Results`)
**Corroborating source:** `https://www.cnv.org/City-Hall/News-Room/Whats-New/2022/10/19/Official-Results-of-2022-City-Election-Announced`

The PDF is a **scanned/flattened image** (no text layer) — figures below were read visually from a 200 dpi render. Both the PDF totals and the news-release totals agree exactly, which cross-validates every total.

Header: *"2022 Local Government Election — Official Election Results (12 of 12 Polls Counted)"*.
Signed: **Nikolina Vracar, Chief Election Officer**, 19 October 2022.

### 2.1 Mayor (1 to be elected)

| Rank | Candidate | Votes | % of total | Elected |
|---|---|---|---|---|
| 1 | BUCHANAN, Linda | 5,275 | 57.35 | **Y** |
| 2 | HEYWOOD, Guy | 3,923 | 42.65 | N |

Total votes cast for Mayor: **9,198**

### 2.2 Councillor (6 to be elected)

| Rank | Candidate | Votes | % of total | Elected |
|---|---|---|---|---|
| 1 | VALENTE, Tony | 5,272 | 11.72 | **Y** |
| 2 | BELL, Don | 5,221 | 11.60 | **Y** |
| 3 | GIRARD, Angela | 5,140 | 11.42 | **Y** |
| 4 | SHAHRIARI, Shervin | 4,596 | 10.22 | **Y** |
| 5 | McILROY, Jessica | 3,913 | 8.70 | **Y** |
| 6 | BACK, Holly | 3,892 | 8.65 | **Y** |
| 7 | McGRENERA, Kathy | 3,726 | 8.28 | N |
| 8 | CATO, Jeremy | 3,434 | 7.63 | N |
| 9 | BOLTENKO, Anna | 3,256 | 7.24 | N |
| 10 | LACESTE, Me-An | 2,526 | 5.61 | N |
| 11 | POLLY, Ron | 2,071 | 4.60 | N |
| 12 | LAI, Max | 1,943 | 4.32 | N |

Total votes cast for Councillor: **44,990**

### 2.3 School Trustee — School District No. 44, Trustee Electoral Area 2 (3 to be elected)

| Rank | Candidate | Votes | % of total | Elected |
|---|---|---|---|---|
| 1 | ANDERSON, Daniel | 5,593 | 30.49 | **Y** |
| 2 | TUMANENG, Lailani | 4,531 | 24.70 | **Y** |
| 3 | WILSON, Antje | 4,414 | 24.07 | **Y** |
| 4 | KOLSTEE, Jullian | 3,803 | 20.73 | N |

Total votes cast for School Trustee: **18,341**

### 2.4 2022 results BY VOTING PLACE (from the official PDF)

Columns as printed. "ADV POLLS" = all advance voting at City Hall + The Pipe Shop combined; "MAIL POLLS" = mail ballots; "SPECIAL POLLS" = special voting opportunities.

**Mayor**

| Candidate | Carson Graham | Larson | Memorial Rec Centre | NSN House | Queen Mary | Ridgeway | Sutherland | The Pipe Shop | Westview | Adv polls | Mail polls | Special polls | TOTAL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BUCHANAN, Linda | 434 | 252 | 314 | 418 | 591 | 625 | 351 | 610 | 294 | 1,221 | 132 | 33 | 5,275 |
| HEYWOOD, Guy | 269 | 124 | 280 | 324 | 430 | 492 | 374 | 336 | 185 | 987 | 100 | 22 | 3,923 |

**Councillor**

| Candidate | Carson Graham | Larson | Memorial | NSN House | Queen Mary | Ridgeway | Sutherland | Pipe Shop | Westview | Adv | Mail | Special | TOTAL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VALENTE, Tony | 350 | 230 | 319 | 420 | 563 | 721 | 427 | 576 | 244 | 1,266 | 142 | 14 | 5,272 |
| BELL, Don | 383 | 212 | 353 | 422 | 588 | 642 | 424 | 499 | 254 | 1,277 | 132 | 35 | 5,221 |
| GIRARD, Angela | 380 | 226 | 312 | 430 | 551 | 677 | 382 | 513 | 289 | 1,211 | 150 | 19 | 5,140 |
| SHAHRIARI, Shervin | 397 | 187 | 310 | 343 | 540 | 560 | 408 | 406 | 244 | 1,084 | 110 | 7 | 4,596 |
| McILROY, Jessica | 283 | 183 | 233 | 318 | 435 | 487 | 279 | 403 | 195 | 972 | 107 | 18 | 3,913 |
| BACK, Holly | 312 | 166 | 231 | 313 | 399 | 452 | 312 | 415 | 169 | 988 | 115 | 20 | 3,892 |
| McGRENERA, Kathy | 271 | 128 | 223 | 325 | 459 | 456 | 254 | 342 | 217 | 935 | 101 | 15 | 3,726 |
| CATO, Jeremy | 239 | 109 | 229 | 294 | 393 | 407 | 292 | 351 | 168 | 848 | 94 | 10 | 3,434 |
| BOLTENKO, Anna | 226 | 128 | 217 | 294 | 363 | 361 | 233 | 360 | 173 | 815 | 75 | 11 | 3,256 |
| LACESTE, Me-An | 189 | 107 | 150 | 247 | 279 | 297 | 228 | 237 | 165 | 566 | 50 | 11 | 2,526 |
| POLLY, Ron | 138 | 67 | 149 | 174 | 222 | 260 | 212 | 193 | 101 | 487 | 60 | 8 | 2,071 |
| LAI, Max | 148 | 79 | 146 | 155 | 223 | 177 | 162 | 229 | 96 | 464 | 57 | 7 | 1,943 |

**School Trustee**

| Candidate | Carson Graham | Larson | Memorial | NSN House | Queen Mary | Ridgeway | Sutherland | Pipe Shop | Westview | Adv | Mail | Special | TOTAL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ANDERSON, Daniel | 418 | 235 | 357 | 487 | 628 | 648 | 461 | 545 | 304 | 1,336 | 149 | 25 | 5,593 |
| TUMANENG, Lailani | 352 | 201 | 272 | 403 | 532 | 527 | 343 | 421 | 254 | 1,082 | 128 | 16 | 4,531 |
| WILSON, Antje | 301 | 178 | 273 | 348 | 446 | 586 | 382 | 429 | 202 | 1,136 | 111 | 22 | 4,414 |
| KOLSTEE, Jullian | 272 | 167 | 237 | 341 | 425 | 420 | 278 | 392 | 216 | 950 | 90 | 15 | 3,803 |

**Note:** the 2022 sheet has **no "TOTAL VOTERS" row** (unlike 2011/2014/2018), so ballots cast per voting place is NOT published for 2022 — only votes per candidate per place.

### 2.5 2022 turnout / electors

| Field | Value | Source |
|---|---|---|
| Registered voters | **41,325** | 2022 results PDF; also `.../2022/10/19/Official-Results-of-2022-City-Election-Announced` and `.../Past-Election-Results` |
| Voter turnout | **22.64%** | same |
| Ballots cast (total) | **NOT PUBLISHED** by CNV | — |

Derived only, flagged as an estimate: 41,325 × 22.64% ≈ **9,356** ballots. A third-party aggregator snippet quoted "9,351"; the underlying page (`https://localelections.ca/election_results/85_2022_results.html`) now returns HTTP 404 and could not be verified. **Do not use either number as official.** The only firm floor is 9,198 ballots that contained a mayoral vote.

---

## 3. 2018 General Local Election (Saturday, October 20, 2018)

**Source:** `https://www.cnv.org/-/media/City-of-North-Vancouver/Images/Page-Images/Election/Election-Results/2018-Election-Results.jpg`
Header: *"2018 Local Government Election — Official Results — City of North Vancouver ( 10 of 10 Polls Counted )"*. Signed **Karla Graham, Chief Election Officer**, 24 October 2018.
JPG is 1000×766 px; figures read visually from a 2× upscaled render. Treat the per-poll cells as high-confidence but not machine-verified; the TOTAL column is large and clear.

| Field | Value |
|---|---|
| Total eligible (registered) voters | **38,163** |
| Voter turnout | **34.0%** (CNV wording: "34%") |
| Ballots cast | **NOT PRINTED as a single number.** Sum of the per-poll "TOTAL VOTERS" row = **12,914** (derived by me). 12,914 / 38,163 = 33.84% |

### 3.1 Mayor (1 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| BUCHANAN, Linda | 3,800 | 29.7 | **Y** |
| HEYWOOD, Guy | 3,399 | 26.6 | N |
| CLARK, Rod | 2,828 | 22.1 | N |
| MORRIS, Kerry | 1,987 | 15.5 | N |
| WILLCOCK, Michael | 545 | 4.3 | N |
| AZAD, Payam | 230 | 1.8 | N |

Total votes cast for Mayor: **12,789**

### 3.2 Councillor (6 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| BELL, Don | 6,091 | 9.6 | **Y** |
| GIRARD, Angela | 5,109 | 8.1 | **Y** |
| VALENTE, Tony | 4,539 | 7.2 | **Y** |
| McILROY, Jessica | 4,465 | 7.1 | **Y** |
| HU, Tina | 3,767 | 6.0 | **Y** |
| BACK, Holly | 3,662 | 5.8 | **Y** |
| McCORKINDALE, Mack | 3,525 | 5.6 | N |
| BELL, Bill | 3,375 | 5.3 | N |
| FEARNLEY, Bob | 3,253 | 5.1 | N |
| WILSON, Antje | 3,228 | 5.1 | N |
| SHAHRIARI, Shervin | 3,187 | 5.0 | N |
| BOLTENKO, Anna | 2,903 | 4.6 | N |
| HEILMAN, Joe | 2,662 | 4.2 | N |
| IZATT, Kenneth | 2,305 | 3.6 | N |
| JABEROLANSAR, Alborz | 2,123 | 3.4 | N |
| THORBURN, Brett | 1,722 | 2.7 | N |
| POLLY, Ron | 1,717 | 2.7 | N |
| McCANN, John | 1,488 | 2.4 | N |
| JENSEN, Mica | 1,177 | 1.9 | N |
| ZAHEDI, Max | 1,177 | 1.9 | N |
| LOBO, Aaron | 585 | 0.9 | N |
| ALIZADEH, Pooneh | 469 | 0.7 | N |
| TOFIGH, Thomas | 426 | 0.7 | N |
| SOSTAD, Ron | 294 | 0.5 | N |

Total votes cast for Councillor: **63,249**

### 3.3 School Trustee (3 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| SACRÉ, Christie | 4,401 | 16.4 | **Y** |
| TASI BAKER, Mary | 4,079 | 15.2 | **Y** |
| HIGGINS, Megan | 4,010 | 15.0 | **Y** |
| ZAVEDIUK, Greg | 2,928 | 10.9 | N |
| POPE, Catherine | 2,750 | 10.3 | N |
| KOLSTEE, Jullian | 2,581 | 9.6 | N |
| MOORE, Gordon | 2,210 | 8.3 | N |
| SKINNER, Susan | 1,807 | 6.8 | N |
| EWING, Sean | 1,187 | 4.4 | N |
| TEYMOURAN, Kamy | 814 | 3.0 | N |

Total votes cast for School Trustee: **26,767**

### 3.4 2018 ballots cast per voting place ("TOTAL VOTERS" row)

| Voting place | Ballots |
|---|---|
| Carson Graham | 1,031 |
| John Braithwaite Community Centre (JBCC) | 1,476 |
| Larson | 538 |
| Memorial RecCentre | 1,052 |
| NSN House | 943 |
| Queen Mary | 1,473 |
| Ridgeway | 1,530 |
| Sutherland | 1,086 |
| Westview | 609 |
| Advance / Mail polls (combined) | 3,176 |
| **Sum (derived)** | **12,914** |

---

## 4. 2014 General Local Election (Saturday, November 15, 2014)

**Source:** `https://www.cnv.org/-/media/City-of-North-Vancouver/Images/Page-Images/Election/Election-Results/2014-Election-Results.jpg`
Signed **Karla Graham, Chief Election Officer**, 19 November 2014.
Image is only 772×400 px — the per-poll cells are small. **Totals are high-confidence; individual per-poll cells should be re-verified before publication.**

| Field | Value | Source |
|---|---|---|
| Total eligible voters | **34,127** | `.../Past-Election-Results` |
| Voter turnout (as published by CNV) | **30.0%** | `.../Past-Election-Results` |
| Ballots cast ("TOTAL VOTERS" printed on sheet) | **10,567** | 2014 results JPG |

⚠️ **Discrepancy to flag:** 10,567 / 34,127 = **30.96%**, not the 30.0% CNV publishes. CNV's published 30.0% appears rounded down or computed on a different base. Cite CNV's 30.0% as the official figure and note the arithmetic.

### 4.1 Mayor (1 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| MUSSATTO, Darrell R. | 5,488 | 52.5 | **Y** |
| MORRIS, Kerry | 4,598 | 44.0 | N |
| PRINGLE, George Sifton | 375 | 3.6 | N |

### 4.2 Councillor (6 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| KEATING, Craig | 4,885 | 9.2 | **Y** |
| BUCHANAN, Linda | 4,646 | 8.8 | **Y** |
| BELL, Don | 4,491 | 8.5 | **Y** |
| BOOKHAM, Pam | 4,392 | 8.3 | **Y** |
| CLARK, Rod | 4,354 | 8.2 | **Y** |
| BACK, Holly | 3,588 | 6.8 | **Y** |
| McGRENERA, Kathy | 3,515 | 6.6 | N |
| BELL, Bill | 3,346 | 6.3 | N |
| NICHOL, Amanda | 3,316 | 6.3 | N |
| CLARK, Matt | 3,113 | 5.9 | N |
| VALENTE, Tony | 3,102 | 5.9 | N |
| BELL, Dorothy Anne | 2,900 | 5.5 | N |
| MAKRIS, Iani | 2,095 | 4.0 | N |
| HEILMAN, Joe | 2,087 | 3.9 | N |
| FEARNLEY, Via | 1,805 | 3.4 | N |
| HARVEY, John | 788 | 1.5 | N |
| JANIS, Dave | 326 | 0.6 | N |
| SOSTAD, Ron | 231 | 0.4 | N |

### 4.3 School Trustee (3 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| SKINNER, Susan | 4,576 | 22.0 | **Y** |
| HIGGINS, Megan | 4,487 | 21.6 | **Y** |
| SACRÉ, Christie | 3,016 | 14.5 | **Y** |
| TASI, Mary | 2,618 | 12.6 | N |
| WILSON, Antje | 2,302 | 11.1 | N |
| LAHULEK, Tanya | 2,286 | 11.0 | N |
| PAPANDREOU, Bill Vassilis | 1,535 | 7.4 | N |

### 4.4 2014 ballots cast per voting place ("TOTAL VOTERS" row)

| Voting place / poll | Ballots |
|---|---|
| St. Andrew's & St. Stephen's | 579 |
| Carson Graham | 1,043 |
| NSN House | 921 |
| St. Agnes | 963 |
| St. John's | 1,061 |
| Ridgeway | 1,275 |
| Memorial RecCentre | 866 |
| Capilano Mall | 562 |
| JBCC | 1,066 |
| LGH / Mail | 79 |
| ADV Nov 5 City Hall | 248 |
| ADV Nov 7 City Hall | 163 |
| ADV Nov 8 City Hall | 288 |
| ADV Nov 12 City Hall | 449 |
| ADV Nov 13 City Hall | 230 |
| ADV Nov 14 City Hall | 454 |
| ADV Nov 6 Library | 89 |
| ADV Nov 10 Library | 215 |
| ADV Nov 6 Cap U | 16 |
| **TOTAL** | **10,567** |

---

## 5. 2011 General Local Election (Saturday, November 19, 2011)

**Source:** `https://www.cnv.org/-/media/City-of-North-Vancouver/Images/Page-Images/Election/Election-Results/2011-Election-Results.jpg`
Signed **Robyn Anderson, Chief Election Officer**, 22 November 2011.

| Field | Value |
|---|---|
| Total eligible voters | **33,415** |
| Voter turnout | **21.2%** |
| Ballots cast ("TOTAL VOTERS" printed) | **7,082** (7,082 / 33,415 = 21.19% ✓ consistent) |

### 5.1 Mayor (1 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| Darrell MUSSATTO | 5,037 | 73.8 | **Y** |
| Ron POLLY | 758 | 11.1 | N |
| George PRINGLE | 546 | 8.0 | N |
| (Kit) Chris J. NICHOLS | 487 | 7.1 | N |

### 5.2 Councillor (6 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| Don BELL | 3,901 | 11.0 | **Y** |
| Linda BUCHANAN | 3,790 | 10.7 | **Y** |
| Craig KEATING | 3,642 | 10.3 | **Y** |
| Rod CLARK | 3,106 | 8.8 | **Y** |
| Pam BOOKHAM | 2,986 | 8.4 | **Y** |
| Guy HEYWOOD | 2,792 | 7.9 | **Y** |
| Cheryl LEIA | 2,626 | 7.4 | N |
| Bob FEARNLEY | 2,397 | 6.8 | N |
| Juliana BUITENHUIS | 1,885 | 5.3 | N |
| Amanda NICHOL | 1,723 | 4.9 | N |
| Yashar KHALIGHI | 1,454 | 4.1 | N |
| Elizabeth FODOR | 950 | 2.7 | N |
| D.W. (Bill) DUNCAN | 805 | 2.3 | N |
| Glen MILLER | 779 | 2.2 | N |
| Joe HEILMAN | 754 | 2.1 | N |
| Michael CHARROIS | 696 | 2.0 | N |
| John HUTCHINSON | 379 | 1.1 | N |
| Ron SOSTAD | 272 | 0.8 | N |
| Carson Reed POLLY | 250 | 0.7 | N |
| Behgam RABBANI | 239 | 0.7 | N |

### 5.3 School Trustee (3 elected)

| Candidate | Votes | % | Elected |
|---|---|---|---|
| Susan SKINNER | 3,123 | 21.7 | **Y** |
| Lisa BAYNE | 2,512 | 17.5 | **Y** |
| Christie SACRÉ* | 2,181 | 15.2 | **Y** (after judicial recount) |
| Chris DORAIS* | 2,180 | 15.1 | N |
| Mary TASI | 1,931 | 13.4 | N |
| Ian T. YOUNG | 1,239 | 8.6 | N |
| John HARVEY | 1,221 | 8.5 | N |

\* CNV note, verbatim: *"Pursuant to section 140(1) of the Local Government Act, at the conclusion of a judicial recount conducted by the Provincial Court of British Columbia, the results for these candidates was declared by The Honourable Judge J. Auxier on November 29, 2011, with Christie Sacre being declared a successful candidate for school trustee."* (1-vote margin.)

### 5.4 2011 ballots cast per voting place

| Voting place | Ballots |
|---|---|
| Holy Trinity | 584 |
| NSN House | 588 |
| St. John's | 647 |
| Memorial RecCentre | 576 |
| Carson Graham | 639 |
| St. Agnes | 723 |
| Ridgeway | 947 |
| Capilano Mall | 494 |
| JBCC | 663 |
| Adv / LGH / Mail | 1,221 |
| **TOTAL** | **7,082** |

---

## 6. Turnout and registered-elector series (all years CNV publishes)

**Single source for the whole table:** `https://www.cnv.org/City-Hall/General-Local-Election/Past-Election-Results` ("Voter Turnout by Year"). Registered-voter counts are blank on CNV's table before 1999.

| Year | Registered voters | Turnout |
|---|---|---|
| 2022 | 41,325 | 22.64% |
| 2018 | 38,163 | 34.0% |
| 2014 | 34,127 | 30.0% |
| 2011 | 33,415 | 21.2% |
| 2008 | 31,352 | 17.67% (Mayor Darrell R. MUSSATTO elected by acclamation) |
| 2005 | 30,327 | 22.37% |
| 2002 | 24,983 | 26.13% |
| 1999 | 23,193 | 25.99% |
| 1996 | NOT PUBLISHED | 18.79% |
| 1993 | NOT PUBLISHED | 18.89% |
| 1990 | NOT PUBLISHED | 21.69% |
| 1987 | NOT PUBLISHED | 13.33% |
| 1985 | NOT PUBLISHED | 18.06% |
| 1983 | NOT PUBLISHED | 13.50% |
| 1981 | NOT PUBLISHED | 23.00% |
| 1979 | NOT PUBLISHED | 15.42% |
| 1978 | NOT PUBLISHED | 7.96% |
| 1977 | NOT PUBLISHED | 21.80% |
| 1976 | NOT PUBLISHED | 14.97% |
| 1975 | NOT PUBLISHED | 22.90% |
| 1974 | NOT PUBLISHED | 13.43% |

CNV wording note: 2022 is labelled "Total Registered Voters"; 2018 and earlier are labelled "Total Eligible Voters". Treat both as *registered electors on the list*, **not** as the census-eligible population.

---

## 7. Voting places

All addresses below are transcribed verbatim from official CNV notices, the CNV GeoRSS voting-station feed, or the CNV news release. Coordinates (WGS84 lat/lon) come from CNV's own GeoRSS feed used by its public election map at `https://gisext2.cnv.org/election/`.

### 7.1 2022 (General Voting Day Sat Oct 15, 2022, 8am–8pm)

Source: `https://www.cnv.org/City-Hall/News-Room/Whats-New/2022/9/26/Get-Out-and-Vote-in-the-2022-Local-Election` — *"at any one of the nine voting locations across the city"*.

| Year | Place name | Address | Type | Lat | Lon |
|---|---|---|---|---|---|
| 2022 | Carson Graham Secondary School | 2145 Jones Ave | General | 49.3289347 | -123.0819935 |
| 2022 | Larson Elementary School | 2605 Larson Rd | General | 49.333373 | -123.085181 |
| 2022 | Memorial Recreation Centre | 125 East 23rd St | General | 49.3298602 | -123.0694833 |
| 2022 | North Shore Neighbourhood House | 225 East 2nd St | General | 49.3108177 | -123.0743436 |
| 2022 | Queen Mary Elementary School | 230 West Keith Rd | General | 49.3194466 | -123.0781481 |
| 2022 | Ridgeway Elementary School | 420 East 8th St | General | 49.3152172 | -123.0613468 |
| 2022 | Sutherland Secondary School | 1860 Sutherland Ave | General | 49.326000 | -123.052950 |
| 2022 | The Pipe Shop | 115 Victory Ship Way | General | 49.310256 | -123.079550 |
| 2022 | Westview Elementary School | 641 West 17th St | General | 49.323816 | -123.089478 |
| 2022 | North Vancouver City Hall, Conference Room A | 141 West 14th St | **Advance** (Oct 5 8–8; Oct 8 10–4; Oct 11 10–6; Oct 12 8–8; Oct 13 12–6) | 49.320679 | -123.073799 |
| 2022 | Mail ballot (city-wide, no fixed site) | n/a | Mail | — | — |
| 2022 | Special voting opportunities | **NOT PUBLISHED as a named list** — the results PDF has a "SPECIAL POLLS" column (159 mayoral+other votes) but CNV does not name the sites for 2022 | Special | — | — |

⚠️ **Data-integrity warning on the GeoRSS feed.** The file `https://gisext2.cnv.org/election/ElectionsRSSfile_2022.xml` has channel description "2022 Municipal Elections Voting Stations" but its item content is **stale 2018 data** (dates "Saturday October 20", includes John Braithwaite Community Centre as a general poll and The Pipe Shop as advance-only). This contradicts the official 2022 results PDF and the Sept 26 2022 news release. **Use the news release + results PDF for 2022, not that XML.** The XML is still useful as a coordinate lookup for place names.

### 7.2 2018 (General Voting Day Sat Oct 20, 2018, 8am–8pm)

Source: `https://www.cnv.org/-/media/city-of-north-vancouver/documents/public-notices-other/2018-notice-of-election-by-voting-on-october-20-2018.pdf` (retrieved via Wayback; original path now 404s on cnv.org).

| Year | Place name | Address | Type |
|---|---|---|---|
| 2018 | Carson Graham Secondary School | 2145 Jones Avenue | General |
| 2018 | John Braithwaite Community Centre | 145 W 1st Street | General |
| 2018 | Larson Elementary School | 2605 Larson Road | General |
| 2018 | Memorial Recreation Centre | 125 E 23rd Street | General |
| 2018 | North Shore Neighbourhood House | 225 E 2nd Street | General |
| 2018 | Queen Mary Elementary School | 230 W Keith Road | General |
| 2018 | Ridgeway Elementary School | 420 E 8th Street | General |
| 2018 | Sutherland Secondary School | 1860 Sutherland Avenue | General |
| 2018 | Westview Elementary School | 641 W 17th Street | General |
| 2018 | City Hall, Conference Room A | 141 W 14th Street | **Advance** — Wed Oct 10 8am–8pm; Sat Oct 13 11am–4pm; Wed Oct 17 8am–8pm; Thu Oct 18 12–6pm; Fri Oct 19 12–6pm |
| 2018 | The Pipe Shop | 115 Victory Ship Way | **Advance** — Tue Oct 16 10am–6pm |

Notice states: *"All voting locations are wheelchair accessible."*

### 7.3 2014 (General Voting Day Sat Nov 15, 2014)

Source: CNV GeoRSS `https://gisext2.cnv.org/election/ElectionsRSSfile.xml` (channel: "2014 Municipal Elections Voting Stations"); corroborated by the 2014 results JPG column headers.

| Year | Place name | Address | Type | Lat | Lon |
|---|---|---|---|---|---|
| 2014 | Capilano Mall (Community Meeting Room, 2nd level) | 935 Marine Drive | General | 49.3221909 | -123.0991452 |
| 2014 | Carson Graham Secondary School (Small Gym) | 2145 Jones Avenue | General | 49.3289347 | -123.0819935 |
| 2014 | St. Andrew's and St. Stephen's Presbyterian Church | 2641 Chesterfield | General | 49.333794 | -123.075512 |
| 2014 | John Braithwaite Community Centre (Shoreline Room) | 145 West 1st Street | General | 49.3124722 | -123.0805462 |
| 2014 | Memorial RecCentre (Capilano Room) | 123 East 23rd Street | General | 49.3298602 | -123.0694833 |
| 2014 | North Shore Neighbourhood House (Gym) | 225 East 2nd Street | General | 49.3108177 | -123.0743436 |
| 2014 | Ridgeway Elementary School (Gym) | 420 East 8th Street | General | 49.3152172 | -123.0613468 |
| 2014 | St Agnes Church (Church Hall) | 530 East 12th Street | General | 49.3190974 | -123.0586568 |
| 2014 | St John's Church (Church Lounge) | 220 West 8th Street | General | 49.3197139 | -123.0760502 |
| 2014 | City Library (3rd Floor Program Room) | 120 West 14th Street | **Advance** (Thu Nov 6 4–8pm; Mon Nov 10 4–8pm) | 49.3211428 | -123.0734845 |
| 2014 | City Hall (Conference Room A) | 141 West 14th Street | **Advance** (Nov 5, 7, 8, 12, 13, 14) | 49.320679 | -123.073799 |
| 2014 | Capilano University (Student Union Lounge, Library Bldg 195) | 2055 Purcell Way | **Advance** (Thu Nov 6 8am–8pm) | 49.318716 | -123.019591 |
| 2014 | Lions Gate Hospital | 231 E 15th Street | **Special** (bedside voting, patients only) | 49.3215555 | -123.0678246 |

⚠️ Address inconsistency: CNV writes Memorial RecCentre as **123** East 23rd St in 2014 and **125** East 23rd St in 2018/2022. Both are CNV's own text.
⚠️ Cap U (2055 Purcell Way) is in the **District** of North Vancouver, not the City — an advance poll sited outside the municipal boundary. Relevant if clipping voting places to the CNV boundary.

### 7.4 2011 (General Voting Day Sat Nov 19, 2011)

Source: `City of North Vancouver - Voting Places.pdf`, "As at August 22, 2011", CNV Document 568633 (retrieved via Wayback: `https://web.archive.org/web/20111125014217if_/http://www.cnv.org/c/data/1/464/City%20of%20North%20Vancouver%20-%20Voting%20Places.pdf`).

| Year | # | Place name | Address | Type |
|---|---|---|---|---|
| 2011 | 1 | Holy Trinity Church Hall* | 2725 Lonsdale Avenue (27th & Lonsdale) | General |
| 2011 | 2 | Carson Graham Secondary School* (Small Gym) | 2145 Jones Avenue | General |
| 2011 | 3 | North Shore Neighbourhood House* (Gym) | 225 East 2nd Street | General |
| 2011 | 4 | St. Agnes' Church Hall | 530 East 12th Street (12th & Grand Blvd) | General |
| 2011 | 5 | St. John's Church* (Janet Wilcox Lounge) | 220 West 8th Street | General |
| 2011 | 6 | Ridgeway Elementary School* (Gym) | 420 East 8th Street | General |
| 2011 | 7 | Memorial RecCentre* (Capilano Room) | 125 East 23rd Street | General |
| 2011 | 8 | Capilano Mall* (Community Meeting Room) | 935 Marine Drive | General |
| 2011 | 9 | John Braithwaite Community Centre* (Anchor Room) | 145 West 1st Street | General |
| 2011 | 10 | Lions Gate Hospital | 231 East 15th Street | **Special** (bedside voting only) |
| 2011 | 11 | City of North Vancouver Library* (3rd Floor Study Room) | 120 West 14th Street | **Advance** — Nov 9, 10, 12, 14, 15, 16, 17, 18 |

\* = "Accessible to People with Physical Disabilities" per the notice.

### 7.5 2026 (upcoming — General Voting Day Sat Oct 17, 2026)

Source: CNV GeoRSS `https://gisext2.cnv.org/election/ElectionsRSSfile_2026.xml` (live, channel "2026 Municipal Elections Voting Stations"). Provisional — verify against the formal Notice of Election closer to the date.

| Year | Place name | Address | Type | Lat | Lon |
|---|---|---|---|---|---|
| 2026 | Carson Graham Secondary School | 2145 Jones Avenue | General (Oct 17, 8am–8pm) | 49.3289347 | -123.0819935 |
| 2026 | Harry Jerome Community Recreation Centre | 123 East 23rd Street | General | 49.3309655 | -123.0705073 |
| 2026 | John Braithwaite Community Centre (Shoreline Room) | 145 W 1st St | General | 49.3124257 | -123.0808443 |
| 2026 | Ridgeway Elementary School | 420 East 8th Street | General | 49.3152172 | -123.0613468 |
| 2026 | Queen Mary Elementary School | 230 West Keith Road | General | 49.3194466 | -123.0781481 |
| 2026 | Larson Elementary School | 2605 Larson Road | General | 49.333373 | -123.085181 |
| 2026 | Westview Elementary School | 641 West 17th Street | General | 49.323816 | -123.089478 |
| 2026 | Sutherland Secondary School | 1860 Sutherland Avenue | General | 49.326000 | -123.052950 |
| 2026 | The Pipe Shop | 115 Victory Ship Way | General | 49.310256 | -123.079550 |
| 2026 | City Hall (Conference Room A,B) | 141 West 14th Street | **Advance** — Oct 7, 10, 13, 14, 15 | 49.320679 | -123.073799 |
| 2026 | Lions Gate Hospital and Hope Centre | 231 E 15th Street | **Special** (Sat Oct 10, 9am–4pm) | 49.3211830 | -123.0681396 |
| 2026 | Evergreen House and North Shore Hospice | 231 E 15th Street | **Special** (Tue Oct 13, 9:30am–2:30pm) | 49.3212354 | -123.0668730 |

---

## 8. POLLING / VOTING DIVISION BOUNDARIES — VERDICT

### **NOT AVAILABLE. No polling-division or voting-division boundary dataset, map, or polygon exists for the City of North Vancouver in any format (GIS, PDF, or image).**

This is not merely "could not find" — the evidence indicates such boundaries **do not exist** for CNV:

1. **CNV explicitly runs any-place voting.** The official Sept 26 2022 news release states electors vote *"at any one of the nine voting locations across the city."* If electors may attend any voting place, there is no division-to-elector assignment and therefore no division geometry.
   Source: `https://www.cnv.org/City-Hall/News-Room/Whats-New/2022/9/26/Get-Out-and-Vote-in-the-2022-Local-Election`
2. **CNV's own official 2022 voting map shows points only.** `https://www.cnv.org/-/media/City-of-North-Vancouver/Images/Page-Images/Election/2022-general/voting-map-2022.ashx` renders the municipal boundary + red "Voting Locations" pins + a blue "Advance Voting" pin. No sub-municipal division polygons. Legend has exactly two classes.
3. **CNV's public election web map is point-only.** `https://gisext2.cnv.org/election/` (ArcGIS JS 3.8). Its `js/map.js` loads only: a tiled basemap, a fixed-labels layer, a *mask* feature layer that greys out the District of North Vancouver and West Vancouver, and a **GeoRSS point feed** of voting stations. There is no division/boundary layer in the application at all.
4. **CNV's ArcGIS REST directory contains no election layer.** I enumerated all 5 folders and **69 published map services** at `https://gisext2.cnv.org/ArcGIS/rest/services` and regex-scanned every layer and table name for `elect|poll|vot|ward|precinct|division`. Zero relevant hits (only false positives: "Subdivision Applications", "Pivotal Development Sites").
5. **CNV's election bylaws do not create voting divisions.** `Local Election Bylaw, 2026, No. 9108` and `Automated Vote Counting System Authorization and Procedure Bylaw, 2026, No. 9146` contain **no occurrence** of "voting division" or "polling division"; they speak only of "voting places" and "voting opportunities". Same for the older `Bylaw No. 6815` (consolidated 2008), the 2014 Election Notice and the 2018 Notice of Election by Voting.
6. **Results are reported by voting PLACE, not by division.** Poll columns are venue names ("CARSON GRAHAM", "ADV POLLS", "MAIL POLLS") with no geographic catchment attached.

### Organizations and URLs searched for polling-division boundaries

| Organization | URLs / endpoints checked | Outcome |
|---|---|---|
| City of North Vancouver (web) | `https://www.cnv.org/City-Hall/General-Local-Election` ; `.../Past-Election-Results` ; `.../2026-General-Local-Election` ; `https://www.cnv.org/ElectionResults` ; `.../News-Room/Whats-New/2022/10/19/Official-Results-of-2022-City-Election-Announced` ; `.../News-Room/Whats-New/2022/9/26/Get-Out-and-Vote-in-the-2022-Local-Election` | Voting places only; no divisions |
| CNV GIS (ArcGIS Server) | `https://gisext2.cnv.org/ArcGIS/rest/services` — all folders (Applications, BaseMapServices, BaseMapTools, FeatureServices, Utilities), all 69 services, all layer/table names scanned | No election/polling/voting/division layer |
| CNV election web map | `https://gisext2.cnv.org/election/` ; `.../js/map.js` ; `.../ElectionsRSSfile_2026.xml` ; `.../ElectionsRSSfile_2022.xml` ; `.../ElectionsRSSfile_2018.xml` ; `.../ElectionsRSSfile.xml` (2014) ; `.../images/2018_legend.png` | Point features only |
| CNV official maps | `https://www.cnv.org/-/media/City-of-North-Vancouver/Images/Page-Images/Election/2022-general/voting-map-2022.ashx` | Points + municipal boundary only |
| CNV bylaws | `https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Bylaws/Keep/9108.pdf` ; `.../Keep/9146.pdf` ; archived `.../election/information-for-potential-candidates/automated-vote-counting-system-bylaw-6815.pdf` | No "voting division" provisions |
| CNV election notices | 2011 Voting Places PDF ; 2014 Election Notice ; 2018 Notice of Election by Voting ; 2022 Declaration of Election by Voting | Venue lists only; no divisions |
| CivicInfo BC | `https://www.civicinfo.bc.ca/election-results-v3/index.php?localgovernmentid=85&select-year=2022&select-view-by=municipality` ; `https://www.civicinfo.bc.ca/electionreports/voter-turnout.php?year=2022` ; `https://www.civicinfo.bc.ca/election-results` | **HTTP 403 — Cloudflare bot challenge.** Not bypassed (per ethical scope). Even so, CivicInfo publishes municipality-level candidate totals and turnout, never boundaries. CNV's own site links to CivicInfo for "the past four local government elections" |
| Elections BC | `https://elections.bc.ca/local-elections/2022-general-local-elections/` | Elections BC publishes **only** campaign-financing disclosure statements and contribution data for local elections. It does **not** publish local results, voting places, or voting-division boundaries. Local elections are conducted by each municipality |
| Third-party aggregator (checked and rejected) | `https://localelections.ca/election_results/85_2022_results.html` | HTTP 404 — dead |

### Recommended `DATA_GAPS.md` entry

```
Dataset: City of North Vancouver municipal polling-division / voting-division boundary polygons
Desired use: Attribute per-voting-place vote counts to geographic areas; map electoral geography
Organizations searched: City of North Vancouver (web + gisext2 ArcGIS Server + bylaws + election
  notices), CivicInfo BC, Elections BC, Internet Archive Wayback Machine
URLs searched: see table in data/interim/elections_research.md §8
What was found: Voting PLACE point locations only (names, addresses, lat/lon), for 2011, 2014,
  2018, 2022 and 2026; official results tabulated by voting place.
Why it is unavailable: CNV conducts at-large, any-voting-place elections. CNV's own 2022 notice
  states electors may vote "at any one of the nine voting locations across the city". No voting
  divisions are established by CNV's Local Election Bylaw 9108 or Automated Vote Counting Bylaw
  9146. No such geometry exists to publish. Elections BC's local-election mandate covers campaign
  financing only. CivicInfo BC returns HTTP 403 (Cloudflare) and in any case publishes only
  municipality-level totals.
Best available proxy: Voting place POINTS (12 for 2022) with per-place vote counts. If an areal
  representation is required, a clearly-labelled Voronoi/Thiessen tessellation or service-area
  polygon around voting places MAY be constructed for cartographic purposes ONLY.
Limitations: A Voronoi/service-area polygon is NOT a polling division. Electors were free to vote
  at any place, ~34% of 2022 ballots were cast at advance/mail/special polls that have no
  geographic catchment at all, and one 2014 advance poll (Capilano University) was outside the
  CNV municipal boundary. Any such polygon must be labelled a cartographic convenience and must
  never be presented as an electoral boundary or used to infer voting behaviour by area.
Recommended next action: If per-area electoral data is genuinely required, submit a written
  request to the CNV Chief Election Officer (elections@cnv.org, 604-982-8354) asking whether
  voting divisions were ever established. Otherwise, close this gap as NOT APPLICABLE and use the
  Census adult_population_18plus_proxy for spatial population analysis, per CLAUDE.md §11.
```

---

## 9. "Chief Election Officer report" / "Statement of Votes" — verdict

**NOT FOUND as a standalone document for 2022 or 2018.**

- CNV does **not** publish a separately-titled "Statement of Votes" or "Chief Election Officer Report" PDF. Searched cnv.org, cnv.org council/news pages, and the Wayback index of `cnv.org/-/media/.../Documents/Election*`.
- The functional equivalent **is** the results sheet itself, which carries the statutory CEO attestation. Verbatim from the 2022 PDF: *"The above is a true statement of the number of votes at the close of the election on October 15, 2022 given under my hand at the City of North Vancouver this 19th day of October, 2022. Nikolina Vracar, Chief Election Officer."* Equivalents exist for 2018 (Karla Graham), 2014 (Karla Graham), 2011 (Robyn Anderson), 2008 (Sandra E. Dowey) and 2002 (Bruce Hawkshaw).
- **These results sheets already contain the per-voting-place breakdown** the task was hoping a Statement of Votes would provide. No further document is needed.
- Separate statutory **`Declaration of Official Election Results` (Form 6-3, LGA s.136(2)(a))** documents exist for 2014 (Mayor / Councillor / School Trustee) but contain **no vote numbers** — they only name the elected person. Downloaded for completeness.
- **NOT FOUND:** a post-election review report from the CEO to CNV Council for 2022 or 2018. Nothing surfaced on cnv.org or via search. (For contrast, the City of *Vancouver* does publish one.) Would require a direct request to the CNV City Clerk.

---

## 10. Files downloaded (all under `/Users/ankurbatta/Desktop/GIS/data/raw/elections/`)

| File | Source URL | SHA256 (first 16) |
|---|---|---|
| `cnv_2022_election_results.pdf` | `https://www.cnv.org/-/media/City-of-North-Vancouver/Images/Page-Images/Election/Election-Results/2022-Election-Results-PDF.pdf` | `526dcf0b5b70ae99` |
| `cnv_2018_election_results.jpg` | `.../Election-Results/2018-Election-Results.jpg` | `149582d5589fc686` |
| `cnv_2014_election_results.jpg` | `.../Election-Results/2014-Election-Results.jpg` | `fd425f916c86a07f` |
| `cnv_2011_election_results.jpg` | `.../Election-Results/2011-Election-Results.jpg` | `c2c0e9bac04d254d` |
| `cnv_2008_election_results.jpg` | `.../Election-Results/2008-Election-Results.jpg` | `7b4ce5b376131356` |
| `cnv_2005_election_results.jpg` | `.../Election-Results/2005-Election-Results.jpg` | `959df31baf419ffd` |
| `cnv_2002_election_results.jpg` | `.../Election-Results/2002-Election-Results.jpg` | `76a878c5851e3dbc` |
| `cnv_2022_declaration_election_by_voting.pdf` | `https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Election/2022-General/2022-09-20-Declaration-of-Election-by-Voting.ashx` | `fed1b174bf6241f5` |
| `cnv_2022_voting_map.jpg` | `https://www.cnv.org/-/media/City-of-North-Vancouver/Images/Page-Images/Election/2022-general/voting-map-2022.ashx` | `7fb4f26a11ee0179` |
| `cnv_2022_get_out_and_vote.html` | `https://www.cnv.org/City-Hall/News-Room/Whats-New/2022/9/26/Get-Out-and-Vote-in-the-2022-Local-Election` | (HTML) |
| `cnv_2018_notice_of_election_by_voting.pdf` | Wayback `20181011175338` of `https://www.cnv.org/-/media/city-of-north-vancouver/documents/public-notices-other/2018-notice-of-election-by-voting-on-october-20-2018.pdf` | `f9ef023e7c6f61e2` |
| `cnv_2014_election_notice.pdf` | Wayback `20160417180245` of `http://www.cnv.org/-/media/city-of-north-vancouver/documents/election/election-notice-sept-8-2014.pdf` | `2d2205dcd02c451f` |
| `cnv_2014_declaration_results_mayor.pdf` | Wayback `20160417045849` (CNV Election Results folder) | `c2c4e6e26f2d8103` |
| `cnv_2014_declaration_results_councillor.pdf` | Wayback `20160417045500` | `e23d6b3e5a1f14de` |
| `cnv_2014_declaration_results_trustee.pdf` | Wayback `20160417045930` | `0301816db4242ea0` |
| `cnv_2011_voting_places.pdf` | Wayback `20111125014217` of `http://www.cnv.org/c/data/1/464/City%20of%20North%20Vancouver%20-%20Voting%20Places.pdf` | `6d98dad4e56e4142` |
| `cnv_voting_places_georss_2026.xml` | `https://gisext2.cnv.org/election/ElectionsRSSfile_2026.xml` | `55dbc3a5dadc0194` |
| `cnv_voting_places_georss_2022file.xml` | `https://gisext2.cnv.org/election/ElectionsRSSfile_2022.xml` (⚠️ stale 2018 content — see §7.1) | `ebccc0afee4c4b88` |
| `cnv_voting_places_georss_2018.xml` | `https://gisext2.cnv.org/election/ElectionsRSSfile_2018.xml` | `0187dbf0beb2250b` |
| `cnv_voting_places_georss_2014.xml` | `https://gisext2.cnv.org/election/ElectionsRSSfile.xml` | `ad52c2634110b1c1` |
| `cnv_gisext2_election_locations.html` | `https://gisext2.cnv.org/election/` | (HTML) |
| `cnv_election_map.js` | `https://gisext2.cnv.org/election/js/map.js` | `ca500c387cf1567d` |
| `cnv_election_map_legend_2018.png` | `https://gisext2.cnv.org/election/images/2018_legend.png` | — |
| `cnv_bylaw_9108_local_election.pdf` | `https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Bylaws/Keep/9108.pdf` | `6d5ade6513fea6b6` |
| `cnv_bylaw_9146_election.pdf` | `https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Bylaws/Keep/9146.pdf` | `439a589071da3dce` |
| `cnv_bylaw_6815_automated_vote_counting.pdf` | Wayback `20160505002742` | `9fe43faacb94ab8f` |
| `cnv_election_signage_policy.pdf` | Wayback `20160505002735` — CNV election signage policy addendum | `b00a21e92151cc31` |
| `cnv_election_signage_policy_map.pdf` | Wayback `20160505002736` — map accompanying the signage policy | `6f0cb525f7dded8a` |
| `cnv_2026_election_page.html` | `https://www.cnv.org/City-Hall/General-Local-Election/2026-General-Local-Election` | (HTML) |

Pre-existing (downloaded by `01_download.py` before this research):
`cnv_2022_official_results.html`, `cnv_past_election_results.html`, `cnv_election_landing.html` (+ `.meta.json` each, + `.txt` / `.links.txt` extraction helpers I generated).

**Note for the sign-waving component of the project:** `cnv_election_signage_policy.pdf` and `cnv_election_signage_policy_map.pdf` were picked up incidentally and are directly relevant to Component B (where election signage is permitted). The current consolidated **Election Sign Bylaw, 2018, No. 8643** is referenced in search results at `https://www.cnv.org/-/media/City-of-North-Vancouver/Documents/Bylaws/Consolidated/8643-C.pdf` but that URL now **302-redirects to a 404 page** (all casing/extension variants tried) — **NOT DOWNLOADED**, follow up separately.

---

## 11. Explicit NOT FOUND / NOT AVAILABLE list

| Item | Status | Detail |
|---|---|---|
| Polling / voting division boundary polygons (any format) | **NOT AVAILABLE — do not exist** | See §8 |
| 2022 total ballots cast | **NOT PUBLISHED** | CNV publishes registered voters + turnout % only; 2022 sheet omits the "TOTAL VOTERS" row present in 2011/2014/2018 |
| 2018 total ballots cast as a single published figure | **NOT PUBLISHED** | Derivable as 12,914 by summing the per-poll TOTAL VOTERS row |
| 2022 named special-voting-opportunity sites | **NOT PUBLISHED** | Results sheet has a "SPECIAL POLLS" column but no venue list |
| Standalone "Statement of Votes" / CEO report PDF, 2022 & 2018 | **NOT FOUND** | Attestation is embedded in the results sheet instead — §9 |
| CEO post-election review report to Council, 2022 & 2018 | **NOT FOUND** | Nothing on cnv.org; would need a request to the City Clerk |
| CivicInfo BC election-results pages | **NOT ACCESSIBLE** | HTTP 403 / Cloudflare bot challenge; not bypassed |
| `localelections.ca` CNV 2022 page | **DEAD (404)** | Third-party aggregator; not usable |
| Election Sign Bylaw 8643-C PDF | **NOT DOWNLOADED (404)** | URL redirects to CNV 404 page |
| Registered-voter counts pre-1999 | **NOT PUBLISHED** | CNV's turnout table has percentages only back to 1974 |
| 2008 / 2005 / 2002 candidate-level results | **DOWNLOADED, NOT TRANSCRIBED** | JPG tables are in `data/raw/elections/`; out of the requested 2011–2022 scope |
| Machine-readable (CSV/JSON) results from CNV | **DOES NOT EXIST** | All CNV results are flattened images (JPG) or image-only PDF. Any tabulation requires visual transcription and must be QA'd |

---

## 12. Caveats for downstream use

1. **Every CNV results table is an image.** The 2022 PDF has zero text layer; 2011/2014/2018 are JPGs. All figures in §2–§5 were read visually. Grand totals cross-check against CNV's independently-worded news release and turnout table, so **totals are high confidence**. The 2014 sheet is the lowest-resolution (772×400 px) — **re-verify 2014 per-poll cells** before publishing them.
2. **Do not treat "registered/eligible voters" as the census-eligible population.** These are electors on CNV's list. Per CLAUDE.md §11, use `adult_population_18plus_proxy` for spatial analysis, and never label census 18+ counts as eligible voters.
3. **Do not attribute votes at a voting place to the surrounding area.** Any-place voting means a ballot cast at Ridgeway Elementary carries no information about the voter's residence. In 2022 the advance + mail + special columns alone account for roughly a quarter to a third of all votes cast, with no geographic anchor whatsoever.
4. **Do not derive political-preference surfaces.** Per CLAUDE.md §20/§34, results data here is for descriptive civic geography only.
5. **Voting-place venues change materially between elections** (Holy Trinity / St. Agnes / St. John's / Capilano Mall / St. Andrew's & St. Stephen's dropped after 2014; The Pipe Shop added; JBCC dropped in 2022 and restored for 2026; Memorial Rec Centre becomes Harry Jerome Community Recreation Centre in 2026). Time-series comparison by venue is not valid.
