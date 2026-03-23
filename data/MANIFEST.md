# Data Manifest
**Project:** Electrification WTP Extension
**Papers:** Lee, Miguel & Wolfram (JEP 2019; JPE 2019)
**Last updated:** 2026-03-22

---

## 1. JEP Package — `data/jep/`

**Source paper:** "Does Household Electrification Supercharge Economic Development?"
*Journal of Economic Perspectives*, Lee, Miguel & Wolfram (2019)

### Datasets (`data/jep/data/`)

| File | Format | Size | Content |
|---|---|---|---|
| `demand.dta` | Stata .dta | 707 KB | 2014 baseline household survey + experimental demand data (from JPE study) |
| `impacts_1.dta` | Stata .dta | 1.2 MB | 2016 R1 household follow-up survey (from JPE study) |
| `fig_1.dta` | Stata .dta | 931 KB | World Bank DataBank: electricity access rates + GDP per capita (Figure 1) |
| `fig_2a.dta` | Stata .dta | 11 KB | Labor supply impact estimates from literature (Figure 2a) |
| `fig_2b.dta` | Stata .dta | 9 KB | Education impact estimates from literature (Figure 2b) |
| `fig_3.dta` | Stata .dta | 6.2 KB | Key coefficient estimates from Appendix Table A1 (Figure 3) |
| `fig_A2.dta` | Stata .dta | 6.6 KB | Income impact estimates from literature (Appendix Figure A2) |
| `fig_3.xlsx` | Excel .xlsx | 12 KB | Source spreadsheet for fig_3 bar chart calculations |

### Do-files and Outputs

| Do-file | Inputs | Outputs |
|---|---|---|
| `fig_1/fig_1.do` | `data/fig_1.dta` | `fig_1.png`, `Figure-1.pdf` |
| `fig_2/fig_2.do` | `data/fig_2a.dta`, `data/fig_2b.dta` | `fig_2a.png`, `fig_2b.png`, `Figure-2.pdf` |
| `fig_3/fig_3.do` | `data/fig_3.dta` | `fig_3a.png`–`fig_3f.png`, `Figure-3.pdf` |
| `fig_A1/` | Satellite + population raster data (external) | `Appendix-Figure-1.pdf` (pre-compiled) |
| `fig_A2/fig_A2.do` | `data/fig_A2.dta` | `fig_A2.png`, `Appendix-Figure-2.pdf` |
| `tab_A1_A2/tab_A1_A2.do` | `data/impacts_1.dta` | `tab_A1_c1.tex`, `tab_A1_c2_c3.tex`, `tab_A1_c4.tex`, `tab_A2_c1_c2.tex`, `tab_A2_c3.tex` → Appendix Tables A1, A2 |
| `tab_A3_A4/tab_A3_A4.do` | `data/demand.dta` | `.tex` + `tab_A4.csv` → Appendix Tables A3, A4 |

**Note on `tab_A1_A2.do`:** This is the primary **appliance heterogeneity do-file**. It estimates weighted-average LATEs by adopter type (low-price vs. high-price adopters) across 13 outcome variables: grid electricity spending, kerosene spending, total energy spending, asset value, `number_appliances`, `mobilephone`, `radio`, `television`, `iron`, `solar_shs`, income, consumption, and an additional measure. Uses only R1 (`impacts_1.dta`).

**Note on `fig_A1`:** The satellite (NOAA DMSP-OLS) and gridded population (GPWv4) source files are not included due to size. Methodology is documented in `fig_A1/Methodology.pdf`.

---

## 2. JPE Package — `data/jpe/`

**Source paper:** "Experimental Evidence on the Economics of Rural Electrification"
*Journal of Political Economy*, Lee, Miguel & Wolfram (April 2019)

### Datasets (`data/jpe/data/stata/`)

| File | Format | Size | Content |
|---|---|---|---|
| `demand.dta` | Stata .dta | 707 KB | 2014 baseline household survey + experimental demand data |
| `costs.dta` | Stata .dta | 31 KB | 2014–15 connection construction costs |
| `impacts_1.dta` | Stata .dta | 985 KB | 2016 R1 household follow-up survey |
| `impacts_s.dta` | Stata .dta | 716 KB | 2016 R1 spillover households survey |
| `impacts_2.dta` | Stata .dta | 800 KB | 2017 R2 household follow-up survey |

### Do-files and Outputs (`data/jpe/code/`)

| Do-file | Lines | Inputs | Outputs |
|---|---|---|---|
| `1_figures.do` | 622 | `demand.dta`, `impacts_1.dta`, `impacts_2.dta` | Main figures: `figure1a–c.png`, `figure2a–c.png`, `figure3a–c.png` |
| `2_tables.do` | 231 | `demand.dta`, `impacts_1.dta`, `impacts_2.dta` | `tables/tab1.tex`, `tables/tab2.tex` |
| `3_impacts.do` | 624 | `impacts_1.dta` + `impacts_s.dta` (appended), then `impacts_2.dta` | Tables 3, B6A, B6B, B6C |
| `4_appendix_figures.do` | 2,107 | Multiple .dta files | Appendix figures `figb1`–`figb15` |
| `5_appendix_tables.do` | 1,369 | `costs.dta` + multiple .dta | Appendix tables `taba1`, `tabb3a–c`, `tabb4a–e`, `tabb8a–c` |

**Note on `3_impacts.do`:** Appends `impacts_1.dta` and `impacts_s.dta` for R1 analysis, then separately loads `impacts_2.dta` for R2. Outcome variables include `number_appliances`, `mobilephone`, `radio`, `television`, `iron`, `solar_shs` alongside energy, income, employment, and wellbeing outcomes.

---

## 3. Follow-up Survey Data — R1 and R2

**Confirmation: Both R1 and R2 data are present.**

### Survey PDFs (`data/jpe/surveys/`)

| File | Round | Year | Size |
|---|---|---|---|
| `Baseline Survey Questions (2014).pdf` | Baseline | 2014 | 1.7 MB |
| `Round 1 Follow-up Survey Questions (2016).pdf` | **R1** | 2016 | 3.3 MB |
| `Round 1 Follow-up Survey Questions (2017).pdf` | **R2** | 2017 | 2.0 MB |

> **Note:** The R2 survey PDF is mislabeled — its filename says "Round 1" but it covers the 2017 follow-up (R2). The correct round is identified by the year.

### Survey Data Files

| File | Round | Location |
|---|---|---|
| `impacts_1.dta` | **R1** (2016) | `data/jpe/data/stata/` and `data/jep/data/` |
| `impacts_s.dta` | **R1** (2016) spillover | `data/jpe/data/stata/` only |
| `impacts_2.dta` | **R2** (2017) | `data/jpe/data/stata/` only |

---

## 4. Appliance Heterogeneity Analysis — Gaps and Flags

### What is available
- Appliance adoption variables in `impacts_1.dta` and `impacts_2.dta`: `number_appliances`, `mobilephone`, `radio`, `television`, `iron`, `solar_shs`
- `tab_A1_A2.do` (JEP) already produces LATE heterogeneity by adopter type for appliance outcomes using R1
- `3_impacts.do` (JPE) tracks appliance outcomes across R1 and R2 in a pooled regression framework

### Missing / Gaps

| # | Gap | Notes |
|---|---|---|
| 1 | **No appliance usage intensity data** | All appliance variables are binary adoption indicators; no hours of use, kWh consumed per appliance, or appliance-specific energy consumption |
| 2 | **No appliance purchase cost data** | `costs.dta` covers grid connection and infrastructure costs only; no dataset on appliance prices paid by households |
| 3 | **No R2 appliance heterogeneity table** | `tab_A1_A2.do` uses only R1 (`impacts_1.dta`); R2 appliance effects by adopter type are not tabulated in any JEP do-file |
| 4 | **`impacts_2.dta` unused in JEP package** | The R2 dataset exists in `data/jpe/data/stata/` but is not called by any do-file in `data/jep/`; R2 appliance estimates are only in JPE outputs |
| 5 | **No baseline appliance ownership stratification file** | Heterogeneity by pre-existing appliance ownership (e.g., already owned a radio) is not pre-computed; would need to be constructed from `demand.dta` |
| 6 | **All documentation files are empty** | `CONTEXT.md`, `EXTENSION_NOTE.md`, `REPLICATION_NOTE.md`, `VARIABLES.md` are all 0 bytes |

---

## 5. Willingness-to-Pay Heterogeneity — What Exists and What is Missing

### WTP Variables (in `demand.dta`)

| Variable | Description |
|---|---|
| `WTP_amt` | Randomly assigned CV price (0, 10k, 15k, 20k, 25k, 35k, 75k KES) |
| `WTP_r1` | Response to CV question 1: "Would you pay XX KES for a connection?" |
| `WTP_r2` | Response to CV question 2: same offer with 6-week payment window |
| `fin_WTP_r1`, `fin_WTP_r2` | WTP responses under financing option |
| `fin_npv_15`, `fin_npv_25` | NPV of financing at 15% and 25% discount rates |
| `price` | Actual experimental connection price (KES) |
| `takeup` | Binary: took up connection |

### Heterogeneity Dimensions Already Explored

| Dimension | Variable | Location | Method |
|---|---|---|---|
| **Baseline income** | `earn` (monthly earnings), quartile split | `jpe/code/1_figures.do` lines 108–150 | Separate demand curves (Figure 2B): lower vs. upper earnings quartile |
| **Housing quality** | `wall` (high-quality walls) | `jpe/code/1_figures.do` lines 152–187 | Separate demand curves (Figure 2C): low vs. high quality |
| **Socioeconomic status** | `highses` (composite index: education, employment, bank account, earnings, assets) | `jep/tab_A3_A4/tab_A3_A4.do` lines 94–209 | IV regression with `connected × highses` interaction; Appendix Tables A3–A4 |
| **Adopter type** | Low-price vs. high-price adopters | `jep/tab_A1_A2/tab_A1_A2.do` | LATE by adopter group; Appendix Tables A1–A2 |
| **Community characteristics** | `busia`, `market`, `funded`, `electrification`, `population` | `jpe/code/5_appendix_tables.do` lines 558–664 | Interaction terms; Table B4 |
| **Household characteristics** | `hhsize`, `age`, `senior`, `notfarmer`, `bank` | `jpe/code/5_appendix_tables.do` lines 668–796 | Interaction terms; Table B4 |
| **Elicitation method** | CV vs. revealed preference vs. financing | `jpe/code/1_figures.do` lines 440–611 | Comparison of `cv1`, `cv2`, `rp`, `fin_npv_15/25`; Figure 3C |

### Gaps — WTP Heterogeneity Not Yet Explored

| # | Gap | Notes |
|---|---|---|
| 1 | **No WTP heterogeneity by appliance ownership** | Households that already own a TV, radio, or iron may have higher WTP; not tested |
| 2 | **No WTP heterogeneity by gender** | `female` used only as a control, never as a heterogeneity dimension in demand analysis |
| 3 | **No R2 WTP follow-up** | WTP is measured only at baseline (demand.dta); no elicitation in R1/R2 surveys to track WTP evolution post-connection |
| 4 | **Income split is binary (quartiles 1 vs. 4)** | Figure 2B drops middle quartiles; no continuous income-WTP relationship estimated |
| 5 | **No distance-to-grid WTP gradient** | `distance` appears as a control but no demand curve by distance band |
| 6 | **No WTP heterogeneity by time preferences** | Financing NPV analysis uses aggregate; no individual-level discount rate × WTP interaction |
| 7 | **SES index weights are implicit** | `highses` is a PCA/equal-weight composite; sensitivity to index weighting not shown |
