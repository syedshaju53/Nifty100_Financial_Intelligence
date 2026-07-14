import sqlite3
import pandas as pd
from pathlib import Path

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    capex_intensity,
    cfo_quality_score,
    fcf_conversion_rate,
)

from src.analytics.cagr import calculate_cagr

# --------------------------------------------------
# CONNECT DATABASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

# --------------------------------------------------
# LOAD TABLES
# --------------------------------------------------

profit_loss = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

balance_sheet = pd.read_sql(
    "SELECT * FROM balance_sheet",
    conn
)

cash_flow = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)

# --------------------------------------------------
# CHECK ORIGINAL RECORDS
# --------------------------------------------------

print("Profit Loss :", len(profit_loss))
print("Balance Sheet :", len(balance_sheet))
print("Cash Flow :", len(cash_flow))

print("\nDuplicate Profit Loss")
print(profit_loss.duplicated(["company_id", "year"]).sum())

print("\nDuplicate Balance Sheet")
print(balance_sheet.duplicated(["company_id", "year"]).sum())

print("\nDuplicate Cash Flow")
print(cash_flow.duplicated(["company_id", "year"]).sum())

# --------------------------------------------------
# REMOVE DUPLICATES
# --------------------------------------------------

profit_loss = profit_loss.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
)

balance_sheet = balance_sheet.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
)

cash_flow = cash_flow.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
)

print("\nAfter Removing Duplicates")

print("Profit Loss :", len(profit_loss))
print("Balance Sheet :", len(balance_sheet))
print("Cash Flow :", len(cash_flow))

# --------------------------------------------------
# MERGE TABLES
# --------------------------------------------------

df = (
    profit_loss
    .merge(balance_sheet, on=["company_id", "year"], how="inner")
    .merge(cash_flow, on=["company_id", "year"], how="inner")
)

print("\nMerged Data")

print(df.head())

print("\nRows :", len(df))


# -----------------------------------
# CALCULATE PROFITABILITY KPIs
# -----------------------------------

df["net_profit_margin_pct"] = df.apply(
    lambda x: net_profit_margin(x.net_profit, x.sales),
    axis=1
)

df["operating_profit_margin_pct"] = df.apply(
    lambda x: operating_profit_margin(x.operating_profit, x.sales),
    axis=1
)

df["return_on_equity_pct"] = df.apply(
    lambda x: return_on_equity(
        x.net_profit,
        x.equity_capital,
        x.reserves
    ),
    axis=1
)

# -----------------------------------
# CALCULATE LEVERAGE KPIs
# -----------------------------------

df["debt_to_equity"] = df.apply(
    lambda x: debt_to_equity(
        x.borrowings,
        x.equity_capital,
        x.reserves
    ),
    axis=1
)

df["interest_coverage"] = df.apply(
    lambda x: interest_coverage_ratio(
        x.operating_profit,
        x.other_income,
        x.interest
    ),
    axis=1
)

df["asset_turnover"] = df.apply(
    lambda x: asset_turnover(
        x.sales,
        x.total_assets
    ),
    axis=1
)

print("\n===== KPI Preview =====")

print(df[[
    "company_id",
    "year",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover"
]].head())

# -----------------------------------
# SAVE TO SQLITE
# -----------------------------------

financial_ratios = df[[
    "company_id",
    "year",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover"
]]

financial_ratios.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

print("\nfinancial_ratios table created successfully!")

count = pd.read_sql(
    "SELECT COUNT(*) AS total FROM financial_ratios",
    conn
)

print("\nTotal rows in financial_ratios:")
print(count)

print(df[[
    "company_id",
    "year",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover"
]].head())



conn.close()
