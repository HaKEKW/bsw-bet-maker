from tests.support.client import open_api_client


def test_list_events_returns_seeded_events(seeded_client):
    response = seeded_client.get("/events")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == "evt-1"


def test_list_events_returns_404_when_no_events(container):
    with open_api_client(container) as client:
        response = client.get("/events")

    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "Events not found"


def test_list_events_returns_404_when_line_provider_unavailable(container):
    container.line_provider.fail_on_list = True

    with open_api_client(container) as client:
        response = client.get("/events")

    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "Events not found"
