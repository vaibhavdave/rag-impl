"""
Runs the golden set through the live orchestrator (real Claude API calls —
requires ANTHROPIC_API_KEY and a seeded database/vector store) and does a
loose keyword check on each reply. This is a sanity net, not a substitute
for reading transcripts: keyword presence is a weak signal, so review
failures (and a sample of passes) by eye before trusting a "pass" count.

Run: python eval/run_eval.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from db import get_connection  # noqa: E402
from orchestrator import Orchestrator  # noqa: E402

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.jsonl"


def load_cases():
    with open(GOLDEN_SET_PATH) as f:
        return [json.loads(line) for line in f if line.strip()]


def user_id_for_email(conn, email: str) -> int:
    row = conn.execute("SELECT user_id FROM users WHERE email = ?", (email,)).fetchone()
    if row is None:
        raise ValueError(f"No seeded user found for {email} — did you run data/seed_accounts.py?")
    return row["user_id"]


def main():
    cases = load_cases()
    orchestrator = Orchestrator()
    conn = get_connection()

    passed, failed = 0, 0
    for i, case in enumerate(cases, 1):
        email = case["account"]
        user_id = user_id_for_email(conn, email) if email else user_id_for_email(conn, "demo.pro@nimbus.ai")

        reply = orchestrator.handle_message(user_id=user_id, history=[], user_message=case["query"])
        reply_lower = reply.lower()
        ok = any(kw.lower() in reply_lower for kw in case["expects"])

        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        print(f"[{status}] ({case['use_case']}) {i}/{len(cases)}: {case['query']}")
        if not ok:
            print(f"         expected one of {case['expects']} in reply, got:\n         {reply[:300]}")

    conn.close()
    print(f"\n{passed} passed, {failed} failed out of {len(cases)}")


if __name__ == "__main__":
    main()
