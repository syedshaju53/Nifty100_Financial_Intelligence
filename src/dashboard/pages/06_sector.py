import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import streamlit as st
import plotly.express as px

from utils.db import (
    get_sector_list,
    get_sector_companies,
)

st.set_page_config(
    page_title="Sector Analysis",
    layout="wide"
)

st.title("🏭 Sector Analysis")

# ---------------------------------------------------
# Load Sectors
# ---------------------------------------------------

sector_df = get_sector_list()

selected_sector = st.selectbox(
    "Select Sector",
    sector_df["broad_sector"]
)

companies = get_sector_companies(selected_sector)

if companies.empty:
    st.warning("No data available.")
    st.stop()

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

total_companies = len(companies)

avg_roe = companies["return_on_equity_pct"].fillna(0).mean()

avg_pe = companies["pe_ratio"].fillna(0).mean()

largest_company = companies.iloc[0]["company_name"]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Companies",
        total_companies
    )

with c2:
    st.metric(
        "Average ROE",
        f"{avg_roe:.2f}%"
    )

with c3:
    st.metric(
        "Average P/E",
        f"{avg_pe:.2f}"
    )

with c4:
    st.metric(
        "Largest Company",
        largest_company
    )

st.divider()

# ---------------------------------------------------
# Bubble Chart
# ---------------------------------------------------

st.subheader("Sector Performance")

bubble = px.scatter(

    companies,

    x="index_weight_pct",

    y="return_on_equity_pct",

    size="pe_ratio",

    hover_name="company_name",

    color="market_cap_category",

    title=f"{selected_sector} Sector",

    labels={
        "index_weight_pct": "Index Weight %",
        "return_on_equity_pct": "ROE (%)",
        "pe_ratio": "P/E Ratio",
    },
)

bubble.update_layout(

    height=600,

    template="plotly_dark",

    legend_title="Market Cap",

)

st.plotly_chart(

    bubble,

    width="stretch",

)

st.divider()

# ---------------------------------------------------
# Top Companies
# ---------------------------------------------------

st.subheader("🏆 Top Companies in Sector")

top_companies = companies.sort_values(
    by="index_weight_pct",
    ascending=False
)

display_cols = [
    col for col in [
        "company_name",
        "company_id",
        "index_weight_pct",
        "return_on_equity_pct",
        "pe_ratio",
        "pb_ratio",
        "market_cap_category",
    ]
    if col in top_companies.columns
]

st.dataframe(
    top_companies[display_cols],
    width="stretch",
)

st.divider()

# ---------------------------------------------------
# Sector Summary
# ---------------------------------------------------

st.subheader("📊 Sector Summary")

summary = {
    "Total Companies": len(companies),
    "Average ROE (%)": round(companies["return_on_equity_pct"].fillna(0).mean(), 2),
    "Average P/E": round(companies["pe_ratio"].fillna(0).mean(), 2),
    "Average P/B": round(companies["pb_ratio"].fillna(0).mean(), 2),
    "Maximum Index Weight (%)": round(companies["index_weight_pct"].max(), 2),
    "Minimum Index Weight (%)": round(companies["index_weight_pct"].min(), 2),
}

summary_df = (
    pd.DataFrame(
        summary.items(),
        columns=["Metric", "Value"]
    )
)

st.dataframe(
    summary_df,
    width="stretch"
)

st.divider()

# ---------------------------------------------------
# ROE Ranking Chart
# ---------------------------------------------------

st.subheader("📈 ROE Ranking")

roe_df = (
    companies[
        ["company_name", "return_on_equity_pct"]
    ]
    .fillna(0)
    .sort_values(
        "return_on_equity_pct",
        ascending=False
    )
)

fig = px.bar(
    roe_df,
    x="company_name",
    y="return_on_equity_pct",
    title=f"{selected_sector} — ROE Comparison",
)

fig.update_layout(
    height=500,
    template="plotly_dark",
    xaxis_title="Company",
    yaxis_title="ROE (%)",
)

st.plotly_chart(
    fig,
    width="stretch"
)

st.divider()

# ---------------------------------------------------
# CSV Download
# ---------------------------------------------------

csv = top_companies.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Sector Data (CSV)",
    data=csv,
    file_name=f"{selected_sector.lower().replace(' ', '_')}_sector.csv",
    mime="text/csv",
)

