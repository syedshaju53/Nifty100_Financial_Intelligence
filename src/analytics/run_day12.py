import sqlite3
import pandas as pd
from pathlib import Path

from ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)

from cashflow_kpis import (
    free_cash_flow,
    capex_intensity,
    cfo_quality_score,
    fcf_conversion_rate,
)

from cagr import calculate_cagr


# ============================================================
# DAY 12 — FINANCIAL RATIO & KPI ENGINE
# ============================================================

print("=" * 60)
print("DAY 12 — FINANCIAL RATIO & KPI ENGINE")
print("=" * 60)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"

print("\nDatabase:")
print(DB_PATH)


# ============================================================
# CONNECT DATABASE
# ============================================================

conn = sqlite3.connect(DB_PATH)


# ============================================================
# LOAD SOURCE TABLES
# ============================================================

print("\nLoading source tables...")

profit_loss = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

balance_sheet = pd.read_sql(
    "SELECT * FROM balance_sheet",
    conn
)

cash_flow = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)


# ============================================================
# SOURCE DATA COUNTS
# ============================================================

print("\nSource data counts")

print(f"Profit Loss   : {len(profit_loss)}")
print(f"Balance Sheet : {len(balance_sheet)}")
print(f"Cash Flow     : {len(cash_flow)}")


# ============================================================
# SOURCE COMPANY COUNTS
# ============================================================

print("\nSource company coverage")

print(
    "Profit Loss companies   :",
    profit_loss["company_id"].nunique()
)

print(
    "Balance Sheet companies :",
    balance_sheet["company_id"].nunique()
)

print(
    "Cash Flow companies     :",
    cash_flow["company_id"].nunique()
)


# ============================================================
# CHECK ORIGINAL DUPLICATES
# ============================================================

print("\nDuplicate records before cleaning")

print(
    "Profit Loss   :",
    profit_loss.duplicated(
        ["company_id", "year"]
    ).sum()
)

print(
    "Balance Sheet :",
    balance_sheet.duplicated(
        ["company_id", "year"]
    ).sum()
)

print(
    "Cash Flow     :",
    cash_flow.duplicated(
        ["company_id", "year"]
    ).sum()
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

profit_loss = profit_loss.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
)

balance_sheet = balance_sheet.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
)

cash_flow = cash_flow.drop_duplicates(
    subset=["company_id", "year"],
    keep="first"
)


# ============================================================
# AFTER DUPLICATE CLEANING
# ============================================================

print("\nAfter removing duplicates")

print(
    "Profit Loss   :",
    len(profit_loss)
)

print(
    "Balance Sheet :",
    len(balance_sheet)
)

print(
    "Cash Flow     :",
    len(cash_flow)
)


# ============================================================
# MERGE SOURCE TABLES
# ============================================================
#
# IMPORTANT:
#
# Previous version used INNER JOIN.
#
# That caused:
#
# ATGL → removed because cash_flow was missing
# SBIN → removed because balance_sheet was missing
#
# We now use OUTER JOIN so companies remain in the
# analytical dataset even when one source table is missing.
#
# Missing financial values become NaN.
#
# ============================================================

print("\nMerging financial tables...")

df = (
    profit_loss
    .merge(
        balance_sheet,
        on=["company_id", "year"],
        how="outer",
        suffixes=("", "_bs")
    )
    .merge(
        cash_flow,
        on=["company_id", "year"],
        how="outer",
        suffixes=("", "_cf")
    )
)


# ============================================================
# MERGE VALIDATION
# ============================================================

print("\nMerged Data")

print("Rows :", len(df))

print(
    "Companies :",
    df["company_id"].nunique()
)


# ============================================================
# CHECK ATGL / SBIN
# ============================================================

print("\n============================================================")
print("ATGL / SBIN MERGE CHECK")
print("============================================================")

for company in ["ATGL", "SBIN"]:

    company_df = df[
        df["company_id"].astype(str) == company
    ]

    print(
        f"{company}:",
        len(company_df),
        "rows"
    )

    if not company_df.empty:
        print(
            company_df[
                ["company_id", "year"]
            ].tail(5).to_string(index=False)
        )


# ============================================================
# SAFE NUMERIC CONVERSION
# ============================================================

numeric_columns = [
    "net_profit",
    "sales",
    "operating_profit",
    "equity_capital",
    "reserves",
    "borrowings",
    "other_income",
    "interest",
    "total_assets",
    "operating_activity",
    "investing_activity",
    "financing_activity",
    "net_cash_flow",
]


for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ============================================================
# SAFE KPI FUNCTION
# ============================================================

def safe_kpi(func, *values):
    """
    Safely calculate a KPI.

    Returns NaN when required source data is missing
    or when the calculation is mathematically invalid.
    """

    try:

        if any(pd.isna(value) for value in values):
            return float("nan")

        result = func(*values)

        if result is None:
            return float("nan")

        return result

    except (
        ZeroDivisionError,
        ValueError,
        TypeError,
        OverflowError
    ):

        return float("nan")


# ============================================================
# PROFITABILITY KPIs
# ============================================================

print("\nCalculating profitability KPIs...")


df["net_profit_margin_pct"] = df.apply(
    lambda x: safe_kpi(
        net_profit_margin,
        x.net_profit,
        x.sales
    ),
    axis=1
)


df["operating_profit_margin_pct"] = df.apply(
    lambda x: safe_kpi(
        operating_profit_margin,
        x.operating_profit,
        x.sales
    ),
    axis=1
)


df["return_on_equity_pct"] = df.apply(
    lambda x: safe_kpi(
        return_on_equity,
        x.net_profit,
        x.equity_capital,
        x.reserves
    ),
    axis=1
)


# ============================================================
# LEVERAGE KPIs
# ============================================================

print("Calculating leverage KPIs...")


df["debt_to_equity"] = df.apply(
    lambda x: safe_kpi(
        debt_to_equity,
        x.borrowings,
        x.equity_capital,
        x.reserves
    ),
    axis=1
)


df["interest_coverage"] = df.apply(
    lambda x: safe_kpi(
        interest_coverage_ratio,
        x.operating_profit,
        x.other_income,
        x.interest
    ),
    axis=1
)


# ============================================================
# EFFICIENCY KPI
# ============================================================

print("Calculating efficiency KPI...")


df["asset_turnover"] = df.apply(
    lambda x: safe_kpi(
        asset_turnover,
        x.sales,
        x.total_assets
    ),
    axis=1
)


# ============================================================
# CASH FLOW KPIs
# ============================================================

print("Calculating cash-flow KPIs...")

# Free Cash Flow = Cash Flow from Operating Activities
#                 + Cash Flow from Investing Activities
#
# The investing activity value is normally negative when the
# company is spending on capex, so adding CFO + CFI is the
# intended FCF definition used by this project.
df["free_cash_flow"] = df.apply(
    lambda x: safe_kpi(
        free_cash_flow,
        x.operating_activity,
        x.investing_activity
    ),
    axis=1
)


# ============================================================
# KPI PREVIEW
# ============================================================

print("\n============================================================")
print("KPI PREVIEW")
print("============================================================")


preview_columns = [
    "company_id",
    "year",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow",
]


print(
    df[preview_columns]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# KPI MISSING-VALUE REPORT
# ============================================================

print("\n============================================================")
print("KPI MISSING VALUE REPORT")
print("============================================================")


kpi_columns = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow",
]


for col in kpi_columns:

    missing = df[col].isna().sum()

    total = len(df)

    available = total - missing

    print(
        f"{col:35s}"
        f" available={available:5d}"
        f" missing={missing:5d}"
    )


# ============================================================
# ATGL / SBIN KPI CHECK
# ============================================================

print("\n============================================================")
print("ATGL / SBIN KPI CHECK")
print("============================================================")


for company in ["ATGL", "SBIN"]:

    company_df = df[
        df["company_id"].astype(str) == company
    ]

    print(f"\n{company}")

    if company_df.empty:

        print("WARNING: Company missing from merged dataset")

    else:

        print(
            company_df[
                preview_columns
            ].tail(5).to_string(index=False)
        )


# ============================================================
# PREPARE FINANCIAL RATIOS TABLE
# ============================================================

financial_ratios = df[
    [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow",
    ]
].copy()


# ============================================================
# CLEAN IDENTIFIERS
# ============================================================

financial_ratios["company_id"] = (
    financial_ratios["company_id"]
    .astype(str)
    .str.strip()
)

financial_ratios["year"] = (
    financial_ratios["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)


# Remove rows where there is no company ID or year.
financial_ratios = financial_ratios[
    financial_ratios["company_id"].notna()
    & financial_ratios["year"].notna()
]


# ============================================================
# REMOVE DUPLICATES AGAIN
# ============================================================

# financial_ratios = financial_ratios.drop_duplicates(
#     subset=["company_id", "year"],
#     keep="first"
# )


# ============================================================
# FINAL FINANCIAL RATIO COUNTS
# ============================================================

print("\n============================================================")
print("FINANCIAL RATIOS FINAL VALIDATION")
print("============================================================")


print(
    "Financial ratio rows      :",
    len(financial_ratios)
)

print(
    "Financial ratio companies :",
    financial_ratios["company_id"].nunique()
)

print(
    "Financial ratio years     :",
    financial_ratios["year"].nunique()
)


# ============================================================
# ATGL / SBIN FINAL VALIDATION
# ============================================================

for company in ["ATGL", "SBIN"]:

    company_rows = financial_ratios[
        financial_ratios["company_id"] == company
    ]

    print(
        f"{company:5s}:",
        len(company_rows),
        "rows"
    )


# ============================================================
# SAVE TO SQLITE
# ============================================================

financial_ratios.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)


print(
    "\nfinancial_ratios table created successfully!"
)


# ============================================================
# DATABASE VALIDATION
# ============================================================

count = pd.read_sql(
    """
    SELECT COUNT(*) AS total
    FROM financial_ratios
    """,
    conn
)


print("\nTotal rows in financial_ratios:")

print(count)


company_count = pd.read_sql(
    """
    SELECT COUNT(DISTINCT company_id) AS companies
    FROM financial_ratios
    """,
    conn
)


print("\nTotal companies in financial_ratios:")

print(company_count)


# ============================================================
# FINAL COMPANY COVERAGE
# ============================================================

coverage = pd.read_sql(
    """
    SELECT
        company_id,
        COUNT(*) AS year_count
    FROM financial_ratios
    GROUP BY company_id
    ORDER BY company_id
    """,
    conn
)


print("\nCompany coverage:")

print(
    coverage.to_string(index=False)
)


# ============================================================
# FINAL ATGL / SBIN DATABASE CHECK
# ============================================================

print("\n============================================================")
print("FINAL ATGL / SBIN DATABASE CHECK")
print("============================================================")


for company in ["ATGL", "SBIN"]:

    result = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        conn,
        params=(company,)
    )

    print(f"\n{company}")

    print(
        "Rows:",
        len(result)
    )

    if not result.empty:

        print(
            result.tail(5).to_string(index=False)
        )


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()


# ============================================================
# FINAL STATUS
# ============================================================

print("\n============================================================")
print("DAY 12 FINANCIAL RATIO ENGINE COMPLETED")
print("============================================================")

print(
    "Financial ratio rows      :",
    len(financial_ratios)
)

print(
    "Financial ratio companies :",
    financial_ratios["company_id"].nunique()
)

print(
    "ATGL present              :",
    "YES"
    if "ATGL" in financial_ratios["company_id"].values
    else "NO"
)

print(
    "SBIN present              :",
    "YES"
    if "SBIN" in financial_ratios["company_id"].values
    else "NO"
)

print("=" * 60)