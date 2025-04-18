SHELL := /bin/bash

.PHONY: start stop reset tests clean restart

# Start the services in detached mode with build
start:
	@echo "（　｀ハ´） Starting services..."
	docker compose up -d --build
	docker-compose logs -f app

# Stop the services
stop:
	@echo "(☝◞‸◟)☞ Stopping services..."
	docker compose down

# Reset the services, remove volumes, and rebuild
reset:
	@echo " (^^ゞ Resetting all services..."
	docker compose down -v && docker compose up -d --build

# Run tests inside the 'tests' container
tests:
	@echo " (=ↀωↀ=) Running tests..."
	docker compose exec app pytest tests/ --cov=app --cov-report=term-missing

clean:
	@echo "(/・・)ノ Cleaning up..."
	docker compose down -v
	rm -rf app/__pycache__ tests/__pycache__

restart: stop start

