"""activity media proof attachments"""

from alembic import op
import sqlalchemy as sa


revision = "0005_activity_media"
down_revision = "0004_session_expiry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activity_media",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("activity_id", sa.Uuid(), sa.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
    )
    op.create_index("ix_activity_media_activity_id", "activity_media", ["activity_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_activity_media_activity_id", table_name="activity_media")
    op.drop_table("activity_media")
