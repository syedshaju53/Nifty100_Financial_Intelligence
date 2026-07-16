import sqlite3
import pandas as pd
from pathlib import Path

# ---------------------------------------
# Project Paths
# ---------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

# ---------------------------------------
# Load Tables
# ---------------------------------------

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

profit_loss = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

cash_flow = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)

market_cap = pd.read_sql(
    "SELECT * FROM market_cap",
    conn
)

print("Financial Ratios :", len(financial_ratios))
print("Profit Loss      :", len(profit_loss))
print("Cash Flow        :", len(cash_flow))
print("Market Cap       :", len(market_cap))

# ---------------------------------------
# Remove Duplicates
# ---------------------------------------

financial_ratios = financial_ratios.drop_duplicates(
    subset=["company_id", "year"]
)

profit_loss = profit_loss.drop_duplicates(
    subset=["company_id", "year"]
)

cash_flow = cash_flow.drop_duplicates(
    subset=["company_id", "year"]
)

market_cap = market_cap.drop_duplicates(
    subset=["company_id", "year"]
)

# ---------------------------------------
# Fix Year Column
# ---------------------------------------

financial_ratios["year"] = (
    financial_ratios["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

profit_loss["year"] = (
    profit_loss["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

cash_flow["year"] = (
    cash_flow["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

market_cap["year"] = market_cap["year"].astype(str)

print("\nYear Conversion Complete")

# ---------------------------------------
# Merge
# ---------------------------------------

master = financial_ratios.merge(
    profit_loss,
    on=["company_id", "year"],
    how="left",
    suffixes=("", "_pl")
)

master = master.merge(
    cash_flow,
    on=["company_id", "year"],
    how="left",
    suffixes=("", "_cf")
)

master = master.merge(
    market_cap,
    on=["company_id", "year"],
    how="left",
    suffixes=("", "_mc")
)

print("\nMerged Rows :", len(master))

print("\nColumns Available:\n")

for col in master.columns:
    print(col)

# ---------------------------------------
# Save SQLite
# ---------------------------------------

master.to_sql(
    "master_financials",
    conn,
    if_exists="replace",
    index=False
)

print("\nmaster_financials table created successfully!")

# ---------------------------------------
# Export CSV
# ---------------------------------------

output_dir = BASE_DIR / "output"
output_dir.mkdir(exist_ok=True)

master.to_csv(
    output_dir / "master_financials.csv",
    index=False
)

print("\nCSV Exported Successfully!")

conn.close()