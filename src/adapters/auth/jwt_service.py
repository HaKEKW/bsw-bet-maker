from datetime import datetime, timedelta, timezone

import jwt

from adapters.auth.token_pair import TokenPair
from config.settings import Settings
from domain.entities.user import User, UserRole


class JwtService:
    def __init__(self, settings: Settings) -> None:
        self._secret_key = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._access_expire_minutes = settings.jwt_access_token_expire_minutes
        self._refresh_expire_days = settings.jwt_refresh_token_expire_days

    def create_token_pair(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=self._create_token(
                user, "access", self._access_expire_minutes
            ),
            refresh_token=self._create_token(
                user,
                "refresh",
                self._refresh_expire_days * 24 * 60,
            ),
        )

    def decode_access_token(self, token: str) -> dict:
        payload = self._decode(token)
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError("Invalid access token type")
        return payload

    def decode_refresh_token(self, token: str) -> dict:
        payload = self._decode(token)
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError("Invalid refresh token type")
        return payload

    def user_from_access_payload(self, payload: dict) -> User:
        return User(
            id=int(payload["sub"]),
            name=payload["name"],
            email=payload["email"],
            role=UserRole(payload["role"]),
        )

    def _create_token(self, user: User, token_type: str, expire_minutes: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        payload = {
            "sub": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "type": token_type,
            "exp": expire,
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def _decode(self, token: str) -> dict:
        return jwt.decode(
            token,
            self._secret_key,
            algorithms=[self._algorithm],
        )
