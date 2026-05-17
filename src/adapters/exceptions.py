class ExternalException(Exception):
    def __str__(self) -> str:
        return "Something goes wrong. Please try again later"


class LineProviderException(ExternalException):
    pass


class DatabaseException(ExternalException):
    def __init__(self, *, internal: str | None = None) -> None:
        self.internal = internal

    def __str__(self) -> str:
        return "Database is not available"


class DatabaseNotFoundException(DatabaseException):
    pass
