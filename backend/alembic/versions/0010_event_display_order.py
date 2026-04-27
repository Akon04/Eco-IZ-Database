"""add event display order

Revision ID: 0010_event_display_order
Revises: 0009_event_registration_url
Create Date: 2026-04-23 03:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0010_event_display_order"
down_revision = "0009_event_registration_url"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("eco_events", sa.Column("display_order", sa.Integer(), nullable=False, server_default="100"))


def downgrade() -> None:
    op.drop_column("eco_events", "display_order")
