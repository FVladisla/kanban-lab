import pytest
from fastapi import HTTPException

from app.services.wip import check_wip_limit


class FakeColumn:
    def __init__(self, id=1, name="In Progress", wip_limit=None):
        self.id = id
        self.name = name
        self.wip_limit = wip_limit


@pytest.mark.asyncio
async def test_wip_no_limit_does_nothing(mock_db):
    column = FakeColumn(wip_limit=None)
    await check_wip_limit(mock_db, column)
    mock_db.scalar.assert_not_called()


@pytest.mark.asyncio
async def test_wip_below_limit_passes(mock_db):
    mock_db.scalar.return_value = 1
    column = FakeColumn(wip_limit=2)
    await check_wip_limit(mock_db, column)
    mock_db.scalar.assert_called_once()


@pytest.mark.asyncio
async def test_wip_at_limit_raises_409(mock_db):
    mock_db.scalar.return_value = 2
    column = FakeColumn(wip_limit=2)
    with pytest.raises(HTTPException) as exc:
        await check_wip_limit(mock_db, column)
    assert exc.value.status_code == 409
    assert "Лимит" in exc.value.detail or "limit" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_wip_over_limit_raises_409(mock_db):
    mock_db.scalar.return_value = 5
    column = FakeColumn(wip_limit=2)
    with pytest.raises(HTTPException) as exc:
        await check_wip_limit(mock_db, column)
    assert exc.value.status_code == 409