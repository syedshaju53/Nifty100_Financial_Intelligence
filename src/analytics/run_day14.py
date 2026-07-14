import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# Load Financial Health Table
df = pd.read_sql(
    "SELECT * FROM financial_health_scores",
    conn
)

print("Rows Loaded :", len(df))

# -----------------------------
# Save Dashboard Dataset
# -----------------------------

dashboard_file = OUTPUT_DIR / "dashboard_dataset.csv"

df.to_csv(
    dashboard_file,
    index=False
)

print("\nDashboard dataset created successfully.")

print(dashboard_file)

# -----------------------------
# Validation
# -----------------------------

print("\n========== VALIDATION ==========")

print("Total Rows :", len(df))

print("Duplicate Rows :", df.duplicated().sum())

print("Missing Values :")

print(df.isnull().sum())

print("\n========== SAMPLE DATA ==========")

print(df.head())

conn.close()