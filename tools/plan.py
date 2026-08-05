from db import get_connection


def get_user_plan(user_id: int) -> dict:
    """Returns the caller's current plan tier, role, org, and signup date."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT plan_tier, role, org_id, signup_date FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return {"error": "user not found"}
    return dict(row)
