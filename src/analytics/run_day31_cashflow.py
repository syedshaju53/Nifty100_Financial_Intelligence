import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

# ---------------------------------------
# Load Data
# ---------------------------------------

df = pd.read_sql(
    "SELECT * FROM master_financials",
    conn
)

sector = pd.read_sql(
    """
    SELECT
        company_id,
        broad_sector
    FROM sectors
    """,
    conn
)

print("Financial Rows :", len(df))
print("Sector Rows    :", len(sector))

# ---------------------------------------
# Prepare Data
# ---------------------------------------

df["year"] = df["year"].astype(int)

df = df.sort_values(
    ["company_id", "year"]
)

# Merge sector into every row
df = df.merge(
    sector,
    on="company_id",
    how="left"
)

print("Companies :", df["company_id"].nunique())

# =====================================================
# CFO QUALITY + CAPEX
# =====================================================

summary = []

for company in df["company_id"].unique():

    company_df = (
        df[df["company_id"] == company]
        .sort_values("year")
    )

    latest_row = company_df.iloc[-1]

    # -----------------------------
    # Average CFO / PAT (Last 5 Years)
    # -----------------------------

    last5 = company_df.tail(5)

    ratio = (
        last5["operating_activity"] /
        last5["net_profit"].replace(0, np.nan)
    )

    cfo_score = ratio.mean()

    if pd.isna(cfo_score):
        label = "Unknown"
    elif cfo_score > 1:
        label = "High Quality"
    elif cfo_score >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    # -----------------------------
    # CapEx Intensity
    # -----------------------------

    if latest_row["sales"] > 0:

        capex = (
            abs(latest_row["investing_activity"])
            / latest_row["sales"]
            * 100
        )

    else:

        capex = np.nan

    if pd.isna(capex):
        capex_label = "Unknown"
    elif capex < 3:
        capex_label = "Asset Light"
    elif capex <= 8:
        capex_label = "Moderate"
    else:
        capex_label = "Capital Intensive"

    summary.append({

        "company_id": company,

        "sector": latest_row["broad_sector"],

        "cfo_quality_score": round(cfo_score, 2)
        if pd.notna(cfo_score) else np.nan,

        "cfo_quality_label": label,

        "capex_intensity_pct": round(capex, 2)
        if pd.notna(capex) else np.nan,

        "capex_label": capex_label

    })

cashflow_df = pd.DataFrame(summary)

print("\nPreview\n")

print(cashflow_df.head())

conn.close()

# =====================================================
# Additional Cash Flow Intelligence
# =====================================================

cashflow_df["fcf_conversion_pct"] = np.nan
cashflow_df["distress_flag"] = "No"
cashflow_df["deleveraging_flag"] = "No"
cashflow_df["capital_allocation_label"] = "Stable"

distress_rows = []

for i, row in cashflow_df.iterrows():

    company = row["company_id"]

    latest_company = (
        df[df["company_id"] == company]
        .sort_values("year")
        .iloc[-1]
    )

    # -----------------------------
    # FCF Conversion %
    # -----------------------------

    if latest_company["net_profit"] != 0:

        conversion = (
            latest_company["free_cash_flow"]
            / latest_company["net_profit"]
        ) * 100

    else:

        conversion = np.nan

    cashflow_df.loc[i, "fcf_conversion_pct"] = round(conversion, 2) if pd.notna(conversion) else np.nan

    # -----------------------------
    # Distress Flag
    # -----------------------------

    if (
        latest_company["operating_activity"] < 0
        and
        latest_company["financing_activity"] > 0
    ):

        cashflow_df.loc[i, "distress_flag"] = "Yes"

        distress_rows.append({

            "company_id": company,

            "cfo": latest_company["operating_activity"],

            "cff": latest_company["financing_activity"],

            "net_profit": latest_company["net_profit"]

        })

    # -----------------------------
    # Deleveraging
    # -----------------------------

    if latest_company["financing_activity"] < 0:

        cashflow_df.loc[i, "deleveraging_flag"] = "Yes"

    # -----------------------------
    # Capital Allocation Label
    # -----------------------------

    if (
        latest_company["operating_activity"] > 0
        and latest_company["investing_activity"] < 0
        and latest_company["financing_activity"] < 0
    ):

        label = "Reinvestor"

    elif latest_company["operating_activity"] < 0:

        label = "Distress"

    elif latest_company["financing_activity"] > 0:

        label = "Expansion"

    else:

        label = "Stable"

    cashflow_df.loc[i, "capital_allocation_label"] = label

# Distress DataFrame

distress_df = pd.DataFrame(distress_rows)

print("\nCash Flow Intelligence Preview\n")

print(cashflow_df.head())

print("\nDistress Companies :", len(distress_df))

# =====================================================
# Export Results
# =====================================================

output_dir = BASE_DIR / "output"
output_dir.mkdir(exist_ok=True)

cashflow_df.to_excel(
    output_dir / "cashflow_intelligence.xlsx",
    index=False,
)

distress_df.to_csv(
    output_dir / "distress_alerts.csv",
    index=False,
)

print("\n====================================")
print("Day 31 Completed Successfully")
print("====================================")
print("Cash Flow Intelligence :", output_dir / "cashflow_intelligence.xlsx")
print("Distress Alerts        :", output_dir / "distress_alerts.csv")

conn.close()