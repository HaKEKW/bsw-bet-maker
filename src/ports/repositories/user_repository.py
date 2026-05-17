from abc import ABC, abstractmethod

from domain.entities.user import User, UserRole


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_auth_by_email(self, email: str) -> tuple[User, str] | None:
        pass

    @abstractmethod
    async def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        pass
