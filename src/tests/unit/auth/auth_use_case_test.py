import pytest

from usecases.exceptions.already_exists_exceptions import UserAlreadyExists
from usecases.exceptions.auth_exceptions import UnauthorizedException
from usecases.exceptions.not_found_exceptions import UserNotFoundException
from usecases.auth.refresh_token_use_case import RefreshTokenUseCase
from usecases.auth.sign_in_user_use_case import SignInUserUseCase
from usecases.auth.sign_up_user_use_case import SignUpUserUseCase


@pytest.mark.asyncio
async def test_sign_up_creates_user_and_tokens(user_repository, jwt_service):
    use_case = SignUpUserUseCase(user_repository, jwt_service)

    user, tokens = await use_case(
        name="Bob",
        email="bob@example.com",
        password="12345678",
    )

    assert user.email == "bob@example.com"
    assert tokens.access_token
    assert tokens.refresh_token

    payload = jwt_service.decode_access_token(tokens.access_token)
    assert payload["sub"] == str(user.id)


@pytest.mark.asyncio
async def test_sign_up_duplicate_email_raises(user_repository, jwt_service):
    use_case = SignUpUserUseCase(user_repository, jwt_service)
    await use_case(name="Bob", email="bob@example.com", password="12345678")

    with pytest.raises(UserAlreadyExists):
        await use_case(name="Other", email="bob@example.com", password="87654321")


@pytest.mark.asyncio
async def test_sign_in_and_refresh(user_repository, jwt_service):
    sign_up = SignUpUserUseCase(user_repository, jwt_service)
    sign_in = SignInUserUseCase(user_repository, jwt_service)
    refresh = RefreshTokenUseCase(user_repository, jwt_service)

    await sign_up(name="Bob", email="bob@example.com", password="12345678")
    tokens = await sign_in(email="bob@example.com", password="12345678")
    new_tokens = await refresh(refresh_token=tokens.refresh_token)

    assert new_tokens.access_token
    assert jwt_service.decode_access_token(new_tokens.access_token)["email"] == "bob@example.com"


@pytest.mark.asyncio
async def test_sign_in_unknown_user_raises_not_found(user_repository, jwt_service):
    sign_in = SignInUserUseCase(user_repository, jwt_service)

    with pytest.raises(UserNotFoundException):
        await sign_in(email="missing@example.com", password="12345678")


@pytest.mark.asyncio
async def test_sign_in_invalid_password(user_repository, jwt_service):
    sign_up = SignUpUserUseCase(user_repository, jwt_service)
    sign_in = SignInUserUseCase(user_repository, jwt_service)

    await sign_up(name="Bob", email="bob@example.com", password="12345678")

    with pytest.raises(UnauthorizedException):
        await sign_in(email="bob@example.com", password="wrong-password")
