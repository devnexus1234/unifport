"""
Pytest configuration and fixtures for testing workers
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.core.database import Base, get_db
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.main import app
import os
from typing import Generator
from unittest.mock import patch


# Import all models to ensure they're registered with Base.metadata
from app.models import User, Catalogue, CatalogueCategory, Role, Permission, UserRole, CataloguePermission, CatalogueRolePermission
from app.models.capacity import CapacityValues, RegionZoneMapping, ZoneDeviceMapping
from app.models.capacity_network import CapacityNetworkValues, RegionZoneMappingNetwork, ZoneDeviceMappingNetwork

# Setup logging for tests
setup_logging()

# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(scope="function")
def test_db():
    """Create a test database engine and session for integration tests"""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    # Create all tables
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Return a session factory, not a session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(test_db) -> Generator:
    """Create a test client for unit tests"""
    # Mock the scheduler and job registry to avoid event loop issues during startup
    # Mock the scheduler and job registry in app.main to handle direct imports
    with patch('app.main.start_scheduler'), \
         patch('app.main.shutdown_scheduler'), \
         patch('app.main.register_all_jobs'), \
         patch('app.main.get_engine'):
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client


@pytest.fixture(scope="function")
async def async_client(test_db) -> AsyncClient:
    """Create an async test client for integration/e2e tests"""
    # Mock scheduler and job registry to prevent background jobs
    # And patch DATABASE_URL so startup event doesn't try to connect to Oracle
    # Mock scheduler and job registry in app.main
    with patch('app.main.start_scheduler'), \
         patch('app.main.shutdown_scheduler'), \
         patch('app.main.register_all_jobs'), \
         patch('app.core.config.settings.DATABASE_URL', TEST_DATABASE_URL):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    # Use the default event loop policy
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    try:
        yield loop
    finally:
        # Clean up any pending tasks
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        # Wait for tasks to complete cancellation
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset settings before each test"""
    # This ensures each test starts with clean settings
    yield
    # Settings are reloaded automatically


from typing import Dict
from app.core.security import create_access_token

@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, test_db) -> Dict[str, str]:
    from app.models.user import User
    
    # Check if user exists or create one
    user = test_db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            is_active=True,
            is_admin=False
        )
        test_db.add(user)
        test_db.commit()
    
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    return {"Authorization": f"Bearer {access_token}"}
