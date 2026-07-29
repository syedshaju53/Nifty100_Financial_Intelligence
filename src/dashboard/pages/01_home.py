import streamlit as st
import plotly.express as px

from utils.db import (
    get_master,
    get_sector_distribution,
    get_top_companies,
)

# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------

st.title("🏠 Nifty100 Financial Analytics Dashboard")

st.markdown("---")

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

year = st.sidebar.selectbox(
    "Select Year",
    [2024, 2023, 2022, 2021, 2020, 2019],
    index=0,
    key="home_year",
)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

master = get_master(year)

if master.empty:
    st.warning("No data available.")
    st.stop()

# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------

avg_roe = round(master["return_on_equity_pct"].mean(), 2)

median_pe = round(master["pe_ratio"].median(), 2)

median_de = round(master["debt_to_equity"].median(), 2)

companies = master["company_id"].nunique()

avg_cagr = round(master["revenue_cagr_5yr"].mean(), 2)

debt_free = (master["debt_to_equity"] == 0).sum()

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Average ROE", f"{avg_roe}%")
c2.metric("Median P/E", median_pe)
c3.metric("Median D/E", median_de)
c4.metric("Companies", companies)
c5.metric("Revenue CAGR", f"{avg_cagr}%")
c6.metric("Debt Free", debt_free)

st.markdown("---")

# ---------------------------------------------------------
# SECOND ROW
# ---------------------------------------------------------

left, right = st.columns([2, 1])

# ---------------------------------------------------------
# DONUT CHART
# ---------------------------------------------------------

with left:

    st.subheader("Sector Distribution")

    sector_df = get_sector_distribution()

    fig = px.pie(
        sector_df,
        names="broad_sector",
        values="companies",
        hole=0.45,
    )

    fig.update_layout(height=450)

    st.plotly_chart(
        fig,
        width="stretch",
    )

# ---------------------------------------------------------
# TOP COMPANIES
# ---------------------------------------------------------

with right:

    st.subheader("Top 5 Companies")

    top = get_top_companies(year)

    st.dataframe(
        top,
        width="stretch",
        hide_index=True,
    )

st.markdown("---")

# ---------------------------------------------------------
# DATA PREVIEW
# ---------------------------------------------------------

st.subheader("Financial Dataset Preview")

st.dataframe(
    master.head(20),
    width="stretch",
    hide_index=True,
)

