from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class BoardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class BoardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)


class BoardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    project_id: int
    created_at: datetime
