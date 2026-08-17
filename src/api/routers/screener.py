import sqlite3
from pathlib import Path

from fastapi import APIRouter, Query


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/v1/screener",
    tags=["Screener"],
)


# ============================================================
# DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_connection():
    """
    Create a SQLite connection.

    Each API request gets its own connection, which is
    important for concurrent API requests.
    """
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False,
    )

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# STOCK SCREENER
# ============================================================

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

    The screener returns one row per company.

    Financial ratios:
        Latest available year for each company.

    Sector:
        One sector record per company.

    Supported filters:
        - sector
        - min_roe
        - min_roce
        - max_debt_equity
        - market_cap_category
        - limit
    """

    conn = get_connection()

    try:

        # ====================================================
        # BASE QUERY
        # ====================================================
        #
        # IMPORTANT:
        #
        # We use ROW_NUMBER() instead of joining the complete
        # sectors and financial_ratios tables directly.
        #
        # This guarantees ONE row per company.
        #
        # ====================================================

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

            LEFT JOIN (
                SELECT
                    company_id,
                    broad_sector,
                    sub_sector,
                    market_cap_category,
                    index_weight_pct
                FROM (
                    SELECT
                        s.*,

                        ROW_NUMBER() OVER (
                            PARTITION BY s.company_id
                            ORDER BY
                                CASE
                                    WHEN s.index_weight_pct IS NOT NULL
                                    THEN 0
                                    ELSE 1
                                END,
                                s.rowid DESC
                        ) AS rn

                    FROM sectors s
                )

                WHERE rn = 1
            ) s

                ON c.id = s.company_id

            LEFT JOIN (
                SELECT
                    company_id,
                    year,
                    debt_to_equity,
                    net_profit_margin_pct,
                    operating_profit_margin_pct,
                    return_on_equity_pct,
                    interest_coverage,
                    asset_turnover
                FROM (
                    SELECT
                        fr.*,

                        ROW_NUMBER() OVER (
                            PARTITION BY fr.company_id
                            ORDER BY
                                CAST(fr.year AS INTEGER) DESC,
                                fr.rowid DESC
                        ) AS rn

                    FROM financial_ratios fr
                )

                WHERE rn = 1
            ) fr

                ON c.id = fr.company_id

            WHERE 1 = 1
        """

        params = []

        # ====================================================
        # SECTOR FILTER
        # ====================================================

        if sector is not None and sector.strip():

            query += """
                AND LOWER(TRIM(COALESCE(s.broad_sector, '')))
                    = LOWER(TRIM(?))
            """

            params.append(sector.strip())

        # ====================================================
        # ROE FILTER
        # ====================================================

        if min_roe is not None:

            query += """
                AND c.roe_percentage >= ?
            """

            params.append(min_roe)

        # ====================================================
        # ROCE FILTER
        # ====================================================

        if min_roce is not None:

            query += """
                AND c.roce_percentage >= ?
            """

            params.append(min_roce)

        # ====================================================
        # DEBT / EQUITY FILTER
        # ====================================================

        if max_debt_equity is not None:

            query += """
                AND fr.debt_to_equity <= ?
            """

            params.append(max_debt_equity)

        # ====================================================
        # MARKET CAP FILTER
        # ====================================================

        if market_cap_category is not None and market_cap_category.strip():

            query += """
                AND LOWER(
                    TRIM(
                        COALESCE(s.market_cap_category, '')
                    )
                )
                = LOWER(TRIM(?))
            """

            params.append(market_cap_category.strip())

        # ====================================================
        # ORDERING + LIMIT
        # ====================================================

        query += """
            ORDER BY
                CASE
                    WHEN c.roe_percentage IS NULL THEN 1
                    ELSE 0
                END,

                c.roe_percentage DESC,

                CASE
                    WHEN c.roce_percentage IS NULL THEN 1
                    ELSE 0
                END,

                c.roce_percentage DESC,

                c.company_name ASC

            LIMIT ?
        """

        params.append(limit)

        # ====================================================
        # EXECUTE QUERY
        # ====================================================

        rows = conn.execute(
            query,
            params,
        ).fetchall()

        # ====================================================
        # CONVERT SQLITE ROWS TO DICTIONARIES
        # ====================================================

        data = [
            dict(row)
            for row in rows
        ]

        # ====================================================
        # SAFETY CHECK
        # ====================================================

        company_ids = [
            row["id"]
            for row in data
        ]

        duplicate_ids = {
            company_id
            for company_id in company_ids
            if company_ids.count(company_id) > 1
        }

        # This should never happen because the ROW_NUMBER()
        # logic above guarantees one row per company.

        if duplicate_ids:

            raise RuntimeError(
                f"Duplicate companies detected in screener: "
                f"{sorted(duplicate_ids)}"
            )

        # ====================================================
        # RESPONSE
        # ====================================================

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

        # Always close the connection.
        #
        # This is particularly important for the
        # concurrent screener performance test.

        conn.close()