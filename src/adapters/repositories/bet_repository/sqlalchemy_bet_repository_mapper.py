from uuid import UUID

from adapters.connection_engines.sql_alchemy.models.bet import BetModel
from domain.entities.bet import Bet


class SQLAlchemyBetRepositoryMapper:
    @staticmethod
    def to_entity(bet_orm: BetModel) -> Bet:
        return Bet(
            id=bet_orm.id,
            event_id=bet_orm.event_id,
            user_id=str(bet_orm.user_id),
            amount=bet_orm.amount,
            winner_choice=bet_orm.winner_choice,
            coefficient=bet_orm.coefficient,
            status=bet_orm.status,
            created_at=bet_orm.created_at,
            finished_at=bet_orm.finished_at,
        )

    @staticmethod
    def to_model(bet_orm: BetModel, bet: Bet) -> None:
        bet_orm.id = bet.id
        bet_orm.event_id = bet.event_id
        bet_orm.user_id = int(bet.user_id)
        bet_orm.amount = bet.amount
        bet_orm.winner_choice = bet.winner_choice
        bet_orm.coefficient = bet.coefficient
        bet_orm.status = bet.status
        bet_orm.created_at = bet.created_at
        bet_orm.finished_at = bet.finished_at

    @staticmethod
    def parse_user_id(user_id: str | int) -> int:
        if isinstance(user_id, int):
            return user_id
        if isinstance(user_id, str) and user_id.isdigit():
            return int(user_id)
        raise ValueError(f"Bet user_id must be numeric for ORM mapping: {user_id}")

    @staticmethod
    def parse_bet_id(bet_id: str | UUID) -> UUID:
        if isinstance(bet_id, UUID):
            return bet_id
        return UUID(str(bet_id))
