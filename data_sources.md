# CESG 2025 – NEP Analysis: Data Sources

This document outlines all data tables and external sources used to construct the provincial panel dataset for the analysis of the 1980 National Energy Program (NEP). All monetary values were deflated to 1986 dollars using the appropriate provincial CPI series. Alberta and eight comparator provinces are included; Prince Edward Island was excluded due to missing key indicators.

## 🏭 Economic Output

| Variable | Description | Source |
|---------|-------------|--------|
| GDP (Nominal and Real) | GDP at basic prices, by industry and province (x 1,000,000) | StatCan Table 36-10-0380-01 and 36-10-0381-01 |
| GDP per Capita | Constructed from real GDP (1986 CAD) divided by population | Derived |
| GDP per Worker | Constructed from real GDP (1986 CAD) divided by total employment | Derived |

## 💼 Wages and Employment

| Variable | Description | Source |
|----------|-------------|--------|
| Wages (Nominal) | Average weekly earnings by industry and province | StatCan Table 36-10-0298-01 |
| Employment | Total employment by province, age 15+, all industries, annual | StatCan Table 14-10-0017-01 |
| Wages per Worker | Constructed as real annual wages divided by employment | Derived |

## 👥 Population

| Variable | Description | Source |
|----------|-------------|--------|
| Population | Population estimates by province, July 1st | StatCan Table 17-10-0005-01 |

## 💸 Inflation / Deflation

| Variable | Description | Source |
|----------|-------------|--------|
| CPI (Annual) | Annual provincial CPI (not seasonally adjusted) | StatCan Table 18-10-0005-01 |
| CPI Base Year | 1986 dollars | Fixed internally |

## 🛢 Commodity Prices & Macro Controls

| Variable | Description | Source |
|----------|-------------|--------|
| WTI Crude Oil (USD/bbl) | Spot price | FRED Series: DCOILWTICO |
| Coal Price Index | Producer Price Index for Coal | FRED Series: WPU051 |
| Bank Rate | Bank of Canada Annual Average | StatCan Table 10-10-0122-01 |

## 🔁 Data Processing Notes

- All monetary variables are deflated to 1986 CAD.
- Where values were missing (e.g., 1975 employment/wages), linear interpolation was applied to balance the panel.
- GDP and wage metrics are aggregated from industry-level to provincial-level indicators using population or employment weighting where applicable.

---

## 📬 Questions?

For more details about variable construction or data interpretation, please refer to the methodology section of the paper or contact the author directly at **gwilly84@gmail.com**.
