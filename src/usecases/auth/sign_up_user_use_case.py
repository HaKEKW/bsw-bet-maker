from adapters.auth.jwt_service import JwtService
from adapters.auth.password_hasher import hash_password
from adapters.auth.token_pair import TokenPair
from usecases.exceptions.already_exists_exceptions import UserAlreadyExists
from domain.entities.user import User, UserRole
from ports.repositories.user_repository import UserRepository


class SignUpUserUseCase:
    def __init__(self, user_repository: UserRepository, jwt_service: JwtService) -> None:
        self._user_repository = user_repository
        self._jwt_service = jwt_service

    async def __call__(
        self,
        *,
        name: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
    ) -> tuple[User, TokenPair]:
        normalized_email = email.strip().lower()
        if await self._user_repository.get_by_email(normalized_email):
            raise UserAlreadyExists({"email": normalized_email})

        user = await self._user_repository.create(
            name=name.strip(),
            email=normalized_email,
            password_hash=hash_password(password),
            role=role,
        )
        return user, self._jwt_service.create_token_pair(user)
