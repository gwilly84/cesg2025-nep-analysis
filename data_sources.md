# 🧾 Dominion and Divergence: Creighton, Econometrics, and the National Energy Program

This repository accompanies the CESG 2025 submission:  
**"Dominion and Divergence: Creighton, Econometrics, and the National Energy Program"**  
by **Greg Williams**.

It contains the data documentation code for constructing a custom provincial panel dataset spanning **1975–1990**, used to evaluate the impact of the National Energy Program (NEP) on Alberta relative to other Canadian provinces.

---

## 🗂 Data Sources and Construction

A balanced panel was built from publicly available Canadian data.  
**Prince Edward Island** and **Newfoundland and Labrador** were excluded due to gaps in key macroeconomic series.

All monetary variables are deflated to constant **1986 dollars** using province-specific CPI indices.  
Where 1975 data were unavailable—particularly for employment and wages—values were **linearly interpolated**.

### 📌 Core Indicators

| Indicator              | Description                                                                                           | Source                                                                 |
|------------------------|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| **Nominal GDP (sector)** | Mining, quarrying, and oil & gas extraction sector GDP                                                | [36-10-0380-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610038001) |
| **Nominal GDP (total)**  | All-industry GDP                                                                                     | [36-10-0222-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610022201) |
| **Wages (nominal)**      | Aggregate wages and salaries (all industries)                                                        | [36-10-0480-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610048001) |
| **Employment**           | Annual employment (15+, all industries)                                                              | [14-10-0023-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410002301) |
| **Population**           | July 1 provincial population estimates                                                               | [17-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000501) |
| **CPI (provincial)**     | Consumer Price Index (NSA, 1986 = 100)                                                               | [18-10-0004-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401), [18-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000501) |
| **Bank Rate**            | Annual average Bank of Canada overnight rate                                                         | [10-10-0122-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1010012201) |
| **WTI Crude Oil**        | West Texas Intermediate spot price (USD)                                                             | [FRED DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO)      |
| **Coal PPI**             | U.S. Producer Price Index for coal                                                                   | [FRED WPU051](https://fred.stlouisfed.org/series/WPU051)              |

---

## 🧮 Outcome Variables (Log, Real 1986 CAD)

The following log-transformed and deflated variables are used as outcome variables:

| Variable                   | Formula                                           | Description                                      |
|---------------------------|---------------------------------------------------|--------------------------------------------------|
| `log(GDP per worker)`     | Real GDP (mining) ÷ total employment              | Capital productivity in the resource sector      |
| `log(Wages per worker)`   | Real wages ÷ total employment                     | Labour market returns                            |
| `log(GDP per capita)`     | Real GDP (mining) ÷ population                    | Proxy for general economic performance           |

---

## 📊 Econometric Framework

To identify the effects of the NEP (treatment year: 1981), three causal inference designs are used:

1. **Difference-in-Differences (DiD)**  
   Two-way fixed effects model with Alberta × Post interactions and macroeconomic controls.

2. **Event Study**  
   Dynamic DiD extension using event-time indicators from *k = –5* to *k = +9*.

3. **Synthetic Control Method (SCM)**  
   Ridge-regularized donor weighting minimizes pre-NEP RMSE to build a synthetic Alberta counterfactual.

All model outputs—including figures and regression tables—are found in the paper.

