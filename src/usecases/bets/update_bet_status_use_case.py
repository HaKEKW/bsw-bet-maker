from datetime import datetime

from domain.entities.bet import Bet, BetStatus, WinnerChoice
from domain.entities.event import EventStatus, InputEventStatus
from ports.repositories.bet_repository import BetRepository


class UpdateBetStatusUseCase:
    def __init__(self, bet_repository: BetRepository):
        self._bet_repository = bet_repository

    async def __call__(self, event_status: InputEventStatus) -> list[Bet]:
        bets = await self._bet_repository.get_all_bets_by_event(
            event_id=event_status.event_id
        )
        updated: list[Bet] = []
        for bet in bets:
            if bet.status != BetStatus.PENDING:
                continue
            if (
                bet.winner_choice == WinnerChoice.LEFT_VICTORY
                and event_status.status == EventStatus.LEFT_VICTORY
            ) or (
                bet.winner_choice == WinnerChoice.RIGHT_VICTORY
                and event_status.status == EventStatus.RIGHT_VICTORY
            ):
                bet.status = BetStatus.WON
            else:
                bet.status = BetStatus.LOST

            bet.finished_at = datetime.now()
            await self._bet_repository.save(bet)
            updated.append(bet)
        return updated
