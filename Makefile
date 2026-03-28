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
	@echo "  dev-build  - Build Docker images without cache"
	@echo "  dev-logs   - Tail logs from Docker containers"
	@echo "  migrations - Create a new alembic migration. Usage: make migrations \"Your migration message\""
	@echo "  migrate    - Apply database migrations"
	@echo "  help       - Display this help message"
	@echo "  dev-stop   - Stop the FastAPI app"
	@echo "  dev-clean  - Clean up Docker containers, images, and volumes"

# Setup project: create .venv and install deps
setup:
		@echo "⚙️  Setting up project..."
		$(UV) venv .venv
		$(UV) sync
		docker compose build
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
	@echo "✅ Dependencies installed."

dev-run:
	@echo "🚀 Starting FastAPI app and Streamlit UI in dev mode..."
	docker compose up -d
	@echo "✅ FastAPI app is running at http://localhost:8000"
	@echo "📚 Open FastAPI Swagger UI: http://localhost:8000/docs"
	@echo "✅ Streamlit UI is running at http://localhost:8501"

dev-down:
	@echo "🛑 Stopping FastAPI app and removing containers..."
	docker compose down
	@echo "✅ App stopped and containers removed."

dev-stop:
	@echo "🛑 Stopping FastAPI app..."
	docker compose stop
	@echo "✅ App stopped."

dev-build:
	@echo "🔨 Building Docker images without cache..."
	docker compose build --no-cache
	@echo "✅ Docker images built successfully."

dev-logs:
	@echo "📜 Tailing logs from Docker containers..."
	docker compose logs -f

migrate:
	@echo "🛠️  Applying database migrations..."
	$(UV) run alembic upgrade head
	@echo "✅ Database migrations applied."

dev-clean:
	@echo "🧹 Cleaning up Docker containers, images, and volumes..."
	docker system prune -a 
	@echo "✅ Cleanup complete."