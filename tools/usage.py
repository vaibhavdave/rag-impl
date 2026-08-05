from db import get_connection


def get_usage_status(user_id: int) -> dict:
    """Returns the caller's current-cycle message usage and reset time."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT cycle_start, messages_used, messages_limit, reset_at "
            "FROM usage_logs WHERE user_id = ? ORDER BY usage_id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return {"error": "no usage data found for this account"}

    data = dict(row)
    data["messages_remaining"] = data["messages_limit"] - data["messages_used"]
    return data
