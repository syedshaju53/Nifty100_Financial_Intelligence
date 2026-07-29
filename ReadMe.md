# 📈 Nifty100 Financial Intelligence Platform

An end-to-end Financial Intelligence Platform built using Python, SQL, SQLite, Machine Learning, Financial Analytics, NLP, and Interactive Dashboards for the Nifty 100 companies.

---

# Project Overview

The objective of this project is to build a complete financial analytics platform capable of

- Collecting financial statements
- Cleaning and validating data
- Building an analytical database
- Calculating financial KPIs
- Performing peer comparison
- Sector-wise analytics
- Company quality scoring
- Cash Flow Intelligence
- NLP-based financial text parsing
- Automated Pros & Cons generation
- Capital Allocation Analysis
- PDF Tearsheet generation
- Interactive Dashboard

The project processes financial data of approximately 90 Nifty 100 companies and generates professional analytical reports.

---

# Technology Stack

### Programming

- Python 3.13

### Database

- SQLite

### Libraries

- Pandas
- NumPy
- Matplotlib
- Plotly
- OpenPyXL
- ReportLab
- Streamlit

### IDE

- VS Code

---

# Project Structure

```
Nifty100_Financial_Intelligence/

│
├── config/
├── data/
│   ├── raw/
│   └── processed/
│
├── db/
│   ├── schema.sql
│   └── nifty100.db
│
├── notebooks/
│
├── src/
│   ├── analytics/
│   ├── dashboard/
│   ├── etl/
│   ├── nlp/
│   ├── reports/
│   └── screener/
│
├── reports/
│   ├── sector/
│   ├── tearsheets/
│   └── portfolio/
│
├── output/
│
├── tests/
│
├── README.md
└── requirements.txt
```

---

# Project Modules

## Sprint 1

✔ Environment Setup

✔ ETL Pipeline

✔ Data Cleaning

✔ Data Validation

✔ SQLite Database

✔ Data Loading

---

## Sprint 2

✔ Financial Ratio Engine

✔ Profitability Analysis

✔ Liquidity Analysis

✔ Leverage Analysis

✔ Efficiency Analysis

✔ Health Score

✔ Peer Comparison

---

## Sprint 3

✔ Ranking Engine

✔ Stock Screener

✔ Radar Charts

✔ Company Valuation

✔ Dashboard Development

---

## Sprint 4

✔ NLP Financial Parser

✔ CAGR Validation

✔ Financial Master Dataset

✔ Automated Pros & Cons Generator

---

## Sprint 5

✔ Cash Flow Intelligence

✔ Capital Allocation Analysis

✔ Distress Detection

✔ Sector Reports

✔ Company Tearsheet Generator

✔ Portfolio Summary Report

---

# Database Tables

- Companies
- Profit & Loss
- Balance Sheet
- Cash Flow
- Ratios
- Stock Prices
- Market Cap
- Analysis
- Documents
- Peer Groups
- Pros & Cons
- Sectors

---

# Features

- Automated ETL Pipeline
- Financial KPI Engine
- Company Ranking
- Financial Health Score
- Peer Comparison
- Interactive Dashboard
- NLP Financial Parsing
- Automated Investment Insights
- Cash Flow Intelligence
- Capital Allocation Analysis
- Sector-wise Analytics
- PDF Report Generation

---

# Outputs Generated

## CSV

- analysis_parsed.csv
- cagr_validation.csv
- capital_allocation.csv
- distress_alerts.csv
- pros_cons_generated.csv
- parse_failures.csv
- peer_percentiles.csv
- master_financials.csv

---

## Excel

- screener_output.xlsx
- quality_scores.xlsx
- peer_comparison.xlsx
- cashflow_intelligence.xlsx

---

## PDF

### Company Reports

- 90 Company Tearsheets

### Sector Reports

- Communication Services
- Consumer Discretionary
- Consumer Staples
- Energy
- Financials
- Healthcare
- Industrials
- Information Technology
- Materials
- Real Estate

### Portfolio

- portfolio_summary.pdf

---

# Dashboard

The Streamlit dashboard includes

- Company Search
- Financial KPIs
- Radar Charts
- Peer Comparison
- Sector Analysis
- Cash Flow Intelligence
- Company Rankings
- Investment Insights

Run the dashboard

```bash
streamlit run src/dashboard/app.py
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Nifty100_Financial_Intelligence.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run ETL

```bash
python src/etl/loader.py
```

Run Dashboard

```bash
streamlit run src/dashboard/app.py
```

---

# Key Achievements

- Processed 90+ Nifty companies
- Integrated 1000+ financial records
- Automated ETL workflow
- Financial KPI Engine
- Cash Flow Intelligence
- NLP-based Financial Parser
- Automated PDF Report Generator
- Interactive Dashboard
- Sector Analytics
- Portfolio Analytics

---

# Future Improvements

- Live NSE/BSE API Integration
- AI Investment Recommendation Engine
- Forecasting Models
- Portfolio Optimisation
- LLM-based Financial Chat Assistant
- Real-time Alerts

---

# Author

**Syed Shajahan**

B.Tech – Data Science

---

# License

This project is developed for educational and research purposes.