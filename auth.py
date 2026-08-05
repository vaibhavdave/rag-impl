from dataclasses import dataclass
from typing import Optional

import bcrypt

from db import get_connection


@dataclass
class AuthenticatedUser:
    user_id: int
    email: str
    full_name: str
    role: str
    org_id: Optional[int]
    plan_tier: str


def authenticate(email: str, password: str) -> Optional[AuthenticatedUser]:
    """Verifies credentials against the seeded users table. Returns None on
    any failure — caller should show a generic 'invalid credentials' message
    rather than distinguishing 'unknown email' from 'wrong password'."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT user_id, email, password_hash, full_name, role, org_id, plan_tier "
            "FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    if not bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return None

    return AuthenticatedUser(
        user_id=row["user_id"],
        email=row["email"],
        full_name=row["full_name"],
        role=row["role"],
        org_id=row["org_id"],
        plan_tier=row["plan_tier"],
    )
