"""initial schema

Revision ID: 20260302_0001
Revises:
Create Date: 2026-03-02 20:15:00.000000

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260302_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("budget_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("budget_max", sa.Numeric(10, 2), nullable=True),
        sa.Column("preferred_brands", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("avoid_brands", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("shipping_speed_preference", sa.String(length=32), nullable=False),
        sa.Column("use_case_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profiles_user_id", "profiles", ["user_id"], unique=False)

    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("final_output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_runs_profile_id", "runs", ["profile_id"], unique=False)
    op.create_index("ix_runs_status", "runs", ["status"], unique=False)
    op.create_index("ix_runs_user_id", "runs", ["user_id"], unique=False)

    op.create_table(
        "feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("feedback_type", sa.String(length=32), nullable=False),
        sa.Column("product_provider", sa.String(length=64), nullable=True),
        sa.Column("product_id", sa.String(length=128), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_profile_id", "feedback", ["profile_id"], unique=False)
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"], unique=False)

    op.create_table(
        "product_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("external_product_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_product_snapshots_external_product_id",
        "product_snapshots",
        ["external_product_id"],
        unique=False,
    )
    op.create_index("ix_product_snapshots_provider", "product_snapshots", ["provider"], unique=False)
    op.create_index("ix_product_snapshots_run_id", "product_snapshots", ["run_id"], unique=False)

    op.create_table(
        "run_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("agent_name", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_run_events_agent_name", "run_events", ["agent_name"], unique=False)
    op.create_index("ix_run_events_event_type", "run_events", ["event_type"], unique=False)
    op.create_index("ix_run_events_run_id", "run_events", ["run_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_run_events_run_id", table_name="run_events")
    op.drop_index("ix_run_events_event_type", table_name="run_events")
    op.drop_index("ix_run_events_agent_name", table_name="run_events")
    op.drop_table("run_events")

    op.drop_index("ix_product_snapshots_run_id", table_name="product_snapshots")
    op.drop_index("ix_product_snapshots_provider", table_name="product_snapshots")
    op.drop_index("ix_product_snapshots_external_product_id", table_name="product_snapshots")
    op.drop_table("product_snapshots")

    op.drop_index("ix_feedback_user_id", table_name="feedback")
    op.drop_index("ix_feedback_profile_id", table_name="feedback")
    op.drop_table("feedback")

    op.drop_index("ix_runs_user_id", table_name="runs")
    op.drop_index("ix_runs_status", table_name="runs")
    op.drop_index("ix_runs_profile_id", table_name="runs")
    op.drop_table("runs")

    op.drop_index("ix_profiles_user_id", table_name="profiles")
    op.drop_table("profiles")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
