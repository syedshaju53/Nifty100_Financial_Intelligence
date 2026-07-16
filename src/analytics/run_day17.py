
import sqlite3
import pandas as pd
from pathlib import Path

from src.screener.scoring import calculate_composite_score

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

print("Rows Loaded :", len(df))

df = calculate_composite_score(df)

df = df.sort_values(
    "composite_quality_score",
    ascending=False
)

print("\n===== Top 10 Companies =====\n")

print(
    df[
        [
            "company_id",
            "year",
            "composite_quality_score"
        ]
    ].head(10)
)

# Save SQLite

df.to_sql(
    "master_financials",
    conn,
    if_exists="replace",
    index=False
)

print("\nmaster_financials Updated!")

# Export Excel

output_dir = BASE_DIR / "output"
output_dir.mkdir(exist_ok=True)

excel_path = output_dir / "quality_scores.xlsx"

df.to_excel(
    excel_path,
    index=False
)

print("\nExcel Generated Successfully!")

print(excel_path)

conn.close()