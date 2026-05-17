from adapters.auth.jwt_service import JwtService
from adapters.auth.token_pair import TokenPair
from ports.repositories.user_repository import UserRepository
from usecases.exceptions.auth_exceptions import UnauthorizedException
from usecases.exceptions.not_found_exceptions import UserNotFoundException


class RefreshTokenUseCase:
    def __init__(
        self, user_repository: UserRepository, jwt_service: JwtService
    ) -> None:
        self._user_repository = user_repository
        self._jwt_service = jwt_service

    async def __call__(self, *, refresh_token: str) -> TokenPair:
        try:
            payload = self._jwt_service.decode_refresh_token(refresh_token)
            user_id = int(payload["sub"])
        except Exception as exc:
            raise UnauthorizedException("Invalid or expired refresh token") from exc

        user = await self._user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException()

        return self._jwt_service.create_token_pair(user)
