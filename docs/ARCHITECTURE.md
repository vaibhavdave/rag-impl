# Helpdesk RAG Bot — MVP Architecture

Status: Planning draft for 2-week MVP
Scope: 5 use cases (plan guidance, billing, usage limits, feature troubleshooting, org/seat management), authenticated per-user access.

---

## 1. Design principles

1. **RAG for static knowledge, tool-calls for account data.** Plans/policies/troubleshooting docs live in a vector store. Anything about *this* user (billing, usage, seats) is fetched live from a database via a tool call — never embedded, never stale.
2. **Identity is enforced server-side, not by the model.** Tool functions never accept a `user_id` argument from the LLM. The orchestration layer injects the authenticated session's user ID directly into every tool call. The model cannot request another user's data because it never has the ability to name a user.
3. **Small, boring stack.** No agent framework, no microservices. One Python process, two data stores (vector + relational), a single orchestration loop. Complexity is deferred past the MVP.
4. **Scoped and escorted.** The system prompt restricts the bot to the 5 use cases; anything else triggers a "hand off to human agent" fallback rather than an improvised answer.

---

## 2. Component diagram

```mermaid
graph TB
    subgraph Client["Client"]
        UI["Streamlit Chat UI<br/>+ Login Form"]
    end

    subgraph App["Application Service (single Python process)"]
        AUTH["Auth Module<br/>(session + password check)"]
        ORCH["Orchestrator<br/>(Claude tool-use loop)"]
        RET["Retriever<br/>(top-k semantic search)"]
        TOOLS["Account Tools<br/>get_billing_history()<br/>get_usage_status()<br/>get_org_seats()<br/>get_user_plan()"]
        PROMPT["System Prompt<br/>(scope + guardrails)"]
    end

    subgraph Data["Data layer"]
        VDB[("Vector Store<br/>Chroma<br/>KB docs + embeddings")]
        RDB[("Relational DB<br/>SQLite<br/>users / billing / usage / org_seats")]
    end

    subgraph External["External"]
        CLAUDE["Claude API<br/>(Sonnet, tool use)"]
    end

    UI -->|credentials| AUTH
    AUTH -->|user_id in session| UI
    UI -->|chat message + session user_id| ORCH
    ORCH --> PROMPT
    ORCH -->|query| RET
    RET -->|embed + search| VDB
    ORCH -->|messages + tool defs| CLAUDE
    CLAUDE -->|tool_use request| ORCH
    ORCH -->|inject session user_id, execute| TOOLS
    TOOLS --> RDB
    TOOLS -->|tool_result| ORCH
    ORCH -->|final answer| UI
```

**Why this shape:** the Orchestrator is the only component that ever sees both the Claude API and the authenticated `user_id`. The LLM only ever sees tool *results*, never raw database access or other users' identifiers — that boundary is what makes per-user isolation actually enforceable instead of just prompted-for.

---

## 3. Data model (class / ER diagram)

```mermaid
classDiagram
    class User {
        +int user_id
        +string email
        +string password_hash
        +string role  "member | admin"
        +int org_id
        +string plan_tier  "free | pro | team | enterprise"
        +date signup_date
    }

    class Org {
        +int org_id
        +string org_name
        +string billing_mode  "card | invoice"
        +int seat_limit
    }

    class BillingRecord {
        +int billing_id
        +int user_id
        +date charge_date
        +float amount
        +string status  "success | failed | refunded"
        +string invoice_url
    }

    class UsageLog {
        +int usage_id
        +int user_id
        +date cycle_start
        +int messages_used
        +int messages_limit
        +datetime reset_at
    }

    class OrgSeat {
        +int seat_id
        +int org_id
        +int user_id
        +string status  "active | pending_invite | removed"
    }

    class KBDocument {
        +int doc_id
        +string category  "plans | billing | usage | troubleshooting | admin"
        +string title
        +string content
        +vector embedding
    }

    class SupportTicket {
        +int ticket_id
        +int user_id
        +string use_case
        +string status  "resolved | escalated"
        +datetime created_at
    }

    User "1" --> "0..*" BillingRecord
    User "1" --> "1" UsageLog : current cycle
    User "many" --> "1" Org
    Org "1" --> "0..*" OrgSeat
    User "1" --> "0..1" OrgSeat
    User "1" --> "0..*" SupportTicket
```

`KBDocument` is the only table that feeds the vector store; everything else is queried live via tool calls, never embedded.

---

## 4. Sequence: pure-RAG query (Use Case 4 — feature troubleshooting)

No account data needed — this is the baseline case.

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Streamlit UI
    participant O as Orchestrator
    participant R as Retriever
    participant V as Vector Store
    participant C as Claude API

    U->>UI: "My file upload keeps failing"
    UI->>O: message + session.user_id
    O->>R: retrieve(query)
    R->>V: embed + top-k search (category=troubleshooting)
    V-->>R: top-k KB chunks
    R-->>O: retrieved context
    O->>C: system prompt + context + message
    C-->>O: answer (grounded in KB chunks)
    O-->>UI: final answer
    UI-->>U: display answer
```

---

## 5. Sequence: RAG + account tool-call (Use Case 2 — billing issue)

Account-specific — requires a bound tool call.

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Streamlit UI
    participant O as Orchestrator
    participant R as Retriever
    participant V as Vector Store
    participant C as Claude API
    participant T as Account Tools
    participant D as SQLite DB

    U->>UI: "I was charged twice this month"
    UI->>O: message + session.user_id
    O->>R: retrieve(query)
    R->>V: search (category=billing)
    V-->>R: refund/billing policy chunks
    R-->>O: retrieved context
    O->>C: system prompt + context + message + tool defs
    C-->>O: tool_use: get_billing_history()
    Note over O,T: user_id is injected by Orchestrator<br/>from session — NOT supplied by the model
    O->>T: get_billing_history(user_id=session.user_id)
    T->>D: SELECT * FROM billing_record WHERE user_id=?
    D-->>T: charge records
    T-->>O: tool_result
    O->>C: tool_result appended to conversation
    C-->>O: final answer (grounded in policy + actual charges)
    O-->>UI: final answer
    UI-->>U: display answer, offer escalation if unresolved
```

---

## 6. Sequence: login / session

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Streamlit UI
    participant A as Auth Module
    participant D as SQLite DB

    U->>UI: enter email + password
    UI->>A: authenticate(email, password)
    A->>D: SELECT password_hash FROM users WHERE email=?
    D-->>A: password_hash
    A->>A: bcrypt.verify(password, hash)
    alt valid
        A-->>UI: session.user_id = user.id
        UI-->>U: enter chat
    else invalid
        A-->>UI: error
        UI-->>U: "invalid credentials"
    end
```

---

## 7. Conversation/session state

```mermaid
stateDiagram-v2
    [*] --> LoggedOut
    LoggedOut --> Authenticating: submit credentials
    Authenticating --> LoggedOut: invalid credentials
    Authenticating --> Chatting: valid credentials
    Chatting --> Retrieving: user sends message
    Retrieving --> AwaitingToolCall: Claude requests tool_use
    Retrieving --> Answering: no tool needed
    AwaitingToolCall --> Answering: tool_result returned
    Answering --> Chatting: answer displayed
    Chatting --> Escalated: out-of-scope or unresolved
    Escalated --> [*]
    Chatting --> LoggedOut: logout
```

---

## 8. Repository layout (proposed)

```
rag-impl/
├── app.py                  # Streamlit entrypoint (login gate + chat UI)
├── auth.py                 # session handling, password check
├── orchestrator.py         # Claude tool-use loop, binds user_id server-side
├── retriever.py            # embedding + Chroma top-k search
├── tools/
│   ├── billing.py          # get_billing_history
│   ├── usage.py            # get_usage_status
│   ├── org.py              # get_org_seats
│   └── plan.py             # get_user_plan
├── data/
│   ├── seed_kb.py          # generates + embeds KB docs into Chroma
│   ├── seed_accounts.py    # Faker-generated users/billing/usage/org data -> SQLite
│   └── kb_docs/            # markdown source docs, one per KB article
├── prompts/
│   └── system_prompt.md    # scope + guardrails
├── eval/
│   └── golden_set.jsonl    # ~30-50 labeled test queries across 5 use cases
└── docs/
    └── ARCHITECTURE.md     # this file
```

---

## 9. Tech stack summary

| Layer | Choice | Why |
|---|---|---|
| LLM | Claude (Sonnet) via Anthropic API, native tool use | Skips agent-framework overhead for 5 well-defined use cases |
| Vector store | Chroma (embedded/local) | Zero infra, fast to stand up in a 2-week window |
| Embeddings | Voyage or local `sentence-transformers` | Either is adequate at this corpus size |
| Relational DB | SQLite | Single-file, no server to run, fine for MVP concurrency |
| Frontend | Streamlit | Login form + chat in one framework, fastest path to a demo |
| Orchestration | Plain Python, no LangChain/LlamaIndex | 5 tools + 1 retrieval step doesn't need a framework |
| Auth | Session-based, bcrypt-hashed passwords, seeded users | Real per-user isolation without building SSO |

---

## 10. Security note (do not skip)

The single most important invariant in this system: **tool functions take zero identity parameters from the model.** Every tool signature the orchestrator exposes to Claude should look like `get_billing_history() -> list[Charge]`, not `get_billing_history(user_id: int)`. The Orchestrator wraps each tool at call time with the session's `user_id` before execution. This makes cross-user data leakage structurally impossible rather than dependent on the model refusing a bad prompt.
