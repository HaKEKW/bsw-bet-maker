import pytest

from adapters.auth.jwt_service import JwtService
from adapters.repositories.bet_repository.in_memory_bet_repository import (
    InMemoryBetRepository,
)
from adapters.repositories.event_redis_repository.in_memory_event_repository import (
    InMemoryEventRepository,
)
from adapters.repositories.user_repository.in_memory_user_repository import (
    InMemoryUserRepository,
)
from tests.fakes.fake_line_provider import FakeLineProviderApi
from tests.support.app import TEST_SETTINGS
from usecases.bets.save_bet_use_case import SaveBetUseCase
from usecases.bets.update_bet_status_use_case import UpdateBetStatusUseCase
from usecases.events.add_event_use_case import AddEventUseCase
from usecases.events.list_events_use_case import ListEventsUseCase
from usecases.events.process_event_status_update_use_case import (
    ProcessEventStatusUpdateUseCase,
)


@pytest.fixture
def bet_repository() -> InMemoryBetRepository:
    return InMemoryBetRepository()


@pytest.fixture
def event_repository() -> InMemoryEventRepository:
    return InMemoryEventRepository()


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def jwt_service() -> JwtService:
    return JwtService(TEST_SETTINGS)


@pytest.fixture
def line_provider() -> FakeLineProviderApi:
    return FakeLineProviderApi()


@pytest.fixture
def save_bet_use_case(
    bet_repository: InMemoryBetRepository,
    event_repository: InMemoryEventRepository,
    line_provider: FakeLineProviderApi,
) -> SaveBetUseCase:
    return SaveBetUseCase(bet_repository, event_repository, line_provider)


@pytest.fixture
def update_bet_status_use_case(
    bet_repository: InMemoryBetRepository,
) -> UpdateBetStatusUseCase:
    return UpdateBetStatusUseCase(bet_repository)


@pytest.fixture
def list_events_use_case(
    event_repository: InMemoryEventRepository,
    line_provider: FakeLineProviderApi,
) -> ListEventsUseCase:
    return ListEventsUseCase(event_repository, line_provider)


@pytest.fixture
def add_event_use_case(event_repository: InMemoryEventRepository) -> AddEventUseCase:
    return AddEventUseCase(event_repository)


@pytest.fixture
def process_event_status_update_use_case(
    event_repository: InMemoryEventRepository,
    update_bet_status_use_case: UpdateBetStatusUseCase,
) -> ProcessEventStatusUpdateUseCase:
    return ProcessEventStatusUpdateUseCase(
        event_repository,
        update_bet_status_use_case,
    )
