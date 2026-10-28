import pytest

from app.services.activity import log_action
from app.models.activity_log import ActivityLog


@pytest.mark.asyncio
async def test_log_action_adds_entry(mock_db):
    await log_action(mock_db, card_id=10, user_id=3, action="created")
    mock_db.add.assert_called_once()
    entry = mock_db.add.call_args[0][0]
    assert isinstance(entry, ActivityLog)
    assert entry.card_id == 10
    assert entry.user_id == 3
    assert entry.action == "created"
    mock_db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_log_action_with_none_user(mock_db):
    await log_action(mock_db, card_id=10, user_id=None, action="system")
    entry = mock_db.add.call_args[0][0]
    assert entry.user_id is None