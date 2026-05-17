import pytest

from adapters.auth.password_hasher import hash_password, verify_password
from domain.entities.user import UserRole
from tests.utils import event_to_payload, make_bet, make_event


@pytest.mark.asyncio
async def test_in_memory_user_repository_create_and_auth(user_repository):
    password_hash = hash_password("12345678")

    user = await user_repository.create(
        name="Alice",
        email="alice@example.com",
        password_hash=password_hash,
        role=UserRole.USER,
    )

    assert user.id == 1
    assert user.email == "alice@example.com"

    by_email = await user_repository.get_by_email("alice@example.com")
    assert by_email is not None
    assert by_email.name == "Alice"

    auth = await user_repository.get_auth_by_email("alice@example.com")
    assert auth is not None
    _, stored_hash = auth
    assert verify_password("12345678", stored_hash)


@pytest.mark.asyncio
async def test_in_memory_bet_repository_save_and_list_by_user(bet_repository):
    bet = make_bet(user_id="42", event_id="evt-1")

    await bet_repository.save(bet)
    bets = await bet_repository.get_all_user_bets(user_id="42")

    assert len(bets) == 1
    assert bets[0].event_id == "evt-1"


@pytest.mark.asyncio
async def test_in_memory_event_repository_save_and_get(event_repository):
    event = make_event(event_id="evt-99")

    await event_repository.save(event.id, event_to_payload(event))

    loaded = await event_repository.get("evt-99")
    assert loaded is not None
    assert loaded.name == event.name
