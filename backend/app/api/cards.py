from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.card import Card
from app.models.column import Column
from app.models.user import User
from app.schemas.card import CardCreate, CardMove, CardRead, CardUpdate
from app.services.activity import log_action
from app.services.wip import check_wip_limit

router = APIRouter(tags=["cards"])


@router.get("/columns/{column_id}/cards", response_model=list[CardRead])
async def list_cards(
    column_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Card]:
    column = await db.get(Column, column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
    result = await db.scalars(
        select(Card)
        .options(selectinload(Card.assignee))
        .where(Card.column_id == column_id)
        .order_by(Card.order)
    )
    return list(result)


@router.post(
    "/columns/{column_id}/cards",
    response_model=CardRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_card(
    column_id: int,
    payload: CardCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Card:
    column = await db.get(Column, column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
    await check_wip_limit(db, column)
    card = Card(
        title=payload.title,
        description=payload.description,
        column_id=column_id,
        assignee_id=payload.assignee_id,
        priority=payload.priority,
        deadline=payload.deadline,
    )
    db.add(card)
    await db.flush()
    await log_action(db, card.id, current.id, "created")
    await db.commit()
    await db.refresh(card)
    await db.refresh(card, ["assignee"])
    return card


@router.get("/cards/{card_id}", response_model=CardRead)
async def get_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Card:
    card = await db.scalar(
        select(Card)
        .options(selectinload(Card.assignee))
        .where(Card.id == card_id)
    )
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return card


@router.patch("/cards/{card_id}", response_model=CardRead)
async def update_card(
    card_id: int,
    payload: CardUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Card:
    card = await db.scalar(
        select(Card)
        .options(selectinload(Card.assignee))
        .where(Card.id == card_id)
    )
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(card, field, value)
    if changes:
        await log_action(db, card.id, current.id, f"updated: {', '.join(changes.keys())}")
    await db.commit()
    await db.refresh(card)
    return card


@router.patch("/cards/{card_id}/move", response_model=CardRead)
async def move_card(
    card_id: int,
    payload: CardMove,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Card:
    card = await db.scalar(
        select(Card)
        .options(selectinload(Card.assignee))
        .where(Card.id == card_id)
    )
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    target = await db.get(Column, payload.column_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target column not found")
    if target.id != card.column_id:
        await check_wip_limit(db, target)
    old_column_id = card.column_id
    card.column_id = payload.column_id
    card.order = payload.order
    await log_action(db, card.id, current.id, f"moved: column {old_column_id} -> {payload.column_id}")
    await db.commit()
    await db.refresh(card)
    return card


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    card = await db.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    await db.delete(card)
    await db.commit()
