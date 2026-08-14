# Actuarial Pricing & Portfolio Analytics Platform

End-to-end General Insurance actuarial analytics application built with Python and Streamlit.

## Features

- **Data Upload** — CSV, XLSX, and sample dataset loading
- **Validation Engine** — Data quality scoring with issue tables
- **Cleaning Engine** — Deduplication, imputation, outlier flagging
- **Exploratory Analytics** — Interactive Plotly dashboards
- **Frequency Modeling** — Poisson & Negative Binomial GLMs
- **Severity Modeling** — Gamma & Lognormal distribution fits
- **Pure Premium Engine** — Technical premium estimation
- **Portfolio Analytics** — KPI cards and segment profitability
- **Executive Reporting** — PDF and Excel export

## Quick Start

```bash
pip install -r requirements.txt
python -m src.data.generator
streamlit run app.py
```

## Workflow

1. Load sample data or upload your portfolio CSV/XLSX
2. Run validation and cleaning
3. Explore data through EDA dashboards
4. Fit frequency and severity models
5. Calculate pure premium
6. Review portfolio analytics
7. Export executive report

## Tech Stack

Python, Streamlit, Pandas, NumPy, Plotly, SciPy, Statsmodels, Scikit-Learn

## Tests

```bash
pytest tests/ -v
```
