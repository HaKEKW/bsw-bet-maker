import logging

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.connection_engines.sql_alchemy.models.user import UserModel
from adapters.repositories.user_repository.sqlalchemy_user_repository_mapper import (
    SQLAlchemyUserRepositoryMapper,
)
from adapters.exceptions import DatabaseException
from domain.entities.user import User, UserRole
from ports.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.mapper = SQLAlchemyUserRepositoryMapper()

    async def get_by_id(self, user_id: int) -> User | None:
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_orm = result.scalars().first()
            return self.mapper.to_entity(user_orm) if user_orm else None
        except SQLAlchemyError as exc:
            logger.exception("Failed to get user by id=%s", user_id)
            raise DatabaseException(internal=str(exc)) from exc

    async def get_by_email(self, email: str) -> User | None:
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user_orm = result.scalars().first()
            return self.mapper.to_entity(user_orm) if user_orm else None
        except SQLAlchemyError as exc:
            logger.exception("Failed to get user by email=%s", email)
            raise DatabaseException(internal=str(exc)) from exc

    async def get_auth_by_email(self, email: str) -> tuple[User, str] | None:
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user_orm = result.scalars().first()
            if user_orm is None:
                return None
            return self.mapper.to_entity(user_orm), user_orm.password_hash
        except SQLAlchemyError as exc:
            logger.exception("Failed to get auth for email=%s", email)
            raise DatabaseException(internal=str(exc)) from exc

    async def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        try:
            user_orm = UserModel()
            self.mapper.to_model(
                user_orm,
                name=name,
                email=email,
                password_hash=password_hash,
                role=role,
            )
            self.db.add(user_orm)
            await self.db.flush()
            await self.db.refresh(user_orm)
            return self.mapper.to_entity(user_orm)
        except SQLAlchemyError as exc:
            logger.exception("Failed to create user email=%s", email)
            raise DatabaseException(internal=str(exc)) from exc
