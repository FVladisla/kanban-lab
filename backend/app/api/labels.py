from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.card import Card
from app.models.label import Label
from app.models.user import User, UserRole
from app.schemas.label import LabelCreate, LabelRead

router = APIRouter(tags=["labels"])


@router.get("/labels", response_model=list[LabelRead])
async def list_labels(
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Label]:
    result = await db.scalars(select(Label).order_by(Label.id))
    return list(result)


@router.post("/labels", response_model=LabelRead, status_code=status.HTTP_201_CREATED)
async def create_label(
    payload: LabelCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> Label:
    exists = await db.scalar(select(Label).where(Label.name == payload.name))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Label already exists")
    label = Label(name=payload.name, color=payload.color)
    db.add(label)
    await db.commit()
    await db.refresh(label)
    return label


@router.post("/cards/{card_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def attach_label(
    card_id: int,
    label_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    card = await db.scalar(
        select(Card).options(selectinload(Card.labels)).where(Card.id == card_id)
    )
    label = await db.get(Label, label_id)
    if card is None or label is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card or label not found")
    if label not in card.labels:
        card.labels.append(label)
        await db.commit()


@router.delete("/cards/{card_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_label(
    card_id: int,
    label_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    card = await db.scalar(
        select(Card).options(selectinload(Card.labels)).where(Card.id == card_id)
    )
    label = await db.get(Label, label_id)
    if card is None or label is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card or label not found")
    if label in card.labels:
        card.labels.remove(label)
        await db.commit()
