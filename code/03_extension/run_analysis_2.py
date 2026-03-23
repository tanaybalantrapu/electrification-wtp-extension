"""
WTP Heterogeneity x Appliances & Life Satisfaction — TOT (IV) Extension
========================================================================
Replicates the IV specification from tab_A3_A4.do (lines 152–154) substituting
wtp_high for highses, for two outcomes: number_appliances and life_index.

Outputs:
  outputs/tables/wellbeing_heterogeneity_2.csv
  outputs/tables/tab_wellbeing_main_2.tex
  outputs/figures/wellbeing_wtp_heterogeneity_2.pdf
  outputs/figures/wellbeing_wtp_heterogeneity_2.png
"""

import os
import warnings
import numpy as np
import pandas as pd
import pyreadstat
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import norm

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT  = os.path.expanduser("~/projects/electrification-wtp-extension")
DATA  = os.path.join(ROOT, "data/jpe/data/stata")
OUT_T = os.path.join(ROOT, "outputs/tables")
OUT_F = os.path.join(ROOT, "outputs/figures")
os.makedirs(OUT_T, exist_ok=True)
os.makedirs(OUT_F, exist_ok=True)

# ── 1. Load data ───────────────────────────────────────────────────────────────
print("Loading data...")
imp1, _   = pyreadstat.read_dta(os.path.join(DATA, "impacts_1.dta"))
demand, _ = pyreadstat.read_dta(os.path.join(DATA, "demand.dta"))

# ── 2. Filter impacts: R1 adults, not pre-connected ───────────────────────────
df = imp1[(imp1["child"] == 0) & (imp1["base_connected"] == 0)].copy()
df["base_energyspending"] = df["base_energyspending_ksh"] / 87.94

# Scale connected to 0/1 (confirm range first)
print(f"connected range: [{df['connected'].min()}, {df['connected'].max()}]")
df["connected"] = (df["connected"] > 0).astype(float)

# ── 3. Construct WTP variables from demand.dta ────────────────────────────────
demand["wtp_stated"] = demand["WTP_amt"] * (demand["WTP_r1"] == 1)
demand["wtp_stated"] = demand["wtp_stated"].where(demand["WTP_r1"].notna())
median_wtp = demand["wtp_stated"].median()
demand["wtp_high"] = (demand["wtp_stated"] > median_wtp).astype(float)

print(f"WTP median (KES): {median_wtp:,.1f}")
print(f"High-WTP share (demand sample): {demand['wtp_high'].mean():.3f}")

wtp_cols = ["reppid", "wtp_stated", "wtp_high"]
demand_wtp = demand[wtp_cols].drop_duplicates("reppid")

# ── 4. Merge WTP onto impacts ──────────────────────────────────────────────────
df = df.merge(demand_wtp, on="reppid", how="left")
print(f"WTP merge rate: {df['wtp_high'].notna().mean():.3f}")
print(f"High-WTP share in analysis sample: {df['wtp_high'].mean():.3f}")
print(f"N after filter + merge: {len(df)}")

# ── 5. Construct interaction columns ──────────────────────────────────────────
df["connected_x_wtp"] = df["connected"]  * df["wtp_high"]
df["tl_x_wtp"]        = df["treat_low"]  * df["wtp_high"]
df["tm_x_wtp"]        = df["treat_med"]  * df["wtp_high"]
df["tf_x_wtp"]        = df["treat_full"] * df["wtp_high"]

# ── 6. Define controls ─────────────────────────────────────────────────────────
COMMUNITY = ["busia", "base_market", "base_transearly",
             "base_connected_rate", "base_population"]

# Use age_resp if present (not all-NaN), else base_age
if df["age_resp"].isna().all():
    age_col = "base_age"
    print("age_resp all-NaN; using base_age")
else:
    age_col = "age_resp"
    print(f"Using {age_col} for household age control")

HOUSEHOLD = ["female", age_col, "base_housing", "base_energyspending"]
CONTROLS  = COMMUNITY + HOUSEHOLD

# ── 7. IV2SLS regression function ─────────────────────────────────────────────
ENDOG  = ["connected", "connected_x_wtp"]
INSTRS = ["treat_low", "treat_med", "treat_full", "tl_x_wtp", "tm_x_wtp", "tf_x_wtp"]
EXOG_VARS = ["wtp_high"] + CONTROLS  # const added separately

def run_iv(df_in, outcome):
    """
    Run IV2SLS mirroring tab_A3_A4.do lines 152-154 with wtp_high substituted
    for highses. Returns dict of results.
    """
    needed = [outcome] + ENDOG + INSTRS + EXOG_VARS + ["siteno"]
    # rename age_col to a stable name if needed
    sub = df_in[needed].copy().dropna()
    n = len(sub)

    # Add constant
    sub["const"] = 1.0

    exog_cols = ["const", "wtp_high"] + CONTROLS

    from linearmodels.iv import IV2SLS

    dependent  = sub[outcome]
    exog       = sub[exog_cols]
    endog      = sub[ENDOG]
    instruments = sub[INSTRS]

    model = IV2SLS(dependent, exog, endog, instruments)
    res   = model.fit(cov_type="clustered", clusters=sub["siteno"])

    params = res.params
    cov    = res.cov

    b1  = params["connected"]
    b3  = params["connected_x_wtp"]
    b13 = b1 + b3

    se_b1 = res.std_errors["connected"]
    se_b3 = res.std_errors["connected_x_wtp"]

    # Delta method SE for b1 + b3
    var_b1  = cov.loc["connected", "connected"]
    var_b3  = cov.loc["connected_x_wtp", "connected_x_wtp"]
    cov_b1b3 = cov.loc["connected", "connected_x_wtp"]
    se_b13  = np.sqrt(var_b1 + var_b3 + 2 * cov_b1b3)

    p_b1  = res.pvalues["connected"]
    p_b3  = res.pvalues["connected_x_wtp"]
    p_b13 = 2 * (1 - norm.cdf(abs(b13 / se_b13)))

    # Control group mean/SD
    ctrl_mask = (sub["treat_low"] == 0) & (sub["treat_med"] == 0) & (sub["treat_full"] == 0)
    ctrl_mean = sub.loc[ctrl_mask, outcome].mean()
    ctrl_sd   = sub.loc[ctrl_mask, outcome].std()

    return dict(
        outcome=outcome,
        n_obs=n,
        ctrl_mean=ctrl_mean,
        ctrl_sd=ctrl_sd,
        b1=b1,    b1_se=se_b1,  b1_p=p_b1,
        b3=b3,    b3_se=se_b3,  b3_p=p_b3,
        b13=b13,  b13_se=se_b13, b13_p=p_b13,
    )

# ── 8. Run regressions ─────────────────────────────────────────────────────────
outcomes = ["number_appliances", "life_index"]
outcome_labels = {
    "number_appliances": "Number of appliances owned",
    "life_index":        "Normalised life satisfaction",
}

results = {}
for out in outcomes:
    print(f"\nRunning IV2SLS for: {out}")
    r = run_iv(df, out)
    results[out] = r
    print(f"  b1 (low-WTP TOT):    {r['b1']:.4f}  SE={r['b1_se']:.4f}  p={r['b1_p']:.4f}")
    print(f"  b3 (differential):   {r['b3']:.4f}  SE={r['b3_se']:.4f}  p={r['b3_p']:.4f}")
    print(f"  b1+b3 (high-WTP TOT):{r['b13']:.4f}  SE={r['b13_se']:.4f}  p={r['b13_p']:.4f}")
    print(f"  ctrl_mean={r['ctrl_mean']:.4f}  ctrl_sd={r['ctrl_sd']:.4f}  N={r['n_obs']}")

# ── 9. Save CSV ────────────────────────────────────────────────────────────────
csv_rows = []
for out, r in results.items():
    csv_rows.append({
        "outcome":    out,
        "n_obs":      r["n_obs"],
        "ctrl_mean":  round(r["ctrl_mean"], 4),
        "ctrl_sd":    round(r["ctrl_sd"],   4),
        "b1":         round(r["b1"],     4),
        "b1_se":      round(r["b1_se"],  4),
        "b1_p":       round(r["b1_p"],   4),
        "b3":         round(r["b3"],     4),
        "b3_se":      round(r["b3_se"],  4),
        "b3_p":       round(r["b3_p"],   4),
        "b13":        round(r["b13"],    4),
        "b13_se":     round(r["b13_se"], 4),
        "b13_p":      round(r["b13_p"],  4),
    })

csv_df = pd.DataFrame(csv_rows)
csv_path = os.path.join(OUT_T, "wellbeing_heterogeneity_2.csv")
csv_df.to_csv(csv_path, index=False)
print(f"\nSaved: {csv_path}")

# ── 10. Helper: star string ────────────────────────────────────────────────────
def stars(p):
    if p < 0.01:  return r"\sym{***}"
    if p < 0.05:  return r"\sym{**}"
    if p < 0.10:  return r"\sym{*}"
    return ""

def fmt_coef(b, p):
    return f"${b:.3f}${stars(p)}"

def fmt_se(se):
    return f"$({se:.3f})$"

# ── 11. LaTeX table ────────────────────────────────────────────────────────────
ra = results["number_appliances"]
rb = results["life_index"]

tex = r"""%% Tab: Wellbeing Heterogeneity by Baseline WTP — TOT (IV) specification
%% Standalone table — \input this file into a document that loads:
%%   booktabs, tabu, setspace, caption

\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}

\begin{table}[htbp]
\centering
\caption*{Table 2\textemdash Heterogeneous TOT effects of grid connection,
  by baseline willingness-to-pay}
\vspace{-0.5em}
\begin{tabu} to \linewidth {X[20,l] X[5,c] X[5,c] X[5,c] X[5,c] X[4,c]}
\toprule
 & Control & Low-WTP & High-WTP & TOT\,$\times$ & \\[-0.25em]
 & [SD] & TOT & TOT & HighWTP & $N$ \\[-0.25em]
 & (1) & (2) & (3) & (4) & (5) \\
\midrule \\[-1.2em]

%% ── Panel A ──────────────────────────────────────────────────────────────
\multicolumn{6}{l}{\emph{Panel A: Appliance Outcomes}} \\[0.5em]

""" + \
r"\hspace{2.5mm} A1. " + outcome_labels["number_appliances"] + \
"\n  & " + f"{ra['ctrl_mean']:.3f}" + \
" & " + fmt_coef(ra['b1'], ra['b1_p']) + \
" & " + fmt_coef(ra['b13'], ra['b13_p']) + \
" & " + fmt_coef(ra['b3'], ra['b3_p']) + \
" & " + str(ra['n_obs']) + r" \\" + "\n" + \
"& " + f"[{ra['ctrl_sd']:.3f}]" + \
" & " + fmt_se(ra['b1_se']) + \
" & " + fmt_se(ra['b13_se']) + \
" & " + fmt_se(ra['b3_se']) + \
r" & \\" + r"""[0.8em]

%% ── Panel B ──────────────────────────────────────────────────────────────
\multicolumn{6}{l}{\emph{Panel B: Wellbeing Outcomes}} \\[0.5em]

""" + \
r"\hspace{2.5mm} B1. " + outcome_labels["life_index"] + \
"\n  & " + f"{rb['ctrl_mean']:.3f}" + \
" & " + fmt_coef(rb['b1'], rb['b1_p']) + \
" & " + fmt_coef(rb['b13'], rb['b13_p']) + \
" & " + fmt_coef(rb['b3'], rb['b3_p']) + \
" & " + str(rb['n_obs']) + r" \\" + "\n" + \
"& " + f"[{rb['ctrl_sd']:.3f}]" + \
" & " + fmt_se(rb['b1_se']) + \
" & " + fmt_se(rb['b13_se']) + \
" & " + fmt_se(rb['b3_se']) + \
r" & \\" + r"""[0.8em]

\bottomrule
\end{tabu}

\begin{minipage}{\linewidth}
\footnotesize
\setlength{\parskip}{2pt}
\textit{Notes}: Column~(1) reports the control-group mean with the standard
deviation in brackets. Columns~(2) and~(3) report TOT coefficients estimated
by IV2SLS. Instruments: \texttt{treat\_low}, \texttt{treat\_med},
\texttt{treat\_full} and their interactions with \texttt{HighWTP}.
Column~(2) is $\hat{b}_1$ (low-WTP TOT) and column~(3) is
$\hat{b}_1 + \hat{b}_3$ (high-WTP TOT); standard errors computed by the
delta method. Column~(4) reports $\hat{b}_3$ (differential effect) with its
standard error in parentheses. Sample: adults not pre-connected at baseline
(R1, 2016). \text{HighWTP} $= 1$ if stated WTP $>$ sample median ($43.6\,\%$
of sample). Controls: county, market proximity, transformer timing, baseline
connection rate, population, gender, age, housing quality, baseline energy
spending. Standard errors clustered at community level (\texttt{siteno}).
Asterisks indicate significance (two-tailed):
$^{*}p<0.10$;\;$^{**}p<0.05$;\;$^{***}p<0.01$.
\end{minipage}
\end{table}
"""

tex_path = os.path.join(OUT_T, "tab_wellbeing_main_2.tex")
with open(tex_path, "w") as f:
    f.write(tex)
print(f"Saved: {tex_path}")

# ── 12. AEA-style coefficient figure ──────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

fig, axes = plt.subplots(2, 1, figsize=(6, 5), sharex=False)
fig.patch.set_facecolor("white")

plot_outcomes = [
    ("number_appliances", "Number of appliances"),
    ("life_index",        "Life satisfaction index"),
]

z95 = 1.96

for ax, (out, ylabel) in zip(axes, plot_outcomes):
    r = results[out]

    ax.set_facecolor("white")
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--", zorder=1)

    y_low  = 1.15   # low-WTP row
    y_high = 0.85   # high-WTP row

    # Low-WTP TOT (hollow circle)
    ci_lo = r["b1"]  - z95 * r["b1_se"]
    ci_hi = r["b1"]  + z95 * r["b1_se"]
    ax.errorbar(
        r["b1"], y_low,
        xerr=[[r["b1"] - ci_lo], [ci_hi - r["b1"]]],
        fmt="o", color="black",
        markerfacecolor="white", markeredgecolor="black",
        markersize=7, linewidth=1.2, capsize=3, zorder=3
    )

    # High-WTP TOT (filled circle)
    ci_lo13 = r["b13"] - z95 * r["b13_se"]
    ci_hi13 = r["b13"] + z95 * r["b13_se"]
    ax.errorbar(
        r["b13"], y_high,
        xerr=[[r["b13"] - ci_lo13], [ci_hi13 - r["b13"]]],
        fmt="o", color="black",
        markerfacecolor="black", markeredgecolor="black",
        markersize=7, linewidth=1.2, capsize=3, zorder=3
    )

    ax.set_yticks([y_low, y_high])
    ax.set_yticklabels(["Low-WTP TOT", "High-WTP TOT"], fontsize=9)
    ax.set_ylim(0.4, 1.6)

    ax.set_ylabel(ylabel, fontsize=9, labelpad=6)
    ax.tick_params(axis="x", labelsize=9)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

axes[-1].set_xlabel("TOT coefficient (IV2SLS)", fontsize=10)

# Legend on top panel
low_patch  = mpatches.Patch(facecolor="white", edgecolor="black",
                             label="Low-WTP TOT")
high_patch = mpatches.Patch(facecolor="black", edgecolor="black",
                             label="High-WTP TOT")
axes[0].legend(handles=[low_patch, high_patch], fontsize=9,
               loc="upper right", frameon=False)

caption = (
    "Notes: TOT (IV) coefficients by baseline WTP group. "
    "Instruments: treatment arms \u00d7 WTP. R1 data. "
    "95\\% CI, SEs clustered at community level."
)
fig.text(0.0, -0.03, caption, wrap=True, fontsize=7, fontfamily="serif",
         va="top", ha="left", color="#333333")

plt.tight_layout(rect=[0, 0.02, 1, 1])

pdf_path = os.path.join(OUT_F, "wellbeing_wtp_heterogeneity_2.pdf")
png_path = os.path.join(OUT_F, "wellbeing_wtp_heterogeneity_2.png")
plt.savefig(pdf_path, bbox_inches="tight", dpi=300)
plt.savefig(png_path, bbox_inches="tight", dpi=300)
print(f"Saved: {pdf_path}")
print(f"Saved: {png_path}")

# ── 13. Summary print ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("KEY RESULTS SUMMARY")
print("="*60)
for out in outcomes:
    r = results[out]
    print(f"\nOutcome: {out}")
    print(f"  N={r['n_obs']}  ctrl_mean={r['ctrl_mean']:.4f}  ctrl_sd={r['ctrl_sd']:.4f}")
    print(f"  b1  (low-WTP TOT):    {r['b1']:.4f}  SE={r['b1_se']:.4f}  p={r['b1_p']:.4f}")
    print(f"  b3  (differential):   {r['b3']:.4f}  SE={r['b3_se']:.4f}  p={r['b3_p']:.4f}")
    print(f"  b1+b3(high-WTP TOT):  {r['b13']:.4f}  SE={r['b13_se']:.4f}  p={r['b13_p']:.4f}")
print("="*60)
