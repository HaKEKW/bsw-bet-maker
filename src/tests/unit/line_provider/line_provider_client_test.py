import pytest

from adapters.line_provider.line_provider import BswLineProvider
from adapters.line_provider.schemas import EventItem, EventsCollection
from config.settings import Settings
from tests.utils import make_event
from usecases.exceptions.not_found_exceptions import EventNotFoundException


def test_events_collection_parses_line_provider_payload():
    payload = {
        "total_count": 1,
        "items": [
            {
                "id": "evt-1",
                "name": "Match",
                "status": "live",
                "coefficient": 2.0,
                "description": "desc",
                "created_at": "2026-05-15T10:00:00+00:00",
                "finished_at": None,
                "bet_deadline_at": "2026-05-22T10:00:00+00:00",
            }
        ],
        "links": {},
    }

    entities = EventsCollection.entities_from(payload)

    assert len(entities) == 1
    assert entities[0].id == "evt-1"
    assert EventsCollection.model_validate(payload).total_count == 1


def test_events_collection_without_total_count():
    payload = {
        "items": [
            {
                "id": "87a9d0e1-0000-0000-0000-000000000001",
                "name": "Match",
                "status": "live",
                "coefficient": 2.0,
                "description": "desc",
                "created_at": "2026-05-15T10:00:00+00:00",
                "bet_deadline_at": "2026-05-22T10:00:00+00:00",
            }
        ],
    }

    entities = EventsCollection.entities_from(payload)

    assert len(entities) == 1
    assert entities[0].id == "87a9d0e1-0000-0000-0000-000000000001"
    collection = EventsCollection.model_validate(payload)
    assert collection.total_count == 1


def test_event_item_to_entity_maps_status():
    item = EventItem.model_validate(
        {
            "id": "evt-1",
            "name": "Match",
            "status": "left_victory",
            "coefficient": 2.0,
            "description": "desc",
            "created_at": "2026-05-15T10:00:00+00:00",
            "bet_deadline_at": "2026-05-22T10:00:00+00:00",
        }
    )

    entity = item.to_entity()

    assert entity.status.value == "left_victory"


@pytest.mark.asyncio
async def test_get_event_uses_active_feed_without_total_count(monkeypatch):
    provider = BswLineProvider(
        Settings(line_provider_base_url="http://line-provider", line_provider_api_key="")
    )
    active_event = make_event(event_id="evt-active-only")

    async def no_single_event(*_args, **_kwargs):
        return None

    async def active_events():
        return [active_event]

    monkeypatch.setattr(provider, "_get_json", no_single_event)
    monkeypatch.setattr(provider, "_fetch_active_events", active_events)

    found = await provider.get_event("evt-active-only")

    assert found.id == "evt-active-only"
    assert found.coefficient == active_event.coefficient


@pytest.mark.asyncio
async def test_get_event_raises_event_not_found_with_id(monkeypatch):
    provider = BswLineProvider(
        Settings(line_provider_base_url="http://line-provider", line_provider_api_key="")
    )

    async def no_single_event(*_args, **_kwargs):
        return None

    async def empty_active():
        return []

    monkeypatch.setattr(provider, "_get_json", no_single_event)
    monkeypatch.setattr(provider, "_fetch_active_events", empty_active)

    with pytest.raises(EventNotFoundException) as exc_info:
        await provider.get_event("evt-missing")

    assert str(exc_info.value) == "Event with evt-missing id not found"
