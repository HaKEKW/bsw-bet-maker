from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

from adapters.messaging.rabbitmq.consumer import RabbitMQEventConsumer
from adapters.messaging.rabbitmq.messages import (
    LineProviderEventCreatedMessage,
    LineProviderEventUpdatedMessage,
)
from domain.entities.bet import BetStatus, WinnerChoice
from domain.entities.event import EventStatus
from tests.utils import (
    line_provider_event_created_payload,
    line_provider_event_updated_payload,
    make_bet,
    make_event,
)
from usecases.bets.update_bet_status_use_case import UpdateBetStatusUseCase
from usecases.events.process_event_status_update_use_case import (
    ProcessEventStatusUpdateUseCase,
)


@pytest.mark.asyncio
async def test_add_event_use_case_upserts_into_repository(add_event_use_case, event_repository):
    event = LineProviderEventCreatedMessage.model_validate(
        line_provider_event_created_payload()
    ).to_entity()

    await add_event_use_case(event)

    stored = await event_repository.get("evt-1")
    assert stored is not None
    assert stored.name == "Match A"
    assert stored.status == EventStatus.LIVE


@pytest.mark.asyncio
async def test_add_event_use_case_replaces_existing_event(add_event_use_case, event_repository):
    await event_repository.upsert(make_event(event_id="evt-1", name="Old", coefficient=1.0))

    event = LineProviderEventCreatedMessage.model_validate(
        line_provider_event_created_payload()
    ).to_entity()
    event.name = "New"
    event.coefficient = 2.0
    await add_event_use_case(event)

    stored = await event_repository.get("evt-1")
    assert stored is not None
    assert stored.name == "New"
    assert stored.coefficient == 2.0


@pytest.mark.asyncio
async def test_process_event_update_upserts_redis_and_settles_bets(
    process_event_status_update_use_case,
    event_repository,
    bet_repository,
):
    await bet_repository.save(
        make_bet(
            event_id="evt-1",
            user_id="1",
            winner_choice=WinnerChoice.LEFT_VICTORY,
            status=BetStatus.PENDING,
        )
    )
    await bet_repository.save(
        make_bet(
            event_id="evt-1",
            user_id="2",
            winner_choice=WinnerChoice.RIGHT_VICTORY,
            status=BetStatus.PENDING,
        )
    )

    event = LineProviderEventUpdatedMessage.model_validate(
        line_provider_event_updated_payload(status="left_victory")
    ).to_event()
    settled = await process_event_status_update_use_case(event)

    assert len(settled) == 2
    assert settled[0].status == BetStatus.WON
    assert settled[1].status == BetStatus.LOST
    assert settled[0].finished_at is not None

    stored = await event_repository.get("evt-1")
    assert stored is not None
    assert stored.status == EventStatus.LEFT_VICTORY


@pytest.mark.asyncio
async def test_process_event_update_live_status_only_updates_event(
    process_event_status_update_use_case,
    event_repository,
    bet_repository,
):
    await bet_repository.save(
        make_bet(event_id="evt-1", user_id="1", status=BetStatus.PENDING)
    )

    event = LineProviderEventUpdatedMessage.model_validate(
        line_provider_event_updated_payload(status="live")
    ).to_event()
    settled = await process_event_status_update_use_case(event)

    assert settled == []
    bet = (await bet_repository.get_all_bets_by_event(event_id="evt-1"))[0]
    assert bet.status == BetStatus.PENDING

    stored = await event_repository.get("evt-1")
    assert stored is not None
    assert stored.status == EventStatus.LIVE


@pytest.mark.asyncio
async def test_rabbitmq_consumer_update_event_status_handler(
    monkeypatch,
    event_repository,
    bet_repository,
):
    await bet_repository.save(
        make_bet(
            event_id="evt-1",
            user_id="1",
            winner_choice=WinnerChoice.LEFT_VICTORY,
            status=BetStatus.PENDING,
        )
    )

    @asynccontextmanager
    async def session_factory():
        session = MagicMock()
        session.begin.return_value.__aenter__ = AsyncMock(return_value=None)
        session.begin.return_value.__aexit__ = AsyncMock(return_value=None)
        yield session

    def process_factory(_event_repository, _update_bet_status_use_case):
        return ProcessEventStatusUpdateUseCase(
            event_repository,
            UpdateBetStatusUseCase(bet_repository),
        )

    monkeypatch.setattr(
        "adapters.messaging.rabbitmq.consumer.ProcessEventStatusUpdateUseCase",
        process_factory,
    )

    consumer = RabbitMQEventConsumer(
        rabbitmq_url="amqp://guest:guest@localhost:5672/",
        exchange_name="events",
        event_created_routing_key="event.created",
        event_updated_routing_key="event.updated",
        add_event_queue="q1",
        update_event_status_queue="q2",
        add_event_use_case=AsyncMock(),
        session_factory=session_factory,
        event_repository=event_repository,
    )

    await consumer._handle_update_event_status(
        line_provider_event_updated_payload(status="left_victory")
    )

    bet = (await bet_repository.get_all_bets_by_event(event_id="evt-1"))[0]
    assert bet.status == BetStatus.WON
    assert bet.finished_at is not None

    stored = await event_repository.get("evt-1")
    assert stored is not None
    assert stored.status == EventStatus.LEFT_VICTORY


@pytest.mark.asyncio
async def test_rabbitmq_consumer_add_event_handler():
    add_event_use_case = AsyncMock()

    consumer = RabbitMQEventConsumer(
        rabbitmq_url="amqp://guest:guest@localhost:5672/",
        exchange_name="events",
        event_created_routing_key="event.created",
        event_updated_routing_key="event.updated",
        add_event_queue="q1",
        update_event_status_queue="q2",
        add_event_use_case=add_event_use_case,
        session_factory=AsyncMock(),
        event_repository=AsyncMock(),
    )

    await consumer._handle_add_event(line_provider_event_created_payload())
    add_event_use_case.assert_awaited_once()
