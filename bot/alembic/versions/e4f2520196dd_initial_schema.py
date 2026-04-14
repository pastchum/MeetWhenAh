"""initial schema

Revision ID: e4f2520196dd
Revises:
Create Date: 2026-04-13 15:13:25.289715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'e4f2520196dd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("uuid", UUID(as_uuid=True), primary_key=True),
        sa.Column("tele_id", sa.BigInteger(), unique=True),
        sa.Column("tele_user", sa.Text(), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("initialised", sa.Boolean(), server_default="false"),
        sa.Column("callout_cleared", sa.Boolean(), server_default="false"),
        sa.Column("sleep_start_time", sa.Time(timezone=True)),
        sa.Column("sleep_end_time", sa.Time(timezone=True)),
        sa.Column("tmp_sleep_start", sa.Time(timezone=True)),
    )

    # --- events ---
    op.create_table(
        "events",
        sa.Column("event_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_name", sa.Text(), nullable=False),
        sa.Column("event_description", sa.Text(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("start_hour", sa.Time(timezone=True), nullable=False, server_default=sa.text("'00:00:00+08:00'")),
        sa.Column("end_hour", sa.Time(timezone=True), nullable=False, server_default=sa.text("'23:30:00+08:00'")),
        sa.Column("min_participants", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("min_duration", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("max_duration", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("is_reminders_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("timezone", sa.Text(), nullable=False, server_default="'Asia/Singapore'"),
        sa.Column("cancelled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("creator", UUID(as_uuid=True), sa.ForeignKey("users.uuid", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_events_creator", "events", ["creator"])

    # --- confirmed_events ---
    op.create_table(
        "confirmed_events",
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.event_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("confirmed_start_time", sa.DateTime(timezone=True)),
        sa.Column("confirmed_end_time", sa.DateTime(timezone=True)),
    )

    # --- event_chats ---
    op.create_table(
        "event_chats",
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.event_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("chat_id", sa.BigInteger(), primary_key=True),
        sa.Column("thread_id", sa.BigInteger()),
    )

    # --- membership ---
    op.create_table(
        "membership",
        sa.Column("user_uuid", UUID(as_uuid=True), sa.ForeignKey("users.uuid", ondelete="CASCADE"), primary_key=True),
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.event_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("emoji_icon", sa.Text(), nullable=False),
    )
    op.create_index("idx_membership_event_id", "membership", ["event_id"])
    op.create_index("idx_membership_user_uuid", "membership", ["user_uuid"])

    # --- availability_blocks ---
    op.create_table(
        "availability_blocks",
        sa.Column("event_id", UUID(as_uuid=True), sa.ForeignKey("events.event_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_uuid", UUID(as_uuid=True), sa.ForeignKey("users.uuid", ondelete="CASCADE"), primary_key=True),
        sa.Column("start_time", sa.DateTime(timezone=True), primary_key=True, nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_availability_blocks_event_id", "availability_blocks", ["event_id"])
    op.create_index("idx_availability_blocks_user_uuid", "availability_blocks", ["user_uuid"])
    op.create_index("idx_availability_blocks_start_time", "availability_blocks", ["start_time"])

    # --- blocked_timings ---
    op.create_table(
        "blocked_timings",
        sa.Column("uuid", UUID(as_uuid=True), sa.ForeignKey("users.uuid", ondelete="CASCADE"), primary_key=True),
        sa.Column("start_time", sa.DateTime(timezone=True), primary_key=True, nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), primary_key=True, nullable=False),
    )
    op.create_index("idx_blocked_timings_uuid", "blocked_timings", ["uuid"])

    # --- webapp_share_tokens ---
    op.create_table(
        "webapp_share_tokens",
        sa.Column("token", sa.Text(), primary_key=True),
        sa.Column("tele_id", sa.BigInteger(), sa.ForeignKey("users.tele_id"), nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("thread_id", sa.BigInteger()),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True)),
    )
    op.create_index("idx_share_tokens_expires", "webapp_share_tokens", ["expires_at"])
    op.create_index("idx_share_tokens_user", "webapp_share_tokens", ["tele_id"])


def downgrade() -> None:
    op.drop_table("webapp_share_tokens")
    op.drop_table("blocked_timings")
    op.drop_table("availability_blocks")
    op.drop_table("membership")
    op.drop_table("event_chats")
    op.drop_table("confirmed_events")
    op.drop_table("events")
    op.drop_table("users")
