
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.workers.daily_checklist import DailyChecklistWorker

@pytest.mark.unit
@pytest.mark.asyncio
async def test_daily_checklist_execution():
    """Test daily checklist worker sends emails"""
    worker = DailyChecklistWorker()
    
    # Mock dependencies
    # Implementation is skeleton, so we just verify it runs
    # Mocks for DB query are needed though
    
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value.all.return_value = [] # No users to process, safe path
    
    worker.get_db = MagicMock(return_value=mock_db)
    
    await worker.execute()
    
    # Verify DB was queried
    mock_db.query.assert_called()

    mock_db.query.assert_called()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_daily_checklist_with_users():
    """Test processing users"""
    worker = DailyChecklistWorker()
    
    # Mock user
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value.all.return_value = [mock_user, mock_user]
    
    worker.get_db = MagicMock(return_value=mock_db)
    
    with patch.object(worker.logger, 'info') as mock_info:
        await worker.execute()
        # Should log processing count, twice "Would send...", once "processed"
        assert mock_info.call_count >= 4

@pytest.mark.unit
@pytest.mark.asyncio
async def test_daily_checklist_user_error():
    """Test error for single user continues loop"""
    worker = DailyChecklistWorker()
    mock_user = MagicMock()
    mock_user.email = "test@example.com"
    
    mock_db = MagicMock()
    mock_query = mock_db.query.return_value
    mock_query.filter.return_value.all.return_value = [mock_user]
    worker.get_db = MagicMock(return_value=mock_db)
    
    # Mock logger info to raise exception for the "Would send..." call
    # The first info call is "Processing...", second is "Would send..."
    # We want second call to fail
    with patch.object(worker.logger, 'info') as mock_info, \
         patch.object(worker.logger, 'error') as mock_error:
        mock_info.side_effect = [None, Exception("Send Failed"), None]
        
        await worker.execute()
        
        # Should have called error logger
        mock_error.assert_called()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_daily_checklist_fatal_error():
    """Test fatal error during execution"""
    worker = DailyChecklistWorker()
    
    worker.get_db = MagicMock()
    worker.get_db.return_value.query.side_effect = Exception("DB Error")
    
    with pytest.raises(Exception):
        await worker.execute()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_daily_checklist_name():
    worker = DailyChecklistWorker()
    assert worker.name == "daily_checklist"
