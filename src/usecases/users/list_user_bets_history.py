from domain.entities.bet import Bet
from ports.repositories.bet_repository import BetRepository


class ListUserBetsHistoryUseCase:
    def __init__(self, bet_repository: BetRepository):
        self._bet_repository = bet_repository

    async def __call__(self, user_id: str) -> list[Bet]:
        return await self._bet_repository.get_all_user_bets(user_id=user_id)
