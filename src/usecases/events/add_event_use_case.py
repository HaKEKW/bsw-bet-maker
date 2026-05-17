from datetime import timedelta

from domain.entities.event import Event
from ports.repositories.event_repository import EventRepository


class AddEventUseCase:
    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def __call__(self, event: Event) -> None:
        await self._event_repository.upsert(event, expire=timedelta(minutes=5))
