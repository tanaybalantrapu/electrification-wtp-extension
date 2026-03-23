# Extension Note
**Project:** Electrification WTP Extension
**Papers:** Lee, Miguel & Wolfram (JEP 2019; JPE 2019)
**Last updated:** 2026-03-22

---

## Research Question

Does baseline willingness-to-pay for a grid connection predict the life satisfaction gains from electrification?

The original papers establish that grid connection has small or null average treatment effects on subjective wellbeing (`life_index`). This extension asks whether that null average conceals meaningful heterogeneity: households that stated higher WTP before connection may have had stronger prior expectations of benefit, and those expectations — if met or unmet — could drive divergent wellbeing outcomes.

Two complementary analyses:

1. **Heterogeneous treatment effects by baseline WTP** — does the ITT/TOT effect on `life_index` differ between high- and low-WTP households?
2. **WTP as a predictor of life satisfaction gains conditional on connecting** — among households that connected, does realised life satisfaction scale with what they were willing to pay upfront?

---

## Data

| Dataset | Content | Round |
|---|---|---|
| `demand.dta` | Baseline 2014 survey; WTP elicitation; treatment assignment | Baseline |
| `impacts_1.dta` | Follow-up household survey; `life_index`, `symptoms_index` | R1 2016 |
| `impacts_2.dta` | Follow-up household survey; `life_index`, `symptoms_index` | R2 2017 |

**Merge key:** `reppid` (1:1 across all three datasets). Confirmed feasible — `tab_A1_A2.do` lines 217–227 use this exact merge.

**Sample restriction:** Drop `base_connected == 1` (already connected at baseline) following original papers.

---

## Variables

### Heterogeneity variable (constructed from `demand.dta`)

| Variable | Definition |
|---|---|
| `wtp_stated` | Maximum `WTP_amt` at which `WTP_r1 == 1`; continuous stated WTP (KES) |
| `wtp_high` | Binary: `wtp_stated` above sample median (primary heterogeneity indicator) |
| `wtp_any` | Binary: `WTP_r1 == 1` at any price > 0 (alternative binary measure) |

**Why `WTP_r1` rather than `WTP_r2`:** `WTP_r1` ("Would you pay XX KES?") is the unconditional stated WTP. `WTP_r2` adds a 6-week financing window, which conflates time preferences with WTP; used as robustness check only.

### Outcome variables

Primary: `life_index` (subjective life satisfaction index)
Secondary: `symptoms_index` (mental health symptoms index)

Both present in `impacts_1.dta` (R1) and `impacts_2.dta` (R2).

### Instruments

`treat_low`, `treat_med`, `treat_full` and their interactions with `wtp_high` — exactly as in `tab_A3_A4.do`.

### Controls

- Community: `busia`, `base_market`, `base_transearly`, `base_connected_rate`, `base_population`
- Household: `female`, `age_resp`, `base_housing`, `base_energyspending`

---

## Identification Strategy

### Analysis 1 — Heterogeneous TOT by baseline WTP

Mirrors `tab_A3_A4.do` exactly, substituting `int = wtp_high` for `int = highses`.

**Specification:**

```
ivreg2 life_index wtp_high [community] [household]
    (connected c.connected#c.wtp_high =
     treat_low treat_med treat_full
     c.treat_low#c.wtp_high c.treat_med#c.wtp_high c.treat_full#c.wtp_high)
    if child==0, cl(siteno)
```

Coefficients of interest:
- `connected` — TOT for low-WTP households (wtp_high == 0)
- `c.connected#c.wtp_high` — differential TOT for high-WTP households
- Sum of the two = TOT for high-WTP households

**Instruments:** Treatment arms interacted with `wtp_high`. Randomisation of price assignment ensures `wtp_high` (a function of the randomly assigned `WTP_amt`) is uncorrelated with unobservables conditional on controls — though note `WTP_amt` is randomly assigned, so `wtp_stated` has an exogenous component. The binary `wtp_high` uses sample median as cutoff; robustness checks use terciles.

**Runs separately for:** R1 (`impacts_1.dta`) and R2 (`impacts_2.dta`).

### Analysis 2 — WTP as predictor of life satisfaction gains (among connected)

Restricted to `connected == 1` at follow-up. OLS regression of `life_index` on `wtp_stated` (continuous, in USD) with the same household and community controls.

```
reg life_index wtp_stated [community] [household] if connected==1 & child==0, cl(siteno)
```

This is descriptive — not a clean causal estimate, since selection into connection is non-random even within the treatment group. Interpretation: conditional on connecting, do households with higher ex-ante WTP report higher ex-post life satisfaction? Supports or contradicts an expectations-formation channel.

**Robustness:** Replace `wtp_stated` with `wtp_any` (binary); add `wtp_high × highses` to test whether WTP heterogeneity is just picking up SES.

---

## Outputs

| File | Content |
|---|---|
| `outputs/tables/tab_wtp_r1.tex` | Analysis 1 results — R1 (2016) |
| `outputs/tables/tab_wtp_r2.tex` | Analysis 1 results — R2 (2017) |
| `outputs/tables/tab_wtp_connected.tex` | Analysis 2 results — conditional on connection |
| `outputs/tables/tab_wtp_robustness.tex` | Robustness: WTP_r2, terciles, WTP × highses |

---

## Stata Code Plan

**File:** `code/03_extension/wtp_life_satisfaction.do`

**Steps:**

```
1. Set paths and macros (mirror tab_A3_A4.do header)
2. Load impacts_1.dta → convert KES variables to USD → keep relevant vars → drop base_connected==1 → save temp_r1.dta
3. Load impacts_2.dta → same conversions → save temp_r2.dta
4. Load demand.dta → keep reppid WTP_amt WTP_r1 WTP_r2 takeup price treat_* baseline chars → save temp_demand.dta
5. Construct wtp_stated: for each household, find max WTP_amt where WTP_r1==1
6. Construct wtp_high: binary above median wtp_stated
7. Construct wtp_any: WTP_r1==1 at any positive price

*** ANALYSIS 1: R1 ***
8. Merge temp_r1.dta + temp_demand.dta on reppid
9. ivreg2 life_index with wtp_high interaction → output tab_wtp_r1.tex
10. ivreg2 symptoms_index with wtp_high interaction → append tab_wtp_r1.tex

*** ANALYSIS 1: R2 ***
11. Merge temp_r2.dta + temp_demand.dta on reppid
12. ivreg2 life_index with wtp_high interaction → output tab_wtp_r2.tex
13. ivreg2 symptoms_index with wtp_high interaction → append tab_wtp_r2.tex

*** ANALYSIS 2: Conditional on connection ***
14. Use merged R1 dataset; restrict to connected==1
15. reg life_index wtp_stated controls → output tab_wtp_connected.tex
16. reg symptoms_index wtp_stated controls → append

*** ROBUSTNESS ***
17. Re-run Analysis 1 using WTP_r2 instead of WTP_r1
18. Re-run using WTP terciles instead of median split
19. Add wtp_high × highses interaction to test SES confounding
20. Output tab_wtp_robustness.tex

21. Clean up temp files
```

---

## Caveats and Limitations

1. **`WTP_amt` is randomly assigned** — stated WTP (`WTP_r1`) is a response to a randomly assigned hypothetical price, not an unconditional valuation. `wtp_high` therefore partly reflects the random price draw. Constructing a demand-curve-based WTP (maximum willingness to pay) requires the full distribution of `WTP_r1` across price points per household, which is not directly available (each household sees one price). Use `takeup` as the revealed-preference robustness check.

2. **Null average effects** — the original papers find small/null average effects of connection on `life_index`. Heterogeneity by WTP is therefore an exploratory secondary analysis; multiple testing corrections (FDR, as in `3_impacts.do`) should be applied.

3. **Selection in Analysis 2** — conditioning on `connected==1` induces selection bias. The OLS among connected is descriptive; causal interpretation requires further assumptions.

4. **R2 sample** — `impacts_2.dta` is not merged with `demand.dta` in any original do-file; the merge is feasible via `reppid` but attrition between 2014 and 2017 should be checked.
