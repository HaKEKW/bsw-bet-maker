from redis.asyncio import Redis, from_url

from ports.connection_engine import ConnectionEngine

_connection: "RedisEngine | None" = None


class RedisEngine(ConnectionEngine):
    def __init__(self, redis_engine: Redis):
        self.redis_engine = redis_engine

    @classmethod
    async def start(cls, credentials: dict):
        password = credentials.get("password", "")
        redis_engine = from_url(
            f"redis://:{password}@{credentials['host']}:{credentials['port']}/{credentials['database']}",
            decode_responses=True,
        )
        global _connection
        _connection = cls(redis_engine)
        return _connection

    async def close(self) -> None:
        await self.redis_engine.aclose()
        global _connection
        _connection = None


def get_redis() -> Redis:
    if _connection is None:
        raise RuntimeError("Redis is not connected")
    return _connection.redis_engine
