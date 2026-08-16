import sqlite3
import pandas as pd
from pathlib import Path

from src.screener.presets import (
    quality_compounder,
    value_pick,
    growth_accelerator,
    dividend_champion,
    debt_free_bluechip,
    turnaround_watch,
)

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "screener_output.xlsx"


# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect(DB_PATH)

print("=" * 70)
print("DAY 16 — STOCK SCREENER ENGINE")
print("=" * 70)

print(f"Database: {DB_PATH}")


# ============================================================
# LOAD MASTER FINANCIALS
# ============================================================

df = pd.read_sql(
    """
    SELECT *
    FROM master_financials
    """,
    conn,
)

print("\nRows Loaded     :", len(df))
print("Companies Loaded:", df["company_id"].nunique())
print("Years Loaded    :", df["year"].nunique())


# ============================================================
# CLEAN NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "return_on_equity_pct",
    "debt_to_equity",
    "free_cash_flow",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
    "dividend_payout",
    "sales",
]


for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )


# ============================================================
# SCREENER DEFINITIONS
# ============================================================

screeners = {
    "Quality Compounder": quality_compounder,
    "Value Pick": value_pick,
    "Growth Accelerator": growth_accelerator,
    "Dividend Champion": dividend_champion,
    "Debt Free Bluechip": debt_free_bluechip,
    "Turnaround Watch": turnaround_watch,
}


# ============================================================
# RUN SCREENERS
# ============================================================

results = {}


print("\n" + "=" * 70)
print("SCREENER RESULTS")
print("=" * 70)


for name, function in screeners.items():

    try:

        result = function(df.copy())

        if "return_on_equity_pct" in result.columns:

            result = result.sort_values(
                "return_on_equity_pct",
                ascending=False,
                na_position="last",
            )

        results[name] = result

        companies = (
            result["company_id"].nunique()
            if "company_id" in result.columns
            else 0
        )

        print(
            f"{name:<25}"
            f" rows={len(result):<5}"
            f" companies={companies}"
        )

    except Exception as error:

        print(
            f"{name:<25}"
            f" FAILED -> {error}"
        )


# ============================================================
# SAVE EXCEL
# ============================================================

print("\n" + "=" * 70)
print("EXPORTING RESULTS")
print("=" * 70)


with pd.ExcelWriter(OUTPUT_FILE) as writer:

    for sheet_name, result in results.items():

        result.to_excel(
            writer,
            sheet_name=sheet_name[:31],
            index=False,
        )


print("\nExcel Generated Successfully")
print(f"Output: {OUTPUT_FILE}")


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()


print("\n" + "=" * 70)
print("DAY 16 COMPLETED")
print("=" * 70)