from sqlalchemy import Column as SAColumn, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
card_labels = Table("card_labels", Base.metadata,
    SAColumn("card_id", Integer, ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True),
    SAColumn("label_id", Integer, ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True))
class Label(Base):
    __tablename__ = "labels"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#888888")
    cards = relationship("Card", secondary=card_labels, back_populates="labels")
