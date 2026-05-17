from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from adapters.connection_engines.redis.redis_engine import get_redis
from config.settings import Settings, get_settings


class RedisDependency:
    def __call__(self, _settings: Annotated[Settings, Depends(get_settings)]) -> Redis:
        return get_redis()


redis_client = RedisDependency()


def get_redis_client(redis: Annotated[Redis, Depends(redis_client)]) -> Redis:
    return redis
