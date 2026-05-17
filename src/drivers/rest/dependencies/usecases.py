from typing import Annotated

from fastapi import Depends

from adapters.auth.jwt_service import JwtService
from drivers.rest.dependencies.auth import get_jwt_service
from drivers.rest.dependencies.line_provider import get_line_provider_api
from drivers.rest.dependencies.repositories import (
    get_bet_repository,
    get_event_repository,
    get_user_repository,
)
from ports.api.line_provider_api import LineProviderApi
from ports.repositories.bet_repository import BetRepository
from ports.repositories.event_repository import EventRepository
from ports.repositories.user_repository import UserRepository
from usecases.auth.refresh_token_use_case import RefreshTokenUseCase
from usecases.auth.sign_in_user_use_case import SignInUserUseCase
from usecases.auth.sign_up_user_use_case import SignUpUserUseCase
from usecases.bets.save_bet_use_case import SaveBetUseCase
from usecases.events.list_events_use_case import ListEventsUseCase
from usecases.users.list_user_bets_history import ListUserBetsHistoryUseCase


def get_save_bet_use_case(
    bet_repository: Annotated[BetRepository, Depends(get_bet_repository)],
    event_repository: Annotated[EventRepository, Depends(get_event_repository)],
    line_provider_api: Annotated[LineProviderApi, Depends(get_line_provider_api)],
) -> SaveBetUseCase:
    return SaveBetUseCase(bet_repository, event_repository, line_provider_api)


def get_list_events_use_case(
    event_repository: Annotated[EventRepository, Depends(get_event_repository)],
    line_provider_api: Annotated[LineProviderApi, Depends(get_line_provider_api)],
) -> ListEventsUseCase:
    return ListEventsUseCase(event_repository, line_provider_api)


def get_list_user_bets_history_use_case(
    bet_repository: Annotated[BetRepository, Depends(get_bet_repository)],
) -> ListUserBetsHistoryUseCase:
    return ListUserBetsHistoryUseCase(bet_repository)


def get_sign_up_user_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
) -> SignUpUserUseCase:
    return SignUpUserUseCase(user_repository, jwt_service)


def get_sign_in_user_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
) -> SignInUserUseCase:
    return SignInUserUseCase(user_repository, jwt_service)


def get_refresh_token_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(user_repository, jwt_service)
