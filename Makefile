# Makefile for FastAPI App with Astral UV

# Virtualenv path
VENV = app/.venv
ACTIVATE = source $(VENV)/bin/activate

# Install UV and dependencies
install:
	@echo " Installing uv if not already installed..."
	@if ! command -v uv >/dev/null 2>&1; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@echo " Installing dependencies..."
	@echo " Creating virtual environment..."
	@if [ ! -d "$(VENV)" ]; then \
		cd app && uv venv; \
	fi
	@echo "📥 Installing dependencies with uv..."
	cd app && source .venv/bin/activate && uv pip install -r requirements.txt

init-db:
	@echo "🗄️  Initializing DB..."
	source app/.venv/bin/activate && PYTHONPATH=. python app/init_db.py 

# Run the FastAPI app
run:
	@echo "🚀 Starting FastAPI app..."
	source app/.venv/bin/activate && uvicorn main:app --reload --app-dir app

# Run all steps: install, initialize DB, and start the server
start: install init-db run
