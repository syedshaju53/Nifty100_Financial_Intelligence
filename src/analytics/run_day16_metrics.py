import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql("SELECT * FROM master_financials", conn)

print("Rows Loaded :", len(df))


# -------------------------------
# FREE CASH FLOW
# -------------------------------

df["free_cash_flow"] = (
    df["operating_activity"].fillna(0)
    + df["investing_activity"].fillna(0)
)

# -------------------------------
# Convert year
# -------------------------------

df["year"] = df["year"].astype(int)

df = df.sort_values(["company_id", "year"])


# -------------------------------
# CAGR FUNCTION
# -------------------------------

def calculate_cagr(start, end, years):

    if start <= 0 or end <= 0 or years <= 0:
        return np.nan

    return ((end / start) ** (1 / years) - 1) * 100


df["revenue_cagr_5yr"] = np.nan
df["pat_cagr_5yr"] = np.nan
df["eps_cagr_5yr"] = np.nan


for company in df["company_id"].unique():

    company_df = df[df["company_id"] == company]

    if len(company_df) < 6:
        continue

    company_df = company_df.sort_values("year")

    for i in range(5, len(company_df)):

        current = company_df.index[i]
        previous = company_df.index[i - 5]

        df.loc[current, "revenue_cagr_5yr"] = calculate_cagr(
            df.loc[previous, "sales"],
            df.loc[current, "sales"],
            5,
        )

        df.loc[current, "pat_cagr_5yr"] = calculate_cagr(
            df.loc[previous, "net_profit"],
            df.loc[current, "net_profit"],
            5,
        )

        df.loc[current, "eps_cagr_5yr"] = calculate_cagr(
            df.loc[previous, "eps"],
            df.loc[current, "eps"],
            5,
        )


print("\n===== Preview =====\n")

print(
    df[
        [
            "company_id",
            "year",
            "free_cash_flow",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
        ]
    ].head(15)
)

df.to_sql(
    "master_financials",
    conn,
    if_exists="replace",
    index=False,
)

print("\nmaster_financials Updated Successfully!")

output_dir = BASE_DIR / "output"
output_dir.mkdir(exist_ok=True)

df.to_csv(
    output_dir / "master_financials.csv",
    index=False,
)

print("CSV Updated Successfully!")

conn.close()