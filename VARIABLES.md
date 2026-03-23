# Variable Reference
**Project:** Electrification WTP Extension
**Papers:** Lee, Miguel & Wolfram (JEP 2019; JPE 2019)
**Last updated:** 2026-03-22
**Extension focus:** WTP heterogeneity at baseline × life satisfaction at follow-up

All variables inferred from do-file code. No Stata has been run to inspect .dta directly.

---

## 1. Identifiers (present in all datasets)

| Variable | Datasets | Description |
|---|---|---|
| `reppid` | `demand.dta`, `impacts_1.dta`, `impacts_2.dta`, `impacts_s.dta` | Unique household/respondent ID — **merge key across all datasets** |
| `siteno` | All | Community/site ID |
| `hhid` | All | Household ID within site |
| `child` | `demand.dta` | Child identifier (for student outcomes) |

---

## 2. Treatment Variables (in `demand.dta`)

| Variable | Description |
|---|---|
| `tx1` | Treatment arm 1 indicator |
| `tx2` | Treatment arm 2 indicator |
| `tx3` | Treatment arm 3 indicator |
| `treat_low` | Low subsidy treatment arm |
| `treat_med` | Medium subsidy treatment arm |
| `treat_full` | Full subsidy treatment arm |
| `treated_all` | Any treatment indicator |
| `price` | Randomly assigned connection price (KES) |
| `connected` | Binary: household connected to grid (endogenous; instrumented by treatment arms) |

---

## 3. WTP Variables (in `demand.dta` — baseline 2014)

These are the **key baseline heterogeneity variables** for the extension.

| Variable | Description | Values |
|---|---|---|
| `WTP_amt` | Randomly assigned CV elicitation price | 0, 10k, 15k, 20k, 25k, 35k, 75k KES |
| `WTP_r1` | Response to CV question 1: "Would you pay `WTP_amt` KES for a connection?" | Binary |
| `WTP_r2` | Response to CV question 2: same offer with 6-week payment window | Binary |
| `fin_WTP_r1` | WTP response under financing option, question 1 | Binary |
| `fin_WTP_r2` | WTP response under financing option, question 2 | Binary |
| `fin_npv_15` | NPV of financing payments at 15% discount rate | Continuous (KES) |
| `fin_npv_25` | NPV of financing payments at 25% discount rate | Continuous (KES) |
| `fin_group` | Financing group assignment | Categorical |
| `takeup` | Binary: took up grid connection at offered price | Binary (×100 in figures) |
| `cv1` | Aggregate take-up rate from CV question 1 (by price) | Rate |
| `cv2` | Aggregate take-up rate from CV question 2 (by price) | Rate |

**For the extension:** `WTP_r1` and `WTP_r2` are the primary stated-WTP indicators. A continuous WTP measure can be constructed as the maximum `WTP_amt` at which `WTP_r1 == 1`. `takeup` is the revealed-preference analogue.

---

## 4. Life Satisfaction & Wellbeing Outcomes (in `impacts_1.dta` and `impacts_2.dta`)

These are the **key follow-up outcome variables** for the extension.

| Variable | Datasets | Description | Round |
|---|---|---|---|
| `life_index` | `impacts_1.dta`, `impacts_2.dta` | **Primary life satisfaction index** — composite of subjective wellbeing questions | R1 (2016), R2 (2017) |
| `symptoms_index` | `impacts_1.dta`, `impacts_2.dta` | Mental health symptoms index — secondary wellbeing measure | R1 (2016), R2 (2017) |
| `knowledge_index` | `impacts_1.dta`, `impacts_2.dta` | Knowledge index | R1 (2016), R2 (2017) |

**Note:** Both `life_index` and `symptoms_index` are listed as primary outcomes in `3_impacts.do` (lines 315–326) for R1 adults, R1 spillover, R2 adults, and pooled. The index construction is documented in the survey PDFs: `data/jpe/surveys/Round 1 Follow-up Survey Questions (2016).pdf` (R1) and `Round 1 Follow-up Survey Questions (2017).pdf` (R2; mislabeled "Round 1" in filename).

---

## 5. Appliance Outcome Variables (in `impacts_1.dta` and `impacts_2.dta`)

| Variable | Description |
|---|---|
| `number_appliances` | Count of appliances owned |
| `mobilephone` | Binary: owns mobile phone |
| `radio` | Binary: owns radio |
| `television` | Binary: owns television |
| `iron` | Binary: owns electric iron |
| `solar_shs` | Binary: owns solar home system |
| `electric_lighting` | Binary: uses electric lighting |

---

## 6. Energy & Economic Outcome Variables (in `impacts_1.dta` and `impacts_2.dta`)

| Variable | Description |
|---|---|
| `gridelec_spending` | Monthly grid electricity spending (KES) |
| `kerosene_spending` | Monthly kerosene spending (KES) |
| `energy_spending` | Total monthly energy spending (KES) |
| `asset_value` | Household asset value (KES) |
| `percapcons` | Per capita consumption (KES) |
| `tot_hh_month_earn` | Total household monthly earnings (KES) — R2 only |
| `fraction_employed_all` | Share of household members employed |
| `fraction_employed_f` | Share of female household members employed |
| `fraction_employed_m` | Share of male household members employed |
| `hours_worked` | Hours worked |
| `r_crime_index` | Crime index |
| `EMI` | Electrical meter installed (binary) |
| `NEMI` | No electrical meter installed (binary) |
| `connected` | Binary: grid connected at follow-up |
| `connected_r` | Connected (alternate measure) |

---

## 7. Baseline Characteristics (in `demand.dta` — controls and heterogeneity dimensions)

| Variable | Description | Role |
|---|---|---|
| `earn` | Monthly earnings at baseline (KES) | Heterogeneity (Figure 2B income quartile split) + control |
| `female` | Binary: female respondent | Control only — not yet used as heterogeneity dimension |
| `age` | Age of respondent | Control + Table B4 interaction |
| `wall` | Binary: high-quality wall material | Heterogeneity (Figure 2C housing quality demand curves) |
| `someschool` | Binary: any formal schooling | Control |
| `base_educ` | Education level | Component of `highses` + control |
| `employed` | Binary: employed at baseline | Component of `highses` + control |
| `notfarmer` | Binary: not a farmer | Component of `highses` + Table B4 interaction |
| `base_bank` | Binary: has bank account | Component of `highses` |
| `base_asset_value` | Baseline asset value (KES) | Component of `highses` + control |
| `base_housing` | Baseline housing quality | Control |
| `base_energyspending` | Baseline energy spending (KES) | Control |
| `hhsize` | Household size | Control + Table B4 interaction |
| `senior` | Binary: elderly respondent | Table B4 interaction |
| `distance` | Distance to grid (km) | Control — not yet used as heterogeneity dimension |
| `highses` | High SES composite index (above 75th percentile) constructed from `base_educ`, `notfarmer`, `employed`, `base_bank`, `earn`, `base_asset_value` | Heterogeneity in Appendix Tables A3–A4 (`jep/tab_A3_A4/tab_A3_A4.do` lines 94–209) |
| `quartile` | Earnings quartile (1=bottom, 4=top) | Heterogeneity in Figure 2B demand curves |

---

## 8. Community-Level Controls (in `demand.dta`)

| Variable | Description |
|---|---|
| `busia` | Binary: Busia county (vs. Siaya) |
| `base_market` | Binary: near a market |
| `base_transearly` | Binary: early transformer connection |
| `base_connected_rate` | Baseline community connection rate |
| `base_population` | Community population |
| `market` | Market presence indicator |
| `funded` | Community received external funding |
| `electrification` | Community electrification rate |
| `population` | Community population (Table B4 interaction) |

---

## 9. Student Outcome Variables (in `impacts_1.dta`)

| Variable | Description |
|---|---|
| `st_studenttest` | Student test score |
| `st_score_kcpe` | KCPE exam score |
| `child_female` | Binary: female child |
| `child_age` | Child age |
| `sibs` | Number of siblings |

---

## 10. Merge Map for Extension Analysis

The extension links baseline WTP (`demand.dta`) to follow-up life satisfaction (`impacts_1.dta`, `impacts_2.dta`) via `reppid`.

```
demand.dta  →  merge 1:1 reppid  →  impacts_1.dta   (R1, 2016)
                                  →  impacts_2.dta   (R2, 2017)
```

**Confirmed feasible:** `tab_A1_A2.do` (lines 217–227) already performs this exact merge using `reppid`. The extension adapts this pattern, replacing `highses` with a WTP indicator as the heterogeneity dimension.

**Variables needed per dataset:**

| Dataset | Variables |
|---|---|
| `demand.dta` | `reppid`, `WTP_amt`, `WTP_r1`, `WTP_r2`, `takeup`, `price`, `treat_low`, `treat_med`, `treat_full`, baseline controls |
| `impacts_1.dta` | `reppid`, `life_index`, `symptoms_index`, `connected`, outcome controls |
| `impacts_2.dta` | `reppid`, `life_index`, `symptoms_index`, `connected`, `tot_hh_month_earn`, outcome controls |

---

## 11. Proposed Extension Variables (to be constructed)

| Variable | Definition | Source |
|---|---|---|
| `wtp_stated` | Maximum `WTP_amt` at which `WTP_r1 == 1` (continuous stated WTP in KES) | `demand.dta` |
| `wtp_high` | Binary: `wtp_stated` above sample median | `demand.dta` |
| `wtp_rp` | Revealed-preference WTP: `takeup == 1` at assigned `price` | `demand.dta` |
| `wtp_x_connected` | Interaction `wtp_high × connected` — identifies heterogeneous treatment effect on life satisfaction by WTP group | Merged dataset |
