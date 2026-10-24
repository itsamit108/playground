# Overtake — Multi-User Notes API + Notes AI Assistant

A multi-user, multimedia note-taking API **restructured to the 2026 FastAPI +
GenAI + Agentic AI architecture**. The original single-file backend (auth, notes,
S3 attachments) is preserved feature-for-feature, and a genuine AI layer is wired
on top: a **RAG assistant and agent that operate over each user's own notes**.

> Architecture reference: [`docs/FastAPI GenAI Agentic AI Architecture 2026.md`](../../../../docs/FastAPI%20GenAI%20Agentic%20AI%20Architecture%202026.md)

---

## Stack

| Layer            | Technology                                            |
|------------------|-------------------------------------------------------|
| Framework        | FastAPI + `APIRouter` (versioned under `/api/v1`)      |
| Validation       | Pydantic v2 / pydantic-settings                       |
| ORM              | SQLModel (SQLAlchemy + Pydantic)                      |
| Database         | PostgreSQL via AWS RDS (LocalStack); SQLite in tests  |
| File storage     | AWS S3 (LocalStack)                                   |
| Auth             | JWT (python-jose) + bcrypt                            |
| AI (offline-first) | Provider abstraction + EchoProvider, RAG, agent     |
| IaC / local cloud| Terraform + LocalStack                                |
| Packaging        | uv (`pyproject.toml` + `uv.lock`) — **uv only**       |

---

## Architecture layout

```
app/
├── main.py                 # app factory + lifespan (DB tables, S3 bucket)
├── core/                   # config, logging, security (JWT/bcrypt), exceptions
├── api/
│   ├── deps.py             # settings, db session, storage, current-user deps
│   └── v1/                 # auth, notes, attachments, chat, retrieval, agents, health
├── schemas/                # request/response models (chat, agents, retrieval, notes, common)
├── services/               # auth/note/attachment + chat/agent/retrieval/eval use cases
├── ai/
│   ├── models/             # LLMClient protocol, factory, providers (Echo + extension points)
│   ├── agents/             # base agent, workflows (notes organizer), state
│   ├── tools/              # registry + builtins (e.g. search_notes)
│   ├── prompts/            # system prompt + loader
│   ├── rag/                # chunking, embeddings, vector_store, retriever, reranker
│   ├── memory.py  guardrails.py  evals.py
├── infra/                  # db (engine + ORM models), cache, queue, storage (S3), observability
tests/                      # unit / integration / evals  (SQLite + EchoProvider, fully offline)
scripts/                    # ingest, run_evals
migrations/                 # (kept for Alembic when needed)
terraform/                  # RDS + S3 resources
```

**Dependency direction:** `api → services → ai / infra`. Routers never call the
LLM, the vector store, or the database directly. There is **no DDD layer** (no
`domain/`), per the default structure in the architecture doc.

---

## Quick start

```bash
# 1. Install deps (uv only)
uv sync

# 2a. Run with zero infrastructure — the AI endpoints work offline (EchoProvider).
#     (note/attachment endpoints need Postgres; see 2b)
uv run fastapi dev app/main.py

# 2b. Full stack with LocalStack (Postgres RDS + S3):
localstack start            # separate terminal
make infra-up               # terraform: provision RDS + S3
uv run fastapi dev app/main.py
```

Docs: http://localhost:8000/docs · Health: http://localhost:8000/api/v1/health

### Docker

```bash
docker compose up --build   # starts localstack + the api container
# then provision infra once: make infra-up
```

---

## API surface (all under `/api/v1`)

**Auth** — `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
**Notes** — `POST/GET /notes`, `GET/PUT/DELETE /notes/{id}` (search + pagination)
**Attachments** — `POST/GET /notes/{id}/attachments`, `GET /attachments/{id}/download`, `DELETE /attachments/{id}`
**AI: Chat** — `POST /chat` — ask a question answered from *your* notes (RAG, with citations)
**AI: Retrieval** — `POST /retrieval/search`, `POST /retrieval/reindex` — semantic search over your notes
**AI: Agents** — `POST /agents/organize` — notes-organizer agent (tool-using)
**Health** — `GET /health`

All AI endpoints run offline by default via the deterministic `EchoProvider` and
an in-memory vector store — no API keys required. Set `LLM_PROVIDER` and a key in
`.env` to plug in a real provider.

---

## Ecosystem fit (where each framework would live)

| Concern        | This repo                          | Drop-in alternatives                          |
|----------------|------------------------------------|-----------------------------------------------|
| Provider layer | `ai/models/` (Echo + factory)      | LiteLLM, OpenAI, Anthropic, Bedrock, Gemini   |
| Agents         | `ai/agents/` (custom workflow)     | Pydantic AI, LangGraph, CrewAI, OpenAI Agents |
| RAG            | `ai/rag/` (hashing embedder + store)| LlamaIndex, Haystack, pgvector, Qdrant       |
| Tools / MCP    | `ai/tools/registry.py`             | MCP client wrappers                           |
| Observability  | `infra/observability.py`           | Langfuse, OpenTelemetry GenAI                 |
| Evals          | `ai/evals.py`, `tests/evals/`      | Pydantic Evals, promptfoo                     |

---

## Testing

```bash
uv run python -m pytest -q       # 25 tests, fully offline (SQLite + EchoProvider)
```

Tests never touch Postgres, S3, or any network: the suite forces SQLite, fakes S3
storage, and uses the EchoProvider (see `tests/conftest.py`).

---

## Make targets

`make install` · `make run` · `make infra-up` / `make infra-down` · `make fmt` ·
`make test` · `make clean`
