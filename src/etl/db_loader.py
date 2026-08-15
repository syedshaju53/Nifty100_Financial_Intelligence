from pathlib import Path
import sqlite3
import pandas as pd

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_PATH = BASE_DIR / "outputs"

# -----------------------------
# Excel Files
# -----------------------------
TABLES = {
    "companies.xlsx": ("companies", 1),
    "profitandloss.xlsx": ("profit_loss", 1),
    "balancesheet.xlsx": ("balance_sheet", 1),
    "cashflow.xlsx": ("cash_flow", 1),
    "analysis.xlsx": ("analysis", 1),
    "prosandcons.xlsx": ("pros_and_cons", 1),
    "documents.xlsx": ("documents", 1),

    "stock_prices.xlsx": ("stock_prices", 0),
    "financial_ratios.xlsx": ("ratios", 0),
    "market_cap.xlsx": ("market_cap", 0),
    "peer_groups.xlsx": ("peer_groups", 0),
    "sectors.xlsx": ("sectors", 0),
}


def load_all_tables():

    OUTPUT_PATH.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Load valid company IDs
    companies_df = pd.read_excel(RAW_DATA / "companies.xlsx", header=1)
    companies_df.columns = companies_df.columns.str.strip()

    valid_ids = set(
        companies_df["id"]
        .astype(str)
        .str.strip()
    )

    audit = []

    for excel_file, (table_name, header) in TABLES.items():

        file_path = RAW_DATA / excel_file

        if not file_path.exists():

            audit.append([table_name, 0, "File Not Found"])
            print(f"{excel_file} not found")
            continue

        try:

            df = pd.read_excel(file_path, header=header)

            # Clean column names
            df.columns = df.columns.astype(str).str.strip()

            # Remove empty columns
            df = df.dropna(axis=1, how="all")

            # Clean text values
            for col in df.select_dtypes(include=["object", "string"]).columns:
                df[col] = df[col].astype(str).str.strip()

            # Remove duplicate rows
            df = df.drop_duplicates()

            # Validate company_id
            if "company_id" in df.columns:

                before = len(df)

                df = df[df["company_id"].isin(valid_ids)]

                removed = before - len(df)

                if removed > 0:
                    print(f"{table_name}: Removed {removed} invalid records")

            # Load table
            df.to_sql(
                table_name,
                conn,
                if_exists="append",
                index=False
            )

            audit.append(
                [table_name, len(df), "Success"]
            )

            print(f"Loaded {table_name:<20} {len(df)} rows")

        except Exception as e:

            audit.append(
                [table_name, 0, str(e)]
            )

            print(f"{table_name}: {e}")

    conn.commit()
    conn.close()

    audit_df = pd.DataFrame(
        audit,
        columns=[
            "Table",
            "Rows Loaded",
            "Status"
        ]
    )

    audit_df.to_csv(
        OUTPUT_PATH / "load_audit.csv",
        index=False
    )

    print("\n===================================")
    print("Load Audit Generated Successfully")
    print("outputs/load_audit.csv")
    print("===================================")


if __name__ == "__main__":
    load_all_tables()