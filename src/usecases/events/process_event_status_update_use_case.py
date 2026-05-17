from datetime import timedelta

from domain.entities.bet import Bet
from domain.entities.event import Event, EventStatus, InputEventStatus
from ports.repositories.event_repository import EventRepository
from usecases.bets.update_bet_status_use_case import UpdateBetStatusUseCase


class ProcessEventStatusUpdateUseCase:
    def __init__(
        self,
        event_repository: EventRepository,
        update_bet_status_use_case: UpdateBetStatusUseCase,
    ) -> None:
        self._event_repository = event_repository
        self._update_bet_status_use_case = update_bet_status_use_case

    async def __call__(self, event: Event) -> list[Bet]:
        await self._event_repository.upsert(event, expire=timedelta(minutes=5))

        if event.status not in {EventStatus.LEFT_VICTORY, EventStatus.RIGHT_VICTORY}:
            return []

        return await self._update_bet_status_use_case(
            InputEventStatus(event_id=event.id, status=event.status)
        )
