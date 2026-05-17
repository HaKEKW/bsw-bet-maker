from adapters.connection_engines.sql_alchemy.sqlalchemy_engine import (
    build_database_url,
    create_sqlalchemy_engine,
)
from config.settings import Settings


def test_build_database_url_from_credentials_dict():
    url = build_database_url(
        {
            "drivername": "postgresql+asyncpg",
            "username": "postgres",
            "password": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "bsw_bet_maker",
        }
    )

    assert url.drivername == "postgresql+asyncpg"
    assert url.username == "postgres"
    assert url.database == "bsw_bet_maker"


def test_settings_database_credentials_parsed_from_url():
    settings = Settings(
        database_url="postgresql+asyncpg://postgres:postgres@postgres:5432/bsw_bet_maker"
    )

    credentials = settings.database_credentials

    assert credentials["drivername"] == "postgresql+asyncpg"
    assert credentials["username"] == "postgres"
    assert credentials["host"] == "postgres"
    assert credentials["port"] == 5432
    assert credentials["database"] == "bsw_bet_maker"


def test_create_sqlalchemy_engine_returns_session_maker():
    session_maker = create_sqlalchemy_engine(
        {
            "drivername": "postgresql+asyncpg",
            "username": "postgres",
            "password": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "bsw_bet_maker",
        }
    )

    assert session_maker is not None
