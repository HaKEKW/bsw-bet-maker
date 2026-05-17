from domain.entities.event import Event
from ports.api.line_provider_api import LineProviderApi
from usecases.exceptions.not_found_exceptions import (
    EventNotFoundException,
    EventsNotFoundException,
)


class FakeLineProviderApi(LineProviderApi):
    def __init__(self, events: list[Event] | None = None) -> None:
        self._events: dict[str, Event] = {event.id: event for event in (events or [])}
        self.fail_on_list = False
        self.fail_on_get = False

    def seed(self, *events: Event) -> None:
        for event in events:
            self._events[event.id] = event

    async def get_active_events(self) -> list[Event]:
        if self.fail_on_list:
            raise EventsNotFoundException()
        events = list(self._events.values())
        if not events:
            raise EventsNotFoundException()
        return events

    async def get_event(self, event_id: str) -> Event:
        if self.fail_on_get:
            raise EventsNotFoundException()
        event = self._events.get(event_id)
        if event is None:
            raise EventNotFoundException({"event_id": event_id})
        return event
