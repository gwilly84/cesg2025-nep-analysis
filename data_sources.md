# 📊 Data Sources: CESG 2025 NEP Panel

This analysis draws entirely on **publicly available data** from:

- Statistics Canada (StatCan)
- U.S. Federal Reserve Economic Data (FRED)

These datasets form the basis of the panel used to evaluate the economic impact of the National Energy Program (NEP) on Alberta from 1975–1990.

---

## 🇨🇦 Statistics Canada

| Dataset Description | Table ID | Direct Link |
|---------------------|----------|-------------|
| GDP by industry (nominal) | 36-10-0380-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610038001) |
| GDP by industry (real, chained 2012 $) | 36-10-0381-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610038101) |
| Average weekly earnings by industry | 36-10-0298-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610029801) |
| Employment by province (age 15+) | 14-10-0017-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701) |
| Population estimates by province | 17-10-0005-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000501) |
| Consumer Price Index (CPI), annual average | 18-10-0004-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401) |
| CPI by province | 18-10-0005-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000501) |
| Bank of Canada interest rate | 10-10-0122-01 | [View Table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1010012201) |

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
