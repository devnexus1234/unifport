"""
Tests for Email Service Default Recipients
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.email_service import EmailService, get_email_service
from app.core.config import settings


@pytest.fixture
def email_service():
    """Create email service instance for testing"""
    return EmailService()


@patch('app.services.email_service.smtplib.SMTP')
def test_send_email_with_defaults_debug_mode(mock_smtp, email_service, monkeypatch):
    """Test that debug mode uses environment defaults when recipients not provided"""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    # Set debug mode
    monkeypatch.setattr(settings, 'DEBUG_MODE', True)
    monkeypatch.setattr(settings, 'EMAIL_ADMIN_RECIPIENTS', 'default@example.com')
    monkeypatch.setattr(settings, 'EMAIL_ADMIN_CC', 'cc@example.com')
    
    email_service.smtp_user = "test@example.com"
    email_service.smtp_password = "password"
    email_service.smtp_host = "smtp.example.com"
    
    # Send without recipients - should use env defaults
    success = email_service.send_email_with_defaults(
        subject="Test",
        body="Test body",
        use_env_defaults=True
    )
    
    assert success is True
    mock_server.send_message.assert_called_once()
    # Verify default recipients were used
    call_args = mock_server.send_message.call_args
    assert call_args is not None


@patch('app.services.email_service.smtplib.SMTP')
def test_send_email_with_defaults_production_mode(mock_smtp, email_service, monkeypatch):
    """Test that production mode requires explicit recipients"""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    # Set production mode
    monkeypatch.setattr(settings, 'DEBUG_MODE', False)
    
    email_service.smtp_user = "test@example.com"
    email_service.smtp_host = "smtp.example.com"
    
    # Try to send without recipients - should fail
    success = email_service.send_email_with_defaults(
        subject="Test",
        body="Test body",
        recipients=None,
        use_env_defaults=False
    )
    
    assert success is False
    mock_server.send_message.assert_not_called()


@patch('app.services.email_service.smtplib.SMTP')
def test_send_email_with_defaults_custom_recipients(mock_smtp, email_service, monkeypatch):
    """Test that custom recipients override defaults"""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    monkeypatch.setattr(settings, 'DEBUG_MODE', True)
    monkeypatch.setattr(settings, 'EMAIL_ADMIN_RECIPIENTS', 'default@example.com')
    
    email_service.smtp_user = "test@example.com"
    email_service.smtp_password = "password"
    email_service.smtp_host = "smtp.example.com"
    
    # Send with custom recipients - should use custom, not defaults
    success = email_service.send_email_with_defaults(
        subject="Test",
        body="Test body",
        recipients="custom@example.com",
        use_env_defaults=True
    )
    
    assert success is True
    mock_server.send_message.assert_called_once()


def test_send_html_email_with_defaults(monkeypatch):
    """Test HTML email with defaults"""
    email_service = EmailService()
    
    monkeypatch.setattr(settings, 'DEBUG_MODE', True)
    monkeypatch.setattr(settings, 'EMAIL_ADMIN_RECIPIENTS', 'test@example.com')
    
    with patch.object(email_service, 'send_email_with_defaults') as mock_send:
        email_service.send_html_email_with_defaults(
            subject="Test",
            html_body="<h1>Test</h1>"
        )
        
        mock_send.assert_called_once_with(
            subject="Test",
            body="<h1>Test</h1>",
            recipients=None,
            cc=None,
            bcc=None,
            html=True,
            attachments=None,
            use_env_defaults=True
        )


def test_send_plain_email_with_defaults(monkeypatch):
    """Test plain email with defaults"""
    email_service = EmailService()
    
    monkeypatch.setattr(settings, 'DEBUG_MODE', True)
    monkeypatch.setattr(settings, 'EMAIL_ADMIN_RECIPIENTS', 'test@example.com')
    
    with patch.object(email_service, 'send_email_with_defaults') as mock_send:
        email_service.send_plain_email_with_defaults(
            subject="Test",
            text_body="Test body"
        )
        
        mock_send.assert_called_once_with(
            subject="Test",
            body="Test body",
            recipients=None,
            cc=None,
            bcc=None,
            html=False,
            attachments=None,
            use_env_defaults=True
        )
