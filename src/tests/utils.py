"""Shared test helpers and factories."""

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient

from adapters.repositories.event_redis_repository.redis_event_repository_mapper import (
    RedisEventRepositoryMapper,
)
from domain.entities.bet import Bet, BetStatus, WinnerChoice
from domain.entities.event import Event, EventStatus


def make_event(
    *,
    event_id: str = "evt-1",
    name: str = "Test fight",
    coefficient: float = 2.5,
    status: EventStatus = EventStatus.LIVE,
    bet_deadline_at: datetime | None = None,
) -> Event:
    now = datetime.now()
    return Event(
        id=event_id,
        name=name,
        description="Test description",
        coefficient=coefficient,
        status=status,
        bet_deadline_at=bet_deadline_at or (now + timedelta(hours=2)),
        created_at=now,
    )


def event_to_payload(event: Event) -> dict[str, Any]:
    return RedisEventRepositoryMapper.to_event_payload(event)


def line_provider_event_created_payload(
    *,
    event_id: str = "evt-1",
    status: str = "live",
    name: str = "Match A",
    coefficient: float = 1.5,
) -> dict[str, Any]:
    return {
        "event": "event.created",
        "id": event_id,
        "status": status,
        "line": {
            "id": event_id,
            "name": name,
            "status": status,
            "coefficient": coefficient,
            "description": "desc",
            "created_at": "2026-05-15T10:00:00+00:00",
            "finished_at": None,
            "bet_deadline_at": "2026-05-22T10:00:00+00:00",
        },
    }


def line_provider_event_updated_payload(
    *,
    event_id: str = "evt-1",
    status: str = "left_victory",
    previous_status: str = "live",
    name: str = "Match A",
    coefficient: float = 1.5,
) -> dict[str, Any]:
    return {
        "event": "event.updated",
        "id": event_id,
        "status": status,
        "previous_status": previous_status,
        "line": {
            "id": event_id,
            "name": name,
            "status": status,
            "coefficient": coefficient,
            "description": "desc",
            "bet_deadline_at": "2026-05-22T10:00:00+00:00",
        },
    }


def make_bet(
    *,
    user_id: str = "1",
    event_id: str = "evt-1",
    amount: float = 10.0,
    winner_choice: WinnerChoice = WinnerChoice.LEFT_VICTORY,
    status: BetStatus | None = BetStatus.PENDING,
) -> Bet:
    return Bet(
        id=uuid4(),
        user_id=user_id,
        event_id=event_id,
        amount=amount,
        winner_choice=winner_choice,
        status=status,
        coefficient=2.5,
        created_at=datetime.now(),
    )


def sign_up(
    client: TestClient,
    email: str = "user@example.com",
    password: str = "12345678",
):
    return client.post(
        "/auth/sign-up",
        json={"name": "Test User", "email": email, "password": password},
    )


def sign_in(
    client: TestClient,
    email: str = "user@example.com",
    password: str = "12345678",
):
    return client.post(
        "/auth/sign-in",
        json={"email": email, "password": password},
    )


def auth_headers(
    client: TestClient,
    email: str = "user@example.com",
    password: str = "12345678",
):
    response = sign_up(client, email=email, password=password)
    if response.status_code == 409:
        response = sign_in(client, email=email, password=password)
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
