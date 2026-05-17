import asyncpg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from adapters.exceptions import DatabaseException, DatabaseNotFoundException
from drivers.rest.exception_handlers.exception_handlers import _to_database_exception


def test_to_database_exception_for_invalid_catalog_name():
    exc = asyncpg.InvalidCatalogNameError('database "bsw_bet_maker" does not exist')
    app_exc = _to_database_exception(exc)

    assert isinstance(app_exc, DatabaseNotFoundException)
    assert str(app_exc) == "Database is not available"
    assert "bsw_bet_maker" in (app_exc.internal or "")


def test_to_database_exception_for_operational_error_wrapping_asyncpg():
    orig = asyncpg.InvalidCatalogNameError('database "bsw_bet_maker" does not exist')
    exc = OperationalError("connection failed", {}, orig)
    app_exc = _to_database_exception(exc)

    assert isinstance(app_exc, DatabaseNotFoundException)


def test_to_database_exception_preserves_wrapped_internal():
    original = Exception("connection is closed")
    wrapped = DatabaseException(internal=str(original))

    app_exc = _to_database_exception(wrapped)

    assert app_exc.internal == "connection is closed"


def test_database_error_handler_returns_503_without_traceback(db_error_app):
    with TestClient(db_error_app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 503
    body = response.json()["detail"][0]
    assert body["msg"] == "Database is not available"
    assert "internal" not in body
    assert "code" not in body
