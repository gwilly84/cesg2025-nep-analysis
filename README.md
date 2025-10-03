# 🛢 Dominion and Divergence  
### *Creighton, Econometrics, and the National Energy Program*  
**Author**: Greg Williams  
📄 CESG 2025 Submission

---
## 📚 Overview

This project investigates the economic legacy of the 1980 **National Energy Program (NEP)** through the lens of Canadian political economy. Drawing on Donald Creighton’s *Laurentian thesis*, it explores whether the NEP marked a federal imposition that triggered Alberta’s economic divergence—or simply crystallized trends already underway.

Using a custom-constructed provincial panel (**1975–1995**) and state-of-the-art causal inference techniques—including **Difference-in-Differences**, **event study models**, and a **ridge-regularized Synthetic Control Method**—the analysis quantifies Alberta’s post-NEP trajectory across three outcomes:

- 📈 Real GDP per capita  
- 💼 Compensation per worker  
- ⚖️ Labour’s share of GDP (real ratio)  


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
