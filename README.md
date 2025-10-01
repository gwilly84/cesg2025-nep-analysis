# 🛢 Dominion and Divergence  
### *Creighton, Econometrics, and the National Energy Program*  
**Author**: Greg Williams  
📄 CESG 2025 Submission

---

## 📚 Overview

This paper examines the economic impact of the 1980 National Energy Program (NEP) using provincial-level data from 1975 to 1990. Framed through Donald Creighton’s *Laurentian thesis*, the analysis evaluates whether the NEP was the cause of Alberta’s divergence or a reaction to regional economic realities already in motion.

Using a custom-built panel and modern causal inference tools—including **Difference-in-Differences** and a **Ridge-regularized Synthetic Control Method**—this project contributes to both historical and empirical understandings of Canadian federalism and regional economic policy.

---

## 📁 Repository Contents

| File/Folder | Description |
|-------------|-------------|
| [`paper_dominion_divergence.pdf`](paper_dominion_divergence.pdf) | Final paper submitted to CESG 2025 |
| `00_prepare_base_panel_v2.py` | Python script to build panel dataset from StatCan & FRED |
| `data_sources.md` | Full list of source tables and links (StatCan, FRED, BoC) |
| `outputs/` | Figures, summary tables, and processed datasets |
| `README.md` | You are here |
| `LICENSE` | MIT License for this repository |

---

## 🧠 How to Use This Code

This repository does **not include raw data** due to licensing. You must:

1. Download the raw data files listed in `data_sources.md`
2. Adjust the file paths in `00_prepare_base_panel_v2.py` (see `ROOT_DIR`)
3. Run the script to generate:
   - Cleaned CSV panel (1975–1995)
   - LaTeX summary tables
   - Time series and event-study figures

---

## 🔧 Requirements

This project uses Python 3.10+.  
Install dependencies via:

```bash
pip install pandas numpy duckdb matplotlib
