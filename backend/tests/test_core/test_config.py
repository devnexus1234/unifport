"""
Tests for Configuration Module
"""
import pytest
from unittest.mock import patch, MagicMock
import os
from app.core.config import Settings, load_settings

@pytest.mark.unit
class TestSettings:
    def test_settings_defaults(self):
        """Test default settings values"""
        settings = Settings()
        assert settings.APP_NAME == "Unified Portal"
        assert settings.DEBUG is True
        assert settings.ENVIRONMENT == "development"
    
    def test_get_cors_origins_string(self):
        """Test CORS origins from comma-separated string"""
        settings = Settings(CORS_ORIGINS="http://localhost:3000,http://localhost:4200")
        origins = settings.get_cors_origins()
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
    
    def test_get_cors_origins_list(self):
        """Test CORS origins from list"""
        settings = Settings(CORS_ORIGINS=["http://localhost:3000"])
        origins = settings.get_cors_origins()
        assert origins == ["http://localhost:3000"]
    
    def test_get_database_url_custom(self):
        """Test getting custom database URL"""
        custom_url = "oracle+cx_oracle://custom:pass@host:1521/service"
        settings = Settings(DATABASE_URL=custom_url)
        assert settings.get_database_url() == custom_url
    
    def test_get_database_url_build(self):
        """Test building database URL from components"""
        settings = Settings(
            ORACLE_USER="testuser",
            ORACLE_PASSWORD="testpass",
            ORACLE_HOST="testhost",
            ORACLE_PORT=1521,
            ORACLE_SERVICE="TESTDB"
        )
        url = settings.get_database_url()
        assert "testuser" in url
        assert "testhost" in url
        assert "service_name=TESTDB" in url
    
    def test_is_production(self):
        """Test production environment check"""
        settings = Settings(ENVIRONMENT="production")
        assert settings.is_production() is True
        assert settings.is_development() is False
    
    def test_is_development(self):
        """Test development environment check"""
        settings = Settings(ENVIRONMENT="development")
        assert settings.is_development() is True
        assert settings.is_production() is False
    
    @patch('app.core.config.Path.exists')
    @patch('app.core.config.os.getenv')
    def test_load_settings_development(self, mock_getenv, mock_exists):
        """Test loading development settings"""
        mock_getenv.return_value = "development"
        mock_exists.return_value = False
        
        settings = load_settings()
        assert settings.ENVIRONMENT == "development"
    
    @patch('app.core.config.Path.exists')
    @patch('app.core.config.os.getenv')
    def test_load_settings_production(self, mock_getenv, mock_exists):
        """Test loading production settings"""
        mock_getenv.return_value = "production"
        mock_exists.return_value = True
        
        settings = load_settings()
        assert settings.ENVIRONMENT == "production"
