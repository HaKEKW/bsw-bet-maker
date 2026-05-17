from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient

from tests.support.app import create_test_app
from tests.support.deps import InMemoryDeps


@contextmanager
def open_api_client(container: InMemoryDeps) -> Iterator[TestClient]:
    with TestClient(create_test_app(container)) as client:
        yield client
