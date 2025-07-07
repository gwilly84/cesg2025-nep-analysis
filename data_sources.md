## 🗂️ Data Sources & Construction

This dataset spans **1975–1990** and covers eight Canadian provinces (excluding **PEI** and **Newfoundland and Labrador** due to incomplete series).  
All monetary values are deflated to **constant 1986 CAD** using province-specific CPI data.  
Where values were unavailable—particularly in early years—**linear interpolation** was used to preserve panel balance.

### 📌 Core Indicators

| Indicator                | Description                                                                 | Source                                                                 |
|--------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------|
| **Nominal GDP (sector)** | GDP for mining, quarrying, and oil & gas extraction                         | [36-10-0380-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610038001) |
| **Nominal GDP (total)**  | GDP across all industries                                                   | [36-10-0222-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610022201) |
| **Wages (nominal)**      | Total aggregate wages and salaries (all industries)                         | [36-10-0480-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610048001) |
| **Employment**           | Total employment, persons aged 15+ (all industries)                         | [14-10-0023-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410002301) |
| **Population**           | Provincial July 1 population estimates                                      | [17-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000501) |
| **CPI (provincial)**     | Annual Consumer Price Index (NSA, 1986 = 100)                               | [18-10-0004-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401), [18-10-0005-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000501) |
| **Bank Rate**            | Annual average Bank of Canada overnight rate                                | [10-10-0122-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1010012201) |
| **WTI Crude Oil**        | West Texas Intermediate spot price (USD)                                    | [FRED DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO)      |
| **Coal PPI**             | U.S. Producer Price Index for coal                                          | [FRED WPU051](https://fred.stlouisfed.org/series/WPU051)              |

---

## 🧮 Outcome Variable Construction (Real, Log-Transformed)

All outcomes are measured in **real 1986 CAD** and **log-transformed**:

| Variable                 | Formula                                | Description                                    |
|--------------------------|----------------------------------------|------------------------------------------------|
| `log(GDP per worker)`    | Real GDP (mining, oil & gas) ÷ total employment   | Proxy for resource-sector productivity         |
| `log(Wages per worker)`  | Real total wages ÷ total employment    | Captures average labour returns across sectors |
| `log(GDP per capita)`    | Real total GDP ÷ total population      | Measure of overall economic performance        |

> Note: All CPI adjustments are province-specific. Employment and population figures are total—not sector-specific—to maintain comparability across metrics.
