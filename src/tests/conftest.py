import pytest
from fastapi.testclient import TestClient

from config.logging import setup_logging
from config.settings import get_settings

setup_logging(get_settings())

from tests.support.app import create_test_app
from tests.support.deps import InMemoryDeps
from tests.utils import make_event


@pytest.fixture
def container() -> InMemoryDeps:
    return InMemoryDeps()


@pytest.fixture
def seeded_container(container: InMemoryDeps) -> InMemoryDeps:
    container.line_provider.seed(make_event())
    return container


@pytest.fixture
def app(container: InMemoryDeps):
    return create_test_app(container)


@pytest.fixture
def seeded_app(seeded_container: InMemoryDeps):
    return create_test_app(seeded_container)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_client(seeded_app):
    with TestClient(seeded_app) as test_client:
        yield test_client
