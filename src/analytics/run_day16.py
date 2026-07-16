import sqlite3
import pandas as pd
from pathlib import Path

from src.screener.presets import *

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

print("Rows Loaded :", len(df))

output_dir = BASE_DIR / "output"
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "screener_output.xlsx"

screeners = {
    "Quality Compounder": quality_compounder,
    "Value Pick": value_pick,
    "Growth Accelerator": growth_accelerator,
    "Dividend Champion": dividend_champion,
    "Debt Free Bluechip": debt_free_bluechip,
    "Turnaround Watch": turnaround_watch,
}

results = {}

for name, func in screeners.items():

    try:

        result = func(df)

        result = result.sort_values(
            "return_on_equity_pct",
            ascending=False
        )

        results[name] = result

        print(f"{name:<25} {len(result)} Companies")

    except Exception as e:

        print(f"{name} Failed -> {e}")

with pd.ExcelWriter(output_file) as writer:

    for sheet, data in results.items():

        data.to_excel(
            writer,
            sheet_name=sheet[:31],
            index=False
        )

print("\nExcel Generated Successfully")
print(output_file)

conn.close()