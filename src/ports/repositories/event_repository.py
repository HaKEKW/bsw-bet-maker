from abc import ABC, abstractmethod
from datetime import timedelta

from domain.entities.event import Event, EventStatus


class EventRepository(ABC):
    @abstractmethod
    async def get(self, event_id: str) -> Event | None:
        pass

    @abstractmethod
    async def get_all(self) -> list[Event] | None:
        pass

    @abstractmethod
    async def save(
        self, event_token: str, response: dict, expire: timedelta = timedelta(minutes=5)
    ) -> bool:
        pass

    @abstractmethod
    async def save_all(
        self, events: list[Event], expire: timedelta = timedelta(minutes=5)
    ) -> None:
        pass

    @abstractmethod
    async def upsert(
        self, event: Event, expire: timedelta = timedelta(minutes=5)
    ) -> None:
        pass

    @abstractmethod
    async def update_status(
        self,
        event_id: str,
        status: EventStatus,
        expire: timedelta = timedelta(minutes=5),
    ) -> None:
        pass

    @abstractmethod
    async def delete_all(self) -> None:
        pass
