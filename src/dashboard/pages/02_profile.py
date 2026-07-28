import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.db import get_pros_cons

from utils.db import (
    search_companies,
    get_company_full_profile,
    get_company_history,
)

st.title("🏢 Company Profile")

st.markdown("---")

# ---------------------------------------------------
# LOAD COMPANY LIST
# ---------------------------------------------------

companies = search_companies()

companies["display"] = (
    companies["company_name"]
    + " ("
    + companies["id"]
    + ")"
)

selected = st.selectbox(
    "Search Company",
    companies["display"],
    key="profile_company"
)

company_id = selected.split("(")[-1].replace(")", "")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

profile = get_company_full_profile(company_id)

history = get_company_history(company_id)

if profile.empty:

    st.error("Ticker not found.")

    st.stop()

profile = profile.iloc[0]

st.markdown("---")

# ---------------------------------------------------
# COMPANY CARD
# ---------------------------------------------------

col1, col2 = st.columns([3,2])

with col1:

    st.subheader(profile["company_name"])

    st.write("**Ticker:**", profile["id"])

    st.write("**Sector:**", profile["broad_sector"])

    st.write("**Sub Sector:**", profile["sub_sector"])

    st.write("**Website:**", profile["website"])

with col2:

    st.metric("Face Value", profile["face_value"])

    st.metric("Book Value", round(profile["book_value"],2))

st.markdown("---")

# ---------------------------------------------------
# ABOUT COMPANY
# ---------------------------------------------------

st.subheader("About Company")

about = profile["about_company"]

if pd.isna(about):

    st.info("No description available.")

else:

    st.write(about)

st.markdown("---")

# ---------------------------------------------------
# LATEST YEAR
# ---------------------------------------------------

latest = history.sort_values("year").iloc[-1]

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric(
    "ROE",
    f"{latest['return_on_equity_pct']:.2f}%"
)

c2.metric(
    "ROCE",
    f"{profile['roce_percentage']:.2f}%"
)

c3.metric(
    "Net Margin",
    f"{latest['net_profit_margin_pct']:.2f}%"
)

c4.metric(
    "Debt/Equity",
    round(latest["debt_to_equity"],2)
)

c5.metric(
    "Revenue CAGR",
    f"{latest['revenue_cagr_5yr']:.2f}%"
)

c6.metric(
    "Free Cash Flow",
    f"{latest['free_cash_flow']:.2f}"
)

st.markdown("---")




st.subheader("Revenue & Net Profit (10 Years)")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=history["year"],
        y=history["sales"],
        name="Revenue"
    )
)

fig.add_trace(
    go.Bar(
        x=history["year"],
        y=history["net_profit"],
        name="Net Profit"
    )
)

fig.update_layout(
    barmode="group",
    height=450,
    xaxis_title="Year",
    yaxis_title="₹ Crore"
)

st.plotly_chart(fig, width="stretch")

st.divider()

st.subheader("ROE & ROCE Trend")

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=history["year"],
        y=history["return_on_equity_pct"],
        mode="lines+markers",
        name="ROE"
    )
)

fig2.add_trace(
    go.Scatter(
        x=history["year"],
        y=[profile["roce_percentage"]] * len(history),
        mode="lines",
        name="ROCE"
    )
)

fig2.update_layout(
    height=450,
    xaxis_title="Year",
    yaxis_title="Percentage"
)

st.plotly_chart(fig2, width="stretch")

st.divider()


# ---------------- Strengths & Weaknesses ----------------

pros_cons = get_pros_cons(company_id)

st.subheader("Strengths & Weaknesses")

col1, col2 = st.columns(2)

with col1:
    st.success("Pros")

    if not pros_cons.empty:

        pros = pros_cons["pros"].dropna()
        pros = pros[pros != "nan"]

        if not pros.empty:
            for p in pros:
                st.markdown(f"✅ {p}")
        else:
            st.info("No strengths available.")

    else:
        st.info("No strengths available.")

with col2:
    st.error("Cons")

    if not pros_cons.empty:

        cons = pros_cons["cons"].dropna()
        cons = cons[cons != "nan"]

        if not cons.empty:
            for c in cons:
                st.markdown(f"❌ {c}")
        else:
            st.info("No weaknesses available.")

    else:
        st.info("No weaknesses available.")