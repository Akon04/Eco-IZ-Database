"""add eco events

Revision ID: 0008_eco_events
Revises: 0007_post_reports
Create Date: 2026-04-23 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0008_eco_events"
down_revision = "0007_post_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "eco_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reward_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("badge", sa.String(length=64), nullable=False, server_default="Бесплатно"),
        sa.Column("partner_name", sa.String(length=255), nullable=True),
        sa.Column("image_tint_hex", sa.Integer(), nullable=False, server_default=str(0x7ED957)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
    )
    op.create_index(op.f("ix_eco_events_is_active"), "eco_events", ["is_active"], unique=False)
    op.create_index(op.f("ix_eco_events_starts_at"), "eco_events", ["starts_at"], unique=False)
    op.create_index(op.f("ix_eco_events_title"), "eco_events", ["title"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_eco_events_title"), table_name="eco_events")
    op.drop_index(op.f("ix_eco_events_starts_at"), table_name="eco_events")
    op.drop_index(op.f("ix_eco_events_is_active"), table_name="eco_events")
    op.drop_table("eco_events")
