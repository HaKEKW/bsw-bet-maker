import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import aio_pika
from aio_pika import ExchangeType
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from adapters.messaging.rabbitmq.messages import (
    LineProviderEventCreatedMessage,
    LineProviderEventUpdatedMessage,
)
from adapters.repositories.bet_repository.sqlalchemy_bet_repository import (
    SQLAlchemyBetRepository,
)
from ports.messaging.event_consumer import EventConsumer
from ports.repositories.event_repository import EventRepository
from usecases.bets.update_bet_status_use_case import UpdateBetStatusUseCase
from usecases.events.add_event_use_case import AddEventUseCase
from usecases.events.process_event_status_update_use_case import (
    ProcessEventStatusUpdateUseCase,
)

logger = logging.getLogger(__name__)

MessageHandler = Callable[[dict[str, Any]], Awaitable[None]]


class RabbitMQEventConsumer(EventConsumer):
    def __init__(
        self,
        *,
        rabbitmq_url: str,
        exchange_name: str,
        event_created_routing_key: str,
        event_updated_routing_key: str,
        add_event_queue: str,
        update_event_status_queue: str,
        add_event_use_case: AddEventUseCase,
        session_factory: async_sessionmaker[AsyncSession],
        event_repository: EventRepository,
    ) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._exchange_name = exchange_name
        self._event_created_routing_key = event_created_routing_key
        self._event_updated_routing_key = event_updated_routing_key
        self._add_event_queue = add_event_queue
        self._update_event_status_queue = update_event_status_queue
        self._add_event_use_case = add_event_use_case
        self._session_factory = session_factory
        self._event_repository = event_repository
        self._connection: AbstractRobustConnection | None = None

    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._rabbitmq_url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            self._exchange_name,
            ExchangeType.TOPIC,
            durable=True,
        )

        await self._consume_binding(
            channel,
            exchange,
            queue_name=self._add_event_queue,
            routing_key=self._event_created_routing_key,
            handler=self._handle_add_event,
        )
        await self._consume_binding(
            channel,
            exchange,
            queue_name=self._update_event_status_queue,
            routing_key=self._event_updated_routing_key,
            handler=self._handle_update_event_status,
        )

        logger.info(
            "RabbitMQ consumers bound to exchange=%s keys=[%s, %s] queues=[%s, %s]",
            self._exchange_name,
            self._event_created_routing_key,
            self._event_updated_routing_key,
            self._add_event_queue,
            self._update_event_status_queue,
        )

    async def stop(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def _consume_binding(
        self,
        channel: aio_pika.abc.AbstractChannel,
        exchange: aio_pika.abc.AbstractExchange,
        *,
        queue_name: str,
        routing_key: str,
        handler: MessageHandler,
    ) -> None:
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, routing_key=routing_key)

        async def on_message(message: AbstractIncomingMessage) -> None:
            async with message.process():
                payload = json.loads(message.body.decode())
                await handler(payload)

        await queue.consume(on_message)

    async def _handle_add_event(self, payload: dict[str, Any]) -> None:
        try:
            event = LineProviderEventCreatedMessage.model_validate(payload).to_entity()
        except (ValidationError, ValueError):
            logger.exception("Invalid event.created message: %s", payload)
            return

        await self._add_event_use_case(event)
        logger.info("Event %s stored from event.created", event.id)

    async def _handle_update_event_status(self, payload: dict[str, Any]) -> None:
        try:
            message = LineProviderEventUpdatedMessage.model_validate(payload)
            event = message.to_event()
        except (ValidationError, ValueError):
            logger.exception("Invalid event.updated message: %s", payload)
            return

        async with self._session_factory() as session:
            async with session.begin():
                process_use_case = ProcessEventStatusUpdateUseCase(
                    self._event_repository,
                    UpdateBetStatusUseCase(SQLAlchemyBetRepository(session)),
                )
                bets = await process_use_case(event)

        logger.info(
            "Processed event.updated for event %s status=%s, settled %s bets",
            event.id,
            event.status.value,
            len(bets),
        )
