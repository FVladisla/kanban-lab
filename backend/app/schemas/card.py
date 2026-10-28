from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.card import CardPriority


class CardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    assignee_id: int | None = None
    priority: CardPriority = CardPriority.medium
    deadline: datetime | None = None


class CardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    assignee_id: int | None = None
    priority: CardPriority | None = None
    deadline: datetime | None = None


class CardMove(BaseModel):
    column_id: int
    order: int = 0


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    column_id: int
    assignee_id: int | None
    assignee_email: str | None = None
    priority: CardPriority
    deadline: datetime | None
    order: int
    created_at: datetime
    updated_at: datetime
