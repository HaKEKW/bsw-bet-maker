from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from domain.entities.bet import Bet, BetStatus, WinnerChoice


class BetInput(BaseModel):
    event_id: str
    amount: float = Field(gt=0)
    winner_choice: WinnerChoice

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: float) -> float:
        if round(value, 2) != value:
            raise ValueError("Amount should have at most 2 decimal places")
        return value

    def to_entity(self, user_id: str) -> Bet:
        return Bet(
            id=uuid4(),
            user_id=user_id,
            event_id=self.event_id,
            winner_choice=self.winner_choice,
            amount=self.amount,
        )


class BetItem(BaseModel):
    token: UUID
    user_id: str
    event_id: str
    amount: float
    coefficient: float
    possible_win: float
    status: BetStatus
    created_at: datetime | None = None
    finished_at: datetime | None = None

    @classmethod
    def from_entity(cls, bet: Bet) -> "BetItem":
        coefficient = bet.coefficient or 0.0
        return cls(
            token=bet.id,
            event_id=bet.event_id,
            user_id=bet.user_id,
            amount=bet.amount,
            coefficient=coefficient,
            possible_win=round(bet.amount * coefficient, 2),
            status=bet.status or BetStatus.PENDING,
            created_at=bet.created_at,
            finished_at=bet.finished_at,
        )
