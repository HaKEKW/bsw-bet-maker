from fastapi import APIRouter, Depends

from domain.entities.user import User
from drivers.rest.dependencies.security import get_user_from_access_token
from drivers.rest.dependencies.usecases import (
    get_refresh_token_use_case,
    get_sign_in_user_use_case,
    get_sign_up_user_use_case,
)
from drivers.rest.routers.v1.auth.schema import (
    RefreshInput,
    SignInInput,
    SignUpInput,
    SignUpResponse,
    TokenPairResponse,
    UserResponse,
)
from usecases.auth.refresh_token_use_case import RefreshTokenUseCase
from usecases.auth.sign_in_user_use_case import SignInUserUseCase
from usecases.auth.sign_up_user_use_case import SignUpUserUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sign-up", response_model=SignUpResponse)
async def sign_up(
    payload: SignUpInput,
    sign_up_use_case: SignUpUserUseCase = Depends(get_sign_up_user_use_case),
) -> SignUpResponse:
    user, tokens = await sign_up_use_case(
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )
    return SignUpResponse(
        user=UserResponse.from_entity(user),
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post("/sign-in", response_model=TokenPairResponse)
async def sign_in(
    payload: SignInInput,
    sign_in_use_case: SignInUserUseCase = Depends(get_sign_in_user_use_case),
) -> TokenPairResponse:
    tokens = await sign_in_use_case(email=payload.email, password=payload.password)
    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh_tokens(
    payload: RefreshInput,
    refresh_use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> TokenPairResponse:
    tokens = await refresh_use_case(refresh_token=payload.refresh_token)
    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_user_from_access_token)) -> UserResponse:
    return UserResponse.from_entity(user)
