from typing import Any


class BaseNotFoundException(Exception):
    entity_name: str

    def __init__(self, filters: dict[str, Any] | None = None):
        self.filters = filters or {}

    def __str__(self) -> str:
        filters = ""
        for key, value in self.filters.items():
            filters += f" {key}={value}"
        suffix = filters if filters else ""
        return f"{self.entity_name} not found{suffix}"


class UserNotFoundException(BaseNotFoundException):
    entity_name = "User"


class EventNotFoundException(BaseNotFoundException):
    entity_name = "Event"

    def __str__(self) -> str:
        event_id = self.filters.get("event_id")
        if event_id is not None:
            return f"Event with {event_id} id not found"
        return super().__str__()


class BetNotFoundException(BaseNotFoundException):
    entity_name = "Bet"


class EventsNotFoundException(BaseNotFoundException):
    entity_name = "Events"

    def __str__(self) -> str:
        return "Events not found"
