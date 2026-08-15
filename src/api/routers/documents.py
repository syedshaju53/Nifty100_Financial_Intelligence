from fastapi import APIRouter, HTTPException

from src.api.database import get_connection

router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Documents"],
)


@router.get("/{company_id}/documents")
def get_company_documents(company_id: str):
    """Return annual reports for a company."""

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
                annual_report
            FROM documents
            WHERE company_id = ?
            ORDER BY year DESC
            """,
            (company_id,),
        ).fetchall()

        data = []

        for row in rows:
            report = row["annual_report"]

            data.append(
                {
                    "year": row["year"],
                    "annual_report": report,
                    "is_url_valid": (
                        isinstance(report, str)
                        and report.startswith("http")
                        and report.lower() != "null"
                    ),
                }
            )

        return {
            "status": "success",
            "company_id": company_id,
            "company_name": company["company_name"],
            "count": len(data),
            "data": data,
        }

    finally:
        conn.close()