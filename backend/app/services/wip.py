from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.card import Card
from app.models.column import Column


async def check_wip_limit(db: AsyncSession, column: Column) -> None:
    if column.wip_limit is None:
        return
    count = await db.scalar(
        select(func.count(Card.id)).where(Card.column_id == column.id)
    )
    if count is not None and count >= column.wip_limit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Лимит колонки «{column.name}» достигнут ({column.wip_limit})",
        )
