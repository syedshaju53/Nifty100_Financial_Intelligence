import sqlite3
import pandas as pd
from pathlib import Path

from src.analytics.health_score import (
    profitability_score,
    roe_score,
    leverage_score,
    efficiency_score,
    total_health_score,
    health_rating,
)

# ----------------------------------------
# DATABASE CONNECTION
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

# ----------------------------------------
# LOAD FINANCIAL RATIOS TABLE
# ----------------------------------------

df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print("Rows Loaded :", len(df))

# ----------------------------------------
# CALCULATE SCORES
# ----------------------------------------

df["profitability_score"] = df["net_profit_margin_pct"].apply(
    profitability_score
)

df["roe_score"] = df["return_on_equity_pct"].apply(
    roe_score
)

df["leverage_score"] = df["debt_to_equity"].apply(
    leverage_score
)

df["efficiency_score"] = df["asset_turnover"].apply(
    efficiency_score
)

# ----------------------------------------
# TOTAL SCORE
# ----------------------------------------

df["financial_health_score"] = df.apply(
    lambda x: total_health_score(
        x.profitability_score,
        x.roe_score,
        x.leverage_score,
        x.efficiency_score,
    ),
    axis=1
)

# ----------------------------------------
# RATING
# ----------------------------------------

df["health_rating"] = df["financial_health_score"].apply(
    health_rating
)

# ----------------------------------------
# PREVIEW
# ----------------------------------------

print("\n===== Financial Health Preview =====\n")

print(df[[
    "company_id",
    "year",
    "financial_health_score",
    "health_rating"
]].head())

# ----------------------------------------
# SAVE TO SQLITE
# ----------------------------------------

df.to_sql(
    "financial_health_scores",
    conn,
    if_exists="replace",
    index=False
)

print("\nfinancial_health_scores table created successfully!")

# ----------------------------------------
# EXPORT CSV
# ----------------------------------------

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

csv_path = OUTPUT_DIR / "financial_health_scores.csv"

df.to_csv(csv_path, index=False)

print("\nCSV Saved Successfully")
print(csv_path)

conn.close()