# cesg2025-nep-analysis  
Quantifying the long-run economic impact of the 1980 National Energy Program on Alberta (and what that implies for Canada’s productivity and fiscal capacity)

---

## Project overview

This project builds a reproducible province-year panel (1975–1995) and uses modern causal inference methods to measure how a major federal energy policy shock in 1980 changed Alberta’s long-run economic trajectory.

The focus is not on short-term disruption. The question is structural:

> After the National Energy Program (NEP) was introduced in 1980, did Alberta move onto a different long-run path for prosperity, wages, and income distribution — and if so, what does that mean for Canada’s broader productivity and fiscal base?

All source data are public (Statistics Canada, Bank of Canada, FRED).  
All code is Python/R style, released under MIT.

---

## Key findings (1975–1995 panel, Alberta vs counterfactual)

Using two-way fixed effects difference-in-differences, an event-study design, and a regularized synthetic control that constructs a “synthetic Alberta” from other provinces:

- **Real GDP per capita (1986 CAD):**  
  After 1981, Alberta’s real GDP per capita sits on average **~6% below** the path implied by its pre-1981 trajectory and by similar provinces.  
  Interpretation: Alberta remains high-income, but relative to where it was heading before 1980, its per-person prosperity is durably lower.

- **Compensation per worker (1986 CAD):**  
  Average real compensation per worker in Alberta is **~10% higher** than the counterfactual after 1981.  
  Interpretation: Alberta workers, on average, take home more than they “should have” based on pre-1981 patterns.

- **Wage share proxy:**  
  A province-level wage-to-output ratio (real labour compensation / real provincial GDP) is **~12% higher** than the counterfactual post-1981.  
  Interpretation: A larger share of Alberta’s total output shows up in paycheques rather than in retained rents/capital income.

- **Persistence:**  
  These gaps are not a one- or two-year blip around 1981. The altered pattern is still visible well into the mid-1990s.

Put together, the evidence is consistent with this story:  
A major federal intervention in Alberta’s core industry coincides with (i) a downward bend in Alberta’s long-run per-capita prosperity path and (ii) a redistribution of Alberta’s internal income toward wages. The effect persists across a decade-plus horizon.

---

## Why this matters

Alberta in the late 1970s and early 1980s was one of Canada’s highest-income, highest-investment provincial economies. It was a major driver of national capital formation, productivity growth, and fiscal capacity.

A persistent downward shift in Alberta’s per-capita output path after 1981 is therefore not just a provincial issue. It’s a national capacity issue.

Three reasons this matters for Canada:

1. **Productivity and capital deepening**  
   If a high-output, high-capital, high-wage province moves onto a weaker long-run trajectory, that drags on Canada’s overall productivity base. Canada’s current productivity problem is closely linked to weak business investment and low capital per worker; part of that story is historical shocks to provinces that once anchored national growth.

2. **Investment climate**  
   The Alberta results show that one large policy intervention can permanently change a province’s investment path and wage structure. That should be treated as an “investment climate” question, not only a regional dispute.

3. **Fiscal capacity / federal sustainability**  
   When a province that historically generated outsized fiscal capacity underperforms relative to its implied path, the long-run tax base that supports national programs and transfers is smaller than it otherwise would have been.

In plain terms: regional shocks to key provincial economies become national fiscal and productivity problems.

This project treats the NEP-era Alberta break as Part I of a broader series on how large federal policy decisions in 1980–1995 reshaped provincial economic roles:
- Alberta and energy policy (long-run prosperity path, wage structure, investment incentives),
- Ontario/Quebec and continental integration (CUSFTA/early NAFTA, manufacturing concentration, capital formation),
- Newfoundland and Labrador and the cod moratorium (deindustrialization, transfer dependence, long-run fiscal obligation).

---

## Methods (high-level)

**Panel construction (1975–1995):**
- Provincial GDP (constant 1986 CAD)  
- Population  
- Total labour compensation and employment  
- Monetary/interest rate controls and resource price controls for robustness  
- All deflated to constant dollars using province-appropriate price series

From these we build:
- Real GDP per capita (1986 CAD per resident)  
- Real compensation per worker (1986 CAD per employed worker)  
- Wage share proxy: real labour compensation / real provincial GDP

**Identification strategy:**
1. **Two-way fixed effects Difference-in-Differences (TWFE DiD)**  
   - Alberta treated; 1981+ post period  
   - Province fixed effects + year fixed effects  
   - Clustered standard errors at the province level  
   - Coefficient on Alberta × Post1981 is interpreted as Alberta’s average post-1981 deviation from the counterfactual path implied by other provinces and pre-period trends.

2. **Dynamic event study**  
   - Year-relative-to-1981 bins (leads/lags) instead of a single “post” dummy.  
   - Lets us see whether Alberta was already drifting before 1981 and how the gap evolves after.  
   - Joint F-tests on pre-period coefficients check for parallel trends.

3. **Regularized synthetic control**  
   - Builds a “synthetic Alberta” from weighted combinations of other provinces that best match Alberta’s pre-1981 trajectory for each outcome.  
   - Uses constrained ridge weighting and bias correction to improve stability and interpretability.  
   - The Alberta–Synthetic Alberta gap after 1981 is read as the post-shock deviation.

**Diagnostics included in this repo:**
- Pre-period vs post-period RMSPE for synthetic control fits  
- Placebo-in-time and placebo-in-space checks  
- Sensitivity to energy prices, interest rates, etc.

---

## Repo structure (summary)

- `00_prepare_base_panel_v2.py`  
  End-to-end panel builder. Pulls raw provincial series (GDP, compensation of employees, employment, population, CPI, etc.), aligns units, converts to constant 1986 CAD, and produces a clean province-year dataset for 1975–1995.

- `data_sources.md`  
  Notes on where each source series comes from (Statistics Canada tables, Bank of Canada, FRED), including how they’re transformed.

- Draft writeup(s)  
  The working paper text describing Alberta’s post-1981 trajectory, the methods, and the persistence of the effect.

Everything is MIT-licensed to make external review and replication straightforward.

---

## Replication / reproducibility

- All analysis uses public data only.  
- The panel builder script documents transformations explicitly.  
- The causal estimates in the writeup come directly from this panel and the listed methods (TWFE DiD, event study, regularized synthetic control).

Planned additions:
- A frozen “analysis-ready” CSV export of the processed panel (province-year, 1975–1995).  
- A short data dictionary describing each constructed variable in plain English.

---

## Limitations

- Alberta is uniquely exposed to global oil prices and early-1980s monetary tightening. The fixed effects and synthetic control approaches isolate Alberta relative to other provinces, but they cannot eliminate every macro channel. Results should be interpreted as “persistent structural deviation coincident with the 1980 policy shock,” not a lab experiment.

- With a donor pool of Canadian provinces (excluding PEI in early years due to missing data), power is finite. Results emphasize persistence and magnitude, not single-year precision.

- The wage share proxy is a practical ratio (real labour compensation / real GDP) at the provincial level, not a textbook factor share. It is used as a distributional indicator, not an accounting identity.

---

## Disclaimer

This work was done independently using publicly available data (Statistics Canada, Bank of Canada, FRED).  
It does not include any Technomics client data or proprietary material.  
All analysis, interpretation, and any errors are my own.

This repository is intended to demonstrate transparent, reproducible economic analysis of historical policy shocks using modern causal tools. It should not be read as representing the views of any employer, client, or institution.

---

## About the author

I’m an Ottawa-based quantitative analyst working in cost/schedule and economic performance analytics.  
Before my current role, I spent seven years at Statistics Canada working with large-scale provincial economic and fiscal indicators.

My work focuses on building reproducible data pipelines in Python/R and using causal inference (difference-in-differences, event study, synthetic control) to understand how major policy events affect provincial prosperity, wages, and long-run productivity and fiscal capacity.

Contact: gwilly84@duck.com
