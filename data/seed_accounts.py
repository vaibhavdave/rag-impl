"""
Generates synthetic account data (users, orgs, billing, usage, seats) into
data/app.db. Includes a fixed set of "demo" accounts with known credentials,
each seeded to walk through one of the 5 supported use cases, plus a batch
of randomly generated users for volume/realism.

Run: python data/seed_accounts.py
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
from faker import Faker

sys.path.insert(0, str(Path(__file__).parent.parent))
from db import get_connection, init_schema  # noqa: E402

fake = Faker()
Faker.seed(42)

DEMO_PASSWORD = "NimbusDemo123!"

PLAN_LIMITS = {"free": 20, "pro": 500, "team": 500, "enterprise": 2000}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_user(conn, email, password, full_name, role, org_id, plan_tier, signup_days_ago=30):
    signup_date = (datetime.now(timezone.utc) - timedelta(days=signup_days_ago)).date().isoformat()
    cur = conn.execute(
        "INSERT INTO users (email, password_hash, full_name, role, org_id, plan_tier, signup_date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (email, hash_password(password), full_name, role, org_id, plan_tier, signup_date),
    )
    return cur.lastrowid


def insert_usage_log(conn, user_id, plan_tier, messages_used, hours_since_reset=2):
    cycle_start = (datetime.now(timezone.utc) - timedelta(hours=hours_since_reset)).isoformat()
    reset_at = (datetime.now(timezone.utc) + timedelta(hours=24 - hours_since_reset)).isoformat()
    conn.execute(
        "INSERT INTO usage_logs (user_id, cycle_start, messages_used, messages_limit, reset_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, cycle_start, messages_used, PLAN_LIMITS[plan_tier], reset_at),
    )


def insert_billing(conn, user_id, days_ago, amount, status, description, invoice_url=None):
    charge_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).date().isoformat()
    conn.execute(
        "INSERT INTO billing_records (user_id, charge_date, amount, status, invoice_url, description) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, charge_date, amount, status, invoice_url, description),
    )


def seed_demo_accounts(conn):
    """Six fixed accounts, each pre-loaded to demonstrate one of the 5 use cases."""

    # Org for the team-plan demo accounts
    acme = conn.execute(
        "INSERT INTO orgs (org_name, billing_mode, seat_limit) VALUES (?, ?, ?)",
        ("Acme Corp", "card", 10),
    ).lastrowid

    demo_users = {}

    # 1. Plan guidance — Free plan, close to daily limit
    uid = insert_user(conn, "demo.free@nimbus.ai", DEMO_PASSWORD, "Priya Shah", "member", None, "free")
    insert_usage_log(conn, uid, "free", messages_used=19)
    demo_users["demo.free@nimbus.ai"] = uid

    # General Pro account — used for feature-troubleshooting walkthroughs (no account
    # lookup needed for that use case, but the account still needs to exist to log in)
    uid = insert_user(conn, "demo.pro@nimbus.ai", DEMO_PASSWORD, "Marcus Webb", "member", None, "pro")
    insert_usage_log(conn, uid, "pro", messages_used=42)
    demo_users["demo.pro@nimbus.ai"] = uid

    # 2. Billing issue — duplicate charge in billing history
    uid = insert_user(conn, "demo.billing@nimbus.ai", DEMO_PASSWORD, "Elena Novak", "member", None, "pro")
    insert_usage_log(conn, uid, "pro", messages_used=88)
    insert_billing(conn, uid, days_ago=5, amount=20.00, status="success",
                    description="Nimbus AI Subscription - Pro (monthly)",
                    invoice_url="https://billing.nimbus.ai/inv/8841")
    insert_billing(conn, uid, days_ago=5, amount=20.00, status="success",
                    description="Nimbus AI Subscription - Pro (monthly) - retry",
                    invoice_url="https://billing.nimbus.ai/inv/8842")
    demo_users["demo.billing@nimbus.ai"] = uid

    # 3. Usage limits — Pro user right at the edge of the cap
    uid = insert_user(conn, "demo.limits@nimbus.ai", DEMO_PASSWORD, "Jordan Kim", "member", None, "pro")
    insert_usage_log(conn, uid, "pro", messages_used=498, hours_since_reset=19)
    demo_users["demo.limits@nimbus.ai"] = uid

    # 4. Feature troubleshooting — separate Pro account for a clean upload-error demo
    uid = insert_user(conn, "demo.troubleshoot@nimbus.ai", DEMO_PASSWORD, "Sofia Alvarez", "member", None, "pro")
    insert_usage_log(conn, uid, "pro", messages_used=12)
    demo_users["demo.troubleshoot@nimbus.ai"] = uid

    # 5. Org/seat admin — Team admin at Acme Corp, org has a departed employee
    #    whose seat is still active (the scenario the demo walks through)
    admin_uid = insert_user(conn, "demo.admin@nimbus.ai", DEMO_PASSWORD, "Grace Liu", "admin", acme, "team")
    insert_usage_log(conn, admin_uid, "team", messages_used=140)
    demo_users["demo.admin@nimbus.ai"] = admin_uid

    member_uid = insert_user(conn, "demo.member@nimbus.ai", DEMO_PASSWORD, "Tom Reyes", "member", acme, "team")
    insert_usage_log(conn, member_uid, "team", messages_used=63)
    demo_users["demo.member@nimbus.ai"] = member_uid

    departed_uid = insert_user(conn, "sam.lee.departed@acme-corp.example", DEMO_PASSWORD,
                                "Sam Lee (departed)", "member", acme, "team")
    insert_usage_log(conn, departed_uid, "team", messages_used=0)

    conn.execute(
        "INSERT INTO org_seats (org_id, user_id, invited_email, status) VALUES (?, ?, ?, ?)",
        (acme, admin_uid, "demo.admin@nimbus.ai", "active"),
    )
    conn.execute(
        "INSERT INTO org_seats (org_id, user_id, invited_email, status) VALUES (?, ?, ?, ?)",
        (acme, member_uid, "demo.member@nimbus.ai", "active"),
    )
    # The scenario: this seat is still "active" even though the employee has left.
    conn.execute(
        "INSERT INTO org_seats (org_id, user_id, invited_email, status) VALUES (?, ?, ?, ?)",
        (acme, departed_uid, "sam.lee.departed@acme-corp.example", "active"),
    )
    conn.execute(
        "INSERT INTO org_seats (org_id, user_id, invited_email, status) VALUES (?, ?, ?, ?)",
        (acme, None, "pending.invite@acme-corp.example", "pending_invite"),
    )

    conn.commit()
    return demo_users


def seed_random_users(conn, count=40):
    """Additional Faker-generated users for realism/volume, not used by the demo script."""
    globex = conn.execute(
        "INSERT INTO orgs (org_name, billing_mode, seat_limit) VALUES (?, ?, ?)",
        ("Globex Enterprise", "invoice", 250),
    ).lastrowid

    plan_weights = ["free"] * 5 + ["pro"] * 3 + ["team"] * 1 + ["enterprise"] * 1

    for _ in range(count):
        plan = fake.random_element(plan_weights)
        org_id = globex if plan == "enterprise" else None
        role = "member"
        password = fake.password(length=12)
        email = fake.unique.email()
        uid = insert_user(
            conn, email, password, fake.name(), role, org_id, plan,
            signup_days_ago=fake.random_int(min=1, max=400),
        )
        insert_usage_log(conn, uid, plan, messages_used=fake.random_int(min=0, max=PLAN_LIMITS[plan]))

        if plan in ("pro", "team", "enterprise"):
            for i in range(fake.random_int(min=1, max=3)):
                insert_billing(
                    conn, uid, days_ago=30 * (i + 1),
                    amount={"pro": 20.0, "team": 25.0, "enterprise": 0.0}[plan],
                    status=fake.random_element(["success"] * 9 + ["failed"]),
                    description=f"Nimbus AI Subscription - {plan.title()} (monthly)",
                    invoice_url=f"https://billing.nimbus.ai/inv/{fake.random_int(1000, 9999)}",
                )

        if plan == "enterprise":
            conn.execute(
                "INSERT INTO org_seats (org_id, user_id, invited_email, status) VALUES (?, ?, ?, ?)",
                (globex, uid, email, "active"),
            )

    conn.commit()


def main():
    conn = get_connection()
    init_schema(conn)

    # Idempotent reseed
    for table in ["support_tickets", "org_seats", "usage_logs", "billing_records", "users", "orgs"]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()

    demo_users = seed_demo_accounts(conn)
    seed_random_users(conn)

    print(f"Seeded {len(demo_users)} demo accounts (password for all: {DEMO_PASSWORD}):")
    for email in demo_users:
        print(f"  - {email}")
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"Total users in DB: {total_users}")
    conn.close()


if __name__ == "__main__":
    main()
