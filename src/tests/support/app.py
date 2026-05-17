from contextlib import asynccontextmanager

from fastapi import FastAPI

from adapters.auth.jwt_service import JwtService
from config.settings import Settings
from drivers.rest.dependencies.auth import get_jwt_service
from drivers.rest.dependencies.line_provider import get_line_provider_api
from drivers.rest.dependencies.repositories import (
    get_bet_repository,
    get_event_repository,
    get_user_repository,
)
from drivers.rest.exception_handlers.exception_container import init_exception_container
from drivers.rest.routers.v1.auth.auth import router as auth_router
from drivers.rest.routers.v1.bet.bet import router as bet_router
from drivers.rest.routers.v1.bets.bets import router as bets_router
from drivers.rest.routers.v1.events.events import router as events_router
from tests.support.deps import InMemoryDeps

TEST_SETTINGS = Settings(
    jwt_secret_key="test-secret-key-at-least-32-bytes-long",
    jwt_access_token_expire_minutes=60,
    jwt_refresh_token_expire_days=7,
)


@asynccontextmanager
async def _test_lifespan(_app: FastAPI):
    yield


def create_test_app(container: InMemoryDeps) -> FastAPI:
    app = FastAPI(title="bsw-bet-maker-test", lifespan=_test_lifespan)
    init_exception_container(app)

    app.include_router(auth_router)
    app.include_router(bet_router)
    app.include_router(bets_router)
    app.include_router(events_router)

    @app.get("/healthcheck", include_in_schema=False)
    def healthcheck() -> dict[str, str]:
        return {"status": "OK"}

    jwt_service = JwtService(TEST_SETTINGS)

    app.dependency_overrides[get_bet_repository] = lambda: container.bet_repository
    app.dependency_overrides[get_event_repository] = lambda: container.event_repository
    app.dependency_overrides[get_user_repository] = lambda: container.user_repository
    app.dependency_overrides[get_line_provider_api] = lambda: container.line_provider
    app.dependency_overrides[get_jwt_service] = lambda: jwt_service

    return app
