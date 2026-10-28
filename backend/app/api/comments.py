from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.card import Card
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead

router = APIRouter(tags=["comments"])


@router.get("/cards/{card_id}/comments", response_model=list[CommentRead])
async def list_comments(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Comment]:
    card = await db.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    result = await db.scalars(select(Comment).where(Comment.card_id == card_id).order_by(Comment.id))
    return list(result)


@router.post(
    "/cards/{card_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    card_id: int,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Comment:
    card = await db.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    comment = Comment(text=payload.text, card_id=card_id, author_id=current.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment
