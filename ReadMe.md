# 📊 Nifty100 Financial Intelligence

## Overview

Nifty100 Financial Intelligence is an ETL (Extract, Transform, Load) and Financial Data Management project developed using Python and SQLite. The project processes financial datasets of Nifty 100 companies, performs data validation, and stores the cleaned data in a relational database for further analysis and visualization.

The project follows a structured ETL pipeline with automated validation, database loading, and data quality checks to ensure accurate and reliable financial data.

---

## Project Objectives

- Build a robust ETL pipeline for financial datasets.
- Validate and clean raw Excel files.
- Store cleaned data in a normalized SQLite database.
- Maintain data integrity using Primary Keys and Foreign Keys.
- Generate audit reports for data loading and validation.
- Prepare a reliable data source for financial analysis and dashboards.

---

# Project Structure

```
Nifty100_Financial_Intelligence/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── db/
│   ├── schema.sql
│   └── nifty100.db
│
├── outputs/
│   ├── load_audit.csv
│   └── validation_failures.csv
│
├── reports/
│
├── src/
│   └── etl/
│       ├── loader.py
│       ├── cleaner.py
│       ├── validator.py
│       └── db_loader.py
│
├── tests/
│   └── etl/
│       ├── test_loader.py
│       ├── test_validator.py
│       ├── test_db_loader.py
│       ├── test_data_quality.py
│       └── final_validation.py
│
├── requirements.txt
└── README.md
```

---

# Technologies Used

- Python 3
- Pandas
- NumPy
- SQLite
- OpenPyXL
- Git
- GitHub

---

# Database Tables

The SQLite database contains the following tables:

1. companies
2. profit_loss
3. balance_sheet
4. cash_flow
5. analysis
6. pros_and_cons
7. documents
8. stock_prices
9. ratios
10. market_cap
11. peer_groups
12. sectors

---

# ETL Workflow

### Step 1: Extract

- Read Excel files
- Validate file availability
- Load datasets using Pandas

### Step 2: Transform

- Remove duplicates
- Handle missing values
- Normalize column names
- Validate data quality
- Verify required columns

### Step 3: Load

- Create SQLite database
- Create database schema
- Load validated data
- Generate load audit report

---

# Data Quality Validation

The project performs multiple validation checks including:

- Missing Value Validation
- Duplicate Record Detection
- Required Column Validation
- Data Type Validation
- Foreign Key Validation
- NULL Value Check
- Company ID Validation

---

# Database Summary

| Table | Rows |
|--------|------|
| Companies | 92 |
| Profit Loss | 1177 |
| Balance Sheet | 1227 |
| Cash Flow | 1091 |
| Analysis | 16 |
| Pros & Cons | 14 |
| Documents | 1457 |
| Stock Prices | 5520 |
| Ratios | 1160 |
| Market Cap | 552 |
| Peer Groups | 56 |
| Sectors | 92 |

---

# Validation Results

- Duplicate Company IDs : PASS
- NULL Company IDs : PASS
- Foreign Key Validation : PASS
- Data Loading : PASS
- Record Count Verification : PASS

---

# Sprint 1 Progress

| Day | Status |
|------|--------|
| Day 1 | Completed |
| Day 2 | Completed |
| Day 3 | Completed |
| Day 4 | Completed |
| Day 5 | Completed |
| Day 6 | Completed |
| Day 7 | Completed |

---

# How to Run the Project

## Clone Repository

```bash
git clone https://github.com/syedshaju53/Nifty100_Financial_Intelligence.git
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Database Loader

```bash
python src/etl/db_loader.py
```

## Run Data Quality Validation

```bash
python tests/etl/test_data_quality.py
```

## Run Final Validation

```bash
python tests/etl/final_validation.py
```

---

# Project Deliverables

- ETL Pipeline
- Data Validation Module
- SQLite Database
- Database Loader
- Load Audit Report
- Data Quality Report
- Final Validation Script
- Sprint Reports
- Project Documentation

---

# Future Enhancements

- Power BI Dashboard Integration
- Tableau Dashboard
- Automated ETL Scheduling
- REST API using FastAPI
- Cloud Database Deployment
- Machine Learning for Financial Trend Analysis

---

# Author

**Syed Shaju**

B.Tech – Data Science

Nifty100 Financial Intelligence Project

---

# License

This project is developed for educational and academic purposes.