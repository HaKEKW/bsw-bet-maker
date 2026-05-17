from typing import Any


class BaseAlreadyExists(Exception):
    entity_name: str

    def __init__(self, filters: dict[str, Any] | None = None):
        self.filters = filters or {}

    def __str__(self) -> str:
        filters = ""
        for key, value in self.filters.items():
            filters += f" {key}={value}"
        suffix = filters if filters else ""
        return f"{self.entity_name} with such fields already exists{suffix}"


class UserAlreadyExists(BaseAlreadyExists):
    entity_name = "User"


class UniqueConstraintException(BaseAlreadyExists):
    entity_name = "Resource"
