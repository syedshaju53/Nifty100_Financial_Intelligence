import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import streamlit as st

from utils.db import (
    get_companies,
    get_company_reports,
)

st.set_page_config(
    page_title="Annual Reports",
    layout="wide"
)

st.title("📄 Annual Reports")

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    sorted(companies["id"].unique()),
    key="report_company"
)

reports = get_company_reports(selected_company)

if reports.empty:
    st.warning("No annual reports available.")
    st.stop()

st.subheader(f"{selected_company} Annual Reports")

for _, row in reports.iterrows():

    year = row["year"]
    url = row["annual_report"]

    col1, col2 = st.columns([1, 4])

    with col1:
        st.write(f"**{year}**")

    with col2:
        if url and str(url).startswith("http"):
            st.link_button(
                "📥 Open Annual Report",
                url,
               width="stretch"
            )
        else:
            st.error("Report unavailable")

st.divider()

st.download_button(
    "⬇ Download Report List (CSV)",
    reports.to_csv(index=False).encode("utf-8"),
    file_name=f"{selected_company.lower()}_reports.csv",
    mime="text/csv",
)

