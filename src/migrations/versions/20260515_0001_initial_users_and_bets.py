"""initial users and bets tables

Revision ID: 20260515_0001
Revises:
Create Date: 2026-05-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "user", name="user_role", native_enum=False),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "bets",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column(
            "winner_choice",
            sa.Enum(
                "left_victory",
                "right_victory",
                name="winner_choice",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("coefficient", sa.Float(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "won", "lost", name="bet_status", native_enum=False),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bets_event_id"), "bets", ["event_id"], unique=False)
    op.create_index(op.f("ix_bets_user_id"), "bets", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_bets_user_id"), table_name="bets")
    op.drop_index(op.f("ix_bets_event_id"), table_name="bets")
    op.drop_table("bets")
    op.drop_table("users")
