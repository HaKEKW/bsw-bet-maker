import logging
from datetime import timedelta

from redis.asyncio import Redis
from redis.exceptions import RedisError

from adapters.repositories.event_redis_repository.redis_event_repository_mapper import (
    RedisEventRepositoryMapper,
)
from adapters.repositories.event_redis_repository.utils import (
    deserialize_json,
    serialize_json,
)
from domain.entities.event import Event, EventStatus
from ports.repositories.event_repository import EventRepository

logger = logging.getLogger(__name__)


class RedisEventRepository(EventRepository):
    def __init__(
        self, redis: Redis, *, default_ttl: timedelta = timedelta(minutes=5)
    ) -> None:
        self.redis = redis
        self.mapper = RedisEventRepositoryMapper()
        self._default_ttl = default_ttl

    def _ttl_seconds(self, expire: timedelta | None) -> int:
        return int((expire or self._default_ttl).total_seconds())

    def _event_key(self, event_id: str) -> str:
        return f"events: {event_id}"

    async def get(self, event_id: str) -> Event | None:
        try:
            raw = await self.redis.get(self._event_key(event_id))
            if raw is None:
                return None
            return self.mapper.to_event_entity(deserialize_json(raw))
        except (RedisError, ValueError, TypeError, KeyError):
            logger.exception("Failed to get event id=%s from redis", event_id)
            return None

    async def get_all(self) -> list[Event] | None:
        try:
            raw = await self.redis.get("events:active")
            if raw is None:
                return None

            payloads = deserialize_json(raw)
            if not payloads:
                return None

            return [self.mapper.to_event_entity(item) for item in payloads]
        except (RedisError, ValueError, TypeError, KeyError):
            logger.exception("Failed to get active events from redis")
            return None

    async def save(
        self,
        event_token: str,
        response: dict,
        expire: timedelta = timedelta(minutes=5),
    ) -> bool:
        try:
            await self.redis.set(
                self._event_key(event_token),
                serialize_json(response),
                ex=self._ttl_seconds(expire),
            )
            return True
        except (RedisError, TypeError):
            logger.exception("Failed to save event token=%s to redis", event_token)
            return False

    async def save_all(
        self,
        events: list[Event],
        expire: timedelta = timedelta(minutes=5),
    ) -> None:
        if not events:
            return

        try:
            ttl = self._ttl_seconds(expire)
            payloads = [self.mapper.to_event_payload(event) for event in events]
            pipe = self.redis.pipeline()

            pipe.set("events:active", serialize_json(payloads), ex=ttl)
            for payload in payloads:
                pipe.set(
                    self._event_key(payload["id"]),
                    serialize_json(payload),
                    ex=ttl,
                )

            await pipe.execute()
        except (RedisError, TypeError):
            logger.exception("Failed to save active events to redis")

    async def upsert(
        self,
        event: Event,
        expire: timedelta = timedelta(minutes=5),
    ) -> None:
        await self.save(event.id, self.mapper.to_event_payload(event), expire=expire)

        events = await self.get_all() or []
        by_id = {item.id: item for item in events}
        by_id[event.id] = event
        await self.save_all(list(by_id.values()), expire=expire)

    async def update_status(
        self,
        event_id: str,
        status: EventStatus,
        expire: timedelta = timedelta(minutes=5),
    ) -> None:
        event = await self.get(event_id)
        if event is None:
            return

        event.status = EventStatus(status) if isinstance(status, str) else status
        await self.upsert(event, expire=expire)

    async def delete_all(self) -> None:
        try:
            await self.redis.delete("events:active")
        except RedisError:
            logger.exception("Failed to delete active events from redis")
