"""
Appliance Heterogeneity Replication
Replicates JEP tab_A1_A2.do per-arm IV (LATE) estimates for appliance outcomes.

Strategy: Run IV2SLS separately for each treatment arm vs. control, using
each treatment dummy as instrument for `connected`. This mirrors the
ivreg2 specifications in tab_A1_A2.do lines 129–134.

Data: impacts_1.dta (R1, adults only, not pre-connected at baseline)
Output: outputs/tables/replicated_appliance_heterogeneity.csv
"""

import pathlib
import numpy as np
import pandas as pd
import pyreadstat
from linearmodels.iv import IV2SLS

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = pathlib.Path("/Users/tanaybalantrapu/projects/electrification-wtp-extension")
DATA = ROOT / "data" / "jpe" / "data" / "stata"
OUT  = ROOT / "outputs" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

# ── Exchange rates (from tab_A1_A2.do) ────────────────────────────────────
XR_14 = 87.94
I_15  = 0.0801
I_16  = 0.0635
X_16  = (1 + I_16) * (1 + I_15) * XR_14  # ≈ 101.015 KES/USD at R1

# ── Load data ──────────────────────────────────────────────────────────────
df, meta = pyreadstat.read_dta(str(DATA / "impacts_1.dta"))

# ── Currency conversions (match do-file) ──────────────────────────────────
for v in ["base_energyspending_ksh", "base_asset_value_ksh"]:
    df[v.replace("_ksh", "")] = df[v] / XR_14

for v in ["gridelec_spending_ksh", "kerosene_spending_ksh",
          "energy_spending_ksh", "asset_value_ksh", "percapcons_ksh"]:
    df[v.replace("_ksh", "")] = df[v] / X_16

# ── Sample restriction: adults, not pre-connected ─────────────────────────
df = df[(df["child"] == 0) & (df["base_connected"] == 0)].copy()
df["control"] = ((df["treat_low"] == 0) &
                 (df["treat_med"] == 0) &
                 (df["treat_full"] == 0)).astype(float)

# ── Scale binary appliance vars to pct (match do-file ×100) ───────────────
for v in ["electric_lighting", "mobilephone", "radio",
          "television", "iron", "solar_shs"]:
    if v in df.columns:
        df[v] = df[v] * 100

# ── Outcomes to replicate ─────────────────────────────────────────────────
OUTCOMES = [
    ("electric_lighting",    "Electric lighting (%)"),
    ("number_appliances",    "Number of appliances"),
    ("mobilephone",          "Mobile phone (%)"),
    ("radio",                "Radio (%)"),
    ("television",           "Television (%)"),
    ("iron",                 "Electric iron (%)"),
    ("solar_shs",            "Solar / SHS (%)"),
    ("energy_spending",      "Energy spending (USD/mo)"),
    ("gridelec_spending",    "Grid electricity spending (USD/mo)"),
    ("fraction_employed_all","Employment rate"),
    ("percapcons",           "Per-capita consumption (USD/mo)"),
    ("symptoms_index",       "Health symptoms index"),
    ("life_index",           "Life satisfaction index"),
]

# ── Per-arm IV helper ─────────────────────────────────────────────────────
def iv_arm(data, outcome, treat_col):
    """
    IV2SLS: outcome ~ 1 + [connected ~ treat_col]
    restricted to treat_col==1 or control==1.
    Returns (coef, se, pval, nobs).
    """
    sub = data[(data[treat_col] == 1) | (data["control"] == 1)].copy()
    sub = sub.dropna(subset=[outcome, "connected", treat_col])
    if len(sub) < 20:
        return np.nan, np.nan, np.nan, np.nan
    y  = sub[outcome]
    X  = pd.DataFrame({"const": 1.0}, index=sub.index)
    endog = sub[["connected"]]
    instr = sub[[treat_col]]
    try:
        res = IV2SLS(y, X, endog, instr).fit(cov_type="unadjusted")
        return (float(res.params["connected"]),
                float(res.std_errors["connected"]),
                float(res.pvalues["connected"]),
                int(res.nobs))
    except Exception:
        return np.nan, np.nan, np.nan, np.nan


# ── Pooled ITT helper (simple OLS ITT as reference) ───────────────────────
def ols_itt(data, outcome):
    """
    OLS ITT: outcome ~ 1 + treated_all
    for all adults not pre-connected.
    Returns (coef, se, pval, nobs, ctrl_mean, ctrl_sd).
    """
    sub = data.dropna(subset=[outcome, "treated_all"])
    ctrl = sub[sub["control"] == 1][outcome].dropna()
    ctrl_mean = float(ctrl.mean()) if len(ctrl) > 0 else np.nan
    ctrl_sd   = float(ctrl.std())  if len(ctrl) > 1 else np.nan
    from statsmodels.formula.api import ols as sm_ols
    try:
        fit = sm_ols(f"{outcome} ~ treated_all", data=sub).fit(
            cov_type="HC1"
        )
        return (float(fit.params["treated_all"]),
                float(fit.bse["treated_all"]),
                float(fit.pvalues["treated_all"]),
                int(fit.nobs),
                ctrl_mean, ctrl_sd)
    except Exception:
        return np.nan, np.nan, np.nan, np.nan, ctrl_mean, ctrl_sd


# ── Run regressions ───────────────────────────────────────────────────────
rows = []
for var, label in OUTCOMES:
    if var not in df.columns:
        continue

    ctrl = df[df["control"] == 1][var].dropna()
    ctrl_mean = float(ctrl.mean()) if len(ctrl) > 0 else np.nan
    ctrl_sd   = float(ctrl.std())  if len(ctrl) > 1 else np.nan

    # Per-arm LATEs
    b_low,  se_low,  p_low,  n_low  = iv_arm(df, var, "treat_low")
    b_med,  se_med,  p_med,  n_med  = iv_arm(df, var, "treat_med")
    b_full, se_full, p_full, n_full = iv_arm(df, var, "treat_full")

    rows.append({
        "outcome_var":   var,
        "outcome_label": label,
        "ctrl_mean":     round(ctrl_mean, 3) if not np.isnan(ctrl_mean) else np.nan,
        "ctrl_sd":       round(ctrl_sd,   3) if not np.isnan(ctrl_sd)   else np.nan,
        # Low-price arm (treat_low IV)
        "late_low":      round(b_low,  3) if not np.isnan(b_low)  else np.nan,
        "se_low":        round(se_low, 3) if not np.isnan(se_low) else np.nan,
        "p_low":         round(p_low,  3) if not np.isnan(p_low)  else np.nan,
        "n_low":         n_low,
        # Medium-price arm (treat_med IV)
        "late_med":      round(b_med,  3) if not np.isnan(b_med)  else np.nan,
        "se_med":        round(se_med, 3) if not np.isnan(se_med) else np.nan,
        "p_med":         round(p_med,  3) if not np.isnan(p_med)  else np.nan,
        "n_med":         n_med,
        # Full-subsidy arm (treat_full IV)
        "late_full":     round(b_full,  3) if not np.isnan(b_full)  else np.nan,
        "se_full":       round(se_full, 3) if not np.isnan(se_full) else np.nan,
        "p_full":        round(p_full,  3) if not np.isnan(p_full)  else np.nan,
        "n_full":        n_full,
    })

results = pd.DataFrame(rows)

# ── Save ──────────────────────────────────────────────────────────────────
out_path = OUT / "replicated_appliance_heterogeneity.csv"
results.to_csv(out_path, index=False)
print(f"Saved {len(results)} rows → {out_path}")
print()
print(results[["outcome_label", "ctrl_mean", "late_low", "se_low",
               "late_full", "se_full"]].to_string(index=False))
