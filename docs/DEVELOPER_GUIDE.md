# Developer Guide

Fast orientation for engineers picking this up. Read this instead of the codebase first; come back to specific files once you know what you're looking for. Pairs with `docs/ARCHITECTURE.md` (the diagrams) — this doc is the "what's actually true in the code today" companion to that plan.

## 60-second mental model

One Streamlit process. A user logs in → their `user_id` goes into `st.session_state`. Every chat message goes to `Orchestrator.handle_message(user_id, history, message)`, which runs a Claude tool-use loop with 5 tools: one searches a local KB vector store, four read *that specific user's* account data from SQLite. The account-data tools take **no identity argument** — `user_id` is bound by the orchestrator from the session, never supplied by the model. That's the one invariant everything else is built around.

## File map

| File | What it does |
|---|---|
| `app.py` | Streamlit UI: login form, chat loop. Owns `st.session_state` (user, conversation history). |
| `auth.py` | `authenticate(email, password)` → `AuthenticatedUser` or `None`. bcrypt check against `users` table. |
| `db.py` | SQLite schema (`SCHEMA` string) + `get_connection()`. Single source of truth for the data model. |
| `orchestrator.py` | The tool-use loop. `TOOL_DEFS` (schemas shown to Claude) + `Orchestrator._execute_tool` (actual dispatch, where `user_id` gets injected). |
| `retriever.py` | Wraps the Chroma collection; `Retriever.search(query, category, k)`. |
| `embeddings.py` | The embedding function used by both seeding and retrieval — see "Why TF-IDF" below. |
| `tools/plan.py`, `billing.py`, `usage.py`, `org.py` | One function each, all signature `f(user_id: int) -> dict`. These are what `_execute_tool` calls; they are *not* what Claude sees (Claude sees the zero-argument schemas in `TOOL_DEFS`). |
| `prompts/system_prompt.md` | Scopes the bot to the 5 use cases, tells it how to use the tools, sets escalation behavior. Edit this before touching code if the bot's behavior needs to change. |
| `data/kb_docs/*.md` | Source KB articles (frontmatter: `title`, `category`). Add a file here to add knowledge. |
| `data/seed_kb.py` | Fits the embedding vectorizer on the KB corpus, embeds every doc into Chroma at `data/chroma/`. Rerun after editing/adding KB docs. |
| `data/seed_accounts.py` | Generates `data/app.db`: fixed demo accounts (see below) + ~40 random Faker accounts. Rerun to reset all account data. |
| `eval/golden_set.jsonl` | Labeled test queries, one per line, tagged by use case and (where relevant) which demo account to run as. |
| `eval/run_eval.py` | Runs the golden set through a live `Orchestrator` (real API calls) and does a loose keyword check on each reply. |

## The identity-binding pattern (read this before adding a tool)

`TOOL_DEFS` in `orchestrator.py` defines what Claude can see and call. The four account tools have `"properties": {}` — empty. There is no `user_id` field in their schema. When Claude requests `get_billing_history`, `Orchestrator._execute_tool` calls `get_billing_history(user_id)` using the `user_id` passed into `handle_message` by `app.py` (which got it from `st.session_state.user`, set at login) — never from `block.input`, which is what Claude actually sent.

**When you add a new account-scoped tool**, follow the same shape: the function in `tools/` takes `user_id` as a plain Python argument, but the `TOOL_DEFS` schema for it exposes zero identity fields, and `_execute_tool` is the only place that supplies `user_id`. If you ever find yourself adding `"user_id"` to a tool's `input_schema`, that's the isolation guarantee breaking — don't do it.

## Why TF-IDF instead of a real embedding model

`embeddings.py` fits a `scikit-learn` `TfidfVectorizer` on the KB corpus at seed time (`data/seed_kb.py`) and persists it to `data/tfidf_vectorizer.pkl`; both seeding and query-time retrieval load that same fitted vectorizer so they land in the same vector space. This was a deployment-environment decision, not an architectural one: the sandbox this was built in blocks Hugging Face Hub downloads, so `sentence-transformers` (the original plan in `ARCHITECTURE.md`) wasn't usable without network access we didn't have.

**Tradeoff to know about:** TF-IDF is lexical, not semantic — it matches on shared words/stems, not meaning. It works fine for this KB because support articles are keyword-dense (users say "charged twice," articles say "duplicate charge"), but it will miss paraphrases a real embedding model would catch. If you have network access to a model hub or an embeddings API, swap `embeddings.py`'s `get_embedding_function()` to return a `sentence-transformers` or Voyage embedding function instead — `retriever.py` and `seed_kb.py` don't need to change, they just call whatever `get_embedding_function()` returns.

## Demo accounts (for local testing)

Password for all: `NimbusDemo123!`. Each is pre-loaded with a specific DB state so you can hit a real scenario instead of an empty account:

| Email | Scenario |
|---|---|
| `demo.free@nimbus.ai` | Free plan, 19/20 daily messages used |
| `demo.pro@nimbus.ai` | Plain Pro account, no special state |
| `demo.billing@nimbus.ai` | Two identical $20 charges same day (duplicate-charge scenario) |
| `demo.limits@nimbus.ai` | Pro plan, 498/500 messages used (near-cap scenario) |
| `demo.troubleshoot@nimbus.ai` | Plain Pro account for troubleshooting flows (no account lookup needed) |
| `demo.admin@nimbus.ai` | Team admin at "Acme Corp"; org has a departed employee (`sam.lee.departed@acme-corp.example`) whose seat is still `active`, plus one `pending_invite` seat |
| `demo.member@nimbus.ai` | Team member (non-admin) at the same org — use this to verify `get_org_seats` correctly denies non-admins |

Seeding is idempotent — rerunning `data/seed_accounts.py` or `data/seed_kb.py` wipes and regenerates, safe to run repeatedly.

## Running it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then put your real ANTHROPIC_API_KEY in .env

python data/seed_accounts.py   # -> data/app.db
python data/seed_kb.py         # -> data/chroma/, data/tfidf_vectorizer.pkl

streamlit run app.py
```

Both seed scripts must be run before first use — `retriever.py` and `auth.py` will error clearly (not silently) if `data/app.db` or the Chroma collection don't exist yet.

## Running the eval set

```bash
python eval/run_eval.py
```

This makes real Claude API calls (needs `ANTHROPIC_API_KEY`) and does a keyword-presence check per reply — treat a "PASS" as a weak signal, not proof of correctness, and actually read a sample of the transcripts it prints. It's a regression net for "did I just break something," not a quality bar.

## Adding a 6th use case

1. Write the KB article(s) in `data/kb_docs/` (or extend an existing one) with the right `category` in frontmatter. Rerun `data/seed_kb.py`.
2. If it needs account-specific data: add a table/column to `db.py`'s `SCHEMA`, seed realistic data for it in `data/seed_accounts.py`, write a `tools/your_tool.py` with signature `f(user_id) -> dict`, add its zero-argument schema to `TOOL_DEFS` in `orchestrator.py`, and wire it into `_execute_tool`.
3. Update `prompts/system_prompt.md` to describe the new use case and when to use the new tool.
4. Add labeled cases to `eval/golden_set.jsonl` and run `eval/run_eval.py`.

## Known limitations / next steps

- **TF-IDF retrieval is lexical only** — see above. Biggest quality lever if you have model-hub access.
- **No real SSO** — Enterprise SSO is documented behavior the bot explains, not a live integration. `auth.py` is a single bcrypt-password path for every account.
- **SQLite, single-writer** — fine for an MVP demo, not for concurrent production traffic. Swap `db.py`'s connection logic for Postgres before that matters.
- **No conversation persistence** — chat history lives in `st.session_state` only; refreshing the browser loses it. Add a `conversations` table if that's needed.
- **No reranking/hybrid search** — `retriever.py` does plain top-k cosine search. Fine at 24 KB docs; revisit if the KB grows substantially.
