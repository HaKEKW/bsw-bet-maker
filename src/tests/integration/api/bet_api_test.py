from datetime import datetime, timedelta

from tests.support.client import open_api_client
from tests.utils import auth_headers, make_event, sign_up


def test_create_bet_and_list_bets(seeded_client):
    headers = auth_headers(seeded_client, email="bettor@example.com")

    create_response = seeded_client.post(
        "/bet",
        headers=headers,
        json={
            "event_id": "evt-1",
            "amount": 10,
            "winner_choice": "left_victory",
        },
    )
    assert create_response.status_code == 200, create_response.text
    bet = create_response.json()
    assert bet["event_id"] == "evt-1"
    assert bet["amount"] == 10
    assert bet["coefficient"] == 2.5
    assert bet["status"] == "pending"

    list_response = seeded_client.get("/bets", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()["items"]) == 1
    assert list_response.json()["items"][0]["status"] == "pending"


def test_create_bet_unknown_event_returns_404(seeded_client):
    sign_up(seeded_client, email="unknown-event@example.com")
    headers = auth_headers(seeded_client, email="unknown-event@example.com")

    response = seeded_client.post(
        "/bet",
        headers=headers,
        json={
            "event_id": "missing-event-id",
            "amount": 10,
            "winner_choice": "left_victory",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "Event with missing-event-id id not found"


def test_create_bet_after_deadline_returns_400(container):
    container.line_provider.seed(
        make_event(
            event_id="evt-1",
            bet_deadline_at=datetime.now() - timedelta(minutes=1),
        )
    )

    with open_api_client(container) as client:
        headers = auth_headers(client, email="late@example.com")
        response = client.post(
            "/bet",
            headers=headers,
            json={
                "event_id": "evt-1",
                "amount": 10,
                "winner_choice": "left_victory",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"][0]["msg"] == "Bet deadline has passed for this event"
