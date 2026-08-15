import sqlite3
from pathlib import Path

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    """Create a SQLite connection to the Nifty100 database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# DATABASE INFORMATION
# --------------------------------------------------

def get_database_info():
    """Return database table names and row counts."""

    conn = get_connection()

    try:
        tables = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

        db_row_counts = {}

        for row in tables:
            table_name = row["name"]

            count = conn.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]

            db_row_counts[table_name] = count

        return {
            "database": str(DB_PATH),
            "db_row_counts": db_row_counts,
            "company_count": db_row_counts.get("companies", 0),
            "master_financial_rows": db_row_counts.get(
                "master_financials", 0
            ),
            "master_companies": conn.execute(
                """
                SELECT COUNT(DISTINCT company_id)
                FROM master_financials
                """
            ).fetchone()[0],
        }

    finally:
        conn.close()