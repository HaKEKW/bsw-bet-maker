from copy import deepcopy

from domain.entities.user import User, UserRole
from ports.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, tuple[User, str]] = {}
        self._email_index: dict[str, int] = {}
        self._next_id = 1

    async def get_by_id(self, user_id: int) -> User | None:
        entry = self._users.get(user_id)
        return deepcopy(entry[0]) if entry else None

    async def get_by_email(self, email: str) -> User | None:
        user_id = self._email_index.get(email.strip().lower())
        if user_id is None:
            return None
        return await self.get_by_id(user_id)

    async def get_auth_by_email(self, email: str) -> tuple[User, str] | None:
        user_id = self._email_index.get(email.strip().lower())
        if user_id is None:
            return None
        user, password_hash = self._users[user_id]
        return deepcopy(user), password_hash

    async def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        normalized_email = email.strip().lower()
        user = User(id=self._next_id, name=name, email=normalized_email, role=role)
        self._users[self._next_id] = (user, password_hash)
        self._email_index[normalized_email] = self._next_id
        self._next_id += 1
        return deepcopy(user)

    def clear(self) -> None:
        self._users.clear()
        self._email_index.clear()
        self._next_id = 1
