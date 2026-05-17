from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.connection_engines.redis.redis_engine import get_redis
from adapters.repositories.bet_repository.sqlalchemy_bet_repository import (
    SQLAlchemyBetRepository,
)
from adapters.repositories.event_redis_repository.redis_event_repository import (
    RedisEventRepository,
)
from adapters.repositories.user_repository.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from drivers.rest.dependencies.database import get_session
from ports.repositories.bet_repository import BetRepository
from ports.repositories.event_repository import EventRepository
from ports.repositories.user_repository import UserRepository


def get_bet_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BetRepository:
    return SQLAlchemyBetRepository(session)


def get_event_repository() -> EventRepository:
    return RedisEventRepository(get_redis())


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return SQLAlchemyUserRepository(session)
