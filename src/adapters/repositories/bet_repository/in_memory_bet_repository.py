from copy import deepcopy
from typing import Any

from domain.entities.bet import Bet
from ports.repositories.bet_repository import BetRepository


class InMemoryBetRepository(BetRepository):
    def __init__(self) -> None:
        self._bets: list[Bet] = []

    async def get(self, **filters: Any) -> Bet | None:
        if not filters:
            return None
        for bet in self._bets:
            if all(
                (value := filters.get(key)) is None or getattr(bet, key, None) == value
                for key in filters
            ):
                return deepcopy(bet)
        return None

    async def get_all_user_bets(self, **filters: Any) -> list[Bet]:
        return [
            deepcopy(bet)
            for bet in self._bets
            if (f := filters.get("user_id")) and f == bet.user_id
        ]

    async def get_all_bets_by_event(self, **filters: Any) -> list[Bet]:
        if not filters:
            return list(self._bets)
        return [
            deepcopy(bet)
            for bet in self._bets
            if (f := filters.get("event_id")) and f == bet.event_id
        ]

    async def save(self, bet: Bet) -> None:
        for i, existing in enumerate(self._bets):
            if existing.id == bet.id:
                self._bets[i] = bet
                return
        self._bets.append(bet)
