from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.board import Board
from app.models.column import Column
from app.models.user import User, UserRole
from app.schemas.column import ColumnCreate, ColumnRead, ColumnUpdate

router = APIRouter(tags=["columns"])


@router.get("/boards/{board_id}/columns", response_model=list[ColumnRead])
async def list_columns(
    board_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Column]:
    board = await db.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    result = await db.scalars(select(Column).where(Column.board_id == board_id).order_by(Column.order))
    return list(result)


@router.post(
    "/boards/{board_id}/columns",
    response_model=ColumnRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_column(
    board_id: int,
    payload: ColumnCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> Column:
    board = await db.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    column = Column(
        name=payload.name,
        board_id=board_id,
        order=payload.order,
        wip_limit=payload.wip_limit,
    )
    db.add(column)
    await db.commit()
    await db.refresh(column)
    return column


@router.patch("/columns/{column_id}", response_model=ColumnRead)
async def update_column(
    column_id: int,
    payload: ColumnUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> Column:
    column = await db.get(Column, column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(column, field, value)
    await db.commit()
    await db.refresh(column)
    return column


@router.delete("/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    column_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> None:
    column = await db.get(Column, column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
    await db.delete(column)
    await db.commit()
