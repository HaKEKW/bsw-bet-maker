from datetime import datetime
from typing import Any

from domain.entities.event import Event, EventStatus


class RedisEventRepositoryMapper:
    @staticmethod
    def _as_datetime(value: Any, field: str) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise ValueError(f"Invalid {field}: expected datetime or ISO string")

    @staticmethod
    def to_event_entity(data: dict[str, Any]) -> Event:
        parsed = dict(data)
        status = parsed["status"]
        if isinstance(status, str):
            status = EventStatus(status)

        bet_deadline_raw = parsed.get("bet_deadline_at") or parsed.get("expiration_at")
        bet_deadline_at = RedisEventRepositoryMapper._as_datetime(
            bet_deadline_raw, "bet_deadline_at"
        )
        created_at = RedisEventRepositoryMapper._as_datetime(
            parsed["created_at"], "created_at"
        )

        finished_at: datetime | None = None
        if raw_finished := parsed.get("finished_at"):
            finished_at = RedisEventRepositoryMapper._as_datetime(
                raw_finished, "finished_at"
            )

        return Event(
            id=parsed["id"],
            name=parsed["name"],
            description=parsed["description"],
            coefficient=parsed["coefficient"],
            status=status,
            bet_deadline_at=bet_deadline_at,
            created_at=created_at,
            finished_at=finished_at,
        )

    @staticmethod
    def to_event_payload(event: Event | dict[str, Any]) -> dict[str, Any]:
        if isinstance(event, Event):
            return {
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "coefficient": event.coefficient,
                "status": event.status.value,
                "bet_deadline_at": event.bet_deadline_at.isoformat(),
                "created_at": event.created_at.isoformat(),
                "finished_at": event.finished_at.isoformat()
                if event.finished_at
                else None,
            }
        return dict(event)
