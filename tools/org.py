from db import get_connection


def get_org_seats(user_id: int) -> dict:
    """Returns the caller's org seat roster. Restricted to admin/owner roles —
    a member account gets an explicit denial rather than seat data, enforced
    here (not left to the model to decide whether to comply)."""
    conn = get_connection()
    try:
        caller = conn.execute(
            "SELECT role, org_id FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()

        if caller is None or caller["org_id"] is None:
            return {"error": "this account is not associated with an organization"}

        if caller["role"] not in ("admin", "owner"):
            return {
                "error": "permission denied: only org admins can view seat information; "
                "this account has role 'member'"
            }

        seats = conn.execute(
            """
            SELECT s.seat_id,
                   s.status,
                   COALESCE(u.full_name, s.invited_email) AS name,
                   COALESCE(u.email, s.invited_email) AS email
            FROM org_seats s
            LEFT JOIN users u ON s.user_id = u.user_id
            WHERE s.org_id = ?
            ORDER BY s.seat_id
            """,
            (caller["org_id"],),
        ).fetchall()
    finally:
        conn.close()

    return {"org_id": caller["org_id"], "seats": [dict(row) for row in seats]}
