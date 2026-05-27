# 🤖 LocalStack Bedrock CLI Chatbot

A simple **interactive CLI chatbot** powered by [LocalStack](https://localstack.cloud/) Bedrock emulation and [Ollama](https://ollama.com/) models.
No AWS account required — everything runs locally.

---

## Architecture

```
┌──────────────┐      Converse API       ┌──────────────────┐      Ollama       ┌────────────┐
│  CLI Chatbot │  ──────────────────────▶ │   LocalStack     │  ──────────────▶  │  LLM Model │
│  (Rich TUI)  │  ◀──────────────────────  │   (Bedrock)      │  ◀──────────────  │  (llama3)  │
└──────────────┘                          └──────────────────┘                   └────────────┘
```

## Prerequisites

| Tool | Version |
|------|---------|
| **Docker** (+ Docker Compose) | Latest |
| **Python** | 3.11 – 3.13 |
| **Poetry** | 1.8+ |
| **LocalStack CLI** | Latest (with Pro auth token) |

## Quick Start

### 1. Start LocalStack with Bedrock

**Option A — LocalStack CLI (recommended, handles auth automatically):**

```bash
localstack start -d
```

**Option B — Docker Compose (requires `LOCALSTACK_AUTH_TOKEN` env var):**

```bash
docker compose up -d
```

> **Note:** The first Bedrock request will pull the Ollama model inside LocalStack.
> This can take several minutes depending on your connection. Subsequent calls are fast.

### 2. Install Python dependencies

```bash
poetry install
```

### 3. Run the chatbot

```bash
poetry run chatbot

# Or use the Makefile
make chat
```

## CLI Commands

Once inside the chatbot you can use these slash commands:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/reset` | Clear conversation history |
| `/model` | Show current model info |
| `/models` | List available foundation models |
| `/system` | Show the system prompt |
| `/quit` | Exit (also `Ctrl+C`) |

## Configuration

All settings live in `.env`:

```env
AWS_ENDPOINT_URL=http://localhost:4566
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test

# Use "ollama.<model>" to directly specify an Ollama model
BEDROCK_MODEL_ID=ollama.llama3.2

# System prompt injected into every conversation
SYSTEM_PROMPT=You are a helpful, concise AI assistant.
```

### Changing the Ollama model

1. Update `DEFAULT_BEDROCK_MODEL` in `docker-compose.yml`
2. Restart LocalStack: `make down && make up`

You can also use any Ollama model on-the-fly by setting the model-id to `ollama.<model-name>` in `.env`:

```env
BEDROCK_MODEL_ID=ollama.deepseek-r1
```

## Makefile Targets

```
make help      Show all targets
make up        Start LocalStack (Bedrock)
make down      Stop LocalStack
make logs      Tail LocalStack logs
make status    Check LocalStack health
make install   Install Python deps via Poetry
make chat      Run the interactive chatbot
make models    List available Bedrock models
make test      Run tests
make lint      Lint with ruff
make clean     Remove caches & build artefacts
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bedrock unresponsive | Run `docker system prune` to free Docker VM resources |
| Model takes too long | Use a smaller model: `DEFAULT_BEDROCK_MODEL=tinyllama` |
| Connection refused | Ensure LocalStack is running: `make status` |
| Timeout on first request | The model is still loading — wait or set `BEDROCK_PREWARM=1` |

## Project Structure

```
bedrock-chatbot/
├── chatbot/
│   ├── __init__.py
│   ├── cli.py            # Interactive CLI (Rich TUI)
│   ├── client.py         # boto3 client factory
│   ├── config.py         # .env loader
│   └── conversation.py   # Converse API wrapper + history
├── tests/
│   └── test_conversation.py
├── .env                  # Environment variables
├── .gitignore
├── docker-compose.yml    # LocalStack + Bedrock
├── Makefile
├── pyproject.toml        # Poetry config
└── README.md
```

## License

MIT
