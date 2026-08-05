from db import get_connection


def get_billing_history(user_id: int) -> list[dict]:
    """Returns the caller's most recent charges (up to 10), most recent first."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT charge_date, amount, status, invoice_url, description "
            "FROM billing_records WHERE user_id = ? ORDER BY charge_date DESC, billing_id DESC LIMIT 10",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    return [dict(row) for row in rows]
