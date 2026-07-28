import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import (
    get_peer_groups,
    get_peer_companies,
    get_peer_metrics,
    get_peer_average,
)

st.title("👥 Peer Comparison")

# -----------------------------
# Peer Group
# -----------------------------

groups = get_peer_groups()

selected_group = st.selectbox(
    "Peer Group",
    groups["peer_group_name"],
    key="peer_group"
)

companies = get_peer_companies(selected_group)

selected_company = st.selectbox(
    "Company",
    companies["company_id"],
    key="peer_company"
)

metrics = get_peer_metrics(selected_company)

if metrics.empty:
    st.warning("No financial data available.")
    st.stop()

metrics = metrics.iloc[0]

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "ROE",
    f"{metrics['return_on_equity_pct']:.2f}%"
)

c2.metric(
    "P/E",
    f"{metrics['pe_ratio']:.2f}"
)

c3.metric(
    "Debt/Equity",
    f"{metrics['debt_to_equity']:.2f}"
)

c4.metric(
    "Dividend",
    f"{metrics['dividend_yield_pct']:.2f}%"
)

peer_avg = get_peer_average(selected_group).iloc[0]

categories = [
    "ROE",
    "OPM",
    "Revenue CAGR",
    "PAT CAGR",
    "FCF",
    "Dividend",
]

company_values = [

    metrics["return_on_equity_pct"],

    metrics["opm_percentage"],

    metrics["revenue_cagr_5yr"],

    metrics["pat_cagr_5yr"],

    metrics["free_cash_flow"]/100,

    metrics["dividend_yield_pct"],

]

peer_values = [

    peer_avg["roe"],

    peer_avg["opm"],

    peer_avg["revenue_cagr"],

    peer_avg["pat_cagr"],

    peer_avg["fcf"]/100,

    peer_avg["dividend"],

]

fig = go.Figure()

fig.add_trace(

    go.Scatterpolar(

        r=company_values,

        theta=categories,

        fill="toself",

        name=selected_company,

    )

)

fig.add_trace(

    go.Scatterpolar(

        r=peer_values,

        theta=categories,

        fill="toself",

        name="Peer Average",

    )

)

fig.update_layout(

    polar=dict(

        radialaxis=dict(visible=True)

    ),

    height=650

)

st.plotly_chart(fig, width="stretch")

# ----------------------------- 
# KPI Comparison Table
# -----------------------------

comparison = pd.DataFrame({

    "Metric":[

        "ROE",

        "OPM",

        "Revenue CAGR",

        "PAT CAGR",

        "Dividend Yield",

    ],

    "Selected Company":[

        round(metrics["return_on_equity_pct"],2),

        round(metrics["opm_percentage"],2),

        round(metrics["revenue_cagr_5yr"],2),

        round(metrics["pat_cagr_5yr"],2),

        round(metrics["dividend_yield_pct"],2),

    ],

    "Peer Average":[

        round(peer_avg["roe"],2),

        round(peer_avg["opm"],2),

        round(peer_avg["revenue_cagr"],2),

        round(peer_avg["pat_cagr"],2),

        round(peer_avg["dividend"],2),

    ]

})

st.subheader("Company vs Peer Average")

st.dataframe(
    comparison,
    width="stretch",
)

st.subheader("Peer Companies")

# Highlight Benchmark Company

def highlight(row):

    if str(row["is_benchmark"])=="1":

        return ["background-color:#d4edda"]*len(row)

    return [""]*len(row)

st.subheader("Peer Companies")

st.dataframe(

    companies.style.apply(highlight,axis=1),

    width="stretch",

)

benchmark = companies[companies["is_benchmark"]=="1"]

if not benchmark.empty:

    st.success(

        f"Benchmark Company : {benchmark.iloc[0]['company_id']}"

    )