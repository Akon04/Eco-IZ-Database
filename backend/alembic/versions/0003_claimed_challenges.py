"""claimed challenges"""

from alembic import op
import sqlalchemy as sa


revision = "0003_claimed_challenges"
down_revision = "0002_admin_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_challenges", sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("user_challenges", "claimed_at")
