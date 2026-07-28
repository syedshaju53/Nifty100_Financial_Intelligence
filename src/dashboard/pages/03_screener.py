import streamlit as st
import pandas as pd

from utils.db import get_screener_data

st.title("🔍 Stock Screener")

# ---------------------------------------------------
# YEAR
# ---------------------------------------------------

year = st.sidebar.selectbox(
    "Financial Year",
    [2024, 2023, 2022, 2021, 2020, 2019],
    key="screener_year"
)

df = get_screener_data(year)

numeric_cols = [
    "return_on_equity_pct",
    "debt_to_equity",
    "free_cash_flow",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "opm_percentage",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
    "interest_coverage",
    "composite_quality_score",
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------------------------------------------
# FILTERS
# ---------------------------------------------------

st.sidebar.header("Filters")

roe = st.sidebar.slider("Minimum ROE", 0.0, 50.0, 10.0)
de = st.sidebar.slider("Maximum Debt/Equity", 0.0, 5.0, 2.0)
fcf = st.sidebar.slider(
    "Minimum Free Cash Flow",
    float(df["free_cash_flow"].fillna(0).min()),
    float(df["free_cash_flow"].fillna(0).max()),
    0.0,
)
rev = st.sidebar.slider("Minimum Revenue CAGR", 0.0, 50.0, 5.0)
pat = st.sidebar.slider("Minimum PAT CAGR", 0.0, 50.0, 5.0)
opm = st.sidebar.slider("Minimum OPM", 0.0, 70.0, 10.0)
pe = st.sidebar.slider("Maximum P/E", 0.0, 100.0, 40.0)
pb = st.sidebar.slider("Maximum P/B", 0.0, 20.0, 10.0)
dividend = st.sidebar.slider("Minimum Dividend Yield", 0.0, 15.0, 0.0)
icr = st.sidebar.slider("Minimum Interest Coverage", 0.0, 100.0, 2.0)

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------

filtered = df[
    (df["return_on_equity_pct"].fillna(0) >= roe)
    & (df["debt_to_equity"].fillna(999) <= de)
    & (df["free_cash_flow"].fillna(-999999) >= fcf)
    & (df["revenue_cagr_5yr"].fillna(0) >= rev)
    & (df["pat_cagr_5yr"].fillna(0) >= pat)
    & (df["opm_percentage"].fillna(0) >= opm)
    & (df["pe_ratio"].fillna(9999) <= pe)
    & (df["pb_ratio"].fillna(9999) <= pb)
    & (df["dividend_yield_pct"].fillna(0) >= dividend)
    & (df["interest_coverage"].fillna(0) >= icr)
]

filtered = filtered.sort_values(
    "composite_quality_score",
    ascending=False
)

# ---------------------------------------------------
# RESULT COUNT
# ---------------------------------------------------

st.success(f"✅ {len(filtered)} Companies Match Your Filters")

# ---------------------------------------------------
# TABLE
# ---------------------------------------------------

display = filtered[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "composite_quality_score",
        "return_on_equity_pct",
        "pe_ratio",
        "pb_ratio",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "dividend_yield_pct",
        "free_cash_flow",
    ]
]

st.dataframe(
    display,
    width="stretch",
    height=500,
)

# ---------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------

csv = display.to_csv(index=False).encode("utf-8")

st.download_button(
    " Download CSV",
    csv,
    "stock_screener.csv",
    "text/csv",
)