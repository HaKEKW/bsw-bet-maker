from copy import deepcopy
from datetime import datetime, timedelta

from adapters.repositories.event_redis_repository.redis_event_repository_mapper import (
    RedisEventRepositoryMapper,
)
from domain.entities.event import Event, EventStatus
from ports.repositories.event_repository import EventRepository


class InMemoryEventRepository(EventRepository):
    def __init__(self) -> None:
        self._cache: dict[str, tuple[Event, datetime]] = {}
        self.mapper = RedisEventRepositoryMapper()

    async def get(self, event_id: str) -> Event | None:
        entry = self._cache.get(event_id)
        if entry is None:
            return None

        event, expires_at = entry
        if datetime.now() > expires_at:
            del self._cache[event_id]
            return None

        return deepcopy(event)

    async def get_all(self) -> list[Event] | None:
        now = datetime.now()
        events: list[Event] = []
        expired_keys: list[str] = []

        for key, (event, expires_at) in self._cache.items():
            if now > expires_at:
                expired_keys.append(key)
            else:
                events.append(deepcopy(event))

        for key in expired_keys:
            del self._cache[key]

        return events or None

    async def save(
        self,
        event_token: str,
        response: dict,
        expire: timedelta = timedelta(minutes=5),
    ) -> bool:
        self._cache[event_token] = (
            self.mapper.to_event_entity(response),
            datetime.now() + expire,
        )
        return True

    async def save_all(
        self,
        events: list[Event],
        expire: timedelta = timedelta(minutes=5),
    ) -> None:
        for event in events:
            await self.save(event.id, self.mapper.to_event_payload(event), expire=expire)

    async def upsert(
        self,
        event: Event,
        expire: timedelta = timedelta(minutes=5),
    ) -> None:
        await self.save(event.id, self.mapper.to_event_payload(event), expire=expire)

    async def update_status(
        self,
        event_id: str,
        status: EventStatus,
        expire: timedelta = timedelta(minutes=5),
    ) -> None:
        if (entry := self._cache.get(event_id)) is None:
            return
        event, _ = entry
        event.status = status
        await self.save(event_id, self.mapper.to_event_payload(event), expire=expire)

    async def delete_all(self) -> None:
        self._cache.clear()
