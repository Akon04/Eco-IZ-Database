"""add event registration url

Revision ID: 0009_event_registration_url
Revises: 0008_eco_events
Create Date: 2026-04-23 03:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_event_registration_url"
down_revision = "0008_eco_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("eco_events", sa.Column("registration_url", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("eco_events", "registration_url")
