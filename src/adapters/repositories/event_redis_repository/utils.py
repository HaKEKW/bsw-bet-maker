import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any


def _json_default(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def serialize_json(data: Any) -> str:
    return json.dumps(data, default=_json_default)


def deserialize_json(raw: str | bytes) -> Any:
    if isinstance(raw, bytes):
        raw = raw.decode()
    return json.loads(raw)
