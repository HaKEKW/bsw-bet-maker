class UnauthorizedException(Exception):
    def __init__(self, message: str | None = None) -> None:
        self._message = message

    def __str__(self) -> str:
        return self._message or "Unauthorized"


class ForbiddenException(Exception):
    def __str__(self) -> str:
        return "Forbidden"
