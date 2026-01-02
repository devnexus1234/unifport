
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.workers.status_checker import StatusCheckerWorker

@pytest.mark.unit
@pytest.mark.asyncio
async def test_status_checker_execution():
    """Test status checker runs update logic"""
    worker = StatusCheckerWorker()
    
    # Mock get_engine
    mock_engine = MagicMock()
    # Mock context manager for connect
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    
    with patch('app.services.workers.status_checker.get_engine', return_value=mock_engine), \
         patch('app.services.workers.status_checker.get_email_service') as mock_email_service:
        
        # execution calls _send_status_email which calls email_service
        await worker.execute()
        
        mock_conn.execute.assert_called() # Verifies DB check
        mock_email_service.return_value.send_html_email_with_defaults.assert_called() # Verifies email sent

@pytest.mark.unit
@pytest.mark.asyncio
async def test_status_checker_name():
    worker = StatusCheckerWorker()
    assert worker.name == "status_checker"

@pytest.mark.unit
@pytest.mark.asyncio
async def test_status_checker_db_unavailable():
    """Test when database engine is unavailable"""
    worker = StatusCheckerWorker()
    
    with patch('app.services.workers.status_checker.get_engine', return_value=None), \
         patch('app.services.workers.status_checker.get_email_service') as mock_email_service:
        
        await worker.execute()
        
        # Should still send email with unavailable status
        mock_email_service.return_value.send_html_email_with_defaults.assert_called()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_status_checker_execution_error():
    """Test error during execution"""
    worker = StatusCheckerWorker()
    
    with patch('app.services.workers.status_checker.get_engine', side_effect=Exception("DB Error")), \
         patch('app.services.workers.status_checker.get_email_service') as mock_email_service:
        
        with pytest.raises(Exception):
            await worker.execute()
        
        # Should attempt to send error email
        assert mock_email_service.return_value.send_html_email_with_defaults.call_count >= 1

@pytest.mark.unit
@pytest.mark.asyncio
async def test_status_checker_email_failure():
    """Test when email sending fails"""
    worker = StatusCheckerWorker()
    
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    
    with patch('app.services.workers.status_checker.get_engine', return_value=mock_engine), \
         patch('app.services.workers.status_checker.get_email_service') as mock_email_service:
        
        # Make email sending fail
        mock_email_service.return_value.send_html_email_with_defaults.return_value = False
        
        await worker.execute()
        
        # Should log warning about failed email
        mock_email_service.return_value.send_html_email_with_defaults.assert_called()

@pytest.mark.unit
def test_build_status_email_html():
    """Test HTML email building"""
    worker = StatusCheckerWorker()
    
    status_report = {
        "timestamp": "2025-01-01T00:00:00",
        "checks": [
            {"component": "database", "status": "healthy", "message": "OK"}
        ]
    }
    
    html = worker._build_status_email_html(status_report, is_error=False)
    
    assert "HEALTHY" in html
    assert "database" in html.lower()
    
@pytest.mark.unit
def test_build_status_email_html_error():
    """Test HTML email building for error"""
    worker = StatusCheckerWorker()
    
    status_report = {
        "timestamp": "2025-01-01T00:00:00",
        "checks": [
            {"component": "database", "status": "error", "message": "Failed"}
        ]
    }
    
    html = worker._build_status_email_html(status_report, is_error=True)
    
    assert "ERROR" in html
    assert "database" in html.lower()
