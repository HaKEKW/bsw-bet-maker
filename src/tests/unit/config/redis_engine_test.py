import pytest

from adapters.connection_engines.redis.redis_engine import RedisEngine
from config.settings import Settings


def test_settings_redis_credentials_parsed_from_url():
    settings = Settings(redis_url="redis://localhost:6379/0")

    credentials = settings.redis_credentials

    assert credentials["host"] == "localhost"
    assert credentials["port"] == 6379
    assert credentials["database"] == 0


@pytest.mark.asyncio
async def test_redis_engine_start():
    connection = await RedisEngine.start(
        {"host": "localhost", "port": 6379, "database": 0}
    )

    assert connection.redis_engine is not None
