import sqlite3
import pandas as pd
from pathlib import Path

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)

# ---------------------------------------------
# Database Connection
# ---------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ---------------------------------------------
# Load Tables
# ---------------------------------------------
cashflow = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)

profit_loss = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

# ---------------------------------------------
# Merge Cash Flow + Profit & Loss
# ---------------------------------------------
df = cashflow.merge(
    profit_loss,
    on=["company_id", "year"],
    how="left",
    suffixes=("", "_pl")
)

results = []

# ---------------------------------------------
# Calculate KPIs
# ---------------------------------------------
for _, row in df.iterrows():

    cfo = row.get("operating_activity", 0)
    cfi = row.get("investing_activity", 0)
    cff = row.get("financing_activity", 0)

    sales = row.get("sales", 0)
    operating_profit = row.get("operating_profit", 0)
    pat = row.get("net_profit", 0)

    fcf = free_cash_flow(cfo, cfi)

    quality_score, quality_label = cfo_quality_score(
        cfo,
        pat
    )

    capex_value, capex_label = capex_intensity(
        cfi,
        sales
    )

    fcf_conversion = fcf_conversion_rate(
        fcf,
        operating_profit
    )

    pattern = capital_allocation_pattern(
        cfo,
        cfi,
        cff,
        quality_label if quality_label else "Moderate"
    )

    results.append({

        "company_id": row["company_id"],
        "year": row["year"],

        "free_cash_flow": fcf,

        "cfo_quality_score": quality_score,
        "cfo_quality_label": quality_label,

        "capex_intensity": capex_value,
        "capex_label": capex_label,

        "fcf_conversion": fcf_conversion,

        "cfo_sign": pattern["cfo_sign"],
        "cfi_sign": pattern["cfi_sign"],
        "cff_sign": pattern["cff_sign"],

        "pattern_label": pattern["pattern_label"]

    })

# ---------------------------------------------
# Create Output DataFrame
# ---------------------------------------------
result_df = pd.DataFrame(results)

# ---------------------------------------------
# Save CSV
# ---------------------------------------------
csv_path = OUTPUT_DIR / "capital_allocation.csv"

result_df.to_csv(
    csv_path,
    index=False
)

# ---------------------------------------------
# Preview
# ---------------------------------------------
print("\n==============================")
print("DAY 11 - CASH FLOW KPI ENGINE")
print("==============================\n")

print(result_df.head())

print("\nTotal Rows :", len(result_df))

print("\nCSV Saved Successfully")

print(csv_path)

conn.close()