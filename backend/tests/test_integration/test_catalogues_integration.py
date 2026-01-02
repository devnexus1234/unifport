"""
Integration tests for catalogue endpoints
These tests use a real test database
"""
import pytest
from fastapi import status
from app.models.user import User
from app.models.catalogue import Catalogue, CatalogueCategory
from app.models.rbac import Role, UserRole, CatalogueRolePermission
from app.core.security import create_access_token


@pytest.mark.integration
class TestCataloguesIntegration:
    """Integration tests for catalogues"""
    
    def test_get_catalogues(self, client, test_db):
        """Test getting all catalogues"""
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
        
        # Create admin role and assign to user
        admin_role = Role(name="Admin")
        test_db.add(admin_role)
        test_db.commit()
        test_db.refresh(admin_role)
        
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        test_db.add(user_role)
        test_db.commit()
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/catalogues/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_catalogue_by_id(self, client, test_db):
        """Test getting a specific catalogue"""
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
        
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        test_db.add(user_role)
        test_db.commit()
        
        # Create access token
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            f"/api/v1/catalogues/{catalogue.id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == catalogue.id
        assert data["name"] == "Test Catalogue"
    
    def test_get_catalogue_not_found(self, client, test_db):
        """Test getting non-existent catalogue"""
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create admin role
        admin_role = Role(name="Admin")
        test_db.add(admin_role)
        test_db.commit()
        test_db.refresh(admin_role)
        
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        test_db.add(user_role)
        test_db.commit()
        
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            "/api/v1/catalogues/99999",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_catalogue_access_denied(self, client, test_db):
        """Test getting catalogue without permission"""
        # Create user without admin role
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
        
        # User has no roles/permissions
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        response = client.get(
            f"/api/v1/catalogues/{catalogue.id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_catalogue_disabled_category(self, client, test_db):
        """Test getting catalogue in disabled category (is_enabled=False but is_active=True should still show)"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create category with is_enabled=False but is_active=True (should still appear)
        category = CatalogueCategory(name="Disabled Category", is_enabled=False, is_active=True)
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create catalogue (itself enabled, category is_enabled=False but is_active=True)
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
        
        # Create admin role and assign to user
        admin_role = Role(name="Admin")
        test_db.add(admin_role)
        test_db.commit()
        test_db.refresh(admin_role)
        
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        test_db.add(user_role)
        test_db.commit()
        
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        # Should appear in list because is_active=True (is_enabled is ignored for categories)
        response = client.get(
            "/api/v1/catalogues/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Ensure our catalogue IS in the list (is_enabled doesn't affect visibility)
        catalogue_ids = [c["id"] for c in data]
        assert catalogue.id in catalogue_ids

    def test_get_catalogue_inactive_category(self, client, test_db):
        """Test getting catalogue in inactive category (is_active=False) - should not appear anywhere"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create inactive category (is_active=False) - this is what controls visibility
        category = CatalogueCategory(name="Inactive Category", is_enabled=True, is_active=False)
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create catalogue (itself enabled, but category inactive)
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
        
        # Create admin role and assign to user
        admin_role = Role(name="Admin")
        test_db.add(admin_role)
        test_db.commit()
        test_db.refresh(admin_role)
        
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        test_db.add(user_role)
        test_db.commit()
        
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        # Should not appear in public catalogues list (is_active=False hides it)
        response = client.get(
            "/api/v1/catalogues/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Ensure our catalogue is not in the list
        catalogue_ids = [c["id"] for c in data]
        assert catalogue.id not in catalogue_ids
        
        # Should also not appear in menu (which populates header dropdown)
        menu_response = client.get(
            "/api/v1/menu/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert menu_response.status_code == status.HTTP_200_OK
        menu_data = menu_response.json()
        # Find our category in the menu
        test_category = next((m for m in menu_data["menu"] if m["id"] == category.id), None)
        # It should NOT be there because it is inactive
        assert test_category is None

    def test_admin_can_see_inactive_categories(self, client, test_db):
        """Test that admin can see inactive categories in admin endpoint"""
        # Create admin user
        admin_user = User(username="admin", email="admin@example.com", is_active=True)
        test_db.add(admin_user)
        test_db.commit()
        test_db.refresh(admin_user)
        
        # Create admin role and assign to user
        admin_role = Role(name="Admin")
        test_db.add(admin_role)
        test_db.commit()
        test_db.refresh(admin_role)
        
        user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        test_db.add(user_role)
        test_db.commit()
        
        # Create active category
        active_category = CatalogueCategory(name="Active Category", is_enabled=True, is_active=True)
        test_db.add(active_category)
        test_db.commit()
        test_db.refresh(active_category)
        
        # Create inactive category
        inactive_category = CatalogueCategory(name="Inactive Category", is_enabled=True, is_active=False)
        test_db.add(inactive_category)
        test_db.commit()
        test_db.refresh(inactive_category)
        
        access_token = create_access_token({"sub": admin_user.username, "user_id": admin_user.id, "email": admin_user.email})
        
        # Admin should see both active and inactive categories
        response = client.get(
            "/api/v1/admin/categories",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        category_ids = [c["id"] for c in data]
        # Both categories should be visible to admin
        assert active_category.id in category_ids
        assert inactive_category.id in category_ids
        
        # Verify the is_active field is present
        active_cat_data = next(c for c in data if c["id"] == active_category.id)
        inactive_cat_data = next(c for c in data if c["id"] == inactive_category.id)
        assert active_cat_data["is_active"] is True
        assert inactive_cat_data["is_active"] is False

    def test_menu_excludes_inactive_category_catalogues(self, client, test_db):
        """Test that menu endpoint excludes catalogues from inactive categories (is_active=False)
        Note: is_enabled is no longer checked for categories, only is_active matters"""
        # Create user
        user = User(username="testuser", email="test@example.com", is_active=True)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create inactive category (is_active=False - this controls visibility)
        inactive_category = CatalogueCategory(name="Inactive Category", is_enabled=True, is_active=False)
        test_db.add(inactive_category)
        test_db.commit()
        test_db.refresh(inactive_category)
        
        # Create active category (is_active=True)
        active_category = CatalogueCategory(name="Active Category", is_enabled=True, is_active=True)
        test_db.add(active_category)
        test_db.commit()
        test_db.refresh(active_category)
        
        # Create catalogue in inactive category
        inactive_cat_catalogue = Catalogue(
            name="Catalogue in Inactive Category",
            category_id=inactive_category.id,
            is_enabled=True,
            is_active=True,
            display_order=1
        )
        test_db.add(inactive_cat_catalogue)
        test_db.commit()
        test_db.refresh(inactive_cat_catalogue)
        
        # Create catalogue in active category
        active_cat_catalogue = Catalogue(
            name="Catalogue in Active Category",
            category_id=active_category.id,
            is_enabled=True,
            is_active=True,
            display_order=2
        )
        test_db.add(active_cat_catalogue)
        test_db.commit()
        test_db.refresh(active_cat_catalogue)
        
        # Create admin role and assign to user
        admin_role = Role(name="Admin")
        test_db.add(admin_role)
        test_db.commit()
        test_db.refresh(admin_role)
        
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        test_db.add(user_role)
        test_db.commit()
        
        # Create catalogue permission (required for access, check_catalogue_permission will fail otherwise unless admin)
        # Wait, the user has 'Admin' role created but not linked to specific catalogue permissions?
        # Actually in this test we give them Admin role. is_admin_user checks for Admin role.
        # So explicit permissions might not be needed if they are admin.
        # But let's look at the original test: it added MenuPermission.
        # check_catalogue_permission checks if user is admin. Admin role usually implies admin rights.
        # Let's see if we need to add CatalogueRolePermission.
        # If user is admin, they see everything?
        # The test creates 'Admin' role.
        # Is Admin role "special"?
        # In `rbac.py`: is_admin_user(user, db).
        # Let's assume Admin role grants all access.
        # But originally it added MenuPermission.
        # I'll add CatalogueRolePermission just in case logic requires explicit permission for non-superusers or if Admin role isn't enough for menu visibility logic (though menu logic usually filters by permission).
        
        # Actually, let's just NOT add permissions if Admin role covers it.
        # Or add permissions for both catalogues to the role, so we can verify visibility purely based on Category Active status.
        
        cat_perm1 = CatalogueRolePermission(catalogue_id=inactive_cat_catalogue.id, role_id=admin_role.id, permission_type="read")
        cat_perm2 = CatalogueRolePermission(catalogue_id=active_cat_catalogue.id, role_id=admin_role.id, permission_type="read")
        test_db.add(cat_perm1)
        test_db.add(cat_perm2)
        test_db.commit()
        
        access_token = create_access_token({"sub": user.username, "user_id": user.id, "email": user.email})
        
        # Get menu - should only include catalogue from active category
        # This menu endpoint is what populates the header dropdown
        response = client.get(
            "/api/v1/menu/",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "menu" in data
        assert len(data["menu"]) > 0
        
        # Find our category
        # The menu endpoint returns specific category structure.
        # We expect Active Category to be present.
        active_cat_entry = next((m for m in data["menu"] if m["id"] == active_category.id), None)
        assert active_cat_entry is not None
        
        # Inactive Category should NOT be present
        inactive_cat_entry = next((m for m in data["menu"] if m["id"] == inactive_category.id), None)
        assert inactive_cat_entry is None
        
        # Verify catalogues in active category
        catalogue_names = [c["name"] for c in active_cat_entry["catalogues"]]
        assert active_cat_catalogue.name in catalogue_names


