from datetime import datetime, timedelta

import pytest

from domain.entities.bet import BetStatus, WinnerChoice
from domain.entities.event import EventStatus, InputEventStatus
from tests.fakes.fake_line_provider import FakeLineProviderApi
from tests.utils import event_to_payload, make_bet, make_event
from usecases.exceptions.business_rule_exceptions import BetDeadlinePassedException
from usecases.exceptions.not_found_exceptions import EventNotFoundException


@pytest.mark.asyncio
async def test_save_bet_uses_line_provider_when_event_not_cached(
    save_bet_use_case,
    event_repository,
    line_provider,
):
    line_provider.seed(make_event(event_id="evt-1", coefficient=3.0))

    saved = await save_bet_use_case(make_bet(event_id="evt-1", user_id="1", amount=5.0))

    assert saved.coefficient == 3.0
    assert saved.status == BetStatus.PENDING
    assert await event_repository.get("evt-1") is not None


@pytest.mark.asyncio
async def test_save_bet_uses_cached_event(
    save_bet_use_case,
    event_repository,
    line_provider,
):
    event = make_event(event_id="evt-cached", coefficient=4.0)
    await event_repository.save(event.id, event_to_payload(event))

    saved = await save_bet_use_case(make_bet(event_id="evt-cached", user_id="1"))

    assert saved.coefficient == 4.0
    assert line_provider._events == {}


@pytest.mark.asyncio
async def test_save_bet_unknown_event_raises_event_not_found(save_bet_use_case):
    with pytest.raises(EventNotFoundException) as exc_info:
        await save_bet_use_case(make_bet(event_id="missing-evt", user_id="1"))

    assert "missing-evt" in str(exc_info.value)


@pytest.mark.asyncio
async def test_save_bet_rejects_event_after_bet_deadline(
    save_bet_use_case,
    line_provider: FakeLineProviderApi,
):
    line_provider.seed(
        make_event(
            event_id="evt-expired",
            bet_deadline_at=datetime.now() - timedelta(minutes=1),
        )
    )

    with pytest.raises(BetDeadlinePassedException):
        await save_bet_use_case(make_bet(event_id="evt-expired", user_id="1"))


@pytest.mark.asyncio
async def test_update_bet_status_marks_won_and_lost(
    update_bet_status_use_case,
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

    updated = await update_bet_status_use_case(
        InputEventStatus(event_id="evt-1", status=EventStatus.LEFT_VICTORY)
    )

    assert len(updated) == 2
    statuses = {bet.user_id: bet.status for bet in updated}
    assert statuses["1"] == BetStatus.WON
    assert statuses["2"] == BetStatus.LOST


@pytest.mark.asyncio
async def test_list_events_from_line_provider_and_cache(
    list_events_use_case,
    line_provider: FakeLineProviderApi,
):
    line_provider.seed(make_event(event_id="evt-a"), make_event(event_id="evt-b"))

    events = await list_events_use_case()
    assert len(events) == 2

    line_provider._events.clear()
    cached = await list_events_use_case()
    assert len(cached) == 2
