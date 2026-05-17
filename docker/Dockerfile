FROM python:3.10-slim

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.5 /uv /uvx /bin/

ENV APP_DIR=/src

RUN --mount=type=cache,target=/src/.cache/uv \
    --mount=type=bind,source=src/uv.lock,target=uv.lock \
    --mount=type=bind,source=src/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY src $APP_DIR

RUN --mount=type=cache,target=/src/.cache/uv \
    uv sync --frozen

ENV PYTHONPATH=$APP_DIR

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
