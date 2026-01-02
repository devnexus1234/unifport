import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
from io import BytesIO
from app.services.morning_checklist.emailer import send_morning_checklist_report_email

@patch('app.services.morning_checklist.emailer.generate_morning_checklist_excel')
@patch('app.services.morning_checklist.emailer.get_email_service')
@patch('app.services.morning_checklist.emailer.SessionLocal')
def test_send_morning_checklist_report_email_success(
    mock_session_local,
    mock_get_email_service,
    mock_generate_excel
):
    """Test successful email sending"""
    # Mock DB session
    mock_db = Mock()
    mock_session_local.return_value = mock_db
    
    # Mock Excel generation
    mock_stream = BytesIO(b"fake_excel_content")
    mock_generate_excel.return_value = mock_stream
    
    # Mock Email Service
    mock_email_service = Mock()
    mock_email_service.send_plain_email_with_defaults.return_value = True
    mock_get_email_service.return_value = mock_email_service
    
    # Execute
    send_morning_checklist_report_email()
    
    # Verify interactions
    mock_session_local.assert_called_once()
    mock_generate_excel.assert_called_once_with(mock_db, date.today())
    
    # Mock email service verification
    mock_email_service.send_plain_email_with_defaults.assert_called_once()
    call_kwargs = mock_email_service.send_plain_email_with_defaults.call_args[1]
    
    assert f"Morning Checklist Report - {date.today()}" in call_kwargs['subject']
    assert "Please find attached" in call_kwargs['text_body']
    assert call_kwargs['use_env_defaults'] is True
    
    # Verify attachment
    attachments = call_kwargs['attachments']
    assert len(attachments) == 1
    assert attachments[0]['filename'] == f"checklist_report_{date.today()}.xlsx"
    assert attachments[0]['content'] == b"fake_excel_content"
    
    # Verify DB closed
    mock_db.close.assert_called_once()


@patch('app.services.morning_checklist.emailer.generate_morning_checklist_excel')
@patch('app.services.morning_checklist.emailer.get_email_service')
@patch('app.services.morning_checklist.emailer.SessionLocal')
def test_send_morning_checklist_report_email_failure(
    mock_session_local,
    mock_get_email_service,
    mock_generate_excel
):
    """Test email sending failure handling"""
    # Mock DB session
    mock_db = Mock()
    mock_session_local.return_value = mock_db
    
    # Mock Excel generation
    mock_stream = BytesIO(b"content")
    mock_generate_excel.return_value = mock_stream
    
    # Mock Email Service failure
    mock_email_service = Mock()
    mock_email_service.send_plain_email_with_defaults.return_value = False
    mock_get_email_service.return_value = mock_email_service
    
    # Execute (should handle error gracefully and log it, not raise)
    send_morning_checklist_report_email()
    
    # Verify interactions
    mock_email_service.send_plain_email_with_defaults.assert_called_once()
    
    # Verify DB closed
    mock_db.close.assert_called_once()

@patch('app.services.morning_checklist.emailer.generate_morning_checklist_excel')
@patch('app.services.morning_checklist.emailer.SessionLocal')
def test_send_morning_checklist_report_email_exception(
    mock_session_local,
    mock_generate_excel
):
    """Test exception handling during process"""
    # Mock Exception during excel generation
    mock_session_local.return_value = Mock()
    mock_generate_excel.side_effect = Exception("Generation failed")
    
    # Execute (should confirm exception is caught)
    try:
        send_morning_checklist_report_email()
    except Exception:
        pytest.fail("Exception should be caught inside the function")
        
    # We rely on logs here, but function shouldn't crash.
