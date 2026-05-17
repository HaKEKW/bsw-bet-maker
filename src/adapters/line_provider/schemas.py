from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from domain.entities.event import Event, EventStatus

_STATUS_MAP: dict[str, EventStatus] = {
    "live": EventStatus.LIVE,
    "left_victory": EventStatus.LEFT_VICTORY,
    "right_victory": EventStatus.RIGHT_VICTORY,
}


def _parse_status(value: str) -> EventStatus:
    status = _STATUS_MAP.get(value.lower())
    if status is None:
        raise ValueError(f"Unsupported event status from line provider: {value}")
    return status


class EventItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: str | None = ""
    coefficient: float
    status: str
    bet_deadline_at: datetime
    created_at: datetime
    finished_at: datetime | None = None

    def to_entity(self) -> Event:
        return Event(
            id=self.id,
            name=self.name,
            description=self.description or "",
            coefficient=self.coefficient,
            status=_parse_status(self.status),
            bet_deadline_at=self.bet_deadline_at,
            created_at=self.created_at,
            finished_at=self.finished_at,
        )

    @classmethod
    def entity_from(cls, payload: Any) -> Event | None:
        if not isinstance(payload, dict):
            return None
        if "id" in payload:
            return cls.model_validate(payload).to_entity()
        if items := payload.get("items"):
            return cls.model_validate(items[0]).to_entity() if items else None
        if line := payload.get("line"):
            return cls.model_validate(line).to_entity()
        return None


class EventsCollection(BaseModel):
    total_count: int | None = None
    items: list[EventItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def set_total_count_from_items(self) -> "EventsCollection":
        if self.total_count is None:
            self.total_count = len(self.items)
        return self

    def to_entities(self) -> list[Event]:
        return [item.to_entity() for item in self.items]

    @classmethod
    def from_payload(cls, payload: Any) -> "EventsCollection":
        if isinstance(payload, list):
            return cls(items=[EventItem.model_validate(item) for item in payload])
        if isinstance(payload, dict) and "items" in payload:
            return cls.model_validate(payload)
        if isinstance(payload, dict) and "events" in payload:
            return cls(
                items=[EventItem.model_validate(item) for item in payload["events"]]
            )
        raise ValueError("unexpected events response format from line provider")

    @classmethod
    def entities_from(cls, payload: Any) -> list[Event]:
        return cls.from_payload(payload).to_entities()

    @staticmethod
    def page_complete(
        payload: Any, collected: int, page_size: int, *, page_len: int
    ) -> bool:
        if page_len == 0:
            return True
        if (
            isinstance(payload, dict)
            and (total := payload.get("total_count")) is not None
        ):
            return collected >= total
        return page_len < page_size
