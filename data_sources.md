# 📊 Data Sources: CESG 2025 NEP Panel

This analysis draws entirely on **publicly available data** from:

- Statistics Canada (StatCan)
- U.S. Federal Reserve Economic Data (FRED)

These datasets form the basis of the panel used to evaluate the economic impact of the National Energy Program (NEP) on Alberta from 1975–1990.

---

## 🇨🇦 Statistics Canada

| Dataset Description | Table ID | Direct Link |
|---------------------|----------|-------------|
| Gross domestic product (GDP) at factor cost, by selected industries (x 1,000,000) | 36-10-0380-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610038001) |
| Gross domestic product (GDP) at factor cost, by industry (x 1,000,000) | 36-10-0381-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610038101) |
| Wages and salaries and supplementary labour income, by industry, by province or territory, monthly, 1961 - 1996 (x 1,000) | 36-10-0298-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610029801) |
|Labour force characteristics by gender and detailed age group, monthly, unadjusted for seasonality (x 1,000) | 14-10-0017-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701) |
| Population estimates on July 1, by age and gender | 17-10-0005-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000501) |
| Consumer Price Index, monthly, not seasonally adjusted | 18-10-0004-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401) |
| Consumer Price Index, annual average, not seasonally adjusted | 18-10-0005-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000501) |
| Financial market statistics, last Wednesday unless otherwise stated, Bank of Canada | 10-10-0122-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1010012201) |

---

## 🇺🇸 FRED (Federal Reserve Economic Data)

| Dataset Description | Series ID | Direct Link |
|---------------------|-----------|-------------|
| WTI Crude Oil Spot Price | DCOILWTICO | [View Series](https://fred.stlouisfed.org/series/DCOILWTICO) |
| Coal Price Index | PCOALUSDM | [View Series](https://fred.stlouisfed.org/series/PCOALUSDM) |
| Industrial Chemical Price Index | PCU325311325311 | [View Series](https://fred.stlouisfed.org/series/PCU325311325311) |

---

## 💡 How to Use

To replicate this project:
1. Open each **"View Table"** or **"View Series"** link.
2. Use the **Download CSV** button on StatCan/FRED to save each dataset locally.
3. Save the files into a folder called `data/raw/` in your local project directory.
4. Name the files to match what's expected by the code (e.g., `gdp_by_industry_nominal.csv`).

If you're unsure about file names, check the path setup in `scripts/00_download_sources.py` or your `README.md`.

---

## 📎 Notes

- All data is open-access and does not require login or license.
- All monetary values are deflated to 1986 dollars using CPI as described in the paper.
