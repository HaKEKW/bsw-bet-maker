from contextlib import asynccontextmanager

from fastapi import FastAPI

from adapters.connection_engines.redis.redis_engine import RedisEngine
from config.logging import setup_logging
from config.settings import get_settings
from adapters.messaging.wiring import start_messaging, stop_messaging
from drivers.rest.exception_handlers.exception_container import init_exception_container
from drivers.rest.routers.v1.auth.auth import router as auth_router
from drivers.rest.routers.v1.bet.bet import router as bet_router
from drivers.rest.routers.v1.bets.bets import router as bets_router
from drivers.rest.routers.v1.events.events import router as events_router

setup_logging(get_settings())


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    redis = await RedisEngine.start(settings.redis_credentials)
    await start_messaging(settings)
    yield
    await stop_messaging()
    await redis.close()


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)
init_exception_container(app)

app.include_router(auth_router)
app.include_router(bet_router)
app.include_router(bets_router)
app.include_router(events_router)


@app.get("/healthcheck", include_in_schema=False)
def healthcheck() -> dict[str, str]:
    return {"status": "OK"}
