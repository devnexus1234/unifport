"""
Comprehensive Menu API Tests - Targeting 75%+ coverage
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.rbac import Role, UserRole, CataloguePermission, CatalogueRolePermission
from app.models.catalogue import Catalogue, CatalogueCategory

pytest_plugins = ["tests.fixtures.auth_fixtures"]

@pytest.mark.integration
class TestMenuAPIComprehensive:
    """Comprehensive tests for menu API to reach 75% coverage"""
    
    def test_get_menu_authenticated(self, client, regular_token_headers, test_db, regular_user):
        """Test getting menu with authentication"""
        category = CatalogueCategory(name="menucat", description="Menu", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="menucatalogue",
            description="Menu",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        # Give user permission
        perm = CataloguePermission(
            catalogue_id=catalogue.id,
            user_id=regular_user.id,
            permission_type="read"
        )
        test_db.add(perm)
        test_db.commit()
        
        response = client.get("/api/v1/menu/", headers=regular_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert "menu" in data
    
    def test_get_menu_admin(self, client, admin_token_headers, test_db):
        """Test getting menu as admin"""
        category = CatalogueCategory(name="adminmenu", description="Admin Menu", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="adminmenucatalogue",
            description="Admin Menu",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.get("/api/v1/menu/", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert "menu" in data
        assert isinstance(data["menu"], list)
    
    def test_get_menu_filters_by_permission(self, client, test_db, regular_user, regular_token_headers):
        """Test menu filters catalogues by user permissions"""
        category = CatalogueCategory(name="filtermenu", description="Filter", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        # Create two catalogues
        cat1 = Catalogue(
            name="accessible",
            description="Accessible",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        cat2 = Catalogue(
            name="inaccessible",
            description="Inaccessible",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=2
        )
        test_db.add_all([cat1, cat2])
        test_db.commit()
        
        # Give permission only to cat1
        perm = CataloguePermission(
            catalogue_id=cat1.id,
            user_id=regular_user.id,
            permission_type="read"
        )
        test_db.add(perm)
        test_db.commit()
        
        response = client.get("/api/v1/menu/", headers=regular_token_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should only show category with accessible catalogue
        if data["menu"]:
            for category_item in data["menu"]:
                catalogue_names = [c["name"] for c in category_item["catalogues"]]
                if "accessible" in catalogue_names:
                    assert "inaccessible" not in catalogue_names
    
    def test_get_menu_role_based_permission(self, client, test_db, user_with_role):
        """Test menu with role-based permissions"""
        from app.core.security import create_access_token
        
        category = CatalogueCategory(name="rolemenu", description="Role Menu", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="rolecatalogue",
            description="Role",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        # Get user's role
        user_role = test_db.query(UserRole).filter(UserRole.user_id == user_with_role.id).first()
        
        # Add role-based permission
        role_perm = CatalogueRolePermission(
            catalogue_id=catalogue.id,
            role_id=user_role.role_id,
            permission_type="read"
        )
        test_db.add(role_perm)
        test_db.commit()
        
        token = create_access_token(data={"sub": user_with_role.username, "user_id": user_with_role.id})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/menu/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "menu" in data
    
    def test_get_menu_dl_based_permission(self, client, test_db):
        """Test menu with DL-based permissions"""
        from app.core.security import create_access_token
        
        # Create user with DL role
        user = User(username="dlmenuuser", email="dlmenu@test.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        
        role = Role(name="DLMenuRole", description="DL Menu", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        user_role = UserRole(user_id=user.id, role_id=role.id, is_dl=True, dl_name="test_dl_menu")
        test_db.add(user_role)
        test_db.commit()
        
        category = CatalogueCategory(name="dlmenu", description="DL Menu", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="dlcatalogue",
            description="DL",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        # Add DL permission
        dl_perm = CataloguePermission(
            catalogue_id=catalogue.id,
            dl_name="test_dl_menu",
            permission_type="read"
        )
        test_db.add(dl_perm)
        test_db.commit()
        
        token = create_access_token(data={"sub": user.username, "user_id": user.id})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/menu/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "menu" in data
    
    def test_get_menu_no_permissions(self, client, test_db):
        """Test menu when user has no permissions"""
        from app.core.security import create_access_token
        
        user = User(username="nopermuser", email="noperm@test.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        
        category = CatalogueCategory(name="nopermmenu", description="No Perm", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="nopermcatalogue",
            description="No Perm",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        token = create_access_token(data={"sub": user.username, "user_id": user.id})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/menu/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "menu" in data
        # Menu should be empty or not include the category
        assert len(data["menu"]) == 0 or all(
            cat["name"] != "nopermmenu" for cat in data["menu"]
        )
    
    def test_menu_requires_auth(self, client):
        """Test menu requires authentication"""
        response = client.get("/api/v1/menu/")
        assert response.status_code in [401, 403]
