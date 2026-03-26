import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(String(255))
    target_count: Mapped[int] = mapped_column(Integer)
    reward_points: Mapped[int] = mapped_column(Integer)
    badge_symbol: Mapped[str] = mapped_column(String(128))
    badge_tint_hex: Mapped[int] = mapped_column(Integer)
    badge_background_hex: Mapped[int] = mapped_column(Integer)

    user_challenges: Mapped[list["UserChallenge"]] = relationship(back_populates="challenge", cascade="all, delete-orphan")


class UserChallenge(Base):
    __tablename__ = "user_challenges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    challenge_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    current_count: Mapped[int] = mapped_column(Integer, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="user_challenges")
    challenge: Mapped["Challenge"] = relationship(back_populates="user_challenges")


from app.models.user import User  # noqa: E402
