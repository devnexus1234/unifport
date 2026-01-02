"""
Tests for Middleware
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.core.middleware import (
    extract_user_from_token,
    parse_request_body,
    get_query_params
)

@pytest.mark.unit
class TestMiddlewareHelpers:
    def test_extract_user_no_header(self):
        """Test extracting user without auth header"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        
        user = extract_user_from_token(mock_request)
        assert user is None
    
    def test_extract_user_invalid_format(self):
        """Test extracting user with invalid header format"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "InvalidFormat"
        
        user = extract_user_from_token(mock_request)
        assert user is None
    
    @patch('app.core.middleware.verify_token')
    def test_extract_user_valid_token(self, mock_verify):
        """Test extracting user with valid token"""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer valid_token"
        mock_verify.return_value = {
            "user_id": 1,
            "sub": "testuser",
            "email": "test@example.com"
        }
        
        user = extract_user_from_token(mock_request)
        assert user is not None
        assert user["username"] == "testuser"
    
    def test_parse_request_body_empty(self):
        """Test parsing empty body"""
        result = parse_request_body(b"", "application/json")
        assert result is None
    
    def test_parse_request_body_json(self):
        """Test parsing JSON body"""
        body = b'{"key": "value"}'
        result = parse_request_body(body, "application/json")
        assert result == {"key": "value"}
    
    def test_parse_request_body_sensitive_fields(self):
        """Test masking sensitive fields"""
        body = b'{"username": "test", "password": "secret"}'
        result = parse_request_body(body, "application/json")
        assert result["password"] == "***REDACTED***"
        assert result["username"] == "test"
    
    def test_parse_request_body_form_data(self):
        """Test parsing form data"""
        body = b"key=value&key2=value2"
        result = parse_request_body(body, "application/x-www-form-urlencoded")
        assert result["type"] == "form_data"
    
    def test_get_query_params_empty(self):
        """Test getting query params when none exist"""
        mock_request = MagicMock()
        mock_request.url.query = ""
        
        params = get_query_params(mock_request)
        assert params is None
    
    def test_get_query_params_single(self):
        """Test getting single query params"""
        mock_request = MagicMock()
        mock_request.url.query = "key=value"
        mock_request.query_params.multi_items.return_value = [("key", "value")]
        
        params = get_query_params(mock_request)
        assert params == {"key": "value"}
    
    def test_get_query_params_multiple_values(self):
        """Test getting query params with multiple values"""
        mock_request = MagicMock()
        mock_request.url.query = "key=value1&key=value2"
        mock_request.query_params.multi_items.return_value = [
            ("key", "value1"),
            ("key", "value2")
        ]
        
        params = get_query_params(mock_request)
        assert params["key"] == ["value1", "value2"]
