from datetime import datetime

from pydantic import BaseModel

from domain.entities.event import Event, EventStatus


class EventItem(BaseModel):
    id: str
    name: str
    description: str
    coefficient: float
    status: EventStatus
    bet_deadline_at: datetime
    created_at: datetime
    finished_at: datetime | None = None

    @classmethod
    def from_entity(cls, event: Event) -> "EventItem":
        return cls(
            id=event.id,
            name=event.name,
            description=event.description,
            coefficient=event.coefficient,
            status=event.status,
            bet_deadline_at=event.bet_deadline_at,
            created_at=event.created_at,
            finished_at=event.finished_at,
        )


class EventListResponse(BaseModel):
    items: list[EventItem]
