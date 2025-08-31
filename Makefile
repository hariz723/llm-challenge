# Variables
PYTHON = .venv/bin/python
UV = uv


help:
	@echo "Makefile commands:"
	@echo "  setup      - Setup project: create .venv and install dependencies"
	@echo "  run        - Run FastAPI app (dev mode with auto-reload)"
	@echo "  format     - Format code (requires ruff or black)"
	@echo "  install    - Install all dependencies including extras"
	@echo "  dev-run    - Run the FastAPI app using Docker Compose"
	@echo "  dev-down   - Stop the FastAPI app and remove containers"
	@echo "  build      - Build Docker images without cache"
	@echo "  logs       - Tail logs from Docker containers"

# Setup project: create .venv and install deps
setup:
	@echo "⚙️  Setting up project..."
	$(UV) venv .venv
	$(UV) sync
	@echo "✅ Project setup complete."

# Run FastAPI app (dev mode with auto-reload)
run:
	@echo "🚀 Starting FastAPI app with uvicorn..."
	$(UV) run uvicorn src.main:app --reload

# Format code (requires ruff or black)
format:
	@echo "🎨 Formatting code with ruff and black..."
	$(UV) run ruff check . --fix
	$(UV) run black .

install:
	@echo "📦 Installing dependencies with uv..."
	uv sync --all-extras

dev-run:
	@echo "🚀 Starting FastAPI app with uvicorn in dev mode..."
	docker compose up -d
	@echo "App is running at http://localhost:8000"
	@echo "Swagger UI: http://localhost:8000/docs"

dev-down:
	@echo "🛑 Stopping FastAPI app and removing containers..."
	docker compose down
	@echo "App stopped and containers removed."

dev-build:
	@echo "🔨 Building Docker images without cache..."
	docker compose build --no-cache
	@echo "✅ Docker images built successfully."

dev-logs:
	@echo "📜 Tailing logs from Docker containers..."
	docker compose logs -f