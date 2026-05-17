from asyncio import current_task
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
)

from adapters.connection_engines.sql_alchemy.sqlalchemy_engine import (
    create_sqlalchemy_engine,
)
from config.settings import Settings, get_settings


class SQLAlchemyDependency:
    def __init__(self) -> None:
        self._engine: async_sessionmaker[AsyncSession] | None = None

    def __call__(
        self, settings: Annotated[Settings, Depends(get_settings)]
    ) -> async_sessionmaker[AsyncSession]:
        if not self._engine:
            self._engine = create_sqlalchemy_engine(
                settings.database_credentials,
                echo=settings.debug,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                pool_recycle=settings.database_pool_recycle,
                pool_pre_ping=settings.database_pool_pre_ping,
            )
        return self._engine


sqlalchemy_engine = SQLAlchemyDependency()


async def get_session(
    engine: Annotated[async_sessionmaker[AsyncSession], Depends(sqlalchemy_engine)],
) -> AsyncGenerator[AsyncSession, None]:
    async with engine() as session, session.begin():
        yield session


async def get_scoped_session_factory(
    engine: Annotated[async_sessionmaker[AsyncSession], Depends(sqlalchemy_engine)],
) -> async_scoped_session[AsyncSession]:
    return async_scoped_session(engine, scopefunc=current_task)
