# Nimbus AI Helpdesk Assistant

A RAG + tool-calling support chatbot for Nimbus AI (a fictional Claude-like AI company). Logged-in users get answers grounded in the knowledge base *and* their own account data — billing, usage, plan, and (for org admins) team seats — with per-user data access enforced server-side, not by the model.

Covers 5 use cases: plan guidance, billing issues, usage/rate limits, feature troubleshooting, and org/seat administration.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # add your ANTHROPIC_API_KEY

python data/seed_accounts.py
python data/seed_kb.py

streamlit run app.py
```

Demo logins are shown on the app's login screen (password `NimbusDemo123!` for all).

## Docs

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design, UML diagrams, data model
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — how to use the assistant, with example conversations
- [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) — codebase map, key patterns, how to extend it
