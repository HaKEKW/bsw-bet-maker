from abc import ABC, abstractmethod
from typing import Any

from domain.entities.bet import Bet


class BetRepository(ABC):
    @abstractmethod
    async def get(self, **filters: Any) -> Bet | None:
        pass

    @abstractmethod
    async def get_all_user_bets(self, **filters: Any) -> list[Bet]:
        pass

    @abstractmethod
    async def get_all_bets_by_event(self, **filters: Any) -> list[Bet]:
        pass

    @abstractmethod
    async def save(self, bet: Bet) -> None:
        pass
