from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.attachment import Attachment
from app.models.card import Card
from app.models.user import User
from app.schemas.attachment import AttachmentCreate, AttachmentRead

router = APIRouter(tags=["attachments"])


@router.get("/cards/{card_id}/attachments", response_model=list[AttachmentRead])
async def list_attachments(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Attachment]:
    card = await db.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    result = await db.scalars(
        select(Attachment).where(Attachment.card_id == card_id).order_by(Attachment.id)
    )
    return list(result)


@router.post(
    "/cards/{card_id}/attachments",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_attachment(
    card_id: int,
    payload: AttachmentCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Attachment:
    card = await db.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    attachment = Attachment(filename=payload.filename, url=payload.url, card_id=card_id)
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment
