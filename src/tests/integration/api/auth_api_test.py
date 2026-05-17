from adapters.auth.jwt_service import JwtService
from domain.entities.user import User, UserRole
from tests.support.app import TEST_SETTINGS
from tests.support.client import open_api_client
from tests.utils import auth_headers, sign_in, sign_up


def test_sign_up_sign_in_me_and_refresh(seeded_client):
    sign_up_response = sign_up(seeded_client, email="integration@example.com")
    assert sign_up_response.status_code == 200
    body = sign_up_response.json()
    assert body["user"]["email"] == "integration@example.com"
    assert body["access_token"]
    assert body["refresh_token"]

    headers = {"Authorization": f"Bearer {body['access_token']}"}
    me_response = seeded_client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "integration@example.com"

    refresh_response = seeded_client.post(
        "/auth/refresh",
        json={"refresh_token": body["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]


def test_sign_in_returns_token_pair(seeded_client):
    sign_up(seeded_client, email="signin@example.com")
    response = sign_in(seeded_client, email="signin@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "user" not in data
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_sign_in_unknown_user_returns_404(seeded_client):
    response = sign_in(seeded_client, email="nobody@example.com")
    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "User not found"


def test_me_with_token_for_missing_user_returns_404(container):
    jwt_service = JwtService(TEST_SETTINGS)
    tokens = jwt_service.create_token_pair(
        User(id=999, name="Ghost", email="ghost@example.com", role=UserRole.USER)
    )

    with open_api_client(container) as client:
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tokens.access_token}"},
        )

    assert response.status_code == 404
    assert response.json()["detail"][0]["msg"] == "User not found"


def test_protected_route_without_token_returns_401(seeded_client):
    response = seeded_client.get("/auth/me")
    assert response.status_code == 401
