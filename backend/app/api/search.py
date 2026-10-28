from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.card import Card, CardPriority
from app.models.user import User
from app.schemas.card import CardRead

router = APIRouter(prefix="/cards", tags=["search"])


@router.get("", response_model=list[CardRead])
async def search_cards(
    search: str | None = None,
    assignee_id: int | None = None,
    priority: CardPriority | None = None,
    label: str | None = None,
    column_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Card]:
    stmt = select(Card)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(Card.title.ilike(like) | Card.description.ilike(like))
    if assignee_id is not None:
        stmt = stmt.where(Card.assignee_id == assignee_id)
    if priority is not None:
        stmt = stmt.where(Card.priority == priority)
    if column_id is not None:
        stmt = stmt.where(Card.column_id == column_id)
    if label:
        stmt = stmt.join(Card.labels).where(Card.labels.any(name=label))
    stmt = stmt.order_by(Card.id)
    result = await db.scalars(stmt)
    return list(result)
