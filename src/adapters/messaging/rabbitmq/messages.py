from datetime import datetime, timezone

from pydantic import BaseModel, Field

from domain.entities.event import Event, EventStatus, InputEventStatus

_STATUS_MAP: dict[str, EventStatus] = {
    "live": EventStatus.LIVE,
    "left_victory": EventStatus.LEFT_VICTORY,
    "right_victory": EventStatus.RIGHT_VICTORY,
}


def _parse_status(value: str) -> EventStatus:
    status = _STATUS_MAP.get(value.lower())
    if status is None:
        raise ValueError(f"Unsupported event status: {value}")
    return status


class LinePayload(BaseModel):
    id: str
    name: str
    status: str
    coefficient: float
    description: str | None = None
    created_at: datetime | None = None
    finished_at: datetime | None = None
    bet_deadline_at: datetime

    def to_entity(self) -> Event:
        created_at = self.created_at or datetime.now(timezone.utc)

        return Event(
            id=self.id,
            name=self.name,
            description=self.description or "",
            coefficient=self.coefficient,
            status=_parse_status(self.status),
            bet_deadline_at=self.bet_deadline_at,
            created_at=created_at,
            finished_at=self.finished_at,
        )


class LineProviderEventCreatedMessage(BaseModel):
    event: str = Field(pattern=r"^event\.created$")
    id: str
    status: str
    line: LinePayload

    def to_entity(self) -> Event:
        return self.line.to_entity()


class LineProviderEventUpdatedMessage(BaseModel):
    event: str = Field(pattern=r"^event\.updated$")
    id: str
    status: str
    previous_status: str | None = None
    line: LinePayload

    def to_event(self) -> Event:
        return self.line.to_entity()

    def to_entity(self) -> InputEventStatus:
        return InputEventStatus(event_id=self.id, status=_parse_status(self.status))
