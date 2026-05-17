from abc import ABC, abstractmethod

from domain.entities.event import Event


class LineProviderApi(ABC):
    @abstractmethod
    async def get_active_events(self) -> list[Event]:
        pass

    @abstractmethod
    async def get_event(self, event_id: str) -> Event:
        pass
