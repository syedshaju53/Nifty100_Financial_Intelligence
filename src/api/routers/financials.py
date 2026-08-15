import pandas as pd
from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/api/v1/financials",
    tags=["Financials"]
)

MASTER_FILE = "output/master_financials.csv"


# --------------------------------------------------
# LOAD MASTER DATASET
# --------------------------------------------------

def load_master_data():
    try:
        df = pd.read_csv(MASTER_FILE)

        if "company_id" not in df.columns:
            raise ValueError("company_id column missing")

        if "year" not in df.columns:
            raise ValueError("year column missing")

        return df

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load master financial dataset: {str(e)}"
        )


# --------------------------------------------------
# CLEAN DATA FOR JSON
# --------------------------------------------------

def clean_for_json(data):
    """
    Convert pandas NaN / infinity values into JSON-safe None.
    """

    data = data.replace([float("inf"), float("-inf")], pd.NA)

    data = data.astype(object).where(pd.notna(data), None)

    return data


# --------------------------------------------------
# GET ALL FINANCIAL HISTORY
# --------------------------------------------------

@router.get("/{company_id}")
def get_financial_history(company_id: str):

    df = load_master_data()

    company_id = company_id.upper()

    data = df[
        df["company_id"].astype(str).str.upper() == company_id
    ].copy()

    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No financial data found for {company_id}"
        )

    data = data.sort_values("year")

    data = clean_for_json(data)

    return {
        "status": "success",
        "company_id": company_id,
        "count": len(data),
        "data": data.to_dict(orient="records")
    }


# --------------------------------------------------
# GET LATEST FINANCIAL DATA
# --------------------------------------------------

@router.get("/{company_id}/latest")
def get_latest_financials(company_id: str):

    df = load_master_data()

    company_id = company_id.upper()

    data = df[
        df["company_id"].astype(str).str.upper() == company_id
    ].copy()

    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No financial data found for {company_id}"
        )

    latest_year = data["year"].max()

    latest = data[data["year"] == latest_year].copy()

    latest = clean_for_json(latest)

    record = latest.iloc[0].to_dict()

    return {
        "status": "success",
        "company_id": company_id,
        "year": int(latest_year),
        "data": record
    }


# --------------------------------------------------
# GET CAGR METRICS
# --------------------------------------------------

@router.get("/{company_id}/cagr")
def get_cagr(company_id: str):

    df = load_master_data()

    company_id = company_id.upper()

    data = df[
        df["company_id"].astype(str).str.upper() == company_id
    ].copy()

    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No financial data found for {company_id}"
        )

    latest = data.sort_values("year").iloc[-1]

    metrics = {
        "revenue_cagr_5yr": latest.get("revenue_cagr_5yr"),
        "pat_cagr_5yr": latest.get("pat_cagr_5yr"),
        "eps_cagr_5yr": latest.get("eps_cagr_5yr"),
        "fcf_cagr_5yr": latest.get("fcf_cagr_5yr"),
    }

    metrics = {
        key: None if pd.isna(value) else float(value)
        for key, value in metrics.items()
    }

    return {
        "status": "success",
        "company_id": company_id,
        "year": int(latest["year"]),
        "cagr": metrics
    }


# --------------------------------------------------
# GET VALUATION METRICS
# --------------------------------------------------

@router.get("/{company_id}/valuation")
def get_valuation(company_id: str):

    df = load_master_data()

    company_id = company_id.upper()

    data = df[
        df["company_id"].astype(str).str.upper() == company_id
    ].copy()

    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No financial data found for {company_id}"
        )

    latest = data.sort_values("year").iloc[-1]

    metrics = {
        "market_cap_crore": latest.get("market_cap_crore"),
        "enterprise_value_crore": latest.get("enterprise_value_crore"),
        "pe_ratio": latest.get("pe_ratio"),
        "pb_ratio": latest.get("pb_ratio"),
        "ev_ebitda": latest.get("ev_ebitda"),
        "dividend_yield_pct": latest.get("dividend_yield_pct"),
    }

    metrics = {
        key: None if pd.isna(value) else float(value)
        for key, value in metrics.items()
    }

    return {
        "status": "success",
        "company_id": company_id,
        "year": int(latest["year"]),
        "valuation": metrics
    }