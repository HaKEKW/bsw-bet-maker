from typing import Any

from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def build_database_url(database_credentials: str | dict[str, Any]) -> URL:
    if isinstance(database_credentials, str):
        return make_url(database_credentials)

    return URL.create(**database_credentials)


def create_sqlalchemy_engine(
    db_credentials: dict[str, Any],
    *,
    echo: bool = False,
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_recycle: int = -1,
    pool_pre_ping: bool = True,
) -> async_sessionmaker[AsyncSession]:

    database_url = build_database_url(db_credentials)
    engine = create_async_engine(
        database_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
        pool_pre_ping=pool_pre_ping,
        pool_reset_on_return=None,
    )
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
