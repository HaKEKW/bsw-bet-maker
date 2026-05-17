import jwt
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

import asyncpg
from sqlalchemy.exc import DBAPIError, OperationalError

from adapters.exceptions import DatabaseException, ExternalException
from drivers.rest.exception_handlers.exception_handlers import (
    database_error_handler,
    http_exception_handler_wrapper,
    integrity_error_handler,
    jwt_error_handler,
    status_code_400_exception_handler,
    status_code_401_exception_handler,
    status_code_403_exception_handler,
    status_code_404_exception_handler,
    status_code_409_exception_handler,
    status_code_422_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
    value_error_handler,
)
from usecases.exceptions.already_exists_exceptions import BaseAlreadyExists
from usecases.exceptions.auth_exceptions import ForbiddenException, UnauthorizedException
from usecases.exceptions.business_rule_exceptions import BaseBusinessRuleException
from usecases.exceptions.not_found_exceptions import BaseNotFoundException
from usecases.exceptions.validation_exceptions import MessageValidationException


def init_exception_container(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ExternalException, status_code_400_exception_handler)
    app.add_exception_handler(BaseNotFoundException, status_code_404_exception_handler)
    app.add_exception_handler(BaseAlreadyExists, status_code_409_exception_handler)
    app.add_exception_handler(BaseBusinessRuleException, status_code_400_exception_handler)
    app.add_exception_handler(UnauthorizedException, status_code_401_exception_handler)
    app.add_exception_handler(ForbiddenException, status_code_403_exception_handler)
    app.add_exception_handler(MessageValidationException, status_code_422_exception_handler)

    app.add_exception_handler(asyncpg.InvalidCatalogNameError, database_error_handler)
    app.add_exception_handler(OperationalError, database_error_handler)
    app.add_exception_handler(DBAPIError, database_error_handler)
    app.add_exception_handler(DatabaseException, database_error_handler)

    app.add_exception_handler(StarletteHTTPException, http_exception_handler_wrapper)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(jwt.PyJWTError, jwt_error_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
