from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity_log import ActivityLog


async def log_action(
    db: AsyncSession, card_id: int, user_id: int | None, action: str
) -> None:
    db.add(ActivityLog(card_id=card_id, user_id=user_id, action=action))
    await db.flush()
