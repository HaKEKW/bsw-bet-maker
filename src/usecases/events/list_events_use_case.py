from datetime import timedelta

from adapters.exceptions import LineProviderException
from domain.entities.event import Event
from ports.api.line_provider_api import LineProviderApi
from ports.repositories.event_repository import EventRepository
from usecases.exceptions.not_found_exceptions import EventsNotFoundException


class ListEventsUseCase:
    def __init__(
        self, event_repository: EventRepository, line_provider_api: LineProviderApi
    ):
        self._event_repository = event_repository
        self._line_provider_api = line_provider_api

    async def __call__(self) -> list[Event]:
        if events := await self._event_repository.get_all():
            return events
        return await self.__retrieve_events_from_api()

    async def __retrieve_events_from_api(self) -> list[Event]:
        try:
            events = await self._line_provider_api.get_active_events()
        except EventsNotFoundException:
            raise
        except LineProviderException as exc:
            raise EventsNotFoundException() from exc

        if not events:
            raise EventsNotFoundException()

        await self._event_repository.save_all(events, expire=timedelta(minutes=5))
        return events
