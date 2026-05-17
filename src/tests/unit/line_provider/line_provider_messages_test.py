from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from adapters.messaging.rabbitmq.messages import (
    LineProviderEventCreatedMessage,
    LineProviderEventUpdatedMessage,
)
from domain.entities.event import EventStatus
from tests.utils import (
    line_provider_event_created_payload,
    line_provider_event_updated_payload,
)


def test_event_created_message_parses_line_provider_payload():
    event = LineProviderEventCreatedMessage.model_validate(
        line_provider_event_created_payload()
    ).to_entity()

    assert event.id == "evt-1"
    assert event.status == EventStatus.LIVE
    assert event.bet_deadline_at == datetime(2026, 5, 22, 10, 0, tzinfo=timezone.utc)


def test_event_updated_message_parses_snake_case_status():
    payload = line_provider_event_updated_payload(status="right_victory")
    payload["line"]["description"] = None

    event_status = LineProviderEventUpdatedMessage.model_validate(payload).to_entity()

    assert event_status.event_id == "evt-1"
    assert event_status.status == EventStatus.RIGHT_VICTORY


def test_event_created_message_rejects_invalid_envelope():
    with pytest.raises(ValidationError):
        LineProviderEventCreatedMessage.model_validate(
            {"event": "event.updated", "id": "x", "line": {}}
        )
