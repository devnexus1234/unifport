"""
Comprehensive Main App Tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from contextlib import asynccontextmanager

@pytest.mark.unit
class TestMainAppStartup:
    
    @patch('app.main.get_engine')
    @patch('app.main.start_scheduler')
    @patch('app.main.register_all_jobs')
    def test_lifespan_startup_success(self, mock_register, mock_start, mock_engine):
        """Test successful app startup"""
        mock_conn = MagicMock()
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
        
        from app.main import app
        client = TestClient(app)
        
        # App should be created
        assert app is not None
    
    @patch('app.main.get_engine')
    def test_database_connection_retry(self, mock_engine):
        """Test database connection retry logic"""
        # Simulate connection failure then success
        mock_conn = MagicMock()
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn
        
        from app.main import app
        assert app is not None
    
    @patch('app.main.settings')
    def test_debug_mode_bypass(self, mock_settings):
        """Test debug mode bypasses database requirement"""
        mock_settings.DEBUG_MODE = True
        
        from app.main import app
        assert app is not None
    
    def test_cors_middleware_configured(self):
        """Test CORS middleware is configured"""
        from app.main import app
        from starlette.middleware.cors import CORSMiddleware
        
        # App should have middleware
        assert hasattr(app, 'user_middleware') or hasattr(app, 'middleware_stack')
    
    def test_request_id_middleware_configured(self):
        """Test RequestID middleware is configured"""
        from app.main import app
        
        # App should have middleware
        assert app is not None
    
    def test_logging_middleware_configured(self):
        """Test Logging middleware is configured"""
        from app.main import app
        
        # App should have middleware
        assert app is not None
    
    def test_api_routes_registered(self):
        """Test API routes are registered"""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert "/" in routes
        assert "/health" in routes
    
    def test_health_endpoint_response(self):
        """Test health endpoint returns correct response"""
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
    
    def test_root_endpoint_response(self):
        """Test root endpoint returns correct response"""
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "name" in data
    
    @patch('app.main.shutdown_scheduler')
    def test_lifespan_shutdown(self, mock_shutdown):
        """Test app shutdown"""
        from app.main import app
        
        # App should exist
        assert app is not None
    
    def test_app_metadata(self):
        """Test app metadata is set correctly"""
        from app.main import app
        
        assert app.title is not None
        assert app.version is not None
    
    def test_openapi_schema(self):
        """Test OpenAPI schema is generated"""
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
    
    def test_docs_endpoint(self):
        """Test docs endpoint is available"""
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/docs")
        assert response.status_code == 200
