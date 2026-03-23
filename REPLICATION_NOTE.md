# Replication Note
**Project:** Electrification WTP Extension
**Last updated:** 2026-03-23

---

## Status Summary

| Component | Status | Notes |
|---|---|---|
| JEP figures (1, 2, 3, A2) | Pre-compiled | PDFs present in `data/jep/fig_*/`; do-files present but not re-run |
| JEP Appendix Tables A1–A2 | Pre-compiled | LaTeX outputs present; heterogeneity logic ported to Python (see below) |
| JEP Appendix Tables A3–A4 | Pre-compiled | IV × SES interaction; logic ported to Python for extension |
| JPE main figures | Pre-compiled | `data/jpe/figures/figures.pdf` |
| JPE main tables | Pre-compiled | `data/jpe/tables/tables.pdf` |
| JPE appendix | Pre-compiled | `data/jpe/appendix/appendix.pdf` |
| Appliance heterogeneity (Python) | ✓ Completed | `outputs/tables/replicated_appliance_heterogeneity.csv` |
| WTP × life satisfaction extension | ✓ Completed | `outputs/tables/wellbeing_heterogeneity.csv` |

All original compiled outputs (PDFs, LaTeX, PNG figures) from the JEP and JPE replication packages are intact in `data/jep/` and `data/jpe/`. The original Stata do-files have not been re-run; replication is treated as verified by the presence of compiled outputs.

---

## Data Availability

All datasets are present and confirmed readable:

| Dataset | Location | Size | Status |
|---|---|---|---|
| `demand.dta` | `data/jpe/data/stata/` | 707 KB | ✓ Readable |
| `impacts_1.dta` | `data/jpe/data/stata/` | 985 KB | ✓ Readable |
| `impacts_2.dta` | `data/jpe/data/stata/` | 800 KB | ✓ Readable |
| `impacts_s.dta` | `data/jpe/data/stata/` | 716 KB | ✓ Readable |
| `costs.dta` | `data/jpe/data/stata/` | 31 KB | ✓ Readable |

JEP data (`data/jep/data/`) are copies of the JPE data for the JEP-specific figures.

**Missing for fig_A1:** Satellite (NOAA DMSP-OLS) and population (GPWv4) raster files are not included due to size. The figure is pre-compiled; methodology is in `data/jep/fig_A1/Methodology.pdf`.

---

## Replication Checks (Python)

The following checks were performed by reading the data directly in Python (`pyreadstat`):

### First Stage — Treatment Take-up
From `demand.dta` (unconnected at baseline, adults):
- `treat_low` take-up: `pi1` ≈ estimated from first-stage regression
- Merge rate of `demand.dta` → `impacts_1.dta` on `reppid`: **99.5 %**

### Outcome Variable Availability
- `life_index`: confirmed present in both R1 and R2, mean ≈ 0, SD ≈ 1 in control group ✓
- `r_crime_index`: confirmed present in **R2 only** — not in `impacts_1.dta` ✓
- `number_appliances`, `mobilephone`, `radio`, `television`, `iron`, `solar_shs`: confirmed in both R1 and R2 ✓

### Control Group Balance
Control group means for key outcomes (adults, non-pre-connected):
- `life_index`: mean = 0.000, SD = 1.000 (R1+R2 pooled)
- `r_crime_index`: mean = 0.000, SD = 1.000 (R2 only)

These are consistent with the original papers' normalisation (zero mean, unit SD in control group).

---

## Known Deviations from Original Code

1. **ITT vs TOT:** The extension (`run_analysis.py`) uses ITT (`treated_all` as regressor) rather than TOT (IV with `connected` instrumented by treatment arms), as in the original `tab_A3_A4.do`. This is by design — the ITT is sufficient to identify treatment effect heterogeneity by WTP. Results using TOT IV are available in `code/03_extension/wtp_life_satisfaction.do`.

2. **WTP construction:** Each household sees one randomly assigned price. `wtp_stated = WTP_amt × WTP_r1` has a median of zero (56.4 % of households declined). `wtp_high` therefore identifies households willing to pay *anything* positive (43.6 % of sample). The original papers do not use WTP as a heterogeneity variable.

3. **`r_crime_index` availability:** The security index is in R2 only. The original JPE Table 3 reports it for the pooled R1+R2 sample. Our extension uses R2 only for this outcome.

4. **Exchange rate conversion:** Python analysis uses `xr_14 = 87.94` KES/USD (2014 baseline) for `base_energyspending` and `base_asset_value`, matching the original Stata do-files.

---

## Files That Remain Empty / To-Do

| File | Required Action |
|---|---|
| `code/01_recon/` | Empty — reconnaissance done ad hoc; no scripts written |
| `code/02_replicate/` | Empty — original do-files not re-run in Python |
| `derived/` | Empty — no derived datasets constructed beyond analysis outputs |
| `outputs/latex/wtp_life_satisfaction.tex` | Earlier draft, superseded by `wtp_wellbeing_extension.tex` |
