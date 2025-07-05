SHELL := /bin/bash

.PHONY: start stop reset tests clean restart

start:
	@echo "（　｀ハ´） Starting services..."
	docker compose up -d --build
	docker compose logs -f app

stop:
	@echo "(☝◞‸◟)☞ Stopping services..."
	docker compose down

reset:
	@echo " (^^ゞ Resetting all services..."
	docker compose down -v && docker compose up -d --build
tests:
	@echo " (=ↀωↀ=) Running tests..."
	docker compose exec app pytest tests/ --cov=app --cov-report=term-missing

clean:
	@echo "(/・・)ノ Cleaning up..."
	docker compose down -v
	rm -rf app/__pycache__ tests/__pycache__

restart: stop start

