# cesg2025-nep-analysis

Causal inference analysis of Alberta’s economic divergence during the National Energy Program (1975–1990)

## 📘 Dominion and Divergence: Creighton, Econometrics, and the National Energy Program

This repository accompanies the paper submitted to the **Canadian Econometrics Study Group (CESG) 2025**. It applies causal inference methods to evaluate the economic impact of the 1980 National Energy Program (NEP) on Alberta relative to other Canadian provinces.

---

## 🔍 Abstract

This project reinterprets the NEP as a reactive federal intervention, rather than the origin of Alberta’s economic divergence. Using a custom panel dataset (1975–1990) built from publicly available Statistics Canada and FRED data, we apply:

- Difference-in-Differences (DiD)
- Event Study Analysis
- Synthetic Control Method (SCM with ridge regularization)

The analysis finds that Alberta’s GDP per worker and real wages were outperforming those of other provinces prior to the NEP, with divergence intensifying post-implementation. The findings suggest that the NEP constrained oil-linked growth, deepening federal-provincial tensions.

---

## 📂 Project Structure

- `CESG_2025_Paper_Submission.pdf` — Full submitted paper
- `figures/` — Visualizations used in the paper
- `scripts/` — (To be released post-review)
- `data_sources.md` — Table of data sources and download links

---

## 📊 Data Access

All data used in this analysis is publicly available from Statistics Canada and the U.S. Federal Reserve (FRED). To ensure long-term access and lightweight distribution, **this repository does not host raw data files directly**.

To replicate the analysis, download the required datasets listed in [`data_sources.md`](./data_sources.md), and place them in a local `data/raw/` directory.

---

## 🧪 Code Availability

The replication code will be shared after CESG review. It includes full preprocessing, panel construction, and model execution using Python (3.10+).

---

## ⚙️ Environment

This project uses:

- `pandas`, `numpy`, `matplotlib`
- `linearmodels` for DiD estimation
- `scikit-learn` and custom code for Synthetic Control

A `requirements.txt` file will be added with the public release of the code.

---

## 📄 License

This project is licensed under the MIT License.

---

## 📬 Citation

> Greg Williams. *Dominion and Divergence: Creighton, Econometrics, and the National Energy Program.* CESG 2025 Paper Submission.
