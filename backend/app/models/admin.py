import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EcoCategory(Base):
    __tablename__ = "eco_categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    color: Mapped[str] = mapped_column(String(32), default="#43B244")
    icon: Mapped[str] = mapped_column(String(64), default="leaf")

    habits: Mapped[list["Habit"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=10)
    co2_value: Mapped[float] = mapped_column(Float, default=0)
    water_value: Mapped[float] = mapped_column(Float, default=0)
    energy_value: Mapped[float] = mapped_column(Float, default=0)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("eco_categories.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    category: Mapped["EcoCategory"] = relationship(back_populates="habits")
