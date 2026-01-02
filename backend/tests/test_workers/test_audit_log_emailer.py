import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.services.workers.audit_log_emailer import AuditLogEmailWorker
from app.models.ipam import IpamAuditLog, IpamSegment
from app.models.user import User

@pytest.mark.asyncio
async def test_audit_log_emailer_execution():
    """Test that the worker fetches logs and sends email"""
    
    # Mock settings
    with patch("app.services.workers.audit_log_emailer.settings") as mock_settings:
        mock_settings.JOB_AUDIT_LOG_EMAIL_RECIPIENTS = "admin@example.com, auditor@example.com"
        mock_settings.APP_TITLE = "Test App"
        
        # Mock Email Service
        mock_email_service = MagicMock()
        with patch("app.services.workers.audit_log_emailer.get_email_service", return_value=mock_email_service):
            
            # Mock DB Session
            mock_db = MagicMock()
            with patch("app.services.workers.audit_log_emailer.SessionLocal", return_value=mock_db):
                
                # Mock Time
                now = datetime(2023, 1, 2, 10, 0, 0)
                with patch("app.services.workers.audit_log_emailer.get_ist_time", return_value=now):
                    
                    # Create some mock logs
                    user = User(username="testuser", id=1)
                    segment = IpamSegment(segment="192.168.1.0/24", id=10)
                    
                    log1 = IpamAuditLog(
                        user=user,
                        action="CREATE",
                        segment=segment,
                        changes="Created segment",
                        created_at=now - timedelta(hours=2)
                    )
                    
                    log2 = IpamAuditLog(
                        user=user,
                        action="UPDATE",
                        ip_address="192.168.1.5",
                        changes="Assigned IP",
                        created_at=now - timedelta(hours=5)
                    )
                    
                    # Setup mock query return
                    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [log1, log2]
                    
                    # Run worker
                    worker = AuditLogEmailWorker()
                    await worker.run()
                    
                    # Verify DB query
                    # Should query IpamAuditLog
                    assert mock_db.query.call_count == 1
                    
                    # Verify Email Sent
                    mock_email_service.send_html_email_with_defaults.assert_called_once()
                    call_args = mock_email_service.send_html_email_with_defaults.call_args[1]
                    
                    assert call_args["subject"] == "[Test App] Daily Audit Log Report - 2023-01-01"
                    assert call_args["recipients"] == ["admin@example.com", "auditor@example.com"]
                    assert "192.168.1.0/24" in call_args["html_body"]
                    assert "192.168.1.5" in call_args["html_body"]
                    assert "Created segment" in call_args["html_body"]
                    
                    # Verify Excel Attachment
                    attachments = call_args["attachments"]
                    assert len(attachments) == 1
                    assert attachments[0]["filename"] == "audit_logs_2023-01-01.xlsx"
                    assert attachments[0]["content"] is not None
                    
@pytest.mark.asyncio
async def test_audit_log_emailer_no_recipients():
    """Test that worker skips if no recipients configured"""
    with patch("app.services.workers.audit_log_emailer.settings") as mock_settings:
        mock_settings.JOB_AUDIT_LOG_EMAIL_RECIPIENTS = ""
        
        with patch("app.services.workers.audit_log_emailer.get_email_service") as mock_get_email:
            worker = AuditLogEmailWorker()
            await worker.run()
            
            mock_get_email.assert_not_called()

@pytest.mark.asyncio
async def test_audit_log_emailer_no_logs():
    """Test that worker sends 'no activity' email if no logs found"""
    with patch("app.services.workers.audit_log_emailer.settings") as mock_settings:
        mock_settings.JOB_AUDIT_LOG_EMAIL_RECIPIENTS = "admin@example.com"
        mock_settings.APP_TITLE = "Test App"
        
        mock_email_service = MagicMock()
        with patch("app.services.workers.audit_log_emailer.get_email_service", return_value=mock_email_service):
            mock_db = MagicMock()
            with patch("app.services.workers.audit_log_emailer.SessionLocal", return_value=mock_db):
                with patch("app.services.workers.audit_log_emailer.get_ist_time", return_value=datetime(2023, 1, 2, 10, 0, 0)):
                    
                    # Return empty list
                    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
                    
                    worker = AuditLogEmailWorker()
                    await worker.run()
                    
                    # Verify Email Sent
                    mock_email_service.send_html_email_with_defaults.assert_called_once()
                    call_args = mock_email_service.send_html_email_with_defaults.call_args[1]
                    
                    assert "No audit logs recorded" in call_args["html_body"]
