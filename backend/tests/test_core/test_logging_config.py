"""
Tests for Logging Configuration
"""
import pytest
import logging
import json
from unittest.mock import patch, MagicMock
from app.core.logging_config import (
    JSONFormatter,
    StandardFormatter,
    setup_logging,
    get_logger,
    request_id_var,
    user_var
)

@pytest.mark.unit
class TestJSONFormatter:
    def test_json_formatter_basic(self):
        """Test JSON formatter with basic log record"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        log_dict = json.loads(formatted)
        
        assert log_dict["message"] == "Test message"
        assert log_dict["level"] == "INFO"
        assert log_dict["logger"] == "test"
    
    def test_json_formatter_with_extra(self):
        """Test JSON formatter with extra fields"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=None
        )
        record.user_id = "user123"
        record.request_id = "req456"
        
        formatted = formatter.format(record)
        log_dict = json.loads(formatted)
        
        assert log_dict["user_id"] == "user123"
        assert log_dict["request_id"] == "req456"


@pytest.mark.unit
class TestStandardFormatter:
    def test_standard_formatter(self):
        """Test standard formatter"""
        formatter = StandardFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=10,
            msg="Warning message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert "WARNING" in formatted
        assert "Warning message" in formatted


@pytest.mark.unit
class TestLoggingSetup:
    def test_setup_logging(self):
        """Test logging setup"""
        with patch('app.core.logging_config.settings') as mock_settings:
            mock_settings.LOG_LEVEL = "INFO"
            mock_settings.LOG_FORMAT = "json"
            
            setup_logging()
            
            # Verify root logger is configured
            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO
    
    def test_get_logger(self):
        """Test getting a logger"""
        logger = get_logger("test.module")
        
        assert logger is not None
        assert logger.name.endswith("test.module")
    
    def test_get_logger_with_context(self):
        """Test logger with context variables"""
        # Set context variables
        request_id_var.set("req123")
        user_var.set("user456")
        
        logger = get_logger("test")
        
        # Context should be available
        assert request_id_var.get() == "req123"
        assert user_var.get() == "user456"
        
        # Clean up
        request_id_var.set(None)
        user_var.set(None)
