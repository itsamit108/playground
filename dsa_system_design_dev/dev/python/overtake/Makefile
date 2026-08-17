.PHONY: install sync infra-up infra-down run fmt test clean help

ifeq ($(OS),Windows_NT)
    RM_RF := rmdir /s /q
else
    RM_RF := rm -rf
endif

help: ## Show this help
	@echo Usage: make [target]
	@echo.
	@echo Targets:
	@echo   install     Install/sync all dependencies via uv (creates .venv from uv.lock)
	@echo   sync        Alias for install
	@echo   infra-up    Start LocalStack and provision Terraform resources
	@echo   infra-down  Tear down LocalStack
	@echo   run         Start the FastAPI dev server
	@echo   fmt         Format code with ruff
	@echo   test        Run tests
	@echo   clean       Remove venv, caches, and terraform state

install: ## Install dependencies via uv
	uv sync

sync: install ## Alias for install

infra-up: ## Provision Terraform resources against running LocalStack
	@echo LocalStack should already be running (localstack start)...
	cd terraform && terraform init && terraform apply -auto-approve

infra-down: ## Destroy Terraform resources
	cd terraform && terraform destroy -auto-approve

run: ## Run the FastAPI dev server
	uv run fastapi dev app/main.py

fmt: ## Format code
	uv run ruff format .
	uv run ruff check --fix .

test: ## Run tests
	uv run pytest -v

clean: ## Clean everything
	-$(RM_RF) .venv 2>nul
	-$(RM_RF) __pycache__ 2>nul
	-$(RM_RF) .pytest_cache 2>nul
	-$(RM_RF) terraform\.terraform 2>nul
	-del /q terraform\terraform.tfstate* 2>nul
	@echo Cleaned.
