from fastapi import APIRouter, HTTPException

from src.api.database import get_connection

router = APIRouter(
    prefix="/api/v1/market-cap",
    tags=["Valuation"],
)


@router.get("/{company_id}")
def get_company_valuation(company_id: str):
    """Return historical valuation metrics for a company."""

    conn = get_connection()

    try:
        company = conn.execute(
            """
            SELECT
                id AS company_id,
                company_name
            FROM companies
            WHERE id = ?
            """,
            (company_id,),
        ).fetchone()

        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_id}' not found",
            )

        rows = conn.execute(
            """
            SELECT
                year,
                market_cap_crore,
                enterprise_value_crore,
                pe_ratio,
                pb_ratio,
                ev_ebitda,
                dividend_yield_pct
            FROM market_cap
            WHERE company_id = ?
            ORDER BY year
            """,
            (company_id,),
        ).fetchall()

        return {
            "status": "success",
            "company_id": company_id,
            "company_name": company["company_name"],
            "count": len(rows),
            "data": [dict(row) for row in rows],
        }

    finally:
        conn.close()