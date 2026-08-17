# Deep Dive — PDF → EPUB3 GenAI Application

Upload a PDF, get a professional, standards-compliant **EPUB3** back. The
conversion is a genuine multi-step **agent workflow** (parse → generate sections
→ assemble) driven by an LLM, built on the **2026 FastAPI + GenAI + Agentic AI
architecture** (official-aligned, not official).

The app is **offline-first**: with **zero API keys and zero external services**
it runs end-to-end using a deterministic `EchoProvider`, an in-memory vector
store, and an offline PDF parser. Add keys to upgrade to Google Gemini + LlamaParse.

---

## Quickstart (uv only)

```bash
uv sync
uv run uvicorn app.main:app --reload      # http://localhost:8000/docs
uv run pytest -q                          # tests pass with no keys
```

Configuration: copy `.env.example` → `.env` and fill in what you want. Nothing is
required.

---

## The real AI feature: PDF → EPUB3 (agent workflow)

`POST /api/v1/agents/convert` (multipart PDF) → `202` with a `job_id`. Poll
`GET /api/v1/agents/convert/{job_id}`; when `done`, download from
`GET /api/v1/agents/convert/{job_id}/download`.

Pipeline (`app/ai/agents/workflows.py::EpubConversionAgent`):

```
parse (LlamaParse or offline) → segment into chapters → generate XHTML per
chapter (LLM, multimodal with Gemini) → assemble EPUB3 (app/infra/storage.py)
```

Wired strictly as `api → services → ai/infra`:

| Endpoint                         | Service                  | AI / infra layer                          |
| -------------------------------- | ------------------------ | ----------------------------------------- |
| `api/v1/agents.py` (`/convert`)  | `conversion_service.py`  | `ai/agents/*`, `ai/rag/*`, `infra/storage`|
| `api/v1/agents.py` (`/run`)      | `agent_service.py`       | `ai/agents/workflows.py`                  |
| `api/v1/chat.py`                 | `chat_service.py`        | `ai/models/*`, `ai/memory`, `ai/guardrails`, `ai/rag` |
| `api/v1/retrieval.py`            | `retrieval_service.py`   | `ai/rag/*`                                |

No router imports an LLM SDK, agent orchestration, or a vector store directly.

---

## Other endpoints

* `GET  /health`, `GET /api/v1/health`, `GET /api/v1/ready` — liveness/readiness.
* `POST /api/v1/chat` — chat through the model provider, with guardrails, session
  memory, and optional RAG grounding (`"use_rag": true`).
* `POST /api/v1/retrieval/ingest` / `POST /api/v1/retrieval/search` — ingest text
  and retrieve chunks from the in-memory vector store.
* `POST /api/v1/agents/run` — run a generic plan/act/respond agent (summarize).

Optional auth: set `API_KEY` to require an `X-API-Key` header (no-op when empty).

---

## Architecture map (layers → modules)

```
app/
  core/         config (pydantic-settings), logging, security, exceptions
  api/v1/       chat, agents, retrieval, health routers + deps.py
  schemas/      pydantic request/response + book models (was domain/models.py)
  services/     chat / agent / retrieval / eval / conversion use cases
  ai/
    models/     LLMClient Protocol, factory, EchoProvider + GeminiProvider
    agents/     BaseAgent, RunState, EpubConversionAgent + SummarizeAgent
    tools/      ToolRegistry (+ MCP note), builtin function tools
    prompts/    system.md, epub_author.md, loader
    rag/        chunking, embeddings, vector_store, retriever, reranker,
                document_parser (LlamaParse + offline + chapter segmentation)
    memory.py   conversation/session memory (in-memory, pluggable)
    guardrails.py  PII + prompt-injection + output redaction
    evals.py    metrics + async eval runner
  infra/        db, cache, queue, storage (EPUB writer), observability
tests/          unit / integration / evals  (all pass offline)
scripts/        ingest.py, run_evals.py
migrations/      (no DB by default; Alembic slot)
```

This dissolves the previous DDD layout: `domain/models.py` → `schemas/`,
`domain/services.py` + `infrastructure/llama_parser.py` → `ai/rag/document_parser.py`,
`infrastructure/gemini_generator.py` → `ai/models/providers.py` (GeminiProvider) +
`ai/agents/workflows.py` (XHTML generation), `infrastructure/epub_writer.py` →
`infra/storage.py`, `application/convert_use_case.py` → `services/conversion_service.py`
+ `ai/agents/workflows.py`.

---

## Ecosystem mapping (doc's table → this project)

| Layer / concern        | Framework / library options                                  | Status here |
| ---------------------- | ------------------------------------------------------------ | ----------- |
| Model provider abstraction | **google-genai (Gemini)**, OpenAI, Anthropic, Bedrock, LiteLLM gateway | **Used**: GeminiProvider + EchoProvider behind the `LLMClient` Protocol. LiteLLM/others = drop-in extension points. |
| Agent layer            | Pydantic AI, OpenAI Agents SDK, LangChain, **LangGraph**, CrewAI, Google ADK, MS Agent Framework | **Used**: custom plan/act/respond `BaseAgent` + `EpubConversionAgent`. `workflows.py`/`state.py` are the LangGraph slot. |
| Tools / MCP            | function tools, **MCP** client wrappers                      | **Used**: internal `ToolRegistry` with schemas + human-in-the-loop `requires_approval`. MCP = protocol layered on top (registry/infra). |
| RAG                    | **LlamaIndex**, Haystack, LangChain retrievers, vector DB SDKs | **Used**: custom chunking/embeddings/vector-store/retriever/reranker (offline). LlamaParse (llama-cloud) used for real PDF parsing. |
| Document parsing       | **LlamaParse / llama-cloud**                                 | **Used** when `LLAMA_CLOUD_API_KEY` is set; offline fallback otherwise. |
| EPUB assembly          | **ebooklib + lxml**                                          | **Used** in `infra/storage.py`. |
| Memory                 | in-memory, Redis, MS Agent Framework context providers       | **Used**: in-memory `ConversationMemory`. Redis = `infra/cache.py` slot. |
| Guardrails             | OpenAI Agents SDK guardrails, custom                         | **Used**: PII + prompt-injection + output redaction. |
| Evals                  | Pydantic Evals, promptfoo, LangSmith, DSPy                   | **Used**: small offline metric+runner harness. |
| Observability          | **Langfuse**, LangSmith, **OpenTelemetry** GenAI conventions | **Recommended**: no-op `traced()` span helper as the integration slot. |
| DB / cache / queue     | SQLAlchemy + Alembic, Redis, Celery/RQ/arq                   | **Recommended**: in-memory defaults; documented extension points in `infra/`. |

---

## Docker

```bash
docker build -t deep-dive .
docker compose up        # serves on :8000, offline by default
```

Images target Linux; `.env` supplies any keys (never baked into the image).
