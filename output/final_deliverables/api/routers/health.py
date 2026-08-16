import time
from datetime import datetime, timezone

from fastapi import APIRouter

from src.api.database import get_database_info


START_TIME = time.time()

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"],
)


@router.get("/health")
def health_check():
    """Return API and database health information."""

    db_info = get_database_info()

    return {
        "status": "ok",
        "service": "Nifty100 Financial Intelligence API",
        "version": "1.0.0",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "uptime_seconds": round(
            time.time() - START_TIME,
            2,
        ),
        "database": {
            "status": "connected",
            "db_row_counts": db_info["db_row_counts"],
            "companies": db_info["company_count"],
            "master_companies": db_info["master_companies"],
            "master_financial_rows": db_info[
                "master_financial_rows"
            ],
        },
    }