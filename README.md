# BSW Bet Maker Service (bsw-bet-maker)

## Overview

Service for **user registration**, **placing bets** on **sports events**, and **listing events** from a line provider.  
The **FastAPI** REST API stores users and bets in **PostgreSQL**, caches events in **Redis**, and consumes **RabbitMQ** messages from the line provider. When an event reaches a **final** status, bets are **settled automatically** from queue messages (there is no separate HTTP endpoint to settle bets).

**How it fits together:**

- **HTTP:** users and bets in Postgres; events from **Redis** (when the cache is fresh) or via HTTP to the **line provider**.
- **RabbitMQ `event.created`:** validate payload and **upsert** the event in Redis.
- **RabbitMQ `event.updated`:** upsert in Redis; on **left_victory** / **right_victory**, **settle pending bets** for that `event_id` in Postgres (won/lost, `finished_at`).

Exchange name, routing keys, and queue names **must match** the publisher (for example **bsw-line-provider**) — see `src/.env.example` and `docker/docker-compose.yml`.

---

## Stack

- **Python** 3.10+
- **FastAPI** (ASGI)
- **Pydantic** / **pydantic-settings**
- **SQLAlchemy** 2 (async) + **asyncpg**
- **PostgreSQL**
- **Redis** (async client)
- **RabbitMQ** (**aio-pika**)
- **aiohttp** (line provider HTTP client)
- **Alembic** (migrations)
- **JWT** (PyJWT), **bcrypt**
- **Uvicorn**
- **uv** (dependencies and lockfile)
- **Docker** / **Docker Compose**

---

## Installation and setup

### Prerequisites

- **Docker**
- **Docker Compose**
- (Optional for host-only development) **Python ≥ 3.10** and **[uv](https://docs.astral.sh/uv/)**
- A reachable **line provider** (for example on the host) when you need fresh events with an empty cache. In Docker the default is `LINE_PROVIDER_BASE_URL=http://host.docker.internal:8020`

### Getting started

1. Clone the repository:

```bash
git clone <repository-url>
cd bsw-bet-maker
```

2. (Optional) External Docker network for other BSW services — `docker-compose.yml` already declares **`bsw-shared`**. Create it if needed:

```bash
docker network create bsw-shared
```

If the network already exists, Compose will attach containers to it.

3. Copy the environment example (for running outside Compose or as a reference):

```bash
cp src/.env.example src/.env
```

4. Build and start the stack:

```bash
make up-build
```

or:

```bash
docker compose -f docker/docker-compose.yml up --build
```

This starts **Postgres**, **Redis**, **RabbitMQ**, and the **bet-maker** service: on container start, **Alembic** migrations run and the app launches with **Uvicorn** (`main:app`).

---

## Database migrations

### Create a migration

```bash
make create-migrations m="short_description_of_change"
```

### Apply migrations

```bash
make migrations-upgrade
```

### Roll back the last migration

```bash
make migrations-downgrade
```

---

## Running the service (stack already defined)

```bash
make up
```

or the same `docker compose` command with `docker/docker-compose.yml`.

---

## Stopping the service

```bash
make down
```

---

## Folder permissions (development)

If Alembic cannot write revision files:

```bash
make chmod-versions
```

---

## Removing volumes (full data reset)

```bash
make down-remove-volumes
```

Stops containers and removes associated volumes (including Postgres data and other named volumes from the compose file).

---

## Configuration (important variables)

The full list is in **`src/.env.example`**. In Docker, many values are overridden in **`docker/docker-compose.yml`**.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Postgres (`postgresql+asyncpg://…`) |
| `REDIS_URL` | Event cache |
| `RABBITMQ_URL` | Consumer connection |
| `RABBITMQ_EXCHANGE`, `RABBITMQ_EVENT_*`, `RABBITMQ_*_QUEUE` | Must match the producer |
| `LINE_PROVIDER_BASE_URL` | Base URL of the events API |
| `JWT_SECRET_KEY` | Token signing secret (use a strong value in production) |
| `LOG_LEVEL`, `LOG_JSON` | Log level and format |

---

## API documentation (Swagger)

After startup:

- **Swagger UI:** [http://localhost:8010/docs](http://localhost:8010/docs)  
- **Healthcheck:** `GET http://localhost:8010/healthcheck`

The app is exposed on the host at port **8010** (port **8000** inside the `bet-maker` container).

**RabbitMQ management UI:** [http://localhost:15672](http://localhost:15672) (guest / guest)

### Main routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/sign-up` | No | Sign up; returns user + tokens |
| `POST` | `/auth/sign-in` | No | Returns access + refresh tokens |
| `POST` | `/auth/refresh` | No | New token pair from refresh token |
| `GET` | `/auth/me` | Bearer | Current user |
| `POST` | `/bet` | Bearer | Place a bet |
| `GET` | `/bets` | Bearer | User’s bet history |
| `GET` | `/events` | No | List events (cache + line provider) |

In Swagger: **Authorize** → **HTTP Bearer** → paste `access_token`.

---

## Project layout (short)

| Path | Role |
|------|------|
| `src/domain/` | Domain entities |
| `src/usecases/` | Application use cases |
| `src/ports/` | Interfaces (repositories, line provider API, consumer) |
| `src/adapters/` | Implementations: DB, Redis, RabbitMQ, HTTP |
| `src/drivers/rest/` | FastAPI routers, dependencies, exception handlers |
| `src/config/` | Settings and logging |
| `src/app.py` | FastAPI instance and lifespan |
| `src/main.py` | ASGI entrypoint (`main:app` for Uvicorn), startup log |

---

## Tests

```bash
make test          # uv on host, or pytest in container if it is running
make test-local    # uv + pytest in `src/`
make test-docker   # pytest inside `bsw-bet-maker`
```

---

## Running without Docker (short)

```bash
cd src
cp .env.example .env   # set DATABASE_URL, REDIS_URL, RabbitMQ, line provider
uv sync --extra dev
uv run alembic -c alembic.ini upgrade head
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8010
```

---

## Troubleshooting

- **401** on `/bet` or `/bets` — send header `Authorization: Bearer <access_token>`.
- **503 / database errors** — check `DATABASE_URL`, that Postgres is up and migrations are applied.
- **Empty or broken event list** — line provider URL, network, Redis.
- **Bets not settling** — routing keys and payloads for `event.updated`, final statuses; check application logs for the RabbitMQ consumer.

---

## License

Add your license or organization policy here if applicable.
