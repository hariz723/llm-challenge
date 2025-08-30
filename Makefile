# Variables
PYTHON = .venv/bin/python
UV = uv


help:
	@echo "Makefile commands:"
	@echo "  setup      - Setup project: create .venv and install dependencies"
	@echo "  run        - Run FastAPI app (dev mode with auto-reload)"
	@echo "  format     - Format code (requires ruff or black)"
	@echo "  install    - Install all dependencies including extras"

# Setup project: create .venv and install deps
setup:
	$(UV) venv .venv
	$(UV) sync

# Run FastAPI app (dev mode with auto-reload)
run:
	$(UV) run uvicorn src.main:app --reload

# Format code (requires ruff or black)
format:
	$(UV) run ruff check . --fix
	$(UV) run black .

install:
	@echo "📦 Installing dependencies with uv..."
	uv sync --all-extras