from fastapi import APIRouter, HTTPException

from src.api.database import get_connection

router = APIRouter(
    prefix="/api/v1/peers",
    tags=["Peer Analysis"],
)


@router.get("")
def get_peer_groups():
    """Return all peer groups and their companies."""

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                pg.peer_group_name,
                COUNT(DISTINCT pg.company_id) AS company_count
            FROM peer_groups pg
            GROUP BY pg.peer_group_name
            ORDER BY pg.peer_group_name
            """
        ).fetchall()

        return {
            "status": "success",
            "count": len(rows),
            "data": [dict(row) for row in rows],
        }

    finally:
        conn.close()


@router.get("/{peer_group_name}")
def get_peer_group(peer_group_name: str):
    """Return companies belonging to a peer group."""

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                pg.peer_group_name,
                pg.company_id,
                c.company_name,
                pg.is_benchmark
            FROM peer_groups pg
            LEFT JOIN companies c
                ON pg.company_id = c.id
            WHERE LOWER(pg.peer_group_name) = LOWER(?)
            ORDER BY
                CASE
                    WHEN pg.is_benchmark = '1' THEN 0
                    ELSE 1
                END,
                c.company_name
            """,
            (peer_group_name,),
        ).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Peer group '{peer_group_name}' not found",
            )

        return {
            "status": "success",
            "peer_group": peer_group_name,
            "count": len(rows),
            "data": [dict(row) for row in rows],
        }

    finally:
        conn.close()