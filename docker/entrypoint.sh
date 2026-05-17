#!/bin/sh
set -e

unset VIRTUAL_ENV
export UV_PROJECT_ENVIRONMENT=/usr/local
export PYTHONPATH=/src

cd /src
uv sync --frozen --no-install-project

PYTHONPATH=. alembic -c alembic.ini upgrade head
exec /usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
