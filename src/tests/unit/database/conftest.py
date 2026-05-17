import asyncpg
import pytest
from fastapi import FastAPI

from drivers.rest.exception_handlers.exception_container import init_exception_container


@pytest.fixture
def db_error_app() -> FastAPI:
    app = FastAPI()
    init_exception_container(app)

    @app.get("/boom")
    async def boom() -> None:
        raise asyncpg.InvalidCatalogNameError('database "bsw_bet_maker" does not exist')

    return app
