import sqlite3
import pandas as pd
from pathlib import Path

from src.screener.engine import apply_filters

from pathlib import Path
import sqlite3

# Project Root
BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

print("Database Path:", DB_PATH)
print("Exists:", DB_PATH.exists())

conn = sqlite3.connect(DB_PATH)


df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print("Rows Loaded :", len(df))

filtered = apply_filters(df)

print("\n===== Screener Result =====\n")

print(filtered.head())

print("\nCompanies Found :", len(filtered))

filtered.to_excel(
    BASE_DIR / "outputs" / "screener_output.xlsx",
    index=False
)

print("\nExcel Generated Successfully")