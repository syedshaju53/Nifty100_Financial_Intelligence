import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import streamlit as st
import plotly.graph_objects as go

from utils.db import (
    get_companies,
    get_company_history
)

st.set_page_config(page_title="Trend Analysis", layout="wide")

st.title("📈 Trend Analysis")

# -----------------------------
# Load Companies
# -----------------------------

companies = get_companies()

company = st.selectbox(
    "Select Company",
    sorted(companies["id"].unique()),
    key="trend_company"
)

history = get_company_history(company)

if history.empty:
    st.warning("No financial data available.")
    st.stop()

history = history.sort_values("year")

# -----------------------------
# KPI Cards
# -----------------------------

latest = history.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Revenue",
        f"{latest['sales']:,.0f}"
        if "sales" in latest else "-"
    )

with col2:
    st.metric(
        "Net Profit",
        f"{latest['net_profit']:,.0f}"
        if "net_profit" in latest else "-"
    )

with col3:
    st.metric(
        "ROE",
        f"{latest['return_on_equity_pct']:.2f}%"
        if "return_on_equity_pct" in latest else "-"
    )

with col4:
    st.metric(
        "EPS",
        f"{latest['eps']:.2f}"
        if "eps" in latest else "-"
    )

st.divider()

# -----------------------------
# Metric Mapping
# -----------------------------

metric_labels = {
    "sales": "Sales",
    "operating_profit": "Operating Profit",
    "net_profit": "Net Profit",
    "eps": "EPS",
    "return_on_equity_pct": "ROE (%)",
    "debt_to_equity": "Debt / Equity",
    "free_cash_flow": "Free Cash Flow",
}

available_metrics = [
    metric
    for metric in metric_labels
    if metric in history.columns
]

selected_metrics = st.multiselect(
    "Choose up to 3 Metrics",
    available_metrics,
    default=["sales"],
    max_selections=3,
)

if len(selected_metrics) == 0:
    st.info("Please select at least one metric.")
    st.stop()

# -----------------------------
# Plotly Chart
# -----------------------------

fig = go.Figure()

for metric in selected_metrics:

    fig.add_trace(
        go.Scatter(
            x=history["year"],
            y=history[metric],
            mode="lines+markers",
            name=metric_labels[metric],
        )
    )

    previous = None

    for _, row in history.iterrows():

        value = row[metric]

        if previous is not None:

            try:
                growth = ((value - previous) / previous) * 100

                fig.add_annotation(
                    x=row["year"],
                    y=value,
                    text=f"{growth:.1f}%",
                    showarrow=False,
                    font=dict(size=9),
                )

            except Exception:
                pass

        previous = value

fig.update_layout(

    title=f"{company} — 10 Year Financial Trend",

    xaxis_title="Year",

    yaxis_title="Financial Metric",

    hovermode="x unified",

    template="plotly_dark",

    height=550,
)

st.plotly_chart(
    fig,
    width="stretch",
)

st.divider()

# -----------------------------
# Financial Table
# -----------------------------

st.subheader("Financial Summary")

table_columns = [
    column
    for column in [
        "year",
        "sales",
        "operating_profit",
        "net_profit",
        "eps",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow",
    ]
    if column in history.columns
]

st.dataframe(
    history[table_columns],
    width="stretch",
)

