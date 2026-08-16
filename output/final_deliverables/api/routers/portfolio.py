from fastapi import APIRouter, HTTPException, Query

from src.api.database import get_connection

router = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["Portfolio"],
)


@router.get("")
def get_portfolio(
    companies: str = Query(
        ...,
        description="Comma-separated company IDs, e.g. TCS,INFY,HDFCBANK",
    )
):
    """Return portfolio valuation snapshot for selected companies."""

    company_ids = [
        item.strip().upper()
        for item in companies.split(",")
        if item.strip()
    ]

    if not company_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one company ID is required",
        )

    conn = get_connection()

    try:
        placeholders = ",".join("?" for _ in company_ids)

        rows = conn.execute(
            f"""
            SELECT
                mc.company_id,
                c.company_name,
                mc.year,
                mc.market_cap_crore,
                mc.pe_ratio,
                mc.pb_ratio,
                mc.ev_ebitda,
                mc.dividend_yield_pct
            FROM market_cap mc
            JOIN companies c
                ON mc.company_id = c.id
            WHERE mc.company_id IN ({placeholders})
              AND mc.year = (
                  SELECT MAX(mc2.year)
                  FROM market_cap mc2
                  WHERE mc2.company_id = mc.company_id
              )
            ORDER BY mc.company_id
            """,
            company_ids,
        ).fetchall()

        found = {row["company_id"] for row in rows}
        missing = [cid for cid in company_ids if cid not in found]

        return {
            "status": "success",
            "requested_companies": len(company_ids),
            "returned_companies": len(rows),
            "missing_companies": missing,
            "data": [dict(row) for row in rows],
        }

    finally:
        conn.close()