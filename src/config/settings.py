from functools import lru_cache
from typing import Any
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class AppSettings(BaseSettings):
    name: str = "bsw-bet-maker"
    environment: str = "local"
    debug: bool = False
    api_gateway_url: str = "http://localhost:8010"


class DatabaseSettings(BaseSettings):
    url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/bsw_bet_maker"
    )


class RedisSettings(BaseSettings):
    url: str = "redis://localhost:6379/0"
    events_ttl_seconds: int = 300


class RabbitMQSettings(BaseSettings):
    url: str = "amqp://guest:guest@localhost:5672/"
    exchange: str = "events"
    event_created_routing_key: str = "event.created"
    event_updated_routing_key: str = "event.updated"
    add_event_queue: str = "bet-maker.event.created"
    update_event_status_queue: str = "bet-maker.event.updated"


class LineProviderSettings(BaseSettings):
    base_url: str = "http://localhost:8020"
    api_key: str | None = None
    timeout_seconds: float = 30.0


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    app_name: str = "bsw-bet-maker"
    environment: str = "local"
    debug: bool = False
    api_gateway_url: str = "http://localhost:8010"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/bsw_bet_maker"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_recycle: int = -1
    database_pool_pre_ping: bool = True
    redis_url: str = "redis://localhost:6379/0"
    redis_events_ttl_seconds: int = 300
    redis_max_connections: int = 10

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "events"
    rabbitmq_event_created_routing_key: str = "event.created"
    rabbitmq_event_updated_routing_key: str = "event.updated"
    rabbitmq_add_event_queue: str = "bet-maker.event.created"
    rabbitmq_update_event_status_queue: str = "bet-maker.event.updated"

    line_provider_base_url: str = "http://localhost:8020"
    line_provider_api_key: str | None = None
    line_provider_timeout_seconds: float = 30.0

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    log_level: str = "INFO"
    log_json: bool = False

    @property
    def app(self) -> AppSettings:
        return AppSettings(
            name=self.app_name,
            environment=self.environment,
            debug=self.debug,
            api_gateway_url=self.api_gateway_url,
        )

    @property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings(url=self.database_url)

    @property
    def database_sync_url(self) -> str:
        url = self.database_url
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "+psycopg2", 1)
        return url

    @property
    def redis(self) -> RedisSettings:
        return RedisSettings(
            url=self.redis_url,
            events_ttl_seconds=self.redis_events_ttl_seconds,
        )

    @property
    def redis_credentials(self) -> dict[str, Any]:
        parsed = urlparse(self.redis_url)
        credentials: dict[str, Any] = {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "database": int(parsed.path.lstrip("/") or 0),
        }
        if parsed.password:
            credentials["password"] = parsed.password
        return credentials

    @property
    def rabbitmq(self) -> RabbitMQSettings:
        return RabbitMQSettings(
            url=self.rabbitmq_url,
            exchange=self.rabbitmq_exchange,
            event_created_routing_key=self.rabbitmq_event_created_routing_key,
            event_updated_routing_key=self.rabbitmq_event_updated_routing_key,
            add_event_queue=self.rabbitmq_add_event_queue,
            update_event_status_queue=self.rabbitmq_update_event_status_queue,
        )

    @property
    def line_provider(self) -> LineProviderSettings:
        return LineProviderSettings(
            base_url=self.line_provider_base_url,
            api_key=self.line_provider_api_key,
            timeout_seconds=self.line_provider_timeout_seconds,
        )

    @property
    def db_creds(self) -> str:
        return self.database_url

    @property
    def database_credentials(self) -> dict[str, Any]:
        url = make_url(self.database_url)
        credentials: dict[str, Any] = {
            "drivername": url.drivername or "postgresql+asyncpg",
            "username": url.username or "postgres",
            "password": url.password or "",
            "host": url.host or "localhost",
            "database": url.database or "bsw_bet_maker",
        }
        if url.port is not None:
            credentials["port"] = url.port
        return credentials


@lru_cache
def get_settings() -> Settings:
    return Settings()
