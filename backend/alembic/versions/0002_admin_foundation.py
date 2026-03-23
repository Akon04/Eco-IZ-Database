"""admin foundation"""

from alembic import op
import sqlalchemy as sa


revision = "0002_admin_foundation"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("role", sa.String(length=32), nullable=False, server_default="USER"))
    op.add_column("users", sa.Column("status", sa.String(length=32), nullable=False, server_default="ACTIVE"))
    op.add_column("users", sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("admin_note", sa.Text(), nullable=True))
    op.execute("UPDATE users SET username = split_part(email, '@', 1) WHERE username IS NULL")
    op.alter_column("users", "username", nullable=False)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.add_column("posts", sa.Column("visibility", sa.String(length=32), nullable=False, server_default="PUBLIC"))
    op.add_column("posts", sa.Column("moderation_state", sa.String(length=32), nullable=False, server_default="Published"))
    op.add_column("posts", sa.Column("reports_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("posts", sa.Column("moderator_note", sa.Text(), nullable=True))

    op.create_table(
        "eco_categories",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("color", sa.String(length=32), nullable=False, server_default="#43B244"),
        sa.Column("icon", sa.String(length=64), nullable=False, server_default="leaf"),
    )
    op.create_index("ix_eco_categories_name", "eco_categories", ["name"], unique=True)

    op.create_table(
        "habits",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("co2_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("water_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("energy_value", sa.Float(), nullable=False, server_default="0"),
        sa.Column("category_id", sa.Uuid(), sa.ForeignKey("eco_categories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_habits_title", "habits", ["title"])
    op.create_index("ix_habits_category_id", "habits", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_habits_category_id", table_name="habits")
    op.drop_index("ix_habits_title", table_name="habits")
    op.drop_table("habits")
    op.drop_index("ix_eco_categories_name", table_name="eco_categories")
    op.drop_table("eco_categories")

    op.drop_column("posts", "moderator_note")
    op.drop_column("posts", "reports_count")
    op.drop_column("posts", "moderation_state")
    op.drop_column("posts", "visibility")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "admin_note")
    op.drop_column("users", "is_email_verified")
    op.drop_column("users", "status")
    op.drop_column("users", "role")
    op.drop_column("users", "username")
