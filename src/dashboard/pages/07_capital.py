
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import pandas as pd
import streamlit as st
import plotly.express as px

from utils.db import get_capital_allocation

st.set_page_config(
    page_title="Capital Allocation",
    layout="wide"
)

st.title("🌳 Capital Allocation Map")

df = get_capital_allocation()

if df.empty:
    st.warning("No data available.")
    st.stop()

# -----------------------
# Create Capital Patterns
# -----------------------

def classify(row):

    roe = row["return_on_equity_pct"] or 0
    debt = row["debt_to_equity"] or 0
    div = row["dividend_yield_pct"] or 0
    fcf = row["free_cash_flow"] or 0

    if debt < 0.5 and roe > 20:
        return "Capital Efficient"

    elif div > 2:
        return "Dividend Leaders"

    elif fcf > 0:
        return "Cash Generators"

    elif debt > 2:
        return "Highly Leveraged"

    elif roe < 10:
        return "Low Return"

    elif debt < 0.2:
        return "Debt Free"

    elif roe > 15:
        return "Growth Compounders"

    return "Balanced"

df["capital_pattern"] = df.apply(classify, axis=1)

# -----------------------
# KPIs
# -----------------------

c1, c2, c3 = st.columns(3)

c1.metric("Companies", len(df))
c2.metric("Patterns", df["capital_pattern"].nunique())
c3.metric("Sectors", df["broad_sector"].nunique())

st.divider()

# -----------------------
# Treemap
# -----------------------

fig = px.treemap(
    df,
    path=["capital_pattern", "company_name"],
    values="sales",
    color="return_on_equity_pct",
    title="Capital Allocation Treemap",
)

fig.update_layout(
    height=700
)

st.plotly_chart(
    fig,
    width="stretch"
)

st.divider()

# -----------------------
# Pattern Filter
# -----------------------

pattern = st.selectbox(
    "Capital Allocation Pattern",
    sorted(df["capital_pattern"].unique())
)

filtered = df[df["capital_pattern"] == pattern]

st.subheader(f"{pattern} Companies")

st.dataframe(
    filtered,
    width="stretch"
)

csv = filtered.to_csv(index=False).encode()

st.download_button(
    "📥 Download CSV",
    csv,
    file_name="capital_allocation.csv",
    mime="text/csv"
)

