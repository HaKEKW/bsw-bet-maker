from adapters.connection_engines.sql_alchemy.models.bet import BetModel
from adapters.connection_engines.sql_alchemy.models.user import UserModel
from adapters.repositories.bet_repository.sqlalchemy_bet_repository_mapper import (
    SQLAlchemyBetRepositoryMapper,
)
from adapters.repositories.user_repository.sqlalchemy_user_repository_mapper import (
    SQLAlchemyUserRepositoryMapper,
)
from domain.entities.bet import BetStatus, WinnerChoice
from domain.entities.user import UserRole
from tests.utils import make_bet


def test_user_mapper_round_trip():
    user_orm = UserModel(
        id=1,
        name="Alice",
        email="alice@example.com",
        password_hash="hash",
        role=UserRole.USER,
    )

    entity = SQLAlchemyUserRepositoryMapper.to_entity(user_orm)

    assert entity.id == 1
    assert entity.email == "alice@example.com"


def test_bet_mapper_round_trip():
    bet = make_bet(user_id="42", event_id="evt-1", status=BetStatus.PENDING)
    bet_orm = BetModel()

    SQLAlchemyBetRepositoryMapper.to_model(bet_orm, bet)
    restored = SQLAlchemyBetRepositoryMapper.to_entity(bet_orm)

    assert restored.user_id == "42"
    assert restored.event_id == "evt-1"
    assert restored.status == BetStatus.PENDING
    assert restored.winner_choice == WinnerChoice.LEFT_VICTORY
