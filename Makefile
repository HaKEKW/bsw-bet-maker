.PHONY: help run test test-local test-docker create-migrations migrations-upgrade migrations-downgrade \
	up up-build down down-remove-volumes postman-tests chmod-versions logs install lock sync

ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
SRC_DIR := $(ROOT_DIR)/src
COMPOSE_FILE := docker/docker-compose.yml
SERVICE := bet-maker
APP_CONTAINER := bsw-bet-maker
PYTEST_CMD := cd /src && uv sync --frozen --extra dev --no-install-project -q && pytest -v
UV_LOCK := docker run --rm -v $(SRC_DIR):/app -w /app python:3.10-slim sh -c "pip install -q uv && uv lock"
UV_SYNC := docker run --rm -v $(SRC_DIR):/app -w /app python:3.10-slim sh -c "pip install -q uv && uv sync"

help:
	@echo "bsw-bet-maker"
	@echo ""
	@echo "  make run                  Alias for up-build"
	@echo "  make test                 Run tests (local uv, or exec into bsw-bet-maker)"
	@echo "  make test-local           Run tests on host with uv"
	@echo "  make test-docker          Run tests inside running bsw-bet-maker container"
	@echo "  make up-build             docker-compose up --build"
	@echo "  make up                   docker-compose up"
	@echo "  make down                 docker-compose down"
	@echo "  make down-remove-volumes  docker-compose down -v"
	@echo "  make logs                 Follow bet-maker logs"
	@echo ""
	@echo "  make create-migrations m='message'   Autogenerate migration"
	@echo "  make migrations-upgrade              Apply migrations"
	@echo "  make migrations-downgrade            Roll back one migration"
	@echo "  make chmod-versions                  Fix permissions on migration files"
	@echo ""
	@echo "  make postman-tests        Run Newman e2e tests"
	@echo "  make install              Install deps (uv locally, or via Docker)"
	@echo "  make lock                 Regenerate src/uv.lock (no local uv required)"

run: up-build

test:
	@if command -v uv >/dev/null 2>&1; then \
		$(MAKE) test-local; \
	elif docker ps --format '{{.Names}}' 2>/dev/null | grep -qx '$(APP_CONTAINER)'; then \
		$(MAKE) test-docker; \
	else \
		echo "No uv on host and $(APP_CONTAINER) is not running."; \
		echo "  - install uv and run: make test-local"; \
		echo "  - or start the stack: make run   then: make test-docker"; \
		exit 1; \
	fi

test-local:
	cd $(SRC_DIR) && uv sync --extra dev -q && uv run pytest -v

test-docker:
	docker exec $(APP_CONTAINER) sh -c "$(PYTEST_CMD)"

create-migrations:
	@test -n "$(m)" || (echo "Usage: make create-migrations m='migration message'" && exit 1)
	docker-compose -f $(COMPOSE_FILE) run --rm $(SERVICE) alembic -c alembic.ini revision --autogenerate -m "$(m)"

migrations-upgrade:
	docker-compose -f $(COMPOSE_FILE) run --rm $(SERVICE) alembic -c alembic.ini upgrade head

migrations-downgrade:
	docker-compose -f $(COMPOSE_FILE) run --rm $(SERVICE) alembic -c alembic.ini downgrade -1

up:
	docker-compose -f $(COMPOSE_FILE) up

up-build:
	docker-compose -f $(COMPOSE_FILE) up --build

down:
	docker-compose -f $(COMPOSE_FILE) down

down-remove-volumes:
	docker-compose -f $(COMPOSE_FILE) down -v

postman-tests:
	docker run --rm --network host -v $$PWD/src/tests/e2e:/etc/newman -t postman/newman:alpine run postman_tests.json \
		--environment environment_local.json \
		--working-dir test_files/

chmod-versions:
	sudo chmod -R a+w src/migrations/versions/

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE)

install sync:
	@if command -v uv >/dev/null 2>&1; then \
		cd $(SRC_DIR) && uv sync; \
	else \
		$(UV_SYNC); \
	fi

lock uv-lock:
	$(UV_LOCK)
