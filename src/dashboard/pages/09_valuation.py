import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.db import (
    get_companies,
    get_valuation_data,
    get_sector_valuation,
)

st.set_page_config(
    page_title="Valuation Dashboard",
    layout="wide",
)

st.title("💰 Stock Valuation Dashboard")

# -------------------------------------------------
# Company Selection
# -------------------------------------------------

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    sorted(companies["id"].unique()),
)

valuation_df = get_valuation_data(selected_company)

if valuation_df.empty:
    st.warning("No valuation data available.")
    st.stop()

valuation = valuation_df.iloc[0]

sector = valuation["broad_sector"]

sector_avg = get_sector_valuation(sector).iloc[0]

# ---------------------------------------
# Investment Score
# ---------------------------------------

score = 0

# P/E
if pd.notna(valuation["pe_ratio"]):
    if valuation["pe_ratio"] < 20:
        score += 25
    elif valuation["pe_ratio"] < 35:
        score += 18
    else:
        score += 10

# P/B
if pd.notna(valuation["pb_ratio"]):
    if valuation["pb_ratio"] < 3:
        score += 25
    elif valuation["pb_ratio"] < 6:
        score += 18
    else:
        score += 10

# Dividend Yield
if pd.notna(valuation["dividend_yield_pct"]):
    if valuation["dividend_yield_pct"] > 2:
        score += 20
    elif valuation["dividend_yield_pct"] > 1:
        score += 15
    else:
        score += 10

# Quality Score
quality = valuation["composite_quality_score"]

if pd.notna(quality):
    score += quality * 0.3

score = min(round(score, 1), 100)

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------

st.subheader("Key Valuation Metrics")

c1, c2, c3, c4 = st.columns(4)

pe_delta = 0
pb_delta = 0

if pd.notna(valuation["pe_ratio"]) and pd.notna(sector_avg["sector_pe"]):
    pe_delta = valuation["pe_ratio"] - sector_avg["sector_pe"]

if pd.notna(valuation["pb_ratio"]) and pd.notna(sector_avg["sector_pb"]):
    pb_delta = valuation["pb_ratio"] - sector_avg["sector_pb"]

with c1:
    st.metric(
        "P/E Ratio",
        f"{valuation['pe_ratio']:.2f}"
        if pd.notna(valuation["pe_ratio"]) else "-",
        f"{pe_delta:.2f} vs Sector"
    )

with c2:
    st.metric(
        "P/B Ratio",
        f"{valuation['pb_ratio']:.2f}"
        if pd.notna(valuation["pb_ratio"]) else "-",
        f"{pb_delta:.2f} vs Sector"
    )

with c3:
    st.metric(
        "Dividend Yield",
        f"{valuation['dividend_yield_pct']:.2f}%"
        if pd.notna(valuation["dividend_yield_pct"]) else "-"
    )

with c4:
    st.metric(
        "Market Cap",
        f"₹ {valuation['market_cap_crore']:,.0f} Cr"
        if pd.notna(valuation["market_cap_crore"]) else "-"
    )

st.divider()

st.subheader("Investment Score")

st.progress(score / 100)

st.metric(
    "Overall Score",
    f"{score}/100"
)

# -------------------------------------------------
# QUALITY SCORE
# -------------------------------------------------

st.subheader("Composite Quality Score")

quality = valuation["composite_quality_score"]

if pd.isna(quality):
    quality = 0

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=quality,
        title={"text": "Quality Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "green"},
            "steps": [
                {"range": [0, 40], "color": "#5e2129"},
                {"range": [40, 70], "color": "#8c6d1f"},
                {"range": [70, 100], "color": "#1d5f2d"},
            ],
        },
    )
)

fig.update_layout(height=350)

st.plotly_chart(
    fig,
   width="stretch",
)

st.divider()

if score >= 80:
    st.success("★★★★★ Strong Buy")

elif score >= 65:
    st.info("★★★★ Buy")

elif score >= 50:
    st.warning("★★★ Hold")

else:
    st.error("★★ Sell")
# -------------------------------------------------
# PE COMPARISON
# -------------------------------------------------

st.subheader("P/E Comparison")

pe_df = pd.DataFrame({
    "Type": ["Company", "Sector Average"],
    "Value": [
        valuation["pe_ratio"],
        sector_avg["sector_pe"],
    ],
})

fig = px.bar(
    pe_df,
    x="Type",
    y="Value",
    text="Value",
    color="Type",
)

fig.update_layout(
    template="plotly_dark",
    height=420,
)

st.plotly_chart(
    fig,
    width="stretch",
)

st.divider()

# -------------------------------------------------
# PB COMPARISON
# -------------------------------------------------

st.subheader("P/B Comparison")

pb_df = pd.DataFrame({
    "Type": ["Company", "Sector Average"],
    "Value": [
        valuation["pb_ratio"],
        sector_avg["sector_pb"],
    ],
})

fig = px.bar(
    pb_df,
    x="Type",
    y="Value",
    text="Value",
    color="Type",
)

fig.update_layout(
    template="plotly_dark",
    height=420,
)

st.plotly_chart(
    fig,
    width="stretch",
)

st.divider()

# -------------------------------------------------
# VALUATION STATUS
# -------------------------------------------------

st.subheader("Valuation Status")

status = "Fairly Valued"

if (
    pd.notna(valuation["pe_ratio"])
    and pd.notna(sector_avg["sector_pe"])
):
    if valuation["pe_ratio"] < sector_avg["sector_pe"] * 0.90:
        status = "🟢 Undervalued"
    elif valuation["pe_ratio"] > sector_avg["sector_pe"] * 1.10:
        status = "🔴 Overvalued"
    else:
        status = "🟡 Fairly Valued"

st.success(status)

st.divider()

# -------------------------------------------------
# INVESTMENT SUMMARY
# -------------------------------------------------

st.subheader("Investment Summary")

summary = f"""
### {selected_company}

**Sector:** {sector}

• P/E Ratio: **{valuation['pe_ratio']:.2f}**

• Sector Average P/E: **{sector_avg['sector_pe']:.2f}**

• P/B Ratio: **{valuation['pb_ratio']:.2f}**

• Sector Average P/B: **{sector_avg['sector_pb']:.2f}**

• Dividend Yield: **{valuation['dividend_yield_pct']:.2f}%**

• Market Cap: **₹ {valuation['market_cap_crore']:,.0f} Cr**

• Composite Quality Score: **{quality:.2f}/100**

### Overall Opinion

{selected_company} is currently **{status.replace('🟢','').replace('🟡','').replace('🔴','').strip()}** based on sector valuation.

Always combine valuation with revenue growth, profitability, cash flow, and qualitative analysis before making investment decisions.
"""

st.markdown(summary)

st.divider()

# -------------------------------------------------
# SECTOR COMPARISON TABLE
# -------------------------------------------------

st.subheader("Company vs Sector")

comparison_table = pd.DataFrame({
    "Metric": [
        "P/E",
        "P/B",
        "Dividend Yield",
    ],
    "Company": [
        valuation["pe_ratio"],
        valuation["pb_ratio"],
        valuation["dividend_yield_pct"],
    ],
    "Sector Average": [
        sector_avg["sector_pe"],
        sector_avg["sector_pb"],
        sector_avg["sector_dividend"],
    ],
})

comparison_table = comparison_table.round(2)

st.dataframe(
    comparison_table,
    width="stretch",
)

st.divider()

# -------------------------------------------------
# DOWNLOAD REPORT
# -------------------------------------------------

download_df = pd.DataFrame([valuation])

st.download_button(
    label="📥 Download Valuation Report",
    data=download_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{selected_company}_valuation_report.csv",
    mime="text/csv",
)

st.divider()

# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.caption(
    "Nifty100 Financial Intelligence • Sprint 4 • Day 26 • Valuation Dashboard"
)