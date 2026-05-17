from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class BetStatus(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"


class WinnerChoice(str, Enum):
    LEFT_VICTORY = "left_victory"
    RIGHT_VICTORY = "right_victory"


@dataclass
class Bet:
    event_id: str
    user_id: str
    amount: float
    winner_choice: WinnerChoice
    id: UUID = field(default_factory=uuid4)
    coefficient: float | None = None
    status: BetStatus | None = None
    created_at: datetime | None = field(default=None, compare=False)
    finished_at: datetime | None = field(default=None, compare=False)
