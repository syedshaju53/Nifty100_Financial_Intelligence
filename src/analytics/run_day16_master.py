import sqlite3
import pandas as pd
from pathlib import Path
import numpy as np

# ============================================================
# DAY 16 — MASTER FINANCIAL DATASET
# ============================================================

print("=" * 60)
print("DAY 16 — MASTER FINANCIAL DATASET")
print("=" * 60)

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MASTER_OUTPUT = OUTPUT_DIR / "master_financials.csv"

conn = sqlite3.connect(DB_PATH)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_company_id(df):
    """Clean company identifiers."""

    if "company_id" in df.columns:
        df["company_id"] = (
            df["company_id"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    return df


def clean_year(df):
    """Extract four-digit year."""

    if "year" in df.columns:
        df["year"] = (
            df["year"]
            .astype(str)
            .str.extract(r"(\d{4})")[0]
        )

        df["year"] = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

    return df


def numeric_columns(df, columns):
    """Convert selected columns to numeric."""

    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


def remove_duplicate_keys(df):
    """Remove duplicate company/year records."""

    if "company_id" in df.columns and "year" in df.columns:
        before = len(df)

        df = df.drop_duplicates(
            subset=["company_id", "year"],
            keep="first"
        )

        after = len(df)

        if before != after:
            print(
                f"Removed {before - after} duplicate "
                f"company/year rows"
            )

    return df


# ============================================================
# LOAD TABLES
# ============================================================

print("\nLoading source tables...")

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

profit_loss = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

cash_flow = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)

market_cap = pd.read_sql(
    "SELECT * FROM market_cap",
    conn
)

print(f"Financial Ratios : {len(financial_ratios)}")
print(f"Profit Loss      : {len(profit_loss)}")
print(f"Cash Flow        : {len(cash_flow)}")
print(f"Market Cap       : {len(market_cap)}")

# ============================================================
# CLEAN COMPANY IDS
# ============================================================

financial_ratios = clean_company_id(financial_ratios)
profit_loss = clean_company_id(profit_loss)
cash_flow = clean_company_id(cash_flow)
market_cap = clean_company_id(market_cap)

# ============================================================
# CLEAN YEARS
# ============================================================

financial_ratios = clean_year(financial_ratios)
profit_loss = clean_year(profit_loss)
cash_flow = clean_year(cash_flow)
market_cap = clean_year(market_cap)

# ============================================================
# REMOVE INVALID KEYS
# ============================================================

financial_ratios = financial_ratios.dropna(
    subset=["company_id", "year"]
)

profit_loss = profit_loss.dropna(
    subset=["company_id", "year"]
)

cash_flow = cash_flow.dropna(
    subset=["company_id", "year"]
)

market_cap = market_cap.dropna(
    subset=["company_id", "year"]
)

# ============================================================
# REMOVE DUPLICATES
# ============================================================

print("\nChecking duplicate company/year records...")

financial_ratios = remove_duplicate_keys(
    financial_ratios
)

profit_loss = remove_duplicate_keys(
    profit_loss
)

cash_flow = remove_duplicate_keys(
    cash_flow
)

market_cap = remove_duplicate_keys(
    market_cap
)

# ============================================================
# NUMERIC CONVERSION
# ============================================================

financial_ratio_cols = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover"
]

profit_loss_cols = [
    "sales",
    "expenses",
    "operating_profit",
    "opm_percentage",
    "other_income",
    "interest",
    "depreciation",
    "profit_before_tax",
    "tax_percentage",
    "net_profit",
    "eps",
    "dividend_payout"
]

cash_flow_cols = [
    "operating_activity",
    "investing_activity",
    "financing_activity",
    "net_cash_flow",
    "free_cash_flow"
]

market_cap_cols = [
    "market_cap_crore",
    "enterprise_value_crore",
    "pe_ratio",
    "pb_ratio",
    "ev_ebitda",
    "dividend_yield_pct"
]

financial_ratios = numeric_columns(
    financial_ratios,
    financial_ratio_cols
)

profit_loss = numeric_columns(
    profit_loss,
    profit_loss_cols
)

cash_flow = numeric_columns(
    cash_flow,
    cash_flow_cols
)

market_cap = numeric_columns(
    market_cap,
    market_cap_cols
)

# ============================================================
# MERGE FINANCIAL RATIOS + PROFIT LOSS
# ============================================================

print("\nMerging financial ratios + profit/loss...")

master = financial_ratios.merge(
    profit_loss,
    on=["company_id", "year"],
    how="left",
    suffixes=("", "_pl")
)

# ============================================================
# MERGE CASH FLOW
# ============================================================

print("Merging cash flow...")

master = master.merge(
    cash_flow,
    on=["company_id", "year"],
    how="left",
    suffixes=("", "_cf")
)

# ============================================================
# MERGE MARKET CAP
# ============================================================

print("Merging market cap...")

master = master.merge(
    market_cap,
    on=["company_id", "year"],
    how="left",
    suffixes=("", "_mc")
)

print("\nMerged Rows :", len(master))

# ============================================================
# FIX OPERATING PROFIT MARGIN
# ============================================================
#
# IMPORTANT:
#
# The source `opm_percentage` column is inconsistent.
#
# Examples from the current data:
#
# HDFCBANK 2013:
# sales = 35861
# operating_profit = 12631
# correct OPM ≈ 35.22%
#
# but source opm_percentage = 3534
#
# Therefore we DO NOT trust the original opm_percentage.
#
# Instead:
#
# OPM = operating_profit / sales * 100
#
# ============================================================

print("\nRecalculating operating profit margin...")

if (
    "sales" in master.columns
    and "operating_profit" in master.columns
):

    master["sales"] = pd.to_numeric(
        master["sales"],
        errors="coerce"
    )

    master["operating_profit"] = pd.to_numeric(
        master["operating_profit"],
        errors="coerce"
    )

    master["opm_percentage"] = np.where(
        master["sales"].notna()
        & master["operating_profit"].notna()
        & (master["sales"] != 0),

        (
            master["operating_profit"]
            / master["sales"]
            * 100
        ),

        np.nan
    )

    master["opm_percentage"] = (
        master["opm_percentage"]
        .round(2)
    )

else:

    print(
        "WARNING: sales or operating_profit "
        "column not available."
    )

# ============================================================
# ALSO FIX OPERATING PROFIT MARGIN PCT
# ============================================================

if (
    "sales" in master.columns
    and "operating_profit" in master.columns
):

    calculated_opm = np.where(
        master["sales"].notna()
        & master["operating_profit"].notna()
        & (master["sales"] != 0),

        (
            master["operating_profit"]
            / master["sales"]
            * 100
        ),

        np.nan
    )

    master["operating_profit_margin_pct"] = (
        pd.Series(
            calculated_opm,
            index=master.index
        ).round(2)
    )

# ============================================================
# CALCULATE FCF
# ============================================================

print("\nChecking Free Cash Flow...")

if (
    "operating_activity" in master.columns
    and "investing_activity" in master.columns
):

    calculated_fcf = (
        pd.to_numeric(
            master["operating_activity"],
            errors="coerce"
        )
        +
        pd.to_numeric(
            master["investing_activity"],
            errors="coerce"
        )
    )

    if "free_cash_flow" not in master.columns:

        master["free_cash_flow"] = calculated_fcf

    else:

        # Replace missing FCF values using calculated value
        master["free_cash_flow"] = (
            master["free_cash_flow"]
            .fillna(calculated_fcf)
        )

# ============================================================
# RE-CALCULATE FINANCIAL RATIOS WHERE POSSIBLE
# ============================================================

print("\nValidating financial ratios...")

# ------------------------------------------------------------
# Net Profit Margin
# ------------------------------------------------------------

if (
    "sales" in master.columns
    and "net_profit" in master.columns
):

    calculated_npm = np.where(
        master["sales"].notna()
        & master["net_profit"].notna()
        & (master["sales"] != 0),

        (
            master["net_profit"]
            / master["sales"]
            * 100
        ),

        np.nan
    )

    master["net_profit_margin_pct"] = (
        pd.Series(
            calculated_npm,
            index=master.index
        ).round(2)
    )

# ------------------------------------------------------------
# ROE
# ------------------------------------------------------------
#
# Do not overwrite source ROE because balance-sheet
# equity data may not be present in this master merge.
#
# ------------------------------------------------------------

# ============================================================
# CAGR CALCULATIONS
# ============================================================

print("\nCalculating CAGR metrics...")

master = master.sort_values(
    ["company_id", "year"]
).reset_index(drop=True)


def calculate_cagr(group, column, years=5):
    """
    Calculate rolling CAGR using a five-year lookback.

    CAGR = (Ending / Beginning)^(1/n) - 1
    """

    values = pd.to_numeric(
        group[column],
        errors="coerce"
    )

    years_values = pd.to_numeric(
        group["year"],
        errors="coerce"
    )

    result = []

    for i in range(len(group)):

        current_year = years_values.iloc[i]

        target_year = current_year - years

        previous_indices = np.where(
            years_values.iloc[:i].values == target_year
        )[0]

        if len(previous_indices) == 0:
            result.append(np.nan)
            continue

        j = previous_indices[-1]

        start_value = values.iloc[j]
        end_value = values.iloc[i]

        if (
            pd.isna(start_value)
            or pd.isna(end_value)
            or start_value <= 0
            or end_value <= 0
        ):
            result.append(np.nan)
            continue

        cagr = (
            (end_value / start_value)
            ** (1 / years)
            - 1
        ) * 100

        result.append(cagr)

    return pd.Series(
        result,
        index=group.index
    )


# ------------------------------------------------------------
# Revenue CAGR
# ------------------------------------------------------------

if "sales" in master.columns:

    master["revenue_cagr_5yr"] = (
        master
        .groupby("company_id", group_keys=False)
        .apply(
            lambda g: calculate_cagr(
                g,
                "sales",
                5
            )
        )
        .reset_index(
            level=0,
            drop=True
        )
    )

# ------------------------------------------------------------
# PAT CAGR
# ------------------------------------------------------------

if "net_profit" in master.columns:

    master["pat_cagr_5yr"] = (
        master
        .groupby("company_id", group_keys=False)
        .apply(
            lambda g: calculate_cagr(
                g,
                "net_profit",
                5
            )
        )
        .reset_index(
            level=0,
            drop=True
        )
    )

# ------------------------------------------------------------
# EPS CAGR
# ------------------------------------------------------------

if "eps" in master.columns:

    master["eps_cagr_5yr"] = (
        master
        .groupby("company_id", group_keys=False)
        .apply(
            lambda g: calculate_cagr(
                g,
                "eps",
                5
            )
        )
        .reset_index(
            level=0,
            drop=True
        )
    )

# ------------------------------------------------------------
# FCF CAGR
# ------------------------------------------------------------

if "free_cash_flow" in master.columns:

    master["fcf_cagr_5yr"] = (
        master
        .groupby("company_id", group_keys=False)
        .apply(
            lambda g: calculate_cagr(
                g,
                "free_cash_flow",
                5
            )
        )
        .reset_index(
            level=0,
            drop=True
        )
    )

# ============================================================
# ROUND NUMERIC COLUMNS
# ============================================================

percentage_columns = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "opm_percentage",
    "tax_percentage",
    "dividend_payout",
    "dividend_yield_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "fcf_cagr_5yr"
]

for col in percentage_columns:

    if col in master.columns:

        master[col] = pd.to_numeric(
            master[col],
            errors="coerce"
        ).round(2)

# ============================================================
# FINAL COLUMN ORDER
# ============================================================

preferred_columns = [
    "company_id",
    "year",

    # Ratios
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",

    # Profit & Loss
    "sales",
    "expenses",
    "operating_profit",
    "opm_percentage",
    "other_income",
    "interest",
    "depreciation",
    "profit_before_tax",
    "tax_percentage",
    "net_profit",
    "eps",
    "dividend_payout",

    # Cash Flow
    "operating_activity",
    "investing_activity",
    "financing_activity",
    "net_cash_flow",
    "free_cash_flow",

    # Market Cap
    "market_cap_crore",
    "enterprise_value_crore",
    "pe_ratio",
    "pb_ratio",
    "ev_ebitda",
    "dividend_yield_pct",

    # CAGR
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "fcf_cagr_5yr"
]

existing_columns = [
    col
    for col in preferred_columns
    if col in master.columns
]

remaining_columns = [
    col
    for col in master.columns
    if col not in existing_columns
]

master = master[
    existing_columns + remaining_columns
]

# ============================================================
# FINAL DATA QUALITY CHECK
# ============================================================

print("\n" + "=" * 60)
print("FINAL DATA QUALITY CHECK")
print("=" * 60)

# ------------------------------------------------------------
# OPM validation
# ------------------------------------------------------------

if (
    "opm_percentage" in master.columns
    and "operating_profit_margin_pct" in master.columns
):

    # Validate that both OPM columns agree.
    opm_difference = (
        master["opm_percentage"]
        - master["operating_profit_margin_pct"]
    ).abs()

    inconsistent_opm = master[
        opm_difference > 0.01
    ]

    print(
        "OPM consistency check:"
    )

    print(
        f"Rows checked       : {len(master)}"
    )

    print(
        f"Inconsistent OPM rows: "
        f"{len(inconsistent_opm)}"
    )

    if len(inconsistent_opm) > 0:

        display_columns = [
            "company_id",
            "year",
            "sales",
            "operating_profit",
            "operating_profit_margin_pct",
            "opm_percentage"
        ]

        display_columns = [
            col
            for col in display_columns
            if col in inconsistent_opm.columns
        ]

        print("\nInconsistent rows:")
        print(
            inconsistent_opm[
                display_columns
            ]
            .head(20)
            .to_string(index=False)
        )

    else:

        print(
            "✓ All OPM values are consistent."
        )
# ------------------------------------------------------------
# Missing values
# ------------------------------------------------------------

print("\nMissing values in important columns:")

important_columns = [
    "company_id",
    "year",
    "sales",
    "operating_profit",
    "opm_percentage",
    "net_profit",
    "free_cash_flow"
]

for col in important_columns:

    if col in master.columns:

        missing = master[col].isna().sum()

        print(
            f"{col:<35} {missing}"
        )

# ------------------------------------------------------------
# Duplicate check
# ------------------------------------------------------------

duplicates = master.duplicated(
    subset=["company_id", "year"]
).sum()

print(
    f"\nDuplicate company/year rows: "
    f"{duplicates}"
)

# ============================================================
# SAVE MASTER DATASET
# ============================================================

print("\nSaving master dataset...")

master.to_csv(
    MASTER_OUTPUT,
    index=False
)

print(
    f"Saved: {MASTER_OUTPUT}"
)

# ============================================================
# PREVIEW
# ============================================================

print("\n" + "=" * 60)
print("MASTER DATASET PREVIEW")
print("=" * 60)

preview_columns = [
    "company_id",
    "year",
    "sales",
    "operating_profit",
    "operating_profit_margin_pct",
    "opm_percentage",
    "net_profit"
]

preview_columns = [
    col
    for col in preview_columns
    if col in master.columns
]

print(
    master[
        preview_columns
    ]
    .head(15)
    .to_string(index=False)
)

# ============================================================
# HDFCBANK VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("HDFCBANK OPM VALIDATION")
print("=" * 60)

hdfc = master[
    master["company_id"] == "HDFCBANK"
]

if len(hdfc) > 0:

    hdfc_columns = [
        "company_id",
        "year",
        "sales",
        "operating_profit",
        "operating_profit_margin_pct",
        "opm_percentage"
    ]

    hdfc_columns = [
        col
        for col in hdfc_columns
        if col in hdfc.columns
    ]

    print(
        hdfc[
            hdfc_columns
        ]
        .to_string(index=False)
    )

# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()

print("\n" + "=" * 60)
print("DAY 16 MASTER DATASET COMPLETED")
print("=" * 60)
print(f"Output: {MASTER_OUTPUT}")
print(f"Rows  : {len(master)}")
print(f"Cols  : {len(master.columns)}")
print("=" * 60)