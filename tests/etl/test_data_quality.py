from pathlib import Path
import sqlite3

# ---------------------------------------
# Project Paths
# ---------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("DAY 6 - DATA QUALITY VALIDATION")
print("=" * 60)


# -------------------------------------------------
# 1. Duplicate Company IDs
# -------------------------------------------------

print("\nChecking Duplicate Company IDs...")

cursor.execute("""
SELECT id, COUNT(*)
FROM companies
GROUP BY id
HAVING COUNT(*) > 1
""")

duplicates = cursor.fetchall()

if duplicates:
    print("FAIL")
    print(f"Duplicate IDs Found : {len(duplicates)}")
else:
    print("PASS")


# -------------------------------------------------
# 2. Null Company IDs
# -------------------------------------------------

print("\nChecking NULL IDs...")

cursor.execute("""
SELECT COUNT(*)
FROM companies
WHERE id IS NULL
""")

null_ids = cursor.fetchone()[0]

if null_ids == 0:
    print("PASS")
else:
    print(f"FAIL - {null_ids} NULL IDs")


# -------------------------------------------------
# 3. Company Count
# -------------------------------------------------

cursor.execute("""
SELECT COUNT(*)
FROM companies
""")

company_count = cursor.fetchone()[0]

print(f"\nCompanies Loaded : {company_count}")


# -------------------------------------------------
# 4. Profit & Loss Year Range
# -------------------------------------------------

cursor.execute("""
SELECT MIN(year), MAX(year)
FROM profit_loss
""")

print("\nProfit & Loss Year Range :", cursor.fetchone())


# -------------------------------------------------
# 5. Balance Sheet Year Range
# -------------------------------------------------

cursor.execute("""
SELECT MIN(year), MAX(year)
FROM balance_sheet
""")

print("Balance Sheet Year Range :", cursor.fetchone())


# -------------------------------------------------
# 6. Cash Flow Year Range
# -------------------------------------------------

cursor.execute("""
SELECT MIN(year), MAX(year)
FROM cash_flow
""")

print("Cash Flow Year Range :", cursor.fetchone())


# -------------------------------------------------
# 7. Foreign Key Validation
# -------------------------------------------------

print("\nForeign Key Check")

tables = [
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

failed = False

for table in tables:

    cursor.execute(f"""
    SELECT COUNT(*)
    FROM {table}
    WHERE id NOT IN (
        SELECT id
        FROM companies
    )
    """)

    invalid = cursor.fetchone()[0]

    if invalid > 0:
        print(f"{table:<20} FAIL ({invalid} Invalid IDs)")
        failed = True

if not failed:
    print("PASS")


# -------------------------------------------------
# 8. Record Counts
# -------------------------------------------------

print("\nRecord Counts")
print("-" * 35)

for table in [
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
]:

    cursor.execute(f"SELECT COUNT(*) FROM {table}")

    count = cursor.fetchone()[0]

    print(f"{table:<20} {count}")


print("\n" + "=" * 60)
print("DAY 6 REVIEW COMPLETED")
print("=" * 60)

conn.close()