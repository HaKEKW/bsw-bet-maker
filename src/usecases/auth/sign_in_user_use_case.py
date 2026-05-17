from adapters.auth.jwt_service import JwtService
from adapters.auth.password_hasher import verify_password
from adapters.auth.token_pair import TokenPair
from usecases.exceptions.auth_exceptions import UnauthorizedException
from usecases.exceptions.not_found_exceptions import UserNotFoundException
from ports.repositories.user_repository import UserRepository


class SignInUserUseCase:
    def __init__(self, user_repository: UserRepository, jwt_service: JwtService) -> None:
        self._user_repository = user_repository
        self._jwt_service = jwt_service

    async def __call__(self, *, email: str, password: str) -> TokenPair:
        normalized_email = email.strip().lower()
        auth = await self._user_repository.get_auth_by_email(normalized_email)
        if auth is None:
            raise UserNotFoundException()

        user, password_hash = auth
        if not verify_password(password, password_hash):
            raise UnauthorizedException("Invalid email or password")

        return self._jwt_service.create_token_pair(user)
