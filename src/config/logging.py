from __future__ import annotations

import json
import logging
import sys
from logging import Formatter, LogRecord
from typing import Any

from config.settings import Settings


class JsonFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info).strip()
        return json.dumps(payload, ensure_ascii=False)


def _resolve_level(name: str) -> int:
    level = getattr(logging, name.upper(), None)
    return level if isinstance(level, int) else logging.INFO


def setup_logging(settings: Settings) -> None:
    """Configure root logging once (replaces existing root handlers)."""
    level = _resolve_level(settings.log_level)

    if settings.log_json:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logging.basicConfig(level=level, handlers=[handler], force=True)
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        logging.basicConfig(
            level=level,
            format=fmt,
            datefmt="%Y-%m-%d %H:%M:%S",
            stream=sys.stdout,
            force=True,
        )

    logging.captureWarnings(True)

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.debug else logging.WARNING
    )
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("aiormq").setLevel(logging.WARNING)
    logging.getLogger("aio_pika").setLevel(logging.INFO)
