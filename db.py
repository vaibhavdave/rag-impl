import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS orgs (
    org_id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_name TEXT NOT NULL,
    billing_mode TEXT NOT NULL,
    seat_limit INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('member', 'admin', 'owner')),
    org_id INTEGER REFERENCES orgs(org_id),
    plan_tier TEXT NOT NULL CHECK (plan_tier IN ('free', 'pro', 'team', 'enterprise')),
    signup_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS billing_records (
    billing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    charge_date TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'refunded')),
    invoice_url TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS usage_logs (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    cycle_start TEXT NOT NULL,
    messages_used INTEGER NOT NULL,
    messages_limit INTEGER NOT NULL,
    reset_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS org_seats (
    seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL REFERENCES orgs(org_id),
    user_id INTEGER REFERENCES users(user_id),
    invited_email TEXT,
    status TEXT NOT NULL CHECK (status IN ('active', 'pending_invite', 'removed'))
);

CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    use_case TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('resolved', 'escalated')),
    created_at TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
