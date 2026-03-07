.PHONY: venv install infra-up infra-down run fmt clean help

VENV  := .venv
ifeq ($(OS),Windows_NT)
    PY    := $(VENV)/Scripts/python.exe
    RM_RF := rmdir /s /q
else
    PY    := $(VENV)/bin/python
    RM_RF := rm -rf
endif

help: ## Show this help
	@echo Usage: make [target]
	@echo.
	@echo Targets:
	@echo   venv        Create Python virtual environment via uv
	@echo   install     Install all dependencies via uv
	@echo   infra-up    Start LocalStack and provision Terraform resources
	@echo   infra-down  Tear down LocalStack
	@echo   run         Start the FastAPI dev server
	@echo   fmt         Format code with ruff
	@echo   clean       Remove venv, caches, and terraform state

venv: ## Create virtual environment
	uv venv $(VENV) || echo Venv already exists
	@echo Virtual environment ready at $(VENV)

install: venv ## Install dependencies
	uv pip install --python $(PY) "fastapi[standard]" sqlmodel psycopg2-binary "python-jose[cryptography]" python-multipart boto3 python-dotenv httpx pytest ruff bcrypt

infra-up: ## Provision Terraform resources against running LocalStack
	@echo LocalStack should already be running (localstack start)...
	cd terraform && terraform init && terraform apply -auto-approve

infra-down: ## Destroy Terraform resources
	cd terraform && terraform destroy -auto-approve

run: ## Run the FastAPI dev server
	$(PY) -m fastapi dev main.py

fmt: ## Format code
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

clean: ## Clean everything
	-$(RM_RF) $(VENV) 2>nul
	-$(RM_RF) __pycache__ 2>nul
	-$(RM_RF) .pytest_cache 2>nul
	-$(RM_RF) terraform\.terraform 2>nul
	-del /q terraform\terraform.tfstate* 2>nul
	@echo Cleaned.
