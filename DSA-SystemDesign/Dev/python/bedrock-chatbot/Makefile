.PHONY: help up up-compose down logs status install chat models test lint clean

# ── Default ─────────────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

# ── Infrastructure ──────────────────────────────────────────────
up: ## Start LocalStack (Bedrock) — uses localstack CLI (handles auth automatically)
	localstack start -d
	localstack wait -t 120
	@echo "✅  LocalStack is ready!"

up-compose: ## Start LocalStack via docker compose (needs LOCALSTACK_AUTH_TOKEN env var)
	docker compose up -d
	@echo "⏳  Waiting for LocalStack to be ready…"
	@timeout 60 bash -c 'until curl -sf http://localhost:4566/_localstack/health | grep -q running; do sleep 2; done' 2>/dev/null || \
		powershell -Command "for ($$i=0; $$i -lt 30; $$i++) { try { $$r = Invoke-WebRequest -Uri http://localhost:4566/_localstack/health -UseBasicParsing -ErrorAction Stop; if ($$r.Content -match 'running') { break } } catch {} Start-Sleep 2 }"
	@echo "✅  LocalStack is ready!"

down: ## Stop LocalStack
	localstack stop 2>/dev/null || docker compose down

logs: ## Tail LocalStack logs
	docker compose logs -f localstack

status: ## Check LocalStack health
	@curl -sf http://localhost:4566/_localstack/health 2>/dev/null | python -m json.tool || \
		powershell -Command "Invoke-WebRequest -Uri http://localhost:4566/_localstack/health -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json"

# ── Application ─────────────────────────────────────────────────
install: ## Install Python dependencies via Poetry
	poetry install

chat: ## Run the interactive chatbot
	poetry run chatbot

models: ## List available Bedrock foundation models
	awslocal bedrock list-foundation-models --query 'modelSummaries[*].{Id:modelId,Name:modelName,Provider:providerName}' --output table 2>/dev/null || \
		aws --endpoint-url http://localhost:4566 bedrock list-foundation-models --query "modelSummaries[*].{Id:modelId,Name:modelName,Provider:providerName}" --output table

# ── Quality ─────────────────────────────────────────────────────
test: ## Run tests
	poetry run pytest -v

lint: ## Lint with ruff
	poetry run ruff check chatbot/
	poetry run ruff format --check chatbot/

# ── Cleanup ─────────────────────────────────────────────────────
clean: ## Remove caches and build artefacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	rm -rf dist build *.egg-info .pytest_cache .ruff_cache
