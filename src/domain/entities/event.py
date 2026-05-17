from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EventStatus(str, Enum):
    LIVE = "live"
    LEFT_VICTORY = "left_victory"
    RIGHT_VICTORY = "right_victory"


@dataclass
class Event:
    id: str
    name: str
    description: str
    coefficient: float
    status: EventStatus
    bet_deadline_at: datetime
    created_at: datetime
    finished_at: datetime | None = field(default=None, compare=False)

    @property
    def is_bet_deadline_open(self) -> bool:
        now = (
            datetime.now(self.bet_deadline_at.tzinfo)
            if self.bet_deadline_at.tzinfo
            else datetime.now()
        )
        return now < self.bet_deadline_at

    @property
    def is_active(self) -> bool:
        return self.status == EventStatus.LIVE and self.is_bet_deadline_open


@dataclass
class InputEventStatus:
    event_id: str
    status: EventStatus
