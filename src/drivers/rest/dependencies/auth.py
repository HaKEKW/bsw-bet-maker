from functools import lru_cache

from adapters.auth.jwt_service import JwtService
from config.settings import get_settings


@lru_cache
def get_jwt_service() -> JwtService:
    return JwtService(get_settings())
