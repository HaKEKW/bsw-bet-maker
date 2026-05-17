from dataclasses import dataclass, field

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


@dataclass
class InMemoryDeps:
    bet_repository: InMemoryBetRepository = field(default_factory=InMemoryBetRepository)
    event_repository: InMemoryEventRepository = field(
        default_factory=InMemoryEventRepository
    )
    user_repository: InMemoryUserRepository = field(default_factory=InMemoryUserRepository)
    line_provider: FakeLineProviderApi = field(default_factory=FakeLineProviderApi)
