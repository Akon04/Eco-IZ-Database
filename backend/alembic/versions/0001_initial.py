"""initial schema"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("co2_saved_total", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "challenges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("target_count", sa.Integer(), nullable=False),
        sa.Column("reward_points", sa.Integer(), nullable=False),
        sa.Column("badge_symbol", sa.String(length=128), nullable=False),
        sa.Column("badge_tint_hex", sa.Integer(), nullable=False),
        sa.Column("badge_background_hex", sa.Integer(), nullable=False),
    )
    op.create_index("ix_challenges_title", "challenges", ["title"], unique=True)

    op.create_table(
        "session_tokens",
        sa.Column("token", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_session_tokens_user_id", "session_tokens", ["user_id"])

    op.create_table(
        "activities",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("co2_saved", sa.Float(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_activities_user_id", "activities", ["user_id"])
    op.create_index("ix_activities_created_at", "activities", ["created_at"])

    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_name", sa.String(length=255), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_posts_user_id", "posts", ["user_id"])
    op.create_index("ix_posts_created_at", "posts", ["created_at"])

    op.create_table(
        "post_media",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("post_id", sa.Uuid(), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
    )
    op.create_index("ix_post_media_post_id", "post_media", ["post_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_chat_messages_user_id", "chat_messages", ["user_id"])
    op.create_index("ix_chat_messages_created_at", "chat_messages", ["created_at"])

    op.create_table(
        "user_challenges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("challenge_id", sa.Uuid(), sa.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False),
        sa.Column("current_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_user_challenges_user_id", "user_challenges", ["user_id"])
    op.create_index("ix_user_challenges_challenge_id", "user_challenges", ["challenge_id"])


def downgrade() -> None:
    op.drop_index("ix_user_challenges_challenge_id", table_name="user_challenges")
    op.drop_index("ix_user_challenges_user_id", table_name="user_challenges")
    op.drop_table("user_challenges")
    op.drop_index("ix_chat_messages_created_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_user_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_post_media_post_id", table_name="post_media")
    op.drop_table("post_media")
    op.drop_index("ix_posts_created_at", table_name="posts")
    op.drop_index("ix_posts_user_id", table_name="posts")
    op.drop_table("posts")
    op.drop_index("ix_activities_created_at", table_name="activities")
    op.drop_index("ix_activities_user_id", table_name="activities")
    op.drop_table("activities")
    op.drop_index("ix_session_tokens_user_id", table_name="session_tokens")
    op.drop_table("session_tokens")
    op.drop_index("ix_challenges_title", table_name="challenges")
    op.drop_table("challenges")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
