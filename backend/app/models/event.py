import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EcoEvent(Base):
    __tablename__ = "eco_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(255))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    reward_points: Mapped[int] = mapped_column(Integer, default=0)
    badge: Mapped[str] = mapped_column(String(64), default="Бесплатно")
    partner_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    registration_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_tint_hex: Mapped[int] = mapped_column(Integer, default=0x7ED957)
    display_order: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
