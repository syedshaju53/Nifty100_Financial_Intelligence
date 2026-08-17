# ============================================================
# NIFTY100 FINANCIAL INTELLIGENCE
# D-12 — VALUATION SUMMARY GENERATOR
# ============================================================

import os
import sys
import sqlite3
import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    PROJECT_ROOT,
    "db",
    "nifty100.db"
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "output"
)

OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "valuation_summary.xlsx"
)


# ============================================================
# MAKE PROJECT IMPORTABLE
# ============================================================

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


# ============================================================
# IMPORT EXISTING VALUATION ENGINE
# ============================================================

from src.analytics.valuation import (
    valuation_summary
)


# ============================================================
# VALIDATE DATABASE
# ============================================================

if not os.path.exists(DB_PATH):

    raise FileNotFoundError(
        f"Database not found:\n{DB_PATH}"
    )


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

conn = sqlite3.connect(
    DB_PATH
)


# ============================================================
# CHECK REQUIRED TABLES
# ============================================================

required_tables = {
    "companies",
    "financial_ratios",
    "stock_prices",
}

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    """,
    conn
)

available_tables = set(
    tables["name"].tolist()
)

missing_tables = (
    required_tables
    - available_tables
)

if missing_tables:

    conn.close()

    raise RuntimeError(
        "Missing required database tables: "
        + ", ".join(
            sorted(missing_tables)
        )
    )


# ============================================================
# LOAD COMPANIES
# ============================================================

companies = pd.read_sql_query(
    """
    SELECT
        id AS company_id,
        company_name,
        book_value,
        roe_percentage,
        roce_percentage
    FROM companies
    ORDER BY company_name
    """,
    conn
)


# ============================================================
# LOAD LATEST STOCK PRICE
# ============================================================

prices = pd.read_sql_query(
    """
    SELECT
        sp.company_id,
        sp.date,
        sp.close_price
    FROM stock_prices sp

    INNER JOIN (
        SELECT
            company_id,
            MAX(date) AS max_date
        FROM stock_prices
        GROUP BY company_id
    ) latest

        ON sp.company_id = latest.company_id
       AND sp.date = latest.max_date
    """,
    conn
)


# ============================================================
# LOAD LATEST FINANCIAL RATIO
# ============================================================

ratios = pd.read_sql_query(
    """
    SELECT
        fr.company_id,
        fr.year,
        fr.net_profit_margin_pct,
        fr.operating_profit_margin_pct,
        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.interest_coverage,
        fr.asset_turnover,
        fr.free_cash_flow

    FROM financial_ratios fr

    INNER JOIN (
        SELECT
            company_id,
            MAX(
                CAST(year AS INTEGER)
            ) AS max_year

        FROM financial_ratios

        WHERE company_id IS NOT NULL
          AND year IS NOT NULL

        GROUP BY company_id
    ) latest

        ON fr.company_id = latest.company_id

       AND CAST(fr.year AS INTEGER)
           = latest.max_year
    """,
    conn
)


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()


# ============================================================
# NORMALIZE COMPANY IDS
# ============================================================

for dataframe in [
    companies,
    prices,
    ratios,
]:

    dataframe["company_id"] = (

        dataframe["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()

    )


# ============================================================
# NORMALIZE YEAR
# ============================================================

if "year" in ratios.columns:

    ratios["year"] = (

        ratios["year"]
        .astype(str)
        .str.extract(
            r"(\d{4})"
        )[0]

    )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

prices = (
    prices
    .sort_values(
        [
            "company_id",
            "date",
        ]
    )
    .drop_duplicates(
        subset=[
            "company_id"
        ],
        keep="last"
    )
)

ratios = (
    ratios
    .sort_values(
        [
            "company_id",
            "year",
        ]
    )
    .drop_duplicates(
        subset=[
            "company_id"
        ],
        keep="last"
    )
)


# ============================================================
# MERGE DATA
# ============================================================

df = companies.merge(
    prices[
        [
            "company_id",
            "date",
            "close_price",
        ]
    ],
    on="company_id",
    how="left",
)

df = df.merge(
    ratios,
    on="company_id",
    how="left",
)


# ============================================================
# GENERATE VALUATION RESULTS
# ============================================================

results = []


for _, row in df.iterrows():

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    price = row.get(
        "close_price"
    )

    if pd.isna(price):

        price = None


    # --------------------------------------------------------
    # BOOK VALUE
    # --------------------------------------------------------

    book_value = row.get(
        "book_value"
    )

    if pd.isna(book_value):

        book_value = None


    # --------------------------------------------------------
    # CURRENT SOURCE DOES NOT CONTAIN EPS
    # --------------------------------------------------------

    eps = None


    # --------------------------------------------------------
    # CURRENT SOURCE DOES NOT CONTAIN GROWTH
    # --------------------------------------------------------

    earnings_growth = None


    # --------------------------------------------------------
    # CURRENT SOURCE DOES NOT CONTAIN MARKET CAP
    # --------------------------------------------------------

    market_cap = None


    # --------------------------------------------------------
    # CURRENT SOURCE DOES NOT CONTAIN DEBT/CASH/EBITDA
    # --------------------------------------------------------

    total_debt = None

    cash = None

    ebitda = None


    # --------------------------------------------------------
    # RUN EXISTING VALUATION ENGINE
    # --------------------------------------------------------

    valuation = valuation_summary(

        price=price,

        eps=eps,

        book_value_per_share=book_value,

        earnings_growth=earnings_growth,

        market_cap=market_cap,

        total_debt=total_debt,

        cash=cash,

        ebitda=ebitda,
    )


    # --------------------------------------------------------
    # STORE RESULT
    # --------------------------------------------------------

    results.append(

        {

            "company_id":
                row.get(
                    "company_id"
                ),

            "company_name":
                row.get(
                    "company_name"
                ),

            "price_date":
                row.get(
                    "date"
                ),

            "share_price":
                price,

            "book_value":
                book_value,

            "ROE (%)":
                row.get(
                    "roe_percentage"
                ),

            "ROCE (%)":
                row.get(
                    "roce_percentage"
                ),

            "latest_ratio_year":
                row.get(
                    "year"
                ),

            "net_profit_margin (%)":
                row.get(
                    "net_profit_margin_pct"
                ),

            "operating_profit_margin (%)":
                row.get(
                    "operating_profit_margin_pct"
                ),

            "return_on_equity (%)":
                row.get(
                    "return_on_equity_pct"
                ),

            "debt_to_equity":
                row.get(
                    "debt_to_equity"
                ),

            "interest_coverage":
                row.get(
                    "interest_coverage"
                ),

            "asset_turnover":
                row.get(
                    "asset_turnover"
                ),

            "free_cash_flow":
                row.get(
                    "free_cash_flow"
                ),

            # Valuation metrics
            "PE Ratio":
                valuation[
                    "pe_ratio"
                ],

            "PB Ratio":
                valuation[
                    "pb_ratio"
                ],

            "Earnings Yield (%)":
                valuation[
                    "earnings_yield"
                ],

            "PEG Ratio":
                valuation[
                    "peg_ratio"
                ],

            "Enterprise Value":
                valuation[
                    "enterprise_value"
                ],

            "EV/EBITDA":
                valuation[
                    "ev_to_ebitda"
                ],

            "Valuation Label":
                valuation[
                    "valuation_label"
                ],

            # Transparency fields
            "EPS Source":
                "Not available in database schema",

            "Market Cap Source":
                "Not available in database schema",

            "EBITDA Source":
                "Not available in database schema",

        }
    )


# ============================================================
# CREATE RESULT DATAFRAME
# ============================================================

result_df = pd.DataFrame(
    results
)


# ============================================================
# DATA QUALITY CHECKS
# ============================================================

result_df = (
    result_df
    .sort_values(
        "company_id"
    )
    .reset_index(
        drop=True
    )
)


company_count = (
    result_df[
        "company_id"
    ]
    .nunique()
)


# ============================================================
# SOURCE NOTES
# ============================================================

source_notes = pd.DataFrame(

    {

        "Field": [

            "Company information",

            "Share price",

            "Book value",

            "ROE",

            "ROCE",

            "Financial ratios",

            "EPS",

            "Earnings growth",

            "Market cap",

            "Total debt",

            "Cash",

            "EBITDA",

            "PE Ratio",

            "PB Ratio",

            "PEG Ratio",

            "EV/EBITDA",

        ],

        "Source": [

            "companies",

            "stock_prices",

            "companies.book_value",

            "companies.roe_percentage",

            "companies.roce_percentage",

            "financial_ratios",

            "Not available",

            "Not available",

            "Not available",

            "Not available",

            "Not available",

            "Not available",

            "Valuation engine",

            "Valuation engine",

            "Valuation engine",

            "Valuation engine",

        ],

        "Status": [

            "Available",

            "Available where present",

            "Available where present",

            "Available where present",

            "Available where present",

            "Available",

            "N/A",

            "N/A",

            "N/A",

            "N/A",

            "N/A",

            "N/A",

            "Calculated where inputs exist",

            "Calculated where inputs exist",

            "N/A",

            "N/A",

        ],

    }
)


# ============================================================
# SUMMARY SHEET
# ============================================================

summary = pd.DataFrame(

    {

        "Metric": [

            "Companies processed",

            "Unique companies",

            "Rows generated",

            "Companies with share price",

            "Companies with book value",

            "Companies with ROE",

            "Companies with financial ratios",

            "Output file",

        ],

        "Value": [

            len(result_df),

            company_count,

            len(result_df),

            result_df[
                "share_price"
            ].notna().sum(),

            result_df[
                "book_value"
            ].notna().sum(),

            result_df[
                "ROE (%)"
            ].notna().sum(),

            result_df[
                "latest_ratio_year"
            ].notna().sum(),

            OUTPUT_PATH,

        ],

    }
)


# ============================================================
# WRITE EXCEL
# ============================================================

with pd.ExcelWriter(

    OUTPUT_PATH,

    engine="openpyxl",

) as writer:

    result_df.to_excel(

        writer,

        sheet_name="Valuation Summary",

        index=False,

    )

    source_notes.to_excel(

        writer,

        sheet_name="Source Notes",

        index=False,

    )

    summary.to_excel(

        writer,

        sheet_name="Summary",

        index=False,

    )


# ============================================================
# FORMAT EXCEL
# ============================================================

from openpyxl import load_workbook


workbook = load_workbook(
    OUTPUT_PATH
)


for worksheet in workbook.worksheets:

    worksheet.freeze_panes = "A2"

    worksheet.auto_filter.ref = (
        worksheet.dimensions
    )

    for column in worksheet.columns:

        max_length = 0

        column_letter = (
            column[0].column_letter
        )

        for cell in column:

            value = cell.value

            if value is not None:

                max_length = max(
                    max_length,
                    len(str(value))
                )

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 2,
            35
        )


workbook.save(
    OUTPUT_PATH
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print()
print("=" * 70)
print("D-12 — VALUATION SUMMARY")
print("=" * 70)

print(
    f"Companies processed : {len(result_df)}"
)

print(
    f"Unique companies    : {company_count}"
)

print(
    f"Rows generated      : {len(result_df)}"
)

print(
    f"Output file         : {OUTPUT_PATH}"
)

print(
    f"File exists         : "
    f"{os.path.exists(OUTPUT_PATH)}"
)

if os.path.exists(OUTPUT_PATH):

    file_size = (
        os.path.getsize(
            OUTPUT_PATH
        ) / 1024
    )

    print(
        f"File size           : "
        f"{file_size:.2f} KB"
    )


# ============================================================
# D-12 ACCEPTANCE CHECK
# ============================================================

if (

    company_count == 92

    and len(result_df) == 92

    and os.path.exists(
        OUTPUT_PATH
    )

):

    print()
    print(
        "D-12 STATUS: PASS"
    )

else:

    print()
    print(
        "D-12 STATUS: CHECK REQUIRED"
    )

    if company_count != 92:

        print(
            f"Expected 92 companies, "
            f"found {company_count}"
        )
