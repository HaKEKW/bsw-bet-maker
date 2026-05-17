import logging

import asyncpg
from fastapi import Request, Response, status
from fastapi.exception_handlers import request_validation_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from adapters.exceptions import DatabaseException, DatabaseNotFoundException
from usecases.exceptions.already_exists_exceptions import BaseAlreadyExists
from usecases.exceptions.auth_exceptions import UnauthorizedException

logger = logging.getLogger(__name__)


def json_detail(msg: str) -> dict:
    return {"detail": [{"msg": msg}]}


async def validation_exception_handler(request: Request, exc: Exception) -> Response:
    logger.error("RequestValidationError: \n%s", exc)
    return await request_validation_exception_handler(request, exc)  # type: ignore[arg-type]


async def status_code_400_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.warning(
        "Bad request on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=json_detail(str(exc)),
    )


async def status_code_401_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.warning(
        "Unauthorized on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=json_detail(str(exc)),
    )


async def status_code_403_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.warning(
        "Forbidden on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=json_detail(str(exc)),
    )


async def status_code_404_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.warning(
        "Not found on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=json_detail(str(exc)),
    )


async def status_code_409_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.warning(
        "Conflict on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=json_detail(str(exc)),
    )


async def status_code_422_exception_handler(
    request: Request, exc: Exception
) -> Response:
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=json_detail(str(exc)),
    )


async def http_exception_handler_wrapper(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, StarletteHTTPException)
    logger.warning(
        "HTTPException on %s %s: %s",
        request.method,
        request.url.path,
        exc.detail,
    )
    detail = exc.detail
    msg = detail if isinstance(detail, str) else str(detail)
    return JSONResponse(status_code=exc.status_code, content=json_detail(msg))


def _database_not_found_message(exc: BaseException) -> str | None:
    current: BaseException | None = exc
    while current is not None:
        if isinstance(current, asyncpg.InvalidCatalogNameError):
            return str(current)
        message = str(current).lower()
        if "database" in message and "does not exist" in message:
            return str(current)
        current = current.__cause__ or getattr(current, "orig", None)
    return None


def _database_internal_message(exc: BaseException) -> str:
    if isinstance(exc, DatabaseException) and exc.internal:
        return exc.internal
    if _database_not_found_message(exc):
        return _database_not_found_message(exc) or str(exc)
    cause = exc.__cause__ or getattr(exc, "orig", None)
    if cause is not None:
        return _database_internal_message(cause)
    return str(exc)


def _to_database_exception(exc: BaseException) -> DatabaseException:
    if isinstance(exc, DatabaseException):
        return exc
    internal = _database_internal_message(exc)
    if _database_not_found_message(exc):
        return DatabaseNotFoundException(internal=internal)
    return DatabaseException(internal=internal)


async def database_error_handler(request: Request, exc: Exception) -> Response:
    app_exc = _to_database_exception(exc)
    logger.error(
        "Database error on %s %s: %s | internal=%s",
        request.method,
        request.url.path,
        app_exc,
        app_exc.internal or "",
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=json_detail(str(app_exc)),
    )


async def integrity_error_handler(request: Request, exc: Exception) -> Response:
    logger.warning("IntegrityError on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=json_detail(str(BaseAlreadyExists())),
    )


async def jwt_error_handler(request: Request, exc: Exception) -> Response:
    logger.warning("JWT error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=json_detail(str(UnauthorizedException("Invalid or expired token"))),
    )


async def value_error_handler(request: Request, exc: Exception) -> Response:
    logger.warning("ValueError on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=json_detail(str(exc)),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=json_detail("Internal server error"),
    )
