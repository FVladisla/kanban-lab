from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AttachmentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=500)
    url: str = Field(min_length=1, max_length=1000)


class AttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    url: str
    card_id: int
    created_at: datetime
