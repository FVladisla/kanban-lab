from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    card_id: int
    user_id: int | None
    action: str
    created_at: datetime
