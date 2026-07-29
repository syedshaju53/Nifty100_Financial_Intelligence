import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

DB = BASE_DIR / "db" / "nifty100.db"

OUTPUT = BASE_DIR / "output"

conn = sqlite3.connect(DB)

# ---------------------------------------
# Load Files
# ---------------------------------------

capital = pd.read_csv(
    OUTPUT / "capital_allocation.csv"
)

cashflow = pd.read_excel(
    OUTPUT / "cashflow_intelligence.xlsx"
)

print("Capital Allocation Rows :", len(capital))
print("Cashflow Rows :", len(cashflow))

# ---------------------------------------
# Latest Year Pattern
# ---------------------------------------

latest = (
    capital
    .sort_values("year")
    .groupby("company_id")
    .tail(1)
)

distribution = (
    latest["pattern_label"]
    .value_counts()
    .reset_index()
)

distribution.columns = [
    "capital_allocation_pattern",
    "company_count"
]

print("\nPattern Distribution\n")

print(distribution)

# ---------------------------------------
# Merge Latest Pattern
# ---------------------------------------

cashflow = cashflow.merge(

    latest[
        [
            "company_id",
            "pattern_label"
        ]
    ],

    on="company_id",

    how="left"

)

cashflow.rename(

    columns={

        "pattern_label":
        "capital_allocation"

    },

    inplace=True

)

# ---------------------------------------
# Save Updated Excel
# ---------------------------------------

cashflow.to_excel(

    OUTPUT / "cashflow_intelligence.xlsx",

    index=False

)

print("\nCashflow file updated.")
