from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adapters.connection_engines.sql_alchemy.models.base import Base
from domain.entities.bet import BetStatus, WinnerChoice

if TYPE_CHECKING:
    from adapters.connection_engines.sql_alchemy.models.user import UserModel


class BetModel(Base):
    __tablename__ = "bets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    winner_choice: Mapped[WinnerChoice] = mapped_column(
        SAEnum(WinnerChoice, name="winner_choice", native_enum=False),
        nullable=False,
    )
    coefficient: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[BetStatus | None] = mapped_column(
        SAEnum(BetStatus, name="bet_status", native_enum=False),
        nullable=True,
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["UserModel"] = relationship(back_populates="bets")
