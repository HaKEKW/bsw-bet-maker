import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

import aiohttp
from aiohttp.client_exceptions import ClientError
from pydantic import ValidationError

from adapters.line_provider.schemas import EventItem, EventsCollection
from config.settings import Settings
from domain.entities.event import Event
from ports.api.line_provider_api import LineProviderApi
from usecases.exceptions.not_found_exceptions import (
    EventNotFoundException,
    EventsNotFoundException,
)

logger = logging.getLogger(__name__)


T = TypeVar("T")


class BswLineProvider(LineProviderApi):
    def __init__(self, settings: Settings) -> None:
        self._events_url = f"{settings.line_provider_base_url.rstrip('/')}/v1/events"
        self._api_key = settings.line_provider_api_key
        self._timeout = aiohttp.ClientTimeout(
            total=settings.line_provider_timeout_seconds
        )

    async def get_active_events(self) -> list[Event]:
        events = await self._safe(self._paginated_active_events)
        if not events:
            raise EventsNotFoundException()
        return events

    async def get_event(self, event_id: str) -> Event:
        return await self._safe(lambda: self._resolve_event(event_id))

    async def _resolve_event(self, event_id: str) -> Event:
        if payload := await self._get_json(f"/{event_id}", not_found_ok=True):
            if event := EventItem.entity_from(payload):
                return event

        for event in await self._fetch_active_events():
            if event.id == event_id:
                return event

        raise EventNotFoundException({"event_id": event_id})

    async def _fetch_active_events(self) -> list[Event]:
        payload = await self._get_json()
        return EventsCollection.entities_from(payload)

    async def _paginated_active_events(self) -> list[Event]:
        collected: list[Event] = []
        page = 1

        async with self._session() as session:
            while True:
                payload = await self._get_json(
                    session=session,
                    params={"active": "true", "page": page, "limit": 50},
                )
                items = EventsCollection.entities_from(payload)
                if not items:
                    break

                collected.extend(items)
                if EventsCollection.page_complete(
                    payload, len(collected), 50, page_len=len(items)
                ):
                    break
                page += 1

        return collected

    async def _get_json(
        self,
        path: str = "",
        *,
        session: aiohttp.ClientSession | None = None,
        params: dict[str, Any] | None = None,
        not_found_ok: bool = False,
    ) -> Any:
        if session is not None:
            return await self._read_json(
                session, path, params or {"active": "true"}, not_found_ok
            )

        async with self._session() as owned:
            return await self._read_json(
                owned, path, params or {"active": "true"}, not_found_ok
            )

    async def _read_json(
        self,
        session: aiohttp.ClientSession,
        path: str,
        params: dict[str, Any],
        not_found_ok: bool,
    ) -> Any:
        async with session.get(
            f"{self._events_url}{path}",
            headers=self._headers(),
            params=params,
        ) as response:
            if not_found_ok and (response.status == 404 or not response.ok):
                return None
            if not response.ok:
                await self._raise_http_error(response)
            return await response.json()

    @asynccontextmanager
    async def _session(self):
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            yield session

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def _safe(self, action: Callable[[], Awaitable[T]]) -> T:
        try:
            return await action()
        except EventNotFoundException:
            raise
        except ValidationError as exc:
            logger.error("%s - validation error: %s", self.__class__.__name__, exc)
            raise EventsNotFoundException() from exc
        except ValueError as exc:
            logger.error("%s - %s", self.__class__.__name__, exc)
            raise EventsNotFoundException() from exc
        except ClientError as exc:
            logger.exception("%s - request failed", self.__class__.__name__)
            raise EventsNotFoundException() from exc

    @staticmethod
    async def _raise_http_error(response: aiohttp.ClientResponse) -> None:
        body = await response.text()
        logger.warning(
            "line provider HTTP error: status=%s body=%s",
            response.status,
            body[:500],
        )
        raise EventsNotFoundException()
