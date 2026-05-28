from datetime import datetime, timedelta
from uuid import uuid4

from adapters.repositories.event_redis_repository.redis_event_repository_mapper import (
    RedisEventRepositoryMapper,
)
from domain.entities.bet import Bet, BetStatus
from domain.entities.event import Event
from usecases.exceptions.business_rule_exceptions import BetDeadlinePassedException
from ports.api.line_provider_api import LineProviderApi
from ports.repositories.bet_repository import BetRepository
from ports.repositories.event_repository import EventRepository


class SaveBetUseCase:
    def __init__(
        self,
        bet_repository: BetRepository,
        event_repository: EventRepository,
        line_provider_api: LineProviderApi,
    ):
        self._bet_repository = bet_repository
        self._event_repository = event_repository
        self._line_provider_api = line_provider_api

    async def __call__(self, bet: Bet) -> Bet:
        event = await self.__get_event(bet.event_id)
        if not event.is_bet_deadline_open:
            raise BetDeadlinePassedException()
        await self.__ensure_unique_bet_id(bet)
        bet.coefficient = event.coefficient
        bet.status = BetStatus.PENDING
        bet.created_at = datetime.now()
        await self._bet_repository.save(bet)
        return bet

    async def __ensure_unique_bet_id(self, bet: Bet) -> None:
        if await self._bet_repository.get(id=bet.id) is None:
            return
        bet.id = uuid4()

    async def __get_event(self, event_id: str) -> Event:
        if (event := await self._event_repository.get(event_id)) is None:
            event = await self.__get_event_from_api(event_id)
        return event

    async def __get_event_from_api(self, event_id: str) -> Event:
        event = await self._line_provider_api.get_event(event_id)
        await self._event_repository.save(
            event_id,
            RedisEventRepositoryMapper.to_event_payload(event),
            expire=timedelta(minutes=5),
        )
        return event
