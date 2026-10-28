from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.activity_log import ActivityLog
from app.models.card import Card
from app.models.user import User
from app.schemas.activity import ActivityRead

router = APIRouter(tags=["activity"])


@router.get("/cards/{card_id}/history", response_model=list[ActivityRead])
async def card_history(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[ActivityLog]:
    card = await db.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    result = await db.scalars(
        select(ActivityLog)
        .where(ActivityLog.card_id == card_id)
        .order_by(ActivityLog.created_at.desc())
    )
    return list(result)
