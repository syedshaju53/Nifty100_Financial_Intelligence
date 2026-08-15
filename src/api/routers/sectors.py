from fastapi import APIRouter, HTTPException

from src.api.database import get_connection

router = APIRouter(
    prefix="/api/v1/sectors",
    tags=["Sectors"],
)


@router.get("")
def get_sectors():
    """Return all sectors with company counts and average financial metrics."""

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                s.broad_sector AS sector,
                COUNT(DISTINCT s.company_id) AS company_count,
                ROUND(AVG(fr.return_on_equity_pct), 2) AS average_roe,
                ROUND(AVG(fr.debt_to_equity), 2) AS average_debt_to_equity,
                ROUND(AVG(fr.net_profit_margin_pct), 2) AS average_net_profit_margin
            FROM sectors s
            LEFT JOIN financial_ratios fr
                ON s.company_id = fr.company_id
            GROUP BY s.broad_sector
            ORDER BY s.broad_sector
            """
        ).fetchall()

        return {
            "status": "success",
            "count": len(rows),
            "data": [dict(row) for row in rows],
        }

    finally:
        conn.close()


@router.get("/{sector}/companies")
def get_sector_companies(sector: str):
    """Return companies belonging to a sector."""

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                c.id AS company_id,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                s.index_weight_pct,
                s.market_cap_category,
                c.roce_percentage,
                c.roe_percentage
            FROM sectors s
            JOIN companies c
                ON s.company_id = c.id
            WHERE LOWER(s.broad_sector) = LOWER(?)
            ORDER BY c.company_name
            """,
            (sector,),
        ).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Sector '{sector}' not found",
            )

        return {
            "status": "success",
            "sector": sector,
            "count": len(rows),
            "data": [dict(row) for row in rows],
        }

    finally:
        conn.close()