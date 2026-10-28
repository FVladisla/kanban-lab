from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.board import Board
from app.models.project import Project
from app.models.user import User, UserRole
from app.schemas.board import BoardCreate, BoardRead, BoardUpdate

router = APIRouter(tags=["boards"])


@router.get("/projects/{project_id}/boards", response_model=list[BoardRead])
async def list_boards(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[Board]:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    result = await db.scalars(select(Board).where(Board.project_id == project_id).order_by(Board.id))
    return list(result)


@router.post(
    "/projects/{project_id}/boards",
    response_model=BoardRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_board(
    project_id: int,
    payload: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> Board:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    board = Board(name=payload.name, project_id=project_id)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


@router.get("/boards/{board_id}", response_model=BoardRead)
async def get_board(
    board_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Board:
    board = await db.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board


@router.patch("/boards/{board_id}", response_model=BoardRead)
async def update_board(
    board_id: int,
    payload: BoardUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> Board:
    board = await db.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(board, field, value)
    await db.commit()
    await db.refresh(board)
    return board


@router.delete("/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> None:
    board = await db.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    await db.delete(board)
    await db.commit()

@router.get("/boards/{board_id}/details")
async def board_details(
    board_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> dict:
    board = await db.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    project = await db.get(Project, board.project_id)
    return {
        "id": board.id,
        "name": board.name,
        "created_at": board.created_at.isoformat(),
        "project_id": board.project_id,
        "project": {
            "id": project.id,
            "name": project.name,
        } if project else None,
    }
