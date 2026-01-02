"""
Unit and integration tests for dashboard endpoints
"""
import pytest
from fastapi import status
from unittest.mock import patch
from app.models.user import User
from app.models.catalogue import Catalogue, CatalogueCategory
# from app.models.menu import Menu
from app.models.rbac import Role, UserRole
from app.core.security import create_access_token


@pytest.mark.unit
class TestDashboardUnit:
    """Unit tests for dashboard endpoints"""
    
    def test_dashboard_summary_structure(self, client, test_db):
        """Test dashboard summary endpoint returns correct structure"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check structure
        assert "users" in data
        assert "catalogues" in data
        assert "categories" in data
        assert "roles" in data
        assert "timestamp" in data
        
        # Check users structure
        assert "total" in data["users"]
        assert "active" in data["users"]
        assert "inactive" in data["users"]
        
        # Check catalogues structure
        assert "total" in data["catalogues"]
        assert "enabled" in data["catalogues"]
        assert "disabled" in data["catalogues"]
        
        # Check categories structure
        assert "total" in data["categories"]
        assert "active" in data["categories"]
        assert "inactive" in data["categories"]
        
        # Check roles structure
        assert "total" in data["roles"]
        assert "active" in data["roles"]
        assert "inactive" in data["roles"]
        assert "assignments" in data["roles"]


@pytest.mark.integration
class TestDashboardIntegration:
    """Integration tests for dashboard endpoints"""
    
    def test_dashboard_summary_counts_only_active_catalogues(self, client, test_db):
        """Test that dashboard only counts active catalogues"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create category
        category = CatalogueCategory(name="Test Category", is_active=True)
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create 1 active catalogue
        active_catalogue = Catalogue(
            name="Active Catalogue",
            category_id=category.id,
            is_active=True,
            is_enabled=True
        )
        test_db.add(active_catalogue)
        
        # Create 8 inactive catalogues (should not be counted)
        for i in range(8):
            inactive_catalogue = Catalogue(
                name=f"Inactive Catalogue {i}",
                category_id=category.id,
                is_active=False,  # Inactive
                is_enabled=False
            )
            test_db.add(inactive_catalogue)
        
        test_db.commit()
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only count 1 active catalogue, not 9
        assert data["catalogues"]["total"] == 1, f"Expected 1 active catalogue, got {data['catalogues']['total']}"
        assert data["catalogues"]["enabled"] == 1
        assert data["catalogues"]["disabled"] == 0
    
    def test_dashboard_summary_counts_users_correctly(self, client, test_db):
        """Test that dashboard counts users correctly"""
        # Create 3 active users
        active_users = []
        for i in range(3):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                is_active=True
            )
            test_db.add(user)
            active_users.append(user)
        
        # Create 2 inactive users
        for i in range(2):
            user = User(
                username=f"inactive_user{i}",
                email=f"inactive_user{i}@example.com",
                is_active=False
            )
            test_db.add(user)
        
        test_db.commit()
        # Use the first active user for authentication (inactive users can't authenticate)
        test_db.refresh(active_users[0])
        access_token = create_access_token({"sub": active_users[0].username, "user_id": active_users[0].id, "email": active_users[0].email})
        
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Total should be all users (5)
        assert data["users"]["total"] == 5
        # Active should be 3
        assert data["users"]["active"] == 3
        # Inactive should be 2
        assert data["users"]["inactive"] == 2
    
    def test_dashboard_summary_counts_categories_correctly(self, client, test_db):
        """Test that dashboard counts only active categories"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create 2 active categories
        for i in range(2):
            category = CatalogueCategory(name=f"Active Category {i}", is_active=True)
            test_db.add(category)
        
        # Create 3 inactive categories (should not be counted)
        for i in range(3):
            category = CatalogueCategory(name=f"Inactive Category {i}", is_active=False)
            test_db.add(category)
        
        test_db.commit()
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only count 2 active categories
        assert data["categories"]["total"] == 2
        assert data["categories"]["active"] == 2
        assert data["categories"]["inactive"] == 0
    
    def test_dashboard_summary_counts_roles_correctly(self, client, test_db):
        """Test that dashboard counts only active roles"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create 4 active roles
        active_roles = []
        for i in range(4):
            role = Role(name=f"Active Role {i}", is_active=True)
            test_db.add(role)
            active_roles.append(role)
        
        # Create 2 inactive roles (should not be counted)
        for i in range(2):
            role = Role(name=f"Inactive Role {i}", is_active=False)
            test_db.add(role)
        
        test_db.commit()
        
        # Create 3 role assignments
        for i in range(3):
            user_role = UserRole(user_id=user.id, role_id=active_roles[i].id)
            test_db.add(user_role)
        
        test_db.commit()
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only count 4 active roles
        assert data["roles"]["total"] == 4
        assert data["roles"]["active"] == 4
        assert data["roles"]["inactive"] == 0
        # Should count 3 role assignments
        assert data["roles"]["assignments"] == 3
    
    def test_dashboard_summary_enabled_vs_disabled_catalogues(self, client, test_db):
        """Test that dashboard correctly distinguishes enabled and disabled catalogues"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create category
        category = CatalogueCategory(name="Test Category", is_active=True)
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create 2 active and enabled catalogues
        for i in range(2):
            catalogue = Catalogue(
                name=f"Enabled Catalogue {i}",
                category_id=category.id,
                is_active=True,
                is_enabled=True
            )
            test_db.add(catalogue)
        
        # Create 1 active but disabled catalogue
        disabled_catalogue = Catalogue(
            name="Disabled Catalogue",
            category_id=category.id,
            is_active=True,
            is_enabled=False
        )
        test_db.add(disabled_catalogue)
        
        # Create 5 inactive catalogues (should not be counted at all)
        for i in range(5):
            catalogue = Catalogue(
                name=f"Inactive Catalogue {i}",
                category_id=category.id,
                is_active=False,
                is_enabled=False
            )
            test_db.add(catalogue)
        
        test_db.commit()
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should only count 3 active catalogues (2 enabled + 1 disabled)
        assert data["catalogues"]["total"] == 3
        assert data["catalogues"]["enabled"] == 2
        assert data["catalogues"]["disabled"] == 1
    
    def test_dashboard_summary_empty_database(self, client, test_db):
        """Test dashboard summary with empty database"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have 1 user (the one we created for auth)
        assert data["users"]["total"] == 1
        assert data["users"]["active"] == 1
        assert data["users"]["inactive"] == 0
        
        # All other counts should be 0
        assert data["catalogues"]["total"] == 0
        assert data["catalogues"]["enabled"] == 0
        assert data["catalogues"]["disabled"] == 0
        assert data["categories"]["total"] == 0
        assert data["categories"]["active"] == 0
        assert data["categories"]["inactive"] == 0
        assert data["roles"]["total"] == 0
        assert data["roles"]["active"] == 0
        assert data["roles"]["inactive"] == 0
        assert data["roles"]["assignments"] == 0
    
    def test_dashboard_health_structure(self, client, test_db):
        """Test dashboard health endpoint returns correct structure"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/dashboard/health",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check structure
        assert "overall" in data
        assert "components" in data
        assert "timestamp" in data
        
        # Check components
        assert "database" in data["components"]
        assert "api" in data["components"]
        # System may or may not be present depending on psutil availability
        # assert "system" in data["components"]
        
        # Check database health structure
        db_health = data["components"]["database"]
        assert "status" in db_health
        
        # Check API health structure
        api_health = data["components"]["api"]
        assert "status" in api_health
    
    def test_dashboard_health_database_status(self, client, test_db):
        """Test dashboard health endpoint database status"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        # Mock the database connection to test different scenarios
        with patch('app.core.database.get_engine') as mock_get_engine:
            # Test with engine available (SQLite in test mode)
            from sqlalchemy import create_engine
            from sqlalchemy.pool import StaticPool
            test_engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
            mock_get_engine.return_value = test_engine
            
            response = client.get(
                "/api/v1/dashboard/health",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Database status should be set (may be degraded in test mode)
            assert "status" in data["components"]["database"]
            # Status should be one of: healthy, degraded, unhealthy, unknown
            assert data["components"]["database"]["status"] in ["healthy", "degraded", "unhealthy", "unknown"]
    
    def test_dashboard_health_api_status(self, client, test_db):
        """Test dashboard health endpoint API status"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/dashboard/health",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # API should be healthy if we got a response
        api_health = data["components"]["api"]
        assert api_health["status"] == "healthy"
        # Response time should be present
        assert "response_time_ms" in api_health
    
    def test_dashboard_summary_requires_authentication(self, client):
        """Test that dashboard summary requires authentication"""
        response = client.get("/api/v1/dashboard/summary")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_dashboard_health_requires_authentication(self, client):
        """Test that dashboard health requires authentication"""
        response = client.get("/api/v1/dashboard/health")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

