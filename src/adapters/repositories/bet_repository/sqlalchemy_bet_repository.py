import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.connection_engines.sql_alchemy.models.bet import BetModel
from adapters.exceptions import DatabaseException
from adapters.repositories.bet_repository.sqlalchemy_bet_repository_mapper import (
    SQLAlchemyBetRepositoryMapper,
)
from domain.entities.bet import Bet
from ports.repositories.bet_repository import BetRepository

logger = logging.getLogger(__name__)


class SQLAlchemyBetRepository(BetRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.mapper = SQLAlchemyBetRepositoryMapper()

    async def get(self, **filters: Any) -> Bet | None:
        if not filters:
            return None

        try:
            query = select(BetModel)
            if bet_id := filters.get("id"):
                query = query.where(BetModel.id == self.mapper.parse_bet_id(bet_id))
            if event_id := filters.get("event_id"):
                query = query.where(BetModel.event_id == event_id)
            if user_id := filters.get("user_id"):
                query = query.where(
                    BetModel.user_id == self.mapper.parse_user_id(user_id)
                )

            result = await self.db.execute(query)
            bet_orm = result.scalars().first()
            return self.mapper.to_entity(bet_orm) if bet_orm else None
        except (SQLAlchemyError, ValueError) as exc:
            logger.exception("Failed to get bet with filters=%s", filters)
            raise DatabaseException(internal=str(exc)) from exc

    async def get_all_user_bets(self, **filters: Any) -> list[Bet]:
        user_id = filters.get("user_id")
        if not user_id:
            return []

        try:
            query = select(BetModel).where(
                BetModel.user_id == self.mapper.parse_user_id(user_id)
            )
            result = await self.db.execute(query)
            return [self.mapper.to_entity(bet) for bet in result.scalars().all()]
        except (SQLAlchemyError, ValueError) as exc:
            logger.exception("Failed to list bets for user_id=%s", user_id)
            raise DatabaseException(internal=str(exc)) from exc

    async def get_all_bets_by_event(self, **filters: Any) -> list[Bet]:
        try:
            query = select(BetModel)
            if event_id := filters.get("event_id"):
                query = query.where(BetModel.event_id == event_id)

            result = await self.db.execute(query)
            return [self.mapper.to_entity(bet) for bet in result.scalars().all()]
        except SQLAlchemyError as exc:
            logger.exception("Failed to list bets for filters=%s", filters)
            raise DatabaseException(internal=str(exc)) from exc

    async def save(self, bet: Bet) -> None:
        try:
            query = select(BetModel).where(BetModel.id == bet.id)
            result = await self.db.execute(query)
            bet_orm = result.scalars().first()
            if bet_orm is None:
                bet_orm = BetModel()

            self.mapper.to_model(bet_orm, bet)
            self.db.add(bet_orm)
            await self.db.flush()
            await self.db.refresh(bet_orm)

            bet.id = bet_orm.id
            bet.created_at = bet_orm.created_at
            bet.finished_at = bet_orm.finished_at
            bet.status = bet_orm.status
            bet.coefficient = bet_orm.coefficient
        except (SQLAlchemyError, ValueError) as exc:
            logger.exception("Failed to save bet id=%s", bet.id)
            raise DatabaseException(internal=str(exc)) from exc
