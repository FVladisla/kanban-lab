from pydantic import BaseModel, ConfigDict, Field


class ColumnCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    order: int = 0
    wip_limit: int | None = Field(default=None, ge=1)


class ColumnUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    wip_limit: int | None = Field(default=None, ge=1)


class ColumnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    board_id: int
    order: int
    wip_limit: int | None
