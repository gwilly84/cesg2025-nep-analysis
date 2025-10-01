#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script accompanies the paper:
"Dominion and Divergence: Creighton, Econometrics, and the National Energy Program" (Williams, 2025)

📌 Purpose: Builds a 1975–1995 provincial panel from StatsCan and FRED data
📄 Outputs: Cleaned panel CSVs, summary stats, and figures
🛠 Requirements: Python 3.x, DuckDB, pandas, numpy, matplotlib

Author: Greg Williams | License: MIT (except where StatsCan/FRED license restrictions apply)
Note: You must obtain raw data from official sources (StatCan, FRED, etc.)

🧠 Disclaimer: This code is provided as-is for academic transparency. No guarantees of completeness or accuracy.
"""
"""
00_prepare_base_panel_duckdb.py — Construct full NEP panel using DuckDB
Author: gwilly | Finalized: Aug 2025 (rev: FX + GDP fixes, robust totals, comp split)

Notes on this revision:
- Total GDP now uses 36100324 for 1975–1980 (deflated with provincial CPI) and 36100221 for 1981–1995 (prefers constant/chained, otherwise deflates current with CPI).
- Compensation: fixed missing Comp_Real by explicitly deflating monthly sums with CPI after the merge.
- AG_FISH compensation is split into AGRIC/FISH using GDP_Real weights with 50/50 fallback when weights missing.
- Province-level tables are built off totals to avoid sector join holes. Basic diagnostics included.
- Plot x-axis forced to integer years (no “.5” ticks).
"""

import pandas as pd
import numpy as np
import duckdb
from pathlib import Path
from matplotlib.ticker import MaxNLocator, FuncFormatter
import matplotlib.pyplot as plt

# === PATH SETUP ===
ROOT_DIR = Path("/home/gwilly/Documents/Data")
BASE_DIR = Path("/home/gwilly/Documents/Economic History/Industry Comparison")
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === FILE PATHS ===
minegdp80_file = ROOT_DIR / "StatCan/GDP/36100380.csv"
minegdp90_file = ROOT_DIR / "StatCan/GDP/36100381.csv"
totgdp80_file  = ROOT_DIR / "StatCan/GDP/36100324.csv"  # use for 1975–1980
totgdp90_file  = ROOT_DIR / "StatCan/GDP/36100221.csv"  # use for 1981–1995
wages_file     = ROOT_DIR / "StatCan/GDP/36100298.csv"
lfs_file       = ROOT_DIR / "StatCan/LFS/14100017.csv"
cpi_file       = ROOT_DIR / "StatCan/CPI/18100004.csv"
bank_rate_file = ROOT_DIR / "StatCan/BoC/10100122.csv"
wti_file       = ROOT_DIR / "FRED/WTISPLC.csv"
coal_file      = ROOT_DIR / "FRED/WPU051.csv"
chem_file      = ROOT_DIR / "FRED/PCU325311325311.csv"
wheat_file     = ROOT_DIR / "FRED/WPU0121.csv"
pop_file       = ROOT_DIR / "StatCan/Population/17100005.csv"
US_CAD_file    = ROOT_DIR / "FRED/DEXCAUS.csv"

# === GEOGRAPHY STANDARDIZATION ===
included_geo = {
    "Alberta","British Columbia","Manitoba","New Brunswick",
    "Newfoundland And Labrador","Nova Scotia","Ontario","Quebec","Saskatchewan"
}

def normalize_province(prov):
    prov = str(prov).strip().title()
    aliases = {
        "Nfld.": "Newfoundland And Labrador",
        "Nwt": "Northwest Territories",
        "B.C.": "British Columbia",
        "P.E.I.": "Prince Edward Island",
    }
    return aliases.get(prov, prov)


def apply_geo_filter(df):
    geo_col = next((c for c in df.columns if c.lower() in ["geo", "geography", "province"]), None)
    if geo_col is None:
        raise ValueError("No GEO or Province column found")
    out = df.copy()
    out["Province"] = out[geo_col].apply(normalize_province)
    return out[out["Province"].isin(included_geo)].copy()

# === Helpers ===
SCALE_MAP = {"units":1, "thousands":1_000, "millions":1_000_000}

def add_dollar_value(df):
    out = df.copy()
    if "SCALAR_FACTOR" in out.columns:
        mult = out["SCALAR_FACTOR"].astype(str).str.lower().map(SCALE_MAP).fillna(1)
    else:
        mult = 1
    out["VALUE_DOLLARS"] = pd.to_numeric(out["VALUE"], errors="coerce") * mult
    return out

# === CPI ===
print("📥 Loading CPI...")
cpi = pd.read_csv(cpi_file, low_memory=False)
cpi["Year"] = cpi["REF_DATE"].astype(str).str.slice(0, 4).astype(int)
cpi["Province"] = cpi["GEO"].apply(normalize_province)
cpi = cpi[cpi["Products and product groups"].str.lower() == "all-items"]

cpi_prov = (
    cpi[(cpi["Province"].isin(included_geo)) & (cpi["Year"] >= 1978)]
    .groupby(["Year", "Province"], as_index=False)["VALUE"].mean()
)
cpi_canada_avg = (
    cpi[(cpi["GEO"] == "Canada") & (cpi["Year"].between(1975, 1977))]
    .groupby("Year", as_index=False)["VALUE"].mean()
)
cpi_1975 = cpi_canada_avg[cpi_canada_avg["Year"] == 1975].copy()
cpi_1974 = cpi_1975.copy(); cpi_1974["Year"] = 1974
cpi_canada_avg = pd.concat([cpi_1974, cpi_canada_avg], ignore_index=True)
cpi_backfilled = pd.concat([cpi_canada_avg.assign(Province=prov) for prov in included_geo])
cpi_final = pd.concat([cpi_prov, cpi_backfilled], ignore_index=True).rename(columns={"VALUE":"CPI_index"})
print("✅ CPI Final shape:", cpi_final.shape)

# === BANK RATE ===
print("📥 Loading Bank Rate...")
br = pd.read_csv(bank_rate_file)
br["Year"] = br["REF_DATE"].astype(str).str.slice(0, 4).astype(int)
br = br.groupby("Year", as_index=False)["VALUE"].mean().rename(columns={"VALUE":"Bank_Rate"})

# === USD Commodity series ===
print("📥 Loading WTI...")
wti = pd.read_csv(wti_file).rename(columns={"observation_date":"DATE","WTISPLC":"WTI_Crude_USD"})
wti["Year"] = wti["DATE"].astype(str).str[:4].astype(int)
wti = wti.groupby("Year", as_index=False)["WTI_Crude_USD"].mean()

print("📥 Loading Coal...")
coal = pd.read_csv(coal_file).rename(columns={"observation_date":"DATE","WPU051":"Coal_USD"})
coal["Year"] = coal["DATE"].astype(str).str[:4].astype(int)
coal = coal.groupby("Year", as_index=False)["Coal_USD"].mean()

print("📥 Loading Chemicals...")
chem = pd.read_csv(chem_file).rename(columns={"observation_date":"DATE","PCU325311325311":"Chemical_USD"})
chem["Year"] = chem["DATE"].astype(str).str[:4].astype(int)
chem = chem.groupby("Year", as_index=False)["Chemical_USD"].mean()

print("📥 Loading Wheat...")
wheat = pd.read_csv(wheat_file).rename(columns={"observation_date":"DATE","WPU0121":"Wheat_USD"})
wheat["Year"] = wheat["DATE"].astype(str).str[:4].astype(int)
wheat = wheat.groupby("Year", as_index=False)["Wheat_USD"].mean()

# === GDP by industry (sector) ===
print("📥 Loading GDP...")

gdp80 = add_dollar_value(apply_geo_filter(pd.read_csv(minegdp80_file)))
gdp90 = add_dollar_value(apply_geo_filter(pd.read_csv(minegdp90_file)))

gdp80["Year"] = pd.to_numeric(gdp80["REF_DATE"], errors="coerce").astype("Int64")
gdp90["Year"] = pd.to_numeric(gdp90["REF_DATE"], errors="coerce").astype("Int64")

SECTORS = {
    "OIL_GAS": "Mining, quarrying and oil well industries",
    "REFINING": "Refined petroleum and coal products industries",
    "AGRIC": "Agricultural and related services industries",
    "FISH": "Fishing and trapping industries",
    "MANUFACT": "Manufacturing industries",
    "EDU": "Educational service industries"
}

def extract_nominal_block(df, industry, y0, y1):
    return (
        df[(df["Prices"] == "Current dollars (1971 to 1984)") &
           (df["Industry"] == industry) &
           (df["Year"].between(y0, y1))]
        [["Year","Province","VALUE_DOLLARS"]]
        .rename(columns={"VALUE_DOLLARS":"GDP_Nominal"})
    )


def extract_real_block(df, industry, y0, y1):
    return (
        df[(df["Prices"] == "1986 constant dollars") &
           (df["Industry"] == industry) &
           (df["Year"].between(y0, y1))]
        [["Year","Province","VALUE_DOLLARS"]]
        .rename(columns={"VALUE_DOLLARS":"GDP_Real"})
    )


def build_sector(gdp80, gdp90, cpi, sector_key, label):
    ind = SECTORS[sector_key]
    pre  = extract_nominal_block(gdp80, ind, 1975, 1983).merge(cpi, on=["Year","Province"], how="left")
    pre["GDP_Real"] = pre["GDP_Nominal"] / (pre["CPI_index"]/100.0)
    pre  = pre[["Year","Province","GDP_Real"]]
    post = extract_real_block(gdp90, ind, 1984, 1995)
    out  = pd.concat([pre, post], ignore_index=True)
    out["Sector"] = label
    return out


gdp_sectors = pd.concat([
    build_sector(gdp80, gdp90, cpi_final, "OIL_GAS", "OIL_GAS"),
    build_sector(gdp80, gdp90, cpi_final, "REFINING", "REFINING"),
    build_sector(gdp80, gdp90, cpi_final, "AGRIC", "AGRIC"),
    build_sector(gdp80, gdp90, cpi_final, "FISH", "FISH"),
    build_sector(gdp80, gdp90, cpi_final, "MANUFACT", "MANUFACT"),
    build_sector(gdp80, gdp90, cpi_final, "EDU", "EDU")
], ignore_index=True)

# === GDP total (province) ===

totgdp80 = add_dollar_value(apply_geo_filter(pd.read_csv(totgdp80_file)))
totgdp90 = add_dollar_value(apply_geo_filter(pd.read_csv(totgdp90_file)))

totgdp80["Year"] = pd.to_numeric(totgdp80["REF_DATE"], errors="coerce").astype("Int64")
totgdp90["Year"] = pd.to_numeric(totgdp90["REF_DATE"], errors="coerce").astype("Int64")


def _find_col(df, needles):
    """Return first column whose name contains any needle (case-insensitive)."""
    low = {c.lower(): c for c in df.columns}
    for n in needles:
        for k in low:
            if n in k:
                return low[k]
    return None


def _gdp_market_prices_mask(df, concept_col):
    return df[concept_col].astype(str).str.contains(r"gross domestic product.*market prices",
                                                    case=False, regex=True, na=False)


def build_total_gdp_75_80(df80, cpi):
    """36100324, 1975–1980. No Prices column → assume current dollars; deflate with provincial CPI."""
    concept_col = _find_col(df80, ["income-based estimates", "estimates"])
    if concept_col is None:
        raise ValueError("Could not find concept column on 36100324 (look for 'Income-based estimates' or 'Estimates').")

    # Slice first, then apply the concept mask **on the slice**
    sl = df80[df80["Year"].between(1975, 1980)].copy()
    sl = sl.loc[_gdp_market_prices_mask(sl, concept_col)]

    base = (sl[["Year","Province","VALUE_DOLLARS"]]
              .rename(columns={"VALUE_DOLLARS": "GDP_Nominal_Total"}))

    out = base.merge(cpi[["Year","Province","CPI_index"]], on=["Year","Province"], how="left")
    out["GDP_Real_Total"] = out["GDP_Nominal_Total"] / (out["CPI_index"]/100.0)
    return out[["Year","Province","GDP_Real_Total"]]

def build_total_gdp_81_95(df90, cpi):
    """36100221, 1981–1995. Prefer constant/chained dollars if available; otherwise deflate nominal."""
    concept_col = _find_col(df90, ["income-based estimates", "estimates"])
    if concept_col is None:
        raise ValueError("Could not find concept column on 36100221 (look for 'Estimates').")

    price_col = _find_col(df90, ["prices"])
    sl = df90[df90["Year"].between(1981, 1995)]
    sl = sl.loc[_gdp_market_prices_mask(sl, concept_col)]

    if price_col is not None:
        is_real    = sl[price_col].astype(str).str.contains("constant|chained", case=False, na=False)
        is_current = sl[price_col].astype(str).str.contains("current", case=False, na=False)

        part_real = (sl.loc[is_real, ["Year","Province","VALUE_DOLLARS"]]
                       .rename(columns={"VALUE_DOLLARS":"GDP_Real_Total"}))

        part_curr = (sl.loc[is_current, ["Year","Province","VALUE_DOLLARS"]]
                       .rename(columns={"VALUE_DOLLARS":"GDP_Nominal_Total"})
                       .merge(cpi[["Year","Province","CPI_index"]], on=["Year","Province"], how="left"))
        if not part_curr.empty:
            part_curr["GDP_Real_Total"] = part_curr["GDP_Nominal_Total"] / (part_curr["CPI_index"]/100.0)
            part_curr = part_curr[["Year","Province","GDP_Real_Total"]]

        out = pd.concat([part_real, part_curr], ignore_index=True)
    else:
        part_curr = (sl[["Year","Province","VALUE_DOLLARS"]]
                        .rename(columns={"VALUE_DOLLARS":"GDP_Nominal_Total"})
                        .merge(cpi[["Year","Province","CPI_index"]], on=["Year","Province"], how="left"))
        part_curr["GDP_Real_Total"] = part_curr["GDP_Nominal_Total"] / (part_curr["CPI_index"]/100.0)
        out = part_curr[["Year","Province","GDP_Real_Total"]]

    # Prefer real if duplicates exist
    out = (out.sort_values(["Year","Province"])\
             .drop_duplicates(["Year","Province"], keep="first")\
             .reset_index(drop=True))
    return out


gdp_tot_75_80 = build_total_gdp_75_80(totgdp80, cpi_final)
gdp_tot_81_95 = build_total_gdp_81_95(totgdp90, cpi_final)

gdp_total = pd.concat([gdp_tot_75_80, gdp_tot_81_95], ignore_index=True)

# Quick completeness check for 9 provinces × 21 years = 189 rows
_expected = 9 * (1995 - 1975 + 1)
if len(gdp_total) != _expected:
    miss = (pd.MultiIndex.from_product([range(1975, 1996), sorted(included_geo)], names=["Year","Province"])\
            .difference(pd.MultiIndex.from_frame(gdp_total[["Year","Province"]])))
    if len(miss) > 0:
        print("⚠️ Missing GDP_Real_Total rows:", len(miss))
        print(pd.DataFrame(index=miss).reset_index().head(20))

# === COMPENSATION (monthly → annual, provincial, sector & total) ===
comp_raw = add_dollar_value(apply_geo_filter(pd.read_csv(wages_file, low_memory=False)))
comp_raw["Year"] = comp_raw["REF_DATE"].astype(str).str[:4].astype(int)

COMP_INDMAP = {
    "Labour income": "TOTAL",
    "Agriculture, fishing and trapping": "AG_FISH",
    "Mining, quarrying and oil wells": "OIL_GAS",
    "Refined petroleum and coal products industries": "REFINING",
    "Manufacturing": "MANUFACT",
    "Education and related services": "EDU",
}
# explicit .keys()
comp = comp_raw[comp_raw["Sector"].isin(COMP_INDMAP.keys())].copy()
comp["Sector"] = comp["Sector"].map(COMP_INDMAP)

# Use VALUE_DOLLARS directly, then deflate to real
comp_monthly = comp.rename(columns={"VALUE_DOLLARS":"Comp_Nominal"})

comp_annual = (
    comp_monthly
    .groupby(["Year","Province","Sector"], as_index=False)["Comp_Nominal"].sum()
)
comp_annual = comp_annual.merge(cpi_final[["Year","Province","CPI_index"]], on=["Year","Province"], how="left")
# 🔧 FIX: compute real compensation after CPI merge
comp_annual["Comp_Real"] = comp_annual["Comp_Nominal"] / (comp_annual["CPI_index"]/100.0)

# === Split to TOTAL vs SECTOR; harmonize sector names with GDP labels ===
# (A) Province-level total compensation (all sectors)
comp_total = (
    comp_annual
    .loc[comp_annual["Sector"]=="TOTAL", ["Year","Province","Comp_Real"]]
    .rename(columns={"Comp_Real":"Comp_Real_Total"})
)

# (B) Sectors that already match GDP labels one-to-one
comp_match = (
    comp_annual
    .loc[comp_annual["Sector"].isin(["OIL_GAS","REFINING","MANUFACT","EDU"]),
         ["Year","Province","Sector","Comp_Real"]]
    .rename(columns={"Comp_Real":"Comp_Real_Sector"})
)

# (C) Allocate AG_FISH → AGRIC & FISH using GDP weights
comp_agfish = (
    comp_annual
    .loc[comp_annual["Sector"]=="AG_FISH", ["Year","Province","Comp_Real"]]
    .rename(columns={"Comp_Real":"Comp_AF_Real"})
)

# Build weights from GDP by industry
w = (
    gdp_sectors[gdp_sectors["Sector"].isin(["AGRIC","FISH"])]
    .pivot_table(index=["Year","Province"], columns="Sector",
                 values="GDP_Real", aggfunc="first")
    .rename(columns=lambda c: str(c))
    .fillna(0.0)
)

# Ensure both columns exist
if "AGRIC" not in w.columns: w["AGRIC"] = 0.0
if "FISH"  not in w.columns: w["FISH"]  = 0.0

w["sum"]  = w["AGRIC"] + w["FISH"]
w["w_ag"] = np.where(w["sum"] > 0, w["AGRIC"]/w["sum"], np.nan)
w["w_fi"] = np.where(w["sum"] > 0, w["FISH"] /w["sum"], np.nan)

# ✅ FIX: correctly reset MultiIndex to columns (avoid KeyError)
w = w.reset_index()[["Year","Province","w_ag","w_fi"]]

# Join weights to AG_FISH comp, fallback to 50/50 when weights missing
alloc = comp_agfish.merge(w, on=["Year","Province"], how="left")
alloc["w_ag"] = alloc["w_ag"].fillna(0.5)
alloc["w_fi"] = alloc["w_fi"].fillna(0.5)

comp_ag = (
    alloc.assign(Sector="AGRIC",
                 Comp_Real_Sector=alloc["Comp_AF_Real"]*alloc["w_ag"])
         [["Year","Province","Sector","Comp_Real_Sector"]]
)
comp_fi = (
    alloc.assign(Sector="FISH",
                 Comp_Real_Sector=alloc["Comp_AF_Real"]*alloc["w_fi"])
         [["Year","Province","Sector","Comp_Real_Sector"]]
)

# Final sector compensation table used in joins
comp_sect = pd.concat([comp_match, comp_ag, comp_fi], ignore_index=True)

# Sanity: allocated AGRIC+FISH equals original AG_FISH
chk = (
    pd.concat([comp_ag, comp_fi], ignore_index=True)
      .groupby(["Year","Province"], as_index=False)["Comp_Real_Sector"].sum()
      .merge(comp_agfish.rename(columns={"Comp_AF_Real":"AG_FISH"}),
             on=["Year","Province"], how="outer")
)
chk["alloc_diff"] = chk["AG_FISH"] - chk["Comp_Real_Sector"]
print("Max allocation abs diff (should be near 0):",
      float(chk["alloc_diff"].abs().max()))

# === EMPLOYMENT ===
print("📥 Loading Employment (LFS monthly)...")
lfs = apply_geo_filter(pd.read_csv(lfs_file))
lfs["Year"] = lfs["REF_DATE"].astype(str).str[:4].astype(int)
lfs = lfs[
    (lfs["Labour force characteristics"].str.lower().str.strip() == "employment") &
    (lfs["Gender"].str.lower().str.strip() == "total - gender") &
    (lfs["Age group"].str.lower().str.contains("15 years"))
]
if lfs["SCALAR_FACTOR"].str.lower().iloc[0] == "thousands":
    lfs["Employment"] = lfs["VALUE"] * 1_000
else:
    lfs["Employment"] = lfs["VALUE"]

lfs_agg = lfs.groupby(["Year", "Province"], as_index=False)["Employment"].mean()
if 1976 in lfs_agg["Year"].values and 1975 not in lfs_agg["Year"].values:
    emp_1976 = lfs_agg[lfs_agg["Year"] == 1976].copy(); emp_1976["Year"] = 1975
    lfs_agg = pd.concat([lfs_agg, emp_1976], ignore_index=True)

# === POPULATION ===
pop = apply_geo_filter(pd.read_csv(pop_file, low_memory=False))
pop["Year"] = pop["REF_DATE"].astype(str).str[:4].astype(int)
pop = pop[(pop["Age group"] == "All ages") & (pop["Gender"] == "Total - gender")]
pop = pop[["Year","Province","VALUE"]].rename(columns={"VALUE":"Population"})
if 1976 in pop["Year"].values and 1975 not in pop["Year"].values:
    pop_1976 = pop[pop["Year"] == 1976].copy(); pop_1976["Year"] = 1975
    pop = pd.concat([pop, pop_1976], ignore_index=True)

# === US/CA EXCHANGE (CAD per USD, daily → annual) ===
fx_raw = (
    pd.read_csv(US_CAD_file, parse_dates=["observation_date"])\
      .rename(columns={"observation_date":"DATE","DEXCAUS":"USDCAD"})
)
fx_raw["USDCAD"] = pd.to_numeric(fx_raw["USDCAD"], errors="coerce")

us_cad = (fx_raw.assign(Year=fx_raw["DATE"].dt.year)
                 .groupby("Year", as_index=False)["USDCAD"].mean())
us_cad = us_cad.query("Year >= 1975 & Year <= 1995").sort_values("Year").reset_index(drop=True)
us_cad["log_USDCAD"]  = np.log(us_cad["USDCAD"]) 
us_cad["dlog_USDCAD"] = us_cad["log_USDCAD"].diff()

# === Harmonize Year dtypes (avoid merge misses) ===
for _df in [gdp_sectors, gdp_total, comp_total, comp_sect, lfs_agg, pop, br, wti, coal, chem, wheat, us_cad]:
    _df["Year"] = _df["Year"].astype(int)

for n, d in {"gdp_total": gdp_total, "comp_total": comp_total,
             "comp_sect": comp_sect, "lfs_agg": lfs_agg,
             "pop": pop}.items():
    print(n, d.shape, d[["Year","Province"]].drop_duplicates().shape)


# --- ENFORCE UNIQUENESS BEFORE REGISTERING WITH DUCKDB ---
# If any many-to-many keys slipped in, squash them deterministically.

# GDP by sector: sum if duplicates ever exist (shouldn’t change correct data)
gdp_sectors = (
    gdp_sectors
    .groupby(["Year", "Province", "Sector"], as_index=False, sort=False)["GDP_Real"]
    .sum()
)

# Compensation by sector: sum duplicates (AGRIC/FISH were allocated earlier so this is safe)
comp_sect = (
    comp_sect
    .groupby(["Year", "Province", "Sector"], as_index=False, sort=False)["Comp_Real_Sector"]
    .sum()
)

# Province totals: if any accidental dup Year–Province rows exist, aggregate (shouldn’t change)
gdp_total = gdp_total.groupby(["Year","Province"], as_index=False, sort=False)["GDP_Real_Total"].sum()
comp_total = comp_total.groupby(["Year","Province"], as_index=False, sort=False)["Comp_Real_Total"].sum()

# Final assertions to catch problems early
assert not gdp_sectors.duplicated(["Year","Province","Sector"]).any(), "Dup keys in gdp_sectors"
assert not comp_sect.duplicated(["Year","Province","Sector"]).any(), "Dup keys in comp_sect"
assert not gdp_total.duplicated(["Year","Province"]).any(), "Dup keys in gdp_total"
assert not comp_total.duplicated(["Year","Province"]).any(), "Dup keys in comp_total"

# === MERGE ALL (DuckDB) ===
print("🦆 Starting DuckDB join...")
con = duckdb.connect(database=":memory:")

for name, df in {
    "gdp_sectors": gdp_sectors,
    "gdp_total"  : gdp_total,
    "comp_total" : comp_total,
    "comp_sect"  : comp_sect,
    "employment" : lfs_agg,
    "population" : pop,
    "bank_rate"  : br,
    "wti"        : wti,
    "coal"       : coal,
    "chem"       : chem,
    "wheat"      : wheat,
    "us_cad"     : us_cad,
}.items():
    con.register(name, df)

query = """
SELECT
  s.Year, s.Province, s.Sector,
  s.GDP_Real                           AS GDP_Real_Sector,
  cs.Comp_Real_Sector,
  t.GDP_Real_Total,
  ct.Comp_Real_Total,
  e.Employment,
  p.Population,
  b.Bank_Rate,
  w.WTI_Crude_USD,
  co.Coal_USD,
  ch.Chemical_USD,
  wh.Wheat_USD,
  u.USDCAD
FROM gdp_sectors AS s
LEFT JOIN comp_sect  AS cs ON cs.Year = s.Year AND cs.Province = s.Province AND cs.Sector = s.Sector
LEFT JOIN gdp_total  AS t  ON t.Year  = s.Year AND t.Province  = s.Province
LEFT JOIN comp_total AS ct ON ct.Year = s.Year AND ct.Province = s.Province
LEFT JOIN employment AS e  ON e.Year  = s.Year AND e.Province  = s.Province
LEFT JOIN population AS p  ON p.Year  = s.Year AND p.Province  = s.Province
LEFT JOIN bank_rate  AS b  ON b.Year  = s.Year
LEFT JOIN wti        AS w  ON w.Year  = s.Year
LEFT JOIN coal       AS co ON co.Year = s.Year
LEFT JOIN chem       AS ch ON ch.Year = s.Year
LEFT JOIN wheat      AS wh ON wh.Year = s.Year
LEFT JOIN us_cad     AS u  ON u.Year  = s.Year
"""
panel_df = con.execute(query).df()

# Bring FX logs
panel_df = panel_df.merge(us_cad[["Year","log_USDCAD","dlog_USDCAD"]], on="Year", how="left")

# Convert USD commodity series to CAD
panel_df["WTI_CAD"]   = panel_df["WTI_Crude_USD"] * panel_df["USDCAD"]
panel_df["Coal_CAD"]  = panel_df["Coal_USD"]      * panel_df["USDCAD"]
panel_df["Chem_CAD"]  = panel_df["Chemical_USD"]  * panel_df["USDCAD"]
panel_df["Wheat_CAD"] = panel_df["Wheat_USD"]     * panel_df["USDCAD"]

# ===== Lock domain =====
panel_df = panel_df[
    panel_df["Year"].between(1975, 1995) & panel_df["Province"].isin(included_geo)
].copy()

# === Province-level outcomes (repeat across sector rows; okay) ===
panel_df["GDP_pc_real_1986"]  = panel_df["GDP_Real_Total"] / panel_df["Population"]
panel_df["Wpw_All"]           = panel_df["Comp_Real_Total"] / panel_df["Employment"].replace({0: np.nan})
panel_df["LabourShare_Total"] = panel_df["Comp_Real_Total"] / panel_df["GDP_Real_Total"].replace({0: np.nan})

# === Sector-level mechanisms ===
panel_df["Sector_LabourIntensity"] = (
    panel_df["Comp_Real_Sector"] / panel_df["GDP_Real_Sector"].replace({0: np.nan})
)
panel_df["MANUF_LabourIntensity"] = np.where(
    panel_df["Sector"] == "MANUFACT", panel_df["Sector_LabourIntensity"], np.nan
)

# Province-level anchor built from totals (avoids holes)
prov_df = (
    gdp_total
      .merge(comp_total, on=["Year","Province"], how="left")
      .merge(lfs_agg,    on=["Year","Province"], how="left")
      .merge(pop[["Year","Province","Population"]], on=["Year","Province"], how="left")
      .merge(br,    on="Year", how="left")
      .merge(wti,   on="Year", how="left")
      .merge(coal,  on="Year", how="left")
      .merge(chem,  on="Year", how="left")
      .merge(wheat, on="Year", how="left")
      .merge(us_cad[["Year","USDCAD","log_USDCAD","dlog_USDCAD"]], on="Year", how="left")
)

prov_df = prov_df[
    prov_df["Year"].between(1975, 1995) & prov_df["Province"].isin(included_geo)
].copy()

# outcomes
prov_df["GDP_pc_real_1986"] = prov_df["GDP_Real_Total"] / prov_df["Population"]
prov_df["Wpw_All"]          = prov_df["Comp_Real_Total"] / prov_df["Employment"].replace({0: np.nan})
prov_df["LabourShare_Total"] = prov_df["Comp_Real_Total"] / prov_df["GDP_Real_Total"].replace({0: np.nan})

# logs (safe)
def safe_log(s):
    return np.log(s.replace({0: np.nan}))
for col in ["GDP_pc_real_1986","Wpw_All","LabourShare_Total"]:
    prov_df[f"log_{col}"] = safe_log(prov_df[col])

# ===== Event-study scaffolding =====
TREAT_AB        = {"Alberta"}
TREAT_PRAIRIES  = {"Alberta","Saskatchewan","Manitoba"}
TREAT_MANU_CORE = {"Ontario","Quebec"}
TREAT_NFLD      = {"Newfoundland And Labrador"}

EVENTS = [
    ("NEP",    1980, TREAT_AB,        6),
    ("CROW",   1984, TREAT_PRAIRIES,  6),
    ("CUSFTA", 1989, TREAT_MANU_CORE, 6),
    ("COD",    1992, TREAT_NFLD,      4),
]

def add_event_vars(df, name, year, treated, window=6):
    df[f"{name}_treated"] = df["Province"].isin(treated).astype(int)
    df[f"{name}_post"]    = ((df["Year"] >= year) & df[f"{name}_treated"].eq(1)).astype(int)
    df[f"{name}_rel"]     = np.where(df[f"{name}_treated"].eq(1), df["Year"] - year, np.nan)
    for k in range(-window, window+1):
        if k == -1:  # omit -1 as baseline
            continue
        col = f"{name}_bin_{'m' if k<0 else 'p'}{abs(k)}"
        df[col] = (df[f"{name}_rel"] == k).astype(int)
    return df

for (ename, eyear, etreat, ewin) in EVENTS:
    prov_df = add_event_vars(prov_df, ename, eyear, etreat, window=ewin)

panel_df_sector = panel_df.copy()
for (ename, eyear, etreat, ewin) in EVENTS:
    panel_df_sector = add_event_vars(panel_df_sector, ename, eyear, etreat, window=ewin)

# ===== Save event-study ready files =====
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
prov_df.to_csv(OUTPUT_DIR / "nep_panel_province_1975_1995.csv", index=False)
panel_df_sector.to_csv(OUTPUT_DIR / "nep_panel_sector_1975_1995.csv", index=False)
print("✅ Saved province-level and sector-level panels with event-study scaffolding.")

# === Tables & Figures ===
TABLE_DIR = OUTPUT_DIR / "tables"; TABLE_DIR.mkdir(exist_ok=True)

# Table 1 — Summary Statistics (province-level)
mining = (panel_df.loc[panel_df["Sector"]=="OIL_GAS", ["Year","Province","GDP_Real_Sector"]]
          .drop_duplicates(["Year","Province"]).rename(columns={"GDP_Real_Sector":"GDP_Real_Mining"}))
prov_level = (panel_df[["Year","Province","Population","Employment","GDP_Real_Total","GDP_pc_real_1986","Wpw_All"]]
              .drop_duplicates(["Year","Province"]).merge(mining, on=["Year","Province"], how="left"))
prov_level["GDP_per_worker_real_1986"] = prov_level["GDP_Real_Total"] / prov_level["Employment"].replace({0: np.nan})

summary_vars = [
    "Year","GDP_Real_Mining","Wpw_All","Population","Employment","GDP_pc_real_1986","GDP_per_worker_real_1986"
]
summary_df = prov_level[summary_vars].describe().T[["count","mean","std","min","25%","50%","75%","max"]].round(2)
summary_df.columns = ["N","Mean","Std. Dev.","Min","P25","Median","P75","Max"]
summary_df.to_latex(TABLE_DIR / "table1_summary_stats.tex")
print("📄 Saved Table 1: Summary Statistics")

# Table 2 — Model Descriptions
model_desc = pd.DataFrame({
    "Outcome": [
        r"$\\log(\\text{GDP per capita})$",
        r"$\\log(\\text{Compensation per worker})$",
        r"$\\log(\\text{Sector labour intensity})$"
    ],
    "Definition": [
        "Log of real provincial GDP per person (1986 CAD).",
        "Log of real total compensation divided by total employment (1986 CAD).",
        "Log of sector compensation divided by sector GDP (proxy for returns to labour)."
    ],
    "Source": [
        "StatCan GDP, CPI, Population",
        "StatCan Compensation (36-10-0298), LFS Employment, CPI",
        "StatCan Compensation & GDP by industry, CPI"
    ]
})
model_desc.to_latex(TABLE_DIR / "table2_model_descriptions.tex", index=False, escape=False)
print("📄 Saved Table 2 (LaTeX math mode): Model Descriptions")

# === Simple figs (integer year ticks, event lines, currency y-axis) ===
def make_timeseries_plot(df, var, ylabel, fname, main_year=1981, ref_year=1980, ylims=None):
    fig, ax = plt.subplots(figsize=(12, 7))

    # plot three provinces
    for prov, style in zip(["Alberta", "Ontario", "Quebec"], ["-", "--", ":"]):
        s = df.loc[df["Province"] == prov]
        ax.plot(s["Year"].astype(int), s[var], linestyle=style, marker="o", markersize=3, label=prov)

    # reference & event lines
    ax.axvline(ref_year,  color="gray", linestyle=":",  linewidth=1)
    ax.axvline(main_year, color="red",  linestyle="--", linewidth=2, alpha=0.9)
    ax.axvspan(main_year, 1995, color="red", alpha=0.06, linewidth=0)  # subtle post-event shading

    # force integer year ticks (no .5 years)
    ax.set_xlim(1975, 1995)
    ax.set_xticks(range(1975, 1996))               # explicit integer ticks
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # currency formatting on y-axis
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))

    # optional shared y-lims for consistency across figures
    if ylims is not None:
        ax.set_ylim(*ylims)

    ax.set_title(f"{ylabel}, 1975–1995: Alberta, Ontario, Quebec")
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)

    fig.tight_layout()
    # leave space for the footer caption and then add it
    fig.subplots_adjust(bottom=0.12)
    fig.text(0.5, 0.01,
         "Sources: StatCan 36-10-0222-01, 17-10-0005-01, 18-10-0005-01.",
         ha="center", fontsize=9)
    fig.savefig(OUTPUT_DIR / f"{fname}.png", dpi=300)
    plt.close(fig)

fig_data = prov_df[prov_df["Province"].isin(["Alberta","Ontario","Quebec"])].copy()

# If you want consistent y-lims across plots, pass ylims=(min,max); otherwise omit.
make_timeseries_plot(fig_data, "Wpw_All",          "Compensation per Worker (1986 CAD)", "fig_wpw_all")
make_timeseries_plot(fig_data, "GDP_pc_real_1986", "GDP per Capita (1986 CAD)",          "fig_gdp_pc")

    
# Table 1b — per-province mean/std (corrected long layout)
latex_varnames = {
    "Employment":            r"$\text{Employment}$",
    "Population":            r"$\text{Population}$",
    "log_GDP_pc_real_1986":  r"$\log(\text{GDP per capita, 1986 CAD})$",
    "log_Wpw_All":           r"$\log(\text{Compensation per worker, 1986 CAD})$",
    "LabourShare_Total":     r"$\text{Labour share of GDP}$",
}
summary_vars2 = ["Employment","Population","log_GDP_pc_real_1986","log_Wpw_All","LabourShare_Total"]

# Build clean long table: Province × Variable with columns [Mean, Std. Dev.]
tmp = (
    prov_df
    .groupby("Province")[summary_vars2]
    .agg(["mean","std"])                # MultiIndex columns: (Variable, stat)
    .stack(level=0)                     # rows: (Province, Variable); cols: mean,std
    .reset_index()
)
tmp.columns = ["Province","Variable","Mean","Std. Dev."]

# Pretty variable labels and ordering
tmp["Variable"] = tmp["Variable"].map(latex_varnames)
tmp = tmp.sort_values(["Variable","Province"]).reset_index(drop=True)

# Reorder to match your intended header
table1b_long = tmp[["Variable","Province","Mean","Std. Dev."]]

TABLE_DIR.mkdir(exist_ok=True, parents=True)
table1b_long.to_latex(TABLE_DIR / "table1b_summary_by_province_long.tex",
                      index=False, escape=False, float_format="%.6f")
print("📄 Rewrote Table 1b (long format): Summary by Province")

# === Diagnostics ===
print("LabourShare_Total quantiles:", prov_df["LabourShare_Total"].quantile([0.01,0.5,0.99]))
check = panel_df.groupby(["Year","Province"]).agg(
    GDP_sector_sum=("GDP_Real_Sector","sum"),
    GDP_total=("GDP_Real_Total","first"),
    Comp_sector_sum=("Comp_Real_Sector","sum"),
    Comp_total=("Comp_Real_Total","first"),
).reset_index()
print("GDP sector sum / total (median):", float((check["GDP_sector_sum"]/check["GDP_total"]).median()))
print("Comp sector sum / total (median):", float((check["Comp_sector_sum"]/check["Comp_total"]).median()))

# Missingness debug before asserts
_tmpl = (pd.MultiIndex
        .from_product([range(1975, 1996), sorted(included_geo)], names=["Year","Province"]) \
        .to_frame(index=False))
_miss = (_tmpl.merge(prov_df[["Year","Province","GDP_Real_Total","Population"]],
                     on=["Year","Province"], how="left")
             .query("GDP_Real_Total.isna() or Population.isna()")
             .sort_values(["Province","Year"]))
print("Missing GDP_Real_Total or Population rows:", len(_miss))
if len(_miss):
    print(_miss.head(20))

# Asserts on province-level outcomes
assert prov_df["GDP_pc_real_1986"].notna().all()
assert prov_df["Wpw_All"].gt(0).all()

# Quick shapes
print(prov_df.shape)
print(prov_df[["Year","Province"]].drop_duplicates().shape)
print(prov_df[["GDP_pc_real_1986","Wpw_All"]].isna().sum())
print(panel_df_sector.shape)
print(panel_df_sector[["Year","Province","Sector"]].drop_duplicates().shape)

for name, df, keys in [
    ("gdp_total", gdp_total, ["Year","Province"]),
    ("comp_total", comp_total, ["Year","Province"]),
    ("lfs_agg", lfs_agg, ["Year","Province"]),
    ("pop", pop, ["Year","Province"]),
]:
    sub = df[(df["Year"].between(1975,1995)) & (df["Province"].isin(included_geo))]
    print(name, sub.shape[0], sub[keys].drop_duplicates().shape[0])

_evt_cols = [c for c in prov_df.columns if c.startswith(("NEP_","CROW_","CUSFTA_","COD_"))]
print(sorted(_evt_cols)[:10], '…', len(_evt_cols))

print(prov_df["LabourShare_Total"].describe(percentiles=[.01,.5,.99]))
