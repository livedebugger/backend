# Makefile for FastAPI App with Astral UV

VENV = app/.venv
ACTIVATE = source $(VENV)/bin/activate
ENV_FILE = app/.env
ENV_EXAMPLE = app/.env.example
DB_USER = live_user
DB_PASS = live_pass
DB_NAME = live_db

install:
	@echo " Installing uv if not already installed..."
	@if ! command -v uv >/dev/null 2>&1; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@echo " Creating virtual environment if missing..."
	@if [ ! -d "$(VENV)" ]; then \
		cd app && uv venv; \
	fi
	@echo "📥 Installing dependencies with uv..."
	cd app && uv pip install -r requirements.txt

init-env:
	@echo "📁 Creating .env if missing..."
	@if [ ! -f $(ENV_FILE) ]; then \
		cp $(ENV_EXAMPLE) $(ENV_FILE); \
		echo "🔐 Copied $(ENV_EXAMPLE) to $(ENV_FILE). Please update secrets manually."; \
	fi

setup-db:
	@if [ "$$(uname)" != "Linux" ]; then \
		echo "🪟 Skipping DB setup (non-Linux system)"; \
	else \
		echo "🐘 Creating PostgreSQL user and database..."; \
		sudo -u postgres psql -c "DO \$$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$(DB_USER)') THEN CREATE ROLE $(DB_USER) LOGIN PASSWORD '$(DB_PASS)'; END IF; END \$$;" || echo "⚠️ Role might already exist"; \
		sudo -u postgres psql -c "CREATE DATABASE $(DB_NAME) OWNER $(DB_USER);" || echo "⚠️ Database might already exist"; \
	fi

init-db:
	@echo "🗄️  Initializing DB..."
	$(ACTIVATE) && PYTHONPATH=. python app/init_db.py

run:
	@echo "🚀 Starting FastAPI app..."
	$(ACTIVATE) && uvicorn main:app --reload --app-dir app

start: init-env install setup-db init-db run
