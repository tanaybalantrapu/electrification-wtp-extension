clear all
local rootDir "/Users/~/projects/electrification-wtp-extension"

local jpe_data "`rootDir'/data/jpe/data/stata"
local out      "`rootDir'/outputs/tables"

* annual average exchange rates (from original do-files)
local xr_14 = 87.94
local xr_16 = 101.53
local xr_17 = 103.41

* annual average inflation
local i_15 = 0.0801
local i_16 = 0.0635
local i_17 = 0.0450

local x_16 = (1+`i_16')*(1+`i_15')*`xr_14'   /* 101.015 KES/USD */
local x_17 = (1+`i_17')*(1+`i_16')*(1+`i_15')*`xr_14'   /* 105.561 KES/USD */

********************************************************************************
* WTP × Life Satisfaction Extension
* Research questions:
*   1. Heterogeneous TOT on life_index by baseline WTP (IV with interaction)
*   2. WTP as predictor of life satisfaction among connected households (OLS)
* Identification mirrors tab_A3_A4.do (substitute wtp_high for highses)
* Last updated: 2026-03-22
********************************************************************************

********************************************************************************
* 1. Prepare impacts_1.dta (R1, 2016)
********************************************************************************

use "`jpe_data'/impacts_1.dta", clear

local base_vars base_energyspending_ksh base_asset_value_ksh
local r1_vars  gridelec_spending_ksh kerosene_spending_ksh energy_spending_ksh ///
               asset_value_ksh percapcons_ksh

foreach var in `base_vars' {
	gen `var'_x = `var' / `xr_14'
}
foreach var in `r1_vars' {
	gen `var'_x = `var' / `x_16'
}

keep reppid siteno hhid child treat_low treat_med treat_full treated_all ///
	busia base_market base_population base_connected_rate base_transearly ///
	base_connected base_housing base_bank base_energyspending_ksh_x ///
	base_female base_age base_educ base_asset_value_ksh_x ///
	female age_resp ///
	connected life_index symptoms_index ///
	gridelec_spending_ksh_x asset_value_ksh_x percapcons_ksh_x ///
	kerosene_spending_ksh_x energy_spending_ksh_x ///
	fraction_employed_all hours_worked number_appliances

foreach var in base_energyspending_ksh_x base_asset_value_ksh_x ///
               gridelec_spending_ksh_x asset_value_ksh_x percapcons_ksh_x ///
               kerosene_spending_ksh_x energy_spending_ksh_x {
	local newname = subinstr("`var'", "_ksh_x", "", 1)
	rename `var' `newname'
}

drop if base_connected == 1

save "`jpe_data'/temp_r1.dta", replace

********************************************************************************
* 2. Prepare impacts_2.dta (R2, 2017)
********************************************************************************

use "`jpe_data'/impacts_2.dta", clear

local base_vars base_energyspending_ksh base_asset_value_ksh
local r2_vars  gridelec_spending_ksh kerosene_spending_ksh energy_spending_ksh ///
               asset_value_ksh percapcons_ksh

foreach var in `base_vars' {
	gen `var'_x = `var' / `xr_14'
}
foreach var in `r2_vars' {
	gen `var'_x = `var' / `x_17'
}

keep reppid siteno hhid child treat_low treat_med treat_full treated_all ///
	busia base_market base_population base_connected_rate base_transearly ///
	base_connected base_housing base_bank base_energyspending_ksh_x ///
	base_female base_age base_educ base_asset_value_ksh_x ///
	female age_resp ///
	connected life_index symptoms_index ///
	gridelec_spending_ksh_x asset_value_ksh_x percapcons_ksh_x ///
	kerosene_spending_ksh_x energy_spending_ksh_x ///
	fraction_employed_all hours_worked number_appliances

foreach var in base_energyspending_ksh_x base_asset_value_ksh_x ///
               gridelec_spending_ksh_x asset_value_ksh_x percapcons_ksh_x ///
               kerosene_spending_ksh_x energy_spending_ksh_x {
	local newname = subinstr("`var'", "_ksh_x", "", 1)
	rename `var' `newname'
}

drop if base_connected == 1

save "`jpe_data'/temp_r2.dta", replace

********************************************************************************
* 3. Prepare demand.dta — WTP variables
********************************************************************************

use "`jpe_data'/demand.dta", clear
sort reppid

* Construct wtp_stated: maximum WTP_amt at which WTP_r1 == 1
* Each household sees one randomly assigned WTP_amt and gives a binary response.
* wtp_stated = WTP_amt if they said yes, 0 if they said no.
gen wtp_stated = WTP_amt * (WTP_r1 == 1)
replace wtp_stated = . if WTP_r1 == .

* Convert to USD at 2014 exchange rate for interpretability
gen wtp_stated_usd = wtp_stated / `xr_14'

* Binary: WTP_r1 == 1 at any positive price (willingness to pay anything)
gen wtp_any = (WTP_r1 == 1 & WTP_amt > 0)
replace wtp_any = . if WTP_r1 == .

* Robustness: WTP_r2 (6-week financing window)
gen wtp_r2_any = (WTP_r2 == 1 & WTP_amt > 0)
replace wtp_r2_any = . if WTP_r2 == .

keep reppid WTP_amt WTP_r1 WTP_r2 wtp_stated wtp_stated_usd wtp_any wtp_r2_any ///
     takeup price earn age female wall someschool employed notfarmer base_bank ///
     base_asset_value hhsize distance

save "`jpe_data'/temp_demand.dta", replace

********************************************************************************
* 4. Construct wtp_high (above-median binary indicator)
*    Must be done after merge so median is from the analytic sample
********************************************************************************

* --- Macro: controls (same as tab_A3_A4.do) ---
local community busia base_market base_transearly base_connected_rate base_population
local household female age_resp base_housing base_energyspending

********************************************************************************
* ANALYSIS 1a: Heterogeneous TOT on life_index by WTP — R1 (2016)
********************************************************************************

use "`jpe_data'/temp_r1.dta", clear
sort reppid
merge reppid using "`jpe_data'/temp_demand.dta"
drop if _merge != 3
drop _merge

* Construct wtp_high in analytic sample (adults only, non-missing WTP)
sum wtp_stated if child == 0 & wtp_stated != ., detail
gen wtp_high = (wtp_stated > `r(p50)') if wtp_stated != .

* Propagate wtp_high to child observations within same household
bysort siteno hhid: egen temp_wtp = max(wtp_high)
replace wtp_high = temp_wtp if wtp_high == .
drop temp_wtp

* Scale binary outcomes to percentages (consistent with originals)
foreach var in connected {
	replace `var' = 100 if `var' == 1
}

* --- Analysis 1a: IV interaction, life_index, R1 ---
replace connected = 1 if connected == 100

eststo r1_life: ivreg2 life_index wtp_high `community' `household' ///
	(connected c.connected#c.wtp_high = ///
	 treat_low treat_med treat_full ///
	 c.treat_low#c.wtp_high c.treat_med#c.wtp_high c.treat_full#c.wtp_high) ///
	if child == 0, cl(siteno)

* --- Analysis 1a: IV interaction, symptoms_index, R1 ---
eststo r1_sym: ivreg2 symptoms_index wtp_high `community' `household' ///
	(connected c.connected#c.wtp_high = ///
	 treat_low treat_med treat_full ///
	 c.treat_low#c.wtp_high c.treat_med#c.wtp_high c.treat_full#c.wtp_high) ///
	if child == 0, cl(siteno)

replace connected = 100 if connected == 1

esttab r1_life r1_sym using "`out'/tab_wtp_r1.tex", replace ///
	title("Heterogeneous TOT on Wellbeing by Baseline WTP — R1 (2016)") ///
	keep(connected c.connected#c.wtp_high wtp_high) ///
	varlabels(connected "Connected (TOT, low-WTP)" ///
	          c.connected#c.wtp_high "Connected × High WTP (differential TOT)" ///
	          wtp_high "High WTP (baseline)") ///
	mtitles("Life Satisfaction Index" "Mental Health Symptoms Index") ///
	star(* 0.1 ** 0.05 *** 0.01) b(3) se compress

* --- Analysis 2: OLS among connected, R1 ---
replace connected = 1 if connected == 100

eststo r1_ols_life: reg life_index wtp_stated_usd `community' `household' ///
	if child == 0 & connected == 1, cl(siteno)

eststo r1_ols_sym: reg symptoms_index wtp_stated_usd `community' `household' ///
	if child == 0 & connected == 1, cl(siteno)

esttab r1_ols_life r1_ols_sym using "`out'/tab_wtp_connected.tex", replace ///
	title("WTP as Predictor of Wellbeing Conditional on Connection — R1 (2016)") ///
	keep(wtp_stated_usd) ///
	varlabels(wtp_stated_usd "Stated WTP (USD, baseline)") ///
	mtitles("Life Satisfaction Index" "Mental Health Symptoms Index") ///
	star(* 0.1 ** 0.05 *** 0.01) b(3) se compress ///
	note("Sample: households connected at R1 follow-up. OLS with community-clustered SE.")

replace connected = 100 if connected == 1

save "`jpe_data'/temp_r1_merged.dta", replace

********************************************************************************
* ANALYSIS 1b: Heterogeneous TOT on life_index by WTP — R2 (2017)
********************************************************************************

use "`jpe_data'/temp_r2.dta", clear
sort reppid
merge reppid using "`jpe_data'/temp_demand.dta"
drop if _merge != 3
drop _merge

sum wtp_stated if child == 0 & wtp_stated != ., detail
gen wtp_high = (wtp_stated > `r(p50)') if wtp_stated != .

bysort siteno hhid: egen temp_wtp = max(wtp_high)
replace wtp_high = temp_wtp if wtp_high == .
drop temp_wtp

foreach var in connected {
	replace `var' = 100 if `var' == 1
}

replace connected = 1 if connected == 100

eststo r2_life: ivreg2 life_index wtp_high `community' `household' ///
	(connected c.connected#c.wtp_high = ///
	 treat_low treat_med treat_full ///
	 c.treat_low#c.wtp_high c.treat_med#c.wtp_high c.treat_full#c.wtp_high) ///
	if child == 0, cl(siteno)

eststo r2_sym: ivreg2 symptoms_index wtp_high `community' `household' ///
	(connected c.connected#c.wtp_high = ///
	 treat_low treat_med treat_full ///
	 c.treat_low#c.wtp_high c.treat_med#c.wtp_high c.treat_full#c.wtp_high) ///
	if child == 0, cl(siteno)

replace connected = 100 if connected == 1

esttab r2_life r2_sym using "`out'/tab_wtp_r2.tex", replace ///
	title("Heterogeneous TOT on Wellbeing by Baseline WTP — R2 (2017)") ///
	keep(connected c.connected#c.wtp_high wtp_high) ///
	varlabels(connected "Connected (TOT, low-WTP)" ///
	          c.connected#c.wtp_high "Connected × High WTP (differential TOT)" ///
	          wtp_high "High WTP (baseline)") ///
	mtitles("Life Satisfaction Index" "Mental Health Symptoms Index") ///
	star(* 0.1 ** 0.05 *** 0.01) b(3) se compress

********************************************************************************
* ROBUSTNESS
********************************************************************************

use "`jpe_data'/temp_r1_merged.dta", clear

* --- Robustness 1: WTP_r2 (financing window) as heterogeneity indicator ---
sum wtp_stated if child == 0 & wtp_stated != ., detail
* Reconstruct wtp_high_r2 using WTP_r2
gen wtp_high_r2 = (wtp_r2_any == 1) if wtp_r2_any != .
bysort siteno hhid: egen temp = max(wtp_high_r2)
replace wtp_high_r2 = temp if wtp_high_r2 == .
drop temp

replace connected = 1 if connected == 100

eststo rob_r2: ivreg2 life_index wtp_high_r2 `community' `household' ///
	(connected c.connected#c.wtp_high_r2 = ///
	 treat_low treat_med treat_full ///
	 c.treat_low#c.wtp_high_r2 c.treat_med#c.wtp_high_r2 c.treat_full#c.wtp_high_r2) ///
	if child == 0, cl(siteno)

* --- Robustness 2: wtp_any (binary: willing to pay anything) ---
gen wtp_any_hh = wtp_any
bysort siteno hhid: egen temp = max(wtp_any_hh)
replace wtp_any_hh = temp if wtp_any_hh == .
drop temp

eststo rob_any: ivreg2 life_index wtp_any_hh `community' `household' ///
	(connected c.connected#c.wtp_any_hh = ///
	 treat_low treat_med treat_full ///
	 c.treat_low#c.wtp_any_hh c.treat_med#c.wtp_any_hh c.treat_full#c.wtp_any_hh) ///
	if child == 0, cl(siteno)

* --- Robustness 3: Add highses to test WTP not just picking up SES ---
* Reconstruct highses (mirroring tab_A3_A4.do lines 96-109)
foreach var in base_educ notfarmer employed base_bank {
	replace `var' = `var' * 100
}
local het "base_educ notfarmer employed base_bank earn base_asset_value"
gen ses = 0
foreach var in `het' {
	sum `var'
	gen norm`var' = (`var' - `r(mean)') / `r(sd)'
	replace ses = ses + norm`var'
}
sum ses, detail
gen highses = (ses > `r(p75)') if ses != .
bysort siteno hhid: egen temp = max(highses)
replace highses = temp if highses == .
drop temp

eststo rob_ses: ivreg2 life_index wtp_high highses `community' `household' ///
	(connected c.connected#c.wtp_high c.connected#c.highses = ///
	 treat_low treat_med treat_full ///
	 c.treat_low#c.wtp_high c.treat_med#c.wtp_high c.treat_full#c.wtp_high ///
	 c.treat_low#c.highses c.treat_med#c.highses c.treat_full#c.highses) ///
	if child == 0, cl(siteno)

replace connected = 100 if connected == 1

esttab rob_r2 rob_any rob_ses using "`out'/tab_wtp_robustness.tex", replace ///
	title("Robustness: Alternative WTP Measures and SES Control — R1 (2016)") ///
	keep(connected c.connected#c.wtp_high_r2 c.connected#c.wtp_any_hh c.connected#c.wtp_high c.connected#c.highses) ///
	mtitles("WTP_r2 Binary" "WTP Any" "WTP + High SES") ///
	star(* 0.1 ** 0.05 *** 0.01) b(3) se compress ///
	note("Dep. var.: life_index. IV-2SLS, community-clustered SE.")

********************************************************************************
* 5. Clean up temp files
********************************************************************************

rm "`jpe_data'/temp_r1.dta"
rm "`jpe_data'/temp_r2.dta"
rm "`jpe_data'/temp_demand.dta"
rm "`jpe_data'/temp_r1_merged.dta"
