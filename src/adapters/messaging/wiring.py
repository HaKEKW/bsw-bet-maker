from adapters.connection_engines.redis.redis_engine import get_redis
from adapters.messaging.rabbitmq.consumer import RabbitMQEventConsumer
from adapters.repositories.event_redis_repository.redis_event_repository import (
    RedisEventRepository,
)
from config.settings import get_settings
from drivers.rest.dependencies.database import sqlalchemy_engine
from ports.messaging.event_consumer import EventConsumer
from usecases.events.add_event_use_case import AddEventUseCase

_consumer: EventConsumer | None = None


def build_rabbitmq_event_consumer() -> EventConsumer:
    settings = get_settings()
    event_repository = RedisEventRepository(get_redis())
    return RabbitMQEventConsumer(
        rabbitmq_url=settings.rabbitmq_url,
        exchange_name=settings.rabbitmq_exchange,
        event_created_routing_key=settings.rabbitmq_event_created_routing_key,
        event_updated_routing_key=settings.rabbitmq_event_updated_routing_key,
        add_event_queue=settings.rabbitmq_add_event_queue,
        update_event_status_queue=settings.rabbitmq_update_event_status_queue,
        add_event_use_case=AddEventUseCase(event_repository),
        session_factory=sqlalchemy_engine(settings),
        event_repository=event_repository,
    )


async def start_messaging(settings=None) -> None:
    global _consumer
    _consumer = build_rabbitmq_event_consumer()
    await _consumer.start()


async def stop_messaging() -> None:
    global _consumer
    if _consumer is not None:
        await _consumer.stop()
        _consumer = None
