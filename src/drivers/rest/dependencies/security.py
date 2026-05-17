from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from adapters.auth.jwt_service import JwtService
from domain.entities.user import User
from drivers.rest.dependencies.auth import get_jwt_service
from drivers.rest.dependencies.repositories import get_user_repository
from ports.repositories.user_repository import UserRepository
from usecases.exceptions.auth_exceptions import UnauthorizedException
from usecases.exceptions.not_found_exceptions import UserNotFoundException

bearer_scheme = HTTPBearer(
    scheme_name="Bearer Token",
    description="Paste the access_token from POST /auth/sign-in or /auth/sign-up (without the 'Bearer ' prefix).",
)


async def get_user_from_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    jwt_service: Annotated[JwtService, Depends(get_jwt_service)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    try:
        payload = jwt_service.decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise UnauthorizedException("Invalid or expired token") from exc

    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise UserNotFoundException()

    return user
