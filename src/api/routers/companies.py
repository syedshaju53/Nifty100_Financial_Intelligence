import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query


# --------------------------------------------------
# ROUTER
# --------------------------------------------------

router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Companies"],
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


def get_connection():
    """
    Create a SQLite database connection.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# GET ALL / FILTERED COMPANIES
# --------------------------------------------------

@router.get("")
def get_companies(
    search: str | None = Query(
        default=None,
        description="Search by ticker or company name",
    ),
    sector: str | None = Query(
        default=None,
        description="Filter by broad sector",
    ),
    limit: int = Query(
        default=92,
        ge=1,
        le=500,
        description="Maximum number of companies to return",
    ),
):
    """
    Return companies from the Nifty100 universe.

    Supports:
    - search
    - sector filtering
    - company limit
    """

    conn = get_connection()

    try:
        query = """
            SELECT
                c.id,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                c.roe_percentage AS roe_pct,
                c.roce_percentage AS roce_pct,
                s.market_cap_category,
                s.index_weight_pct
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            WHERE 1 = 1
        """

        params = []

        # ------------------------------------------
        # SEARCH
        # ------------------------------------------

        if search:
            query += """
                AND (
                    c.id LIKE ?
                    OR c.company_name LIKE ?
                )
            """

            search_term = f"%{search.strip()}%"

            params.extend([
                search_term,
                search_term,
            ])

        # ------------------------------------------
        # SECTOR FILTER
        # ------------------------------------------

        if sector:
            query += """
                AND s.broad_sector LIKE ?
            """

            params.append(
                f"%{sector.strip()}%"
            )

        # ------------------------------------------
        # ORDER + LIMIT
        # ------------------------------------------

        query += """
            ORDER BY c.company_name
            LIMIT ?
        """

        params.append(limit)

        cursor = conn.execute(
            query,
            params,
        )

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        return {
            "status": "success",
            "count": len(rows),
            "filters": {
                "search": search,
                "sector": sector,
                "limit": limit,
            },
            "data": rows,
        }

    finally:
        conn.close()


# --------------------------------------------------
# GET SINGLE COMPANY
# --------------------------------------------------

@router.get("/{company_id}")
def get_company(company_id: str):
    """
    Return details for a single company.
    """

    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            SELECT
                c.id,
                c.company_name,
                c.company_logo,
                c.chart_link,
                c.about_company,
                c.website,
                c.nse_profile,
                c.bse_profile,
                c.face_value,
                c.book_value,
                c.roce_percentage,
                c.roe_percentage,
                s.broad_sector,
                s.sub_sector,
                s.index_weight_pct,
                s.market_cap_category
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            WHERE c.id = ?
            """,
            (company_id.upper(),),
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_id.upper()}' not found",
            )

        return {
            "status": "success",
            "data": dict(row),
        }

    finally:
        conn.close()


# --------------------------------------------------
# SEARCH COMPANIES
# --------------------------------------------------

@router.get("/search/query")
def search_companies(
    q: str = Query(
        ...,
        min_length=1,
        description="Company name or ticker to search",
    ),
):
    """
    Search companies by ID or company name.
    """

    conn = get_connection()

    try:
        search_term = f"%{q.strip()}%"

        cursor = conn.execute(
            """
            SELECT
                c.id,
                c.company_name,
                s.broad_sector,
                s.sub_sector,
                c.roe_percentage AS roe_pct,
                c.roce_percentage AS roce_pct,
                s.market_cap_category,
                s.index_weight_pct
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            WHERE
                c.id LIKE ?
                OR c.company_name LIKE ?
            ORDER BY c.company_name
            LIMIT 50
            """,
            (
                search_term,
                search_term,
            ),
        )

        rows = [
            dict(row)
            for row in cursor.fetchall()
        ]

        return {
            "status": "success",
            "query": q,
            "count": len(rows),
            "data": rows,
        }

    finally:
        conn.close()