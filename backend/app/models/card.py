from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.label import card_labels
class CardPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(5000))
    column_id: Mapped[int] = mapped_column(ForeignKey("columns.id", ondelete="CASCADE"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    priority: Mapped[CardPriority] = mapped_column(SAEnum(CardPriority, name="card_priority"), default=CardPriority.medium)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    column = relationship("Column", back_populates="cards")
    assignee = relationship("User", back_populates="cards_assigned")
    labels = relationship("Label", secondary=card_labels, back_populates="cards")
    comments = relationship("Comment", back_populates="card", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="card", cascade="all, delete-orphan")
    activity = relationship("ActivityLog", back_populates="card", cascade="all, delete-orphan")
    @property
    def assignee_email(self) -> str | None:
        return self.assignee.email if self.assignee else None
