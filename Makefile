# Variables
PYTHON = .venv/bin/python
UV = uv

# Setup project: create .venv and install deps
setup:
	$(UV) venv .venv
	$(UV) sync

# Run FastAPI app (dev mode with auto-reload)
run:
	$(UV) run uvicorn main:app --reload

# Format code (requires ruff or black)
format:
	$(UV) run ruff check . --fix
	$(UV) run black .
