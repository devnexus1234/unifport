"""
Tests for Email Service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.email_service import EmailService, get_email_service
from app.core.config import settings


@pytest.fixture
def email_service():
    """Create email service instance for testing"""
    return EmailService()


def test_email_service_initialization(email_service):
    """Test email service initializes with correct settings"""
    assert email_service.smtp_host == settings.SMTP_HOST
    assert email_service.smtp_port == settings.SMTP_PORT
    assert email_service.smtp_from_email == settings.SMTP_FROM_EMAIL


def test_parse_recipients_string(email_service):
    """Test parsing comma-separated recipients string"""
    recipients = email_service._parse_recipients("user1@example.com, user2@example.com")
    assert len(recipients) == 2
    assert "user1@example.com" in recipients
    assert "user2@example.com" in recipients


def test_parse_recipients_list(email_service):
    """Test parsing recipients list"""
    recipients = email_service._parse_recipients(["user1@example.com", "user2@example.com"])
    assert len(recipients) == 2


def test_create_message_plain(email_service):
    """Test creating plain text message"""
    msg, to_list = email_service._create_message(
        subject="Test",
        body="Test body",
        recipients="user@example.com"
    )
    assert msg['Subject'] == "Test"
    assert "user@example.com" in to_list


def test_create_message_with_cc_bcc(email_service):
    """Test creating message with CC and BCC"""
    msg, to_list = email_service._create_message(
        subject="Test",
        body="Test body",
        recipients="user@example.com",
        cc="cc@example.com",
        bcc="bcc@example.com"
    )
    assert "cc@example.com" in to_list
    assert "bcc@example.com" in to_list


@patch('app.services.email_service.smtplib.SMTP')
def test_send_email_success(mock_smtp, email_service):
    """Test sending email successfully"""
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    # Configure service with test credentials
    email_service.smtp_user = "test@example.com"
    email_service.smtp_password = "password"
    email_service.smtp_host = "smtp.example.com"
    
    success = email_service.send_email(
        subject="Test",
        body="Test body",
        recipients="user@example.com"
    )
    
    assert success is True
    mock_server.send_message.assert_called_once()


@patch('app.services.email_service.smtplib.SMTP')
def test_send_email_smtp_error(mock_smtp, email_service):
    """Test handling SMTP errors"""
    mock_smtp.side_effect = Exception("SMTP connection failed")
    
    email_service.smtp_user = "test@example.com"
    email_service.smtp_host = "smtp.example.com"
    
    success = email_service.send_email(
        subject="Test",
        body="Test body",
        recipients="user@example.com"
    )
    
    assert success is False


def test_send_email_no_smtp_config(email_service):
    """Test sending email when SMTP not configured"""
    email_service.smtp_host = ""
    email_service.smtp_user = ""
    
    success = email_service.send_email(
        subject="Test",
        body="Test body",
        recipients="user@example.com"
    )
    
    assert success is False


def test_send_html_email(email_service):
    """Test sending HTML email"""
    with patch.object(email_service, 'send_email') as mock_send:
        email_service.send_html_email(
            subject="Test",
            html_body="<h1>Test</h1>",
            recipients="user@example.com"
        )
        
        mock_send.assert_called_once_with(
            subject="Test",
            body="<h1>Test</h1>",
            recipients="user@example.com",
            cc=None,
            bcc=None,
            html=True,
            attachments=None
        )


def test_send_plain_email(email_service):
    """Test sending plain text email"""
    with patch.object(email_service, 'send_email') as mock_send:
        email_service.send_plain_email(
            subject="Test",
            text_body="Test body",
            recipients="user@example.com"
        )
        
        mock_send.assert_called_once_with(
            subject="Test",
            body="Test body",
            recipients="user@example.com",
            cc=None,
            bcc=None,
            html=False,
            attachments=None
        )


def test_get_email_service():
    """Test getting email service singleton"""
    service1 = get_email_service()
    service2 = get_email_service()
    assert service1 is service2

def test_create_message_with_attachments(email_service):
    """Test creating message with attachments"""
    attachments = [
        {"filename": "test.txt", "content": b"content"}
    ]
    msg, _ = email_service._create_message(
        subject="Test",
        body="Body",
        recipients="user@example.com",
        attachments=attachments
    )
    
    # Verify attachment present
    payload = msg.get_payload()
    # payload[0] is body, payload[1] is attachment
    assert len(payload) == 2
    assert payload[1].get_filename() == "test.txt"

@patch('app.services.email_service.smtplib.SMTP_SSL')
def test_send_email_ssl(mock_smtp_ssl, email_service):
    """Test sending email with SSL"""
    email_service.smtp_use_ssl = True
    email_service.smtp_host = "smtp.example.com"
    email_service.smtp_user = "user"
    email_service.smtp_password = "pass"
    
    email_service.send_email(
        subject="Test",
        body="Body",
        recipients="user@example.com"
    )
    
    mock_smtp_ssl.assert_called_once()

@patch('app.services.email_service.smtplib.SMTP')
def test_send_email_specific_smtp_exception(mock_smtp, email_service):
    """Test handling specific SMTPException"""
    import smtplib
    mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
    
    email_service.smtp_host = "smtp.example.com"
    email_service.smtp_user = "user"
    
    success = email_service.send_email(
        subject="Test",
        body="Body",
        recipients="user@example.com"
    )
    assert success is False

def test_send_email_defaults_production_error(email_service):
    """Test error when no recipients provided in production mode"""
    # Force production mode behavior
    with patch('app.services.email_service.settings') as mock_settings:
        mock_settings.DEBUG_MODE = False
        
        success = email_service.send_email_with_defaults(
            subject="Test",
            body="Body",
            recipients=None,
            use_env_defaults=False 
        )
        assert success is False
