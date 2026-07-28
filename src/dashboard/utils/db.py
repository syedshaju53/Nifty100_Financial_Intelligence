import sqlite3
import pandas as pd
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# -------------------------------
# Companies
# -------------------------------

@st.cache_data(ttl=600)
def get_companies():

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM companies",
        conn,
    )

    conn.close()

    return df


# -------------------------------
# Master Financials
# -------------------------------

@st.cache_data(ttl=600)
def get_master(year=None):

    conn = get_connection()

    if year is not None:

        df = pd.read_sql(
            """
            SELECT *
            FROM master_financials
            WHERE year=?
            """,
            conn,
            params=[year],
        )

    else:

        df = pd.read_sql(
            """
            SELECT *
            FROM master_financials
            """,
            conn,
        )

    conn.close()

    return df


# -------------------------------
# Sector
# -------------------------------

@st.cache_data(ttl=600)
def get_sectors():

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM sectors",
        conn,
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_sector_distribution():

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT
            broad_sector,
            COUNT(*) AS companies
        FROM sectors
        GROUP BY broad_sector
        ORDER BY companies DESC
        """,
        conn,
    )

    conn.close()

    return df


# -------------------------------
# Company Profile
# -------------------------------

@st.cache_data(ttl=600)
def get_company_profile(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM companies
        WHERE id=?
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_company_metrics(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM master_financials
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_company_sector(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM sectors
        WHERE company_id=?
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_pros_cons(company_id):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT *
        FROM pros_and_cons
        WHERE company_id=?
        """,
        conn,
        params=[company_id],
    )

    conn.close()

    return df


# -------------------------------
# Home Page
# -------------------------------

@st.cache_data(ttl=600)
def get_top_companies(year):

    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT
            company_id,
            ROUND(composite_quality_score,2) AS composite_quality_score
        FROM master_financials
        WHERE year=?
        ORDER BY composite_quality_score DESC
        LIMIT 5
        """,
        conn,
        params=[year],
    )

    conn.close()

    return df

@st.cache_data(ttl=600)
def search_companies():
    conn = get_connection()

    query = """
    SELECT
        c.id,
        c.company_name
    FROM companies c
    ORDER BY company_name
    """

    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def get_company_full_profile(company_id):

    conn = get_connection()

    query = """
    SELECT
        c.*,
        s.broad_sector,
        s.sub_sector
    FROM companies c
    LEFT JOIN sectors s
    ON c.id=s.company_id
    WHERE c.id=?
    """

    return pd.read_sql(query, conn, params=[company_id])


@st.cache_data(ttl=600)
def get_company_history(company_id):

    conn = get_connection()

    query = """
    SELECT *
    FROM master_financials
    WHERE company_id=?
    ORDER BY year
    """

    return pd.read_sql(query, conn, params=[company_id])

@st.cache_data(ttl=600)
def get_screener_data(year=2024):
    conn = get_connection()

    query = """
    SELECT
        m.company_id,
        c.company_name,
        s.broad_sector,

        m.composite_quality_score,
        m.return_on_equity_pct,
        m.debt_to_equity,
        m.free_cash_flow,
        m.revenue_cagr_5yr,
        m.pat_cagr_5yr,
        m.opm_percentage,
        m.pe_ratio,
        m.pb_ratio,
        m.dividend_yield_pct,
        m.interest_coverage

    FROM master_financials m

    LEFT JOIN companies c
        ON m.company_id = c.id

    LEFT JOIN sectors s
        ON m.company_id = s.company_id

    WHERE m.year = ?

    ORDER BY m.composite_quality_score DESC
    """

    return pd.read_sql(query, conn, params=[year])

@st.cache_data(ttl=600)
def get_peer_groups():
    conn = get_connection()

    query = """
    SELECT DISTINCT peer_group_name
    FROM peer_groups
    ORDER BY peer_group_name
    """

    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def get_peer_companies(group_name):
    conn = get_connection()

    query = """
    SELECT
        p.company_id,
        c.company_name,
        p.is_benchmark
    FROM peer_groups p
    LEFT JOIN companies c
        ON p.company_id = c.id
    WHERE p.peer_group_name=?
    ORDER BY p.is_benchmark DESC,c.company_name
    """

    return pd.read_sql(query, conn, params=[group_name])


@st.cache_data(ttl=600)
def get_peer_metrics(company_id):

    conn = get_connection()

    query = """
    SELECT *
    FROM master_financials
    WHERE company_id=?
    ORDER BY year DESC
    LIMIT 1
    """

    return pd.read_sql(query, conn, params=[company_id])

@st.cache_data(ttl=600)
def get_peer_average(group_name):

    conn = get_connection()

    query = """
    SELECT
        AVG(m.return_on_equity_pct) AS roe,
        AVG(m.opm_percentage) AS opm,
        AVG(m.revenue_cagr_5yr) AS revenue_cagr,
        AVG(m.pat_cagr_5yr) AS pat_cagr,
        AVG(m.free_cash_flow) AS fcf,
        AVG(m.dividend_yield_pct) AS dividend
    FROM master_financials m
    JOIN peer_groups p
        ON m.company_id = p.company_id
    WHERE p.peer_group_name = ?
      AND m.year = 2024
    """

    return pd.read_sql(query, conn, params=[group_name])

@st.cache_data(ttl=600)
def get_company_history(company_id):
    conn = get_connection()

    query = """
    SELECT *
    FROM master_financials
    WHERE company_id=?
    ORDER BY year
    """

    df = pd.read_sql(query, conn, params=[company_id])

    return df


@st.cache_data(ttl=600)
def get_sector_list():
    conn = get_connection()
    query = """
    SELECT DISTINCT broad_sector
    FROM sectors
    ORDER BY broad_sector
    """
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def get_sector_companies(sector):
    conn = get_connection()

    query = """
    SELECT
        s.company_id,
        c.company_name,
        s.index_weight_pct,
        s.market_cap_category,
        m.return_on_equity_pct,
        m.pe_ratio,
        m.pb_ratio
    FROM sectors s
    LEFT JOIN companies c
        ON s.company_id = c.id
    LEFT JOIN master_financials m
        ON s.company_id = m.company_id
    WHERE s.broad_sector = ?
      AND m.year = (
            SELECT MAX(year)
            FROM master_financials
            WHERE company_id = s.company_id
      )
    ORDER BY s.index_weight_pct DESC
    """

    return pd.read_sql(query, conn, params=[sector])

@st.cache_data(ttl=600)
def get_capital_allocation():

    conn = get_connection()

    query = """
    SELECT
        m.company_id,
        c.company_name,
        s.broad_sector,
        m.return_on_equity_pct,
        m.dividend_yield_pct,
        m.debt_to_equity,
        m.free_cash_flow,
        m.sales
    FROM master_financials m
    LEFT JOIN companies c
        ON m.company_id = c.id
    LEFT JOIN sectors s
        ON m.company_id = s.company_id
    WHERE m.year = (
        SELECT MAX(year)
        FROM master_financials x
        WHERE x.company_id = m.company_id
    )
    """

    return pd.read_sql(query, conn)

@st.cache_data(ttl=600)
def get_company_reports(company_id):
    conn = get_connection()

    query = """
    SELECT
        year,
        annual_report
    FROM documents
    WHERE company_id=?
    ORDER BY year DESC
    """

    return pd.read_sql(query, conn, params=[company_id])

# ==========================================
# DAY 26 - VALUATION
# ==========================================

@st.cache_data(ttl=600)
def get_valuation_data(company):

    conn = get_connection()

    query = """
    SELECT
        m.company_id,
        m.year,
        m.pe_ratio,
        m.pb_ratio,
        m.market_cap_crore,
        m.dividend_yield_pct,
        m.composite_quality_score,
        s.broad_sector
    FROM master_financials m
    LEFT JOIN sectors s
        ON m.company_id=s.company_id
    WHERE m.company_id=?
    ORDER BY m.year DESC
    LIMIT 1
    """

    return pd.read_sql(
        query,
        conn,
        params=[company]
    )

@st.cache_data(ttl=600)
def get_sector_valuation(sector):

    conn = get_connection()

    query = """
    SELECT

        AVG(m.pe_ratio) AS sector_pe,

        AVG(m.pb_ratio) AS sector_pb,

        AVG(m.dividend_yield_pct) AS sector_dividend

    FROM master_financials m

    JOIN sectors s

        ON m.company_id=s.company_id

    WHERE s.broad_sector=?
    """

    return pd.read_sql(
        query,
        conn,
        params=[sector]
    )