# Project Context
**Project:** Electrification WTP Extension
**Last updated:** 2026-03-23

---

## Overview

This project replicates and extends two published papers by Kenneth Lee, Edward Miguel, and Catherine Wolfram on the economics of rural electrification in Kenya. The extension asks whether baseline willingness-to-pay (WTP) for a grid connection predicts life satisfaction gains from electrification — a test of the expectations channel in welfare responses to infrastructure investment.

---

## Source Papers

### Paper 1 — JPE
**Lee, Kenneth, Edward Miguel, and Catherine Wolfram (2019)**
"Experimental Evidence on the Economics of Rural Electrification"
*Journal of Political Economy* 128(4): 1523–1565

The primary randomised experiment. Households in rural Kenya (Busia and Siaya counties) were randomly assigned connection subsidies at three price levels (low, medium, full). The paper estimates:
- Demand for grid connections (take-up by price)
- Impacts on energy, income, employment, assets, and wellbeing at R1 (2016) and R2 (2017) follow-ups
- Cost-benefit analysis of rural electrification programmes

### Paper 2 — JEP
**Lee, Kenneth, Edward Miguel, and Catherine Wolfram (2020)**
"Does Household Electrification Supercharge Economic Development?"
*Journal of Economic Perspectives* 34(1): 122–144

A shorter synthesis paper. Uses a subset of the JPE data to:
- Document the gap between stated WTP and actual economic impacts
- Examine heterogeneity in treatment effects by adopter type (Appendix Tables A1–A2) and by SES (Appendix Tables A3–A4)
- Contextualise the Kenya results within the broader electrification literature

---

## Study Design

**Setting:** Rural Kenya, Busia and Siaya counties, ~150 communities

**Sample:** Unconnected households identified in a 2013 baseline census; baseline survey conducted in 2014

**Intervention:** Random assignment of grid connection subsidies:
- `treat_low` — low subsidy (high price)
- `treat_med` — medium subsidy
- `treat_full` — full subsidy (free connection)

**Follow-up rounds:**
- R1: 2016 (2 years post-baseline) — `impacts_1.dta`
- R2: 2017 (3 years post-baseline) — `impacts_2.dta`

**Key finding from original papers:** Large take-up responses to price subsidies; small or null average effects on income, employment, and wellbeing (including life satisfaction). Consumer surplus is low relative to connection costs.

---

## Extension Goals

1. **WTP × life satisfaction heterogeneity** — Does baseline WTP predict life satisfaction gains? Tests an expectations channel: households with higher prior expectations (proxied by stated WTP) may experience different wellbeing outcomes post-connection.

2. **Appliance heterogeneity replication** — Reproduce the JEP appliance heterogeneity analysis (Appendix Table A1) in Python to verify the data pipeline before extending it.

The extension uses the same datasets as the original papers, merging `demand.dta` (baseline WTP) with `impacts_1.dta` / `impacts_2.dta` (follow-up outcomes) on the household identifier `reppid`.

---

## Project Structure

```
electrification-wtp-extension/
├── code/
│   ├── 01_recon/           — data reconnaissance scripts
│   ├── 02_replicate/       — replication of original analyses
│   └── 03_extension/       — extension analyses
│       ├── run_analysis.py          — WTP × life satisfaction regressions + figure
│       └── wtp_life_satisfaction.do — Stata IV specification (template)
├── data/
│   ├── jep/                — JEP replication package (do-files + datasets)
│   ├── jpe/                — JPE replication package (do-files + datasets)
│   └── MANIFEST.md         — full data inventory and gap analysis
├── outputs/
│   ├── figures/            — coefficient plots (PDF + PNG)
│   ├── latex/              — compiled LaTeX documents and PDFs
│   └── tables/             — regression output CSVs and .tex files
├── CONTEXT.md              — this file
├── EXTENSION_NOTE.md       — research design for the extension
├── REPLICATION_NOTE.md     — notes on replication status
└── VARIABLES.md            — full variable reference
```

---

## Key Variables for the Extension

| Variable | Dataset | Description |
|---|---|---|
| `WTP_amt` | `demand.dta` | Randomly assigned CV elicitation price (KES) |
| `WTP_r1` | `demand.dta` | Binary: accepted the CV offer |
| `wtp_high` | Constructed | Binary: stated WTP above sample median |
| `treated_all` | `impacts_*.dta` | Binary: any treatment arm |
| `life_index` | `impacts_*.dta` | Normalised life satisfaction index |
| `r_crime_index` | `impacts_2.dta` | Perceptions of security index (R2 only) |
| `reppid` | All | Household merge key |

See `VARIABLES.md` for the full variable reference.
