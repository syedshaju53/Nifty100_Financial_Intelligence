from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = [
    "companies",
    "profit_loss",
    "balance_sheet",
    "cash_flow",
    "analysis",
    "pros_and_cons",
    "documents",
    "stock_prices",
    "ratios",
    "market_cap",
    "peer_groups",
    "sectors"
]

print("=" * 60)
print("SPRINT 1 FINAL DATABASE VALIDATION")
print("=" * 60)

all_ok = True

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]

    if count == 0:
        print(f"{table:<20} FAIL")
        all_ok = False
    else:
        print(f"{table:<20} PASS ({count} rows)")

print("\nChecking Foreign Keys...")

cursor.execute("PRAGMA foreign_key_check")

fk = cursor.fetchall()

if len(fk) == 0:
    print("PASS")
else:
    print("FAIL")
    print(fk)
    all_ok = False

print("\nOverall Result")

if all_ok:
    print("SPRINT 1 VALIDATION PASSED")
else:
    print("SPRINT 1 VALIDATION FAILED")

conn.close()