"""
WTP Heterogeneity x Life Satisfaction Extension
================================================
Part A: Regression analysis with BH correction → outputs/tables/wellbeing_heterogeneity.csv
Part B: AEA-style coefficient figure           → outputs/figures/wellbeing_wtp_heterogeneity.{pdf,png}

Specification:
  y = a + b1*Treat + b2*HighWTP + b3*(Treat x HighWTP) + controls + round_FE
  Treat    = treated_all (any subsidy arm, ITT)
  HighWTP  = WTP_r1==1 at assigned WTP_amt > median(WTP_stated)
  Cluster  = siteno (community)

D6 (r_crime_index) is R2-only and flagged as exploratory (does not survive FDR).
"""

import os, warnings
import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT   = os.path.expanduser("~/projects/electrification-wtp-extension")
DATA   = os.path.join(ROOT, "data/jpe/data/stata")
OUT_T  = os.path.join(ROOT, "outputs/tables")
OUT_F  = os.path.join(ROOT, "outputs/figures")
os.makedirs(OUT_T, exist_ok=True)
os.makedirs(OUT_F, exist_ok=True)

# ── 1. Load data ───────────────────────────────────────────────────────────────
demand, _  = pyreadstat.read_dta(os.path.join(DATA, "demand.dta"))
imp1,   _  = pyreadstat.read_dta(os.path.join(DATA, "impacts_1.dta"))
imp2,   _  = pyreadstat.read_dta(os.path.join(DATA, "impacts_2.dta"))

# ── 2. Construct WTP measures from demand.dta ─────────────────────────────────
# wtp_stated: WTP_amt if household said yes (WTP_r1==1), else 0
demand["wtp_stated"] = demand["WTP_amt"] * (demand["WTP_r1"] == 1)
demand["wtp_stated"] = demand["wtp_stated"].where(demand["WTP_r1"].notna())

# wtp_high: above-sample-median stated WTP
median_wtp = demand.loc[demand["wtp_stated"].notna(), "wtp_stated"].median()
demand["wtp_high"] = (demand["wtp_stated"] > median_wtp).astype(float)
demand["wtp_high"] = demand["wtp_high"].where(demand["wtp_stated"].notna())

# wtp_stated_usd (2014 exchange rate 87.94 KES/USD)
demand["wtp_stated_usd"] = demand["wtp_stated"] / 87.94

print(f"WTP median (KES): {median_wtp:,.0f}")
print(f"High-WTP share:   {demand['wtp_high'].mean():.3f}")

wtp_cols = ["reppid", "wtp_stated", "wtp_stated_usd", "wtp_high", "WTP_r1", "WTP_r2",
            "WTP_amt", "takeup"]
demand_wtp = demand[wtp_cols].drop_duplicates("reppid")

# ── 3. Prepare impacts datasets ────────────────────────────────────────────────
def prep_impacts(df, xr_base=87.94):
    df = df.copy()
    df = df[df["base_connected"] != 1]        # drop pre-connected
    df = df[df["child"] == 0]                 # adults only
    df["base_energyspending"] = df["base_energyspending_ksh"] / xr_base
    df["base_asset_value"]    = df["base_asset_value_ksh"]    / xr_base
    return df

imp1p = prep_impacts(imp1)
imp2p = prep_impacts(imp2)

# Stack R1 + R2 for pooled analysis (round already present in each)
pooled = pd.concat([imp1p, imp2p], ignore_index=True)

# ── 4. Merge WTP ───────────────────────────────────────────────────────────────
def merge_wtp(df):
    m = df.merge(demand_wtp, on="reppid", how="left")
    m["treat_x_wtp"] = m["treated_all"] * m["wtp_high"]
    m["round_fe"]    = (m["round"] == 2).astype(float)   # R2 indicator
    return m

pooled_m = merge_wtp(pooled)
r1_m     = merge_wtp(imp1p)
r2_m     = merge_wtp(imp2p)

wtp_merge_rate = pooled_m["wtp_high"].notna().mean()
print(f"WTP merge rate (pooled): {wtp_merge_rate:.3f}")

# ── 5. Define controls ────────────────────────────────────────────────────────
COMMUNITY = ["busia", "base_market", "base_transearly",
             "base_connected_rate", "base_population"]
HOUSEHOLD = ["base_female", "base_age", "base_housing", "base_energyspending"]
CONTROLS  = COMMUNITY + HOUSEHOLD

# ── 6. Regression function ────────────────────────────────────────────────────
def run_reg(df, outcome, with_controls, round_fe=True):
    """
    Returns dict with b1, b1+b3, b3 and their SEs, p-values, 95% CIs, N.
    b1   = Treat effect for HighWTP==0 (low-WTP ITT)
    b3   = differential (Treat x HighWTP)
    b1+b3 = Treat effect for HighWTP==1 (high-WTP ITT)
    """
    sub = df[["reppid", "siteno", outcome, "treated_all", "wtp_high",
              "treat_x_wtp", "round_fe"] + CONTROLS].dropna()

    rhs = "treated_all + wtp_high + treat_x_wtp"
    if round_fe:
        rhs += " + round_fe"
    if with_controls:
        rhs += " + " + " + ".join(CONTROLS)

    formula = f"{outcome} ~ {rhs}"
    res = smf.ols(formula, data=sub).fit(
        cov_type="cluster",
        cov_kwds={"groups": sub["siteno"]}
    )

    b1  = res.params["treated_all"]
    b3  = res.params["treat_x_wtp"]
    b13 = b1 + b3

    # Delta method SE for b1+b3
    cov = res.cov_params()
    se_b1  = res.bse["treated_all"]
    se_b3  = res.bse["treat_x_wtp"]
    se_b13 = np.sqrt(
        cov.loc["treated_all", "treated_all"] +
        cov.loc["treat_x_wtp",  "treat_x_wtp"] +
        2 * cov.loc["treated_all", "treat_x_wtp"]
    )

    from scipy import stats
    df_res = res.df_resid
    t_b1  = b1  / se_b1
    t_b3  = b3  / se_b3
    t_b13 = b13 / se_b13

    p_b1  = 2 * stats.t.sf(abs(t_b1),  df=df_res)
    p_b3  = 2 * stats.t.sf(abs(t_b3),  df=df_res)
    p_b13 = 2 * stats.t.sf(abs(t_b13), df=df_res)

    ci95 = res.conf_int(alpha=0.05)
    # CI for b1+b3 via delta method
    z95 = 1.96
    ci_b13 = (b13 - z95 * se_b13, b13 + z95 * se_b13)

    return dict(
        outcome=outcome,
        with_controls=with_controls,
        N=int(res.nobs),
        b1=b1,   se_b1=se_b1,   p_b1=p_b1,
        ci_b1_lo=ci95.loc["treated_all", 0],
        ci_b1_hi=ci95.loc["treated_all", 1],
        b3=b3,   se_b3=se_b3,   p_b3=p_b3,
        ci_b3_lo=ci95.loc["treat_x_wtp", 0],
        ci_b3_hi=ci95.loc["treat_x_wtp", 1],
        b13=b13, se_b13=se_b13, p_b13=p_b13,
        ci_b13_lo=ci_b13[0], ci_b13_hi=ci_b13[1],
    )

# ── 7. Part A – Run all regressions ───────────────────────────────────────────
rows = []

specs = [
    ("pooled",  pooled_m, True,  True,  False),
    ("pooled",  pooled_m, False, True,  False),
    ("R1",      r1_m,     True,  False, False),
    ("R1",      r1_m,     False, False, False),
    ("R2",      r2_m,     True,  False, False),
    ("R2",      r2_m,     False, False, False),
]

# D2: life_index — all samples
for sample, df_, ctrl, rfe, _ in specs:
    r = run_reg(df_, "life_index", ctrl, round_fe=rfe)
    r["sample"]      = sample
    r["outcome_label"] = "D2: Life satisfaction"
    r["flag_exploratory"] = False
    rows.append(r)

# D6: r_crime_index — R2 only (variable not in R1)
for ctrl in [True, False]:
    r = run_reg(r2_m, "r_crime_index", ctrl, round_fe=False)
    r["sample"]      = "R2"
    r["outcome_label"] = "D6: Security index"
    r["flag_exploratory"] = True   # does not survive FDR — exploratory
    rows.append(r)

# Robustness: separate by WTP group (high/low only) for life_index, pooled
for wtp_val, label in [(1, "high_wtp_only"), (0, "low_wtp_only")]:
    sub = pooled_m[pooled_m["wtp_high"] == wtp_val].copy()
    # Simple ITT within group: y = a + b*Treat + controls + round_fe
    cols_needed = ["reppid", "siteno", "life_index", "treated_all",
                   "round_fe"] + CONTROLS
    sub_c = sub[cols_needed].dropna()
    formula = "life_index ~ treated_all + round_fe + " + " + ".join(CONTROLS)
    res = smf.ols(formula, data=sub_c).fit(
        cov_type="cluster", cov_kwds={"groups": sub_c["siteno"]}
    )
    b = res.params["treated_all"]
    se = res.bse["treated_all"]
    from scipy import stats as st
    p = 2 * st.t.sf(abs(b / se), df=res.df_resid)
    ci = res.conf_int(alpha=0.05)
    rows.append(dict(
        outcome="life_index", outcome_label="D2: Life satisfaction",
        sample=f"pooled_{label}", with_controls=True,
        N=int(res.nobs),
        b1=b, se_b1=se, p_b1=p,
        ci_b1_lo=ci.loc["treated_all", 0], ci_b1_hi=ci.loc["treated_all", 1],
        b3=np.nan, se_b3=np.nan, p_b3=np.nan,
        ci_b3_lo=np.nan, ci_b3_hi=np.nan,
        b13=np.nan, se_b13=np.nan, p_b13=np.nan,
        ci_b13_lo=np.nan, ci_b13_hi=np.nan,
        flag_exploratory=False,
    ))

# Robustness: continuous WTP (wtp_stated_usd) for life_index, pooled
sub_c2 = pooled_m[["reppid", "siteno", "life_index", "treated_all",
                    "wtp_stated_usd", "round_fe"] + CONTROLS].dropna()
sub_c2 = sub_c2.copy()
sub_c2["treat_x_wtp_cont"] = sub_c2["treated_all"] * sub_c2["wtp_stated_usd"]
res_cont = smf.ols(
    "life_index ~ treated_all + wtp_stated_usd + treat_x_wtp_cont + round_fe + "
    + " + ".join(CONTROLS),
    data=sub_c2
).fit(cov_type="cluster", cov_kwds={"groups": sub_c2["siteno"]})
from scipy import stats as st2
b_cont = res_cont.params["treat_x_wtp_cont"]
se_cont = res_cont.bse["treat_x_wtp_cont"]
p_cont  = 2 * st2.t.sf(abs(b_cont / se_cont), df=res_cont.df_resid)
ci_cont = res_cont.conf_int(alpha=0.05)
rows.append(dict(
    outcome="life_index_continuous_wtp",
    outcome_label="D2: Life satisfaction (continuous WTP)",
    sample="pooled", with_controls=True,
    N=int(res_cont.nobs),
    b1=res_cont.params["treated_all"],
    se_b1=res_cont.bse["treated_all"], p_b1=np.nan,
    ci_b1_lo=np.nan, ci_b1_hi=np.nan,
    b3=b_cont, se_b3=se_cont, p_b3=p_cont,
    ci_b3_lo=ci_cont.loc["treat_x_wtp_cont", 0],
    ci_b3_hi=ci_cont.loc["treat_x_wtp_cont", 1],
    b13=np.nan, se_b13=np.nan, p_b13=np.nan,
    ci_b13_lo=np.nan, ci_b13_hi=np.nan,
    flag_exploratory=False,
))

results = pd.DataFrame(rows)

# ── 8. Benjamini-Hochberg correction ──────────────────────────────────────────
# Apply across b1, b13, b3 p-values for main (non-robustness) regressions
main_mask = results["sample"].isin(["pooled", "R1", "R2"]) & \
            ~results["outcome"].str.contains("continuous")

for pcol, qcol in [("p_b1", "q_b1"), ("p_b13", "q_b13"), ("p_b3", "q_b3")]:
    pvals = results.loc[main_mask, pcol].values
    valid = ~np.isnan(pvals)
    q = np.full(len(pvals), np.nan)
    if valid.any():
        _, q[valid], _, _ = multipletests(pvals[valid], method="fdr_bh")
    results.loc[main_mask, qcol] = q

# ── 9. Save CSV ───────────────────────────────────────────────────────────────
col_order = [
    "outcome_label", "sample", "with_controls", "N", "flag_exploratory",
    "b1",  "se_b1",  "p_b1",  "q_b1",  "ci_b1_lo",  "ci_b1_hi",
    "b13", "se_b13", "p_b13", "q_b13", "ci_b13_lo", "ci_b13_hi",
    "b3",  "se_b3",  "p_b3",  "q_b3",  "ci_b3_lo",  "ci_b3_hi",
]
out_cols = [c for c in col_order if c in results.columns]
results[out_cols].round(4).to_csv(
    os.path.join(OUT_T, "wellbeing_heterogeneity.csv"), index=False
)
print("\nSaved: outputs/tables/wellbeing_heterogeneity.csv")
print(results[["outcome_label","sample","with_controls","b1","b13","b3","p_b3"]].to_string(index=False))

# ── 10. Part B – AEA-style coefficient figure ─────────────────────────────────
# Use pooled, with controls rows for D2 and D6 (D6 = R2 only with controls)
plot_rows = {
    "D2: Life satisfaction":
        results[(results["outcome"] == "life_index") &
                (results["sample"] == "pooled") &
                (results["with_controls"] == True)].iloc[0],
    "D6: Security index\n(exploratory, R2 only)":
        results[(results["outcome"] == "r_crime_index") &
                (results["sample"] == "R2") &
                (results["with_controls"] == True)].iloc[0],
}

# Outcomes ordered D2 first (top of y-axis), D6 second
outcome_labels = list(plot_rows.keys())
y_positions    = {lbl: len(outcome_labels) - i for i, lbl in enumerate(outcome_labels)}
offset         = 0.15   # vertical jitter between low/high-WTP points

fig, ax = plt.subplots(figsize=(6, 3.2))

# Style: AEA / JEP-matching
plt.rcParams.update({
    "font.family":     "serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
})
ax.set_facecolor("white")
fig.patch.set_facecolor("white")
ax.yaxis.grid(False)
ax.xaxis.grid(False)

# Vertical dashed line at zero
ax.axvline(0, color="black", linewidth=0.8, linestyle="--", zorder=1)

low_handle  = None
high_handle = None

for label, row in plot_rows.items():
    y_base = y_positions[label]

    # Low-WTP point (hollow circle, b1)
    y_low = y_base + offset
    ax.errorbar(
        row["b1"], y_low,
        xerr=[[row["b1"] - row["ci_b1_lo"]], [row["ci_b1_hi"] - row["b1"]]],
        fmt="o", color="black", markerfacecolor="white", markeredgecolor="black",
        markersize=7, linewidth=1.2, capsize=3, zorder=3
    )

    # High-WTP point (filled circle, b1+b3)
    y_high = y_base - offset
    ax.errorbar(
        row["b13"], y_high,
        xerr=[[row["b13"] - row["ci_b13_lo"]], [row["ci_b13_hi"] - row["b13"]]],
        fmt="o", color="black", markerfacecolor="black", markeredgecolor="black",
        markersize=7, linewidth=1.2, capsize=3, zorder=3
    )

# Y-axis labels
ax.set_yticks([y_positions[lbl] for lbl in outcome_labels])
ax.set_yticklabels(outcome_labels, fontsize=9)

# X-axis
ax.set_xlabel("ITT coefficient (normalised index units)", fontsize=10)
ax.tick_params(axis="x", labelsize=9)

# Y-axis limits
ax.set_ylim(min(y_positions.values()) - 0.6, max(y_positions.values()) + 0.6)

# Legend
low_patch  = mpatches.Patch(facecolor="white", edgecolor="black",
                             label="Low WTP (below median)")
high_patch = mpatches.Patch(facecolor="black", edgecolor="black",
                             label="High WTP (above median)")
ax.legend(handles=[low_patch, high_patch], fontsize=9,
          loc="upper right", frameon=False)

# Caption
caption = (
    "Notes: ITT coefficients from OLS with community-clustered SEs (siteno). "
    "Treat = any subsidy arm (treated_all). HighWTP = stated WTP above sample median "
    "(WTP_r1 × WTP_amt). Pooled R1+R2 for D2; R2 only for D6. "
    "Controls: county, market, transformer timing, baseline connection rate, population, "
    "gender, age, housing quality, baseline energy spending. "
    "Horizontal bars are 95\\% CIs. "
    "D6 is exploratory and does not survive Benjamini-Hochberg correction."
)
fig.text(0.0, -0.22, caption, wrap=True, fontsize=7, fontfamily="serif",
         va="top", ha="left",
         transform=ax.transAxes,
         color="#333333")

plt.tight_layout()

pdf_path = os.path.join(OUT_F, "wellbeing_wtp_heterogeneity.pdf")
png_path = os.path.join(OUT_F, "wellbeing_wtp_heterogeneity.png")
plt.savefig(pdf_path, bbox_inches="tight", dpi=300)
plt.savefig(png_path, bbox_inches="tight", dpi=300)
print(f"\nSaved: {pdf_path}")
print(f"Saved: {png_path}")
