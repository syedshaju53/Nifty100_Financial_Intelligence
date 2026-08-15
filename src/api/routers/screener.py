import sqlite3
from pathlib import Path

from fastapi import APIRouter, Query


# --------------------------------------------------
# ROUTER
# --------------------------------------------------

router = APIRouter(
    prefix="/api/v1/screener",
    tags=["Screener"],
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# STOCK SCREENER
# --------------------------------------------------

@router.get("")
def screen_companies(
    sector: str | None = Query(
        default=None,
        description="Filter by broad sector",
    ),
    min_roe: float | None = Query(
        default=None,
        description="Minimum ROE percentage",
    ),
    min_roce: float | None = Query(
        default=None,
        description="Minimum ROCE percentage",
    ),
    max_debt_equity: float | None = Query(
        default=None,
        description="Maximum debt-to-equity ratio",
    ),
    market_cap_category: str | None = Query(
        default=None,
        description="Large Cap, Mid Cap, etc.",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of results",
    ),
):
    """
    Screen Nifty100 companies.

    Financial ratios are taken from the latest
    available year for each company.
    """

    conn = get_connection()

    try:

        # --------------------------------------------------
        # BASE QUERY
        # --------------------------------------------------

        query = """
            SELECT
                c.id,
                c.company_name,

                s.broad_sector,
                s.sub_sector,
                s.market_cap_category,
                s.index_weight_pct,

                c.roe_percentage AS roe_pct,
                c.roce_percentage AS roce_pct,

                fr.year AS ratio_year,
                fr.debt_to_equity,
                fr.net_profit_margin_pct,
                fr.operating_profit_margin_pct,
                fr.return_on_equity_pct,
                fr.interest_coverage,
                fr.asset_turnover

            FROM companies c

            LEFT JOIN sectors s
                ON c.id = s.company_id

            LEFT JOIN (
                SELECT fr.*
                FROM financial_ratios fr

                INNER JOIN (
                    SELECT
                        company_id,
                        MAX(CAST(year AS INTEGER)) AS latest_year
                    FROM financial_ratios
                    GROUP BY company_id
                ) latest

                    ON fr.company_id = latest.company_id
                    AND CAST(fr.year AS INTEGER) = latest.latest_year

            ) fr

                ON c.id = fr.company_id

            WHERE 1 = 1
        """

        params = []

        # --------------------------------------------------
        # SECTOR FILTER
        # --------------------------------------------------

        if sector:
            query += """
                AND LOWER(TRIM(s.broad_sector)) = LOWER(TRIM(?))
            """
            params.append(sector)

        # --------------------------------------------------
        # ROE FILTER
        # --------------------------------------------------

        if min_roe is not None:
            query += """
                AND c.roe_percentage >= ?
            """
            params.append(min_roe)

        # --------------------------------------------------
        # ROCE FILTER
        # --------------------------------------------------

        if min_roce is not None:
            query += """
                AND c.roce_percentage >= ?
            """
            params.append(min_roce)

        # --------------------------------------------------
        # DEBT / EQUITY FILTER
        # --------------------------------------------------

        if max_debt_equity is not None:
            query += """
                AND fr.debt_to_equity <= ?
            """
            params.append(max_debt_equity)

        # --------------------------------------------------
        # MARKET CAP FILTER
        # --------------------------------------------------

        if market_cap_category:
            query += """
                AND LOWER(TRIM(s.market_cap_category))
                    = LOWER(TRIM(?))
            """
            params.append(market_cap_category)

        # --------------------------------------------------
        # ORDERING
        # --------------------------------------------------

        query += """
            ORDER BY
                c.roe_percentage DESC,
                c.roce_percentage DESC,
                c.company_name ASC

            LIMIT ?
        """

        params.append(limit)

        # --------------------------------------------------
        # EXECUTE
        # --------------------------------------------------

        rows = conn.execute(query, params).fetchall()

        data = [dict(row) for row in rows]

        # --------------------------------------------------
        # SAFETY CHECK
        # --------------------------------------------------

        company_ids = [row["id"] for row in data]

        duplicate_ids = {
            company_id
            for company_id in company_ids
            if company_ids.count(company_id) > 1
        }

        # This should always be empty.
        if duplicate_ids:
            raise RuntimeError(
                f"Duplicate companies detected: {duplicate_ids}"
            )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return {
            "status": "success",
            "count": len(data),
            "filters": {
                "sector": sector,
                "min_roe": min_roe,
                "min_roce": min_roce,
                "max_debt_equity": max_debt_equity,
                "market_cap_category": market_cap_category,
                "limit": limit,
            },
            "data": data,
        }

    finally:
        conn.close()