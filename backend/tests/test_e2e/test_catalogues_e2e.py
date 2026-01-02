"""
End-to-end tests for catalogue workflows
These tests simulate complete user workflows with catalogues
"""
import pytest
from fastapi import status
from app.models.user import User
from app.models.catalogue import Catalogue, CatalogueCategory
from app.models.rbac import Role, UserRole, CatalogueRolePermission
from app.core.security import create_access_token


@pytest.mark.e2e
class TestCataloguesE2E:
    """End-to-end tests for catalogues"""
    
    def test_complete_catalogue_access_flow(self, client, test_db):
        """Test complete flow: login -> get catalogues -> access specific catalogue"""
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
        
        
        # Create catalogue
        catalogue = Catalogue(
            name="Test Catalogue",
            category_id=category.id,
            is_enabled=True,
            is_active=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        test_db.refresh(catalogue)
        
        # Create admin role
        admin_role = Role(name="Admin")
        test_db.add(admin_role)
        test_db.commit()
        test_db.refresh(admin_role)
        
        # Assign role to user
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        test_db.add(user_role)
        test_db.commit()
        
        # Step 1: Login
        with pytest.MonkeyPatch().context() as m:
            from app.api.v1 import auth
            m.setattr(auth, 'authenticate_ldap', lambda u, p: True)
            m.setattr(auth, 'get_user_groups_ldap', lambda u: ["users"])
            
            login_response = client.post(
                "/api/v1/auth/login",
                json={"username": "testuser", "password": "password"}
            )
            
            assert login_response.status_code == status.HTTP_200_OK
            login_data = login_response.json()
            access_token = login_data["access_token"]
            
            # Step 2: Get all catalogues
            catalogues_response = client.get(
                "/api/v1/catalogues/",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert catalogues_response.status_code == status.HTTP_200_OK
            catalogues_data = catalogues_response.json()
            assert isinstance(catalogues_data, list)
            assert len(catalogues_data) >= 1
            
            # Step 3: Get specific catalogue
            catalogue_response = client.get(
                f"/api/v1/catalogues/{catalogue.id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert catalogue_response.status_code == status.HTTP_200_OK
            catalogue_data = catalogue_response.json()
            assert catalogue_data["id"] == catalogue.id
            assert catalogue_data["name"] == "Test Catalogue"
    
    def test_rbac_catalogue_access_flow(self, client, test_db):
        """Test RBAC-based catalogue access flow"""
        # Create regular user
        user = User(username="regularuser", email="regular@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create category
        category = CatalogueCategory(name="Test Category", is_active=True)
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        
        # Create catalogue
        catalogue = Catalogue(
            name="Test Catalogue",
            category_id=category.id,
            is_enabled=True,
            is_active=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        test_db.refresh(catalogue)
        
        # Create role with menu permission
        role = Role(name="MenuUser")
        test_db.add(role)
        test_db.commit()
        test_db.refresh(role)
        
        # Assign role to user
        user_role = UserRole(user_id=user.id, role_id=role.id)
        test_db.add(user_role)
        test_db.commit()
        
        # Create catalogue permission
        catalogue_permission = CatalogueRolePermission(catalogue_id=catalogue.id, role_id=role.id, permission_type="read")
        test_db.add(catalogue_permission)
        test_db.commit()
        
        # Login and access catalogue
        with pytest.MonkeyPatch().context() as m:
            from app.api.v1 import auth
            m.setattr(auth, 'authenticate_ldap', lambda u, p: True)
            m.setattr(auth, 'get_user_groups_ldap', lambda u: ["users"])
            
            login_response = client.post(
                "/api/v1/auth/login",
                json={"username": "regularuser", "password": "password"}
            )
            
            assert login_response.status_code == status.HTTP_200_OK
            access_token = login_response.json()["access_token"]
            
            # User should have access via menu permission
            catalogue_response = client.get(
                f"/api/v1/catalogues/{catalogue.id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert catalogue_response.status_code == status.HTTP_200_OK

