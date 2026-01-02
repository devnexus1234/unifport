"""
Comprehensive Admin API Tests - Targeting 75%+ coverage
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.rbac import Role, UserRole, CatalogueRolePermission
from app.models.catalogue import Catalogue, CatalogueCategory

pytest_plugins = ["tests.fixtures.auth_fixtures"]

@pytest.mark.integration
class TestAdminAPIComprehensive:
    """Comprehensive tests for admin API to reach 75% coverage"""
    
    def test_admin_root(self, client, admin_token_headers):
        """Test admin root endpoint"""
        response = client.get("/api/v1/admin/", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_admin_requires_auth(self, client):
        """Test admin endpoints require authentication"""
        response = client.get("/api/v1/admin/")
        assert response.status_code in [401, 403]
    
    def test_admin_requires_admin_role(self, client, regular_token_headers):
        """Test admin endpoints require admin role"""
        response = client.get("/api/v1/admin/", headers=regular_token_headers)
        assert response.status_code == 403
    
    # Role Management Tests
    def test_get_roles(self, client, admin_token_headers, test_db):
        """Test getting all roles"""
        role = Role(name="TestRole", description="Test", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.get("/api/v1/admin/roles", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_role_by_id(self, client, admin_token_headers, test_db):
        """Test getting specific role"""
        role = Role(name="SpecificRole", description="Specific", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.get(f"/api/v1/admin/roles/{role.id}", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SpecificRole"
    
    def test_get_role_not_found(self, client, admin_token_headers):
        """Test getting non-existent role"""
        response = client.get("/api/v1/admin/roles/99999", headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_create_role(self, client, admin_token_headers, test_db):
        """Test creating a role"""
        response = client.post("/api/v1/admin/roles", json={
            "name": "NewRole",
            "description": "New Role",
            "is_active": True
        }, headers=admin_token_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "NewRole"
    
    def test_create_role_duplicate(self, client, admin_token_headers, test_db):
        """Test creating duplicate role"""
        role = Role(name="DuplicateRole", description="Duplicate", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.post("/api/v1/admin/roles", json={
            "name": "DuplicateRole",
            "description": "Duplicate",
            "is_active": True
        }, headers=admin_token_headers)
        assert response.status_code == 400
    
    def test_update_role(self, client, admin_token_headers, test_db):
        """Test updating a role"""
        role = Role(name="UpdateRole", description="Update", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.put(f"/api/v1/admin/roles/{role.id}", json={
            "description": "Updated Description"
        }, headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated Description"
    
    def test_update_role_not_found(self, client, admin_token_headers):
        """Test updating non-existent role"""
        response = client.put("/api/v1/admin/roles/99999", json={
            "description": "Updated"
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_delete_role(self, client, admin_token_headers, test_db):
        """Test deleting a role"""
        role = Role(name="DeleteRole", description="Delete", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.delete(f"/api/v1/admin/roles/{role.id}", headers=admin_token_headers)
        assert response.status_code == 204
    
    # Catalogue Permission Tests
    def test_assign_catalogue_permission(self, client, admin_token_headers, test_db):
        """Test assigning catalogue permission to role"""
        role = Role(name="PermRole", description="Perm", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        category = CatalogueCategory(name="permcat", description="Perm", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="permcatalogue",
            description="Perm",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.post(f"/api/v1/admin/roles/{role.id}/catalogue-permissions", json={
            "catalogue_id": catalogue.id,
            "permission_type": "read"
        }, headers=admin_token_headers)
        assert response.status_code == 201
    
    def test_remove_catalogue_permission(self, client, admin_token_headers, test_db):
        """Test removing catalogue permission"""
        role = Role(name="RemovePermRole", description="Remove", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        category = CatalogueCategory(name="removecat", description="Remove", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="removecatalogue",
            description="Remove",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        perm = CatalogueRolePermission(
            role_id=role.id,
            catalogue_id=catalogue.id,
            permission_type="read"
        )
        test_db.add(perm)
        test_db.commit()
        
        response = client.delete(
            f"/api/v1/admin/roles/{role.id}/catalogue-permissions/{catalogue.id}",
            headers=admin_token_headers
        )
        assert response.status_code == 204
    
    # Catalogue Management Tests
    def test_get_all_catalogues(self, client, admin_token_headers, test_db):
        """Test getting all catalogues"""
        category = CatalogueCategory(name="admincat", description="Admin", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="admincatalogue",
            description="Admin",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.get("/api/v1/admin/catalogues", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_catalogue(self, client, admin_token_headers, test_db):
        """Test creating catalogue"""
        category = CatalogueCategory(name="createcat", description="Create", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        response = client.post("/api/v1/admin/catalogues", json={
            "name": "newcatalogue",
            "description": "New Catalogue",
            "category_id": category.id,
            "is_active": True,
            "is_enabled": True,
            "display_order": 1
        }, headers=admin_token_headers)
        assert response.status_code == 201
    
    def test_update_catalogue(self, client, admin_token_headers, test_db):
        """Test updating catalogue"""
        category = CatalogueCategory(name="updatecat", description="Update", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="updatecatalogue",
            description="Update",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.put(f"/api/v1/admin/catalogues/{catalogue.id}", json={
            "description": "Updated Description"
        }, headers=admin_token_headers)
        assert response.status_code == 200
    
    def test_delete_catalogue(self, client, admin_token_headers, test_db):
        """Test deleting catalogue"""
        category = CatalogueCategory(name="deletecat", description="Delete", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="deletecatalogue",
            description="Delete",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.delete(f"/api/v1/admin/catalogues/{catalogue.id}", headers=admin_token_headers)
        assert response.status_code == 204
    
    # Category Management Tests
    def test_get_all_categories(self, client, admin_token_headers, test_db):
        """Test getting all categories"""
        category = CatalogueCategory(name="getcat", description="Get", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        response = client.get("/api/v1/admin/categories", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_category(self, client, admin_token_headers):
        """Test creating category"""
        response = client.post("/api/v1/admin/categories", json={
            "name": "newcategory",
            "description": "New Category",
            "is_active": True,
            "display_order": 1
        }, headers=admin_token_headers)
        assert response.status_code == 201
    
    def test_update_category(self, client, admin_token_headers, test_db):
        """Test updating category"""
        category = CatalogueCategory(name="updatecategory", description="Update", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        response = client.put(f"/api/v1/admin/categories/{category.id}", json={
            "description": "Updated Description"
        }, headers=admin_token_headers)
        assert response.status_code == 200
    
    def test_delete_category(self, client, admin_token_headers, test_db):
        """Test deleting category"""
        category = CatalogueCategory(name="deletecategory", description="Delete", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        response = client.delete(f"/api/v1/admin/categories/{category.id}", headers=admin_token_headers)
        assert response.status_code == 204
    
    # User Management Tests
    def test_get_all_users(self, client, admin_token_headers, test_db):
        """Test getting all users"""
        response = client.get("/api/v1/admin/users", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_user_roles(self, client, admin_token_headers, test_db, regular_user):
        """Test getting user roles"""
        response = client.get(f"/api/v1/admin/users/{regular_user.id}/roles", headers=admin_token_headers)
        assert response.status_code == 200
    
    def test_assign_role_to_user(self, client, admin_token_headers, test_db, regular_user):
        """Test assigning role to user"""
        role = Role(name="AssignRole", description="Assign", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.post(f"/api/v1/admin/users/{regular_user.id}/roles", json={
            "role_id": role.id,
            "is_dl": False
        }, headers=admin_token_headers)
        assert response.status_code in [201, 400]  # 400 if already assigned
    
    def test_remove_role_from_user(self, client, admin_token_headers, test_db, regular_user):
        """Test removing role from user"""
        role = Role(name="RemoveRole", description="Remove", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        user_role = UserRole(user_id=regular_user.id, role_id=role.id)
        test_db.add(user_role)
        test_db.commit()
        
        response = client.delete(
            f"/api/v1/admin/users/{regular_user.id}/roles/{role.id}",
            headers=admin_token_headers
        )
        assert response.status_code == 204
    
    # Reordering Tests
    def test_reorder_category(self, client, admin_token_headers, test_db):
        """Test reordering category"""
        category = CatalogueCategory(name="reordercat", description="Reorder", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        response = client.put(f"/api/v1/admin/categories/{category.id}/reorder", json={
            "display_order": 5
        }, headers=admin_token_headers)
        assert response.status_code == 200
    
    def test_reorder_catalogue(self, client, admin_token_headers, test_db):
        """Test reordering catalogue"""
        category = CatalogueCategory(name="reordercat2", description="Reorder", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="reordercatalogue",
            description="Reorder",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.put(f"/api/v1/admin/catalogues/{catalogue.id}/reorder", json={
            "display_order": 10
        }, headers=admin_token_headers)
        assert response.status_code == 200
    
    # Error Handling Tests
    def test_assign_permission_role_not_found(self, client, admin_token_headers, test_db):
        """Test assigning permission to non-existent role"""
        category = CatalogueCategory(name="errcat", description="Error", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="errcatalogue",
            description="Error",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.post("/api/v1/admin/roles/99999/catalogue-permissions", json={
            "catalogue_id": catalogue.id,
            "permission_type": "read"
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_assign_permission_catalogue_not_found(self, client, admin_token_headers, test_db):
        """Test assigning permission for non-existent catalogue"""
        role = Role(name="ErrRole", description="Error", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.post(f"/api/v1/admin/roles/{role.id}/catalogue-permissions", json={
            "catalogue_id": 99999,
            "permission_type": "read"
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_assign_role_user_not_found(self, client, admin_token_headers, test_db):
        """Test assigning role to non-existent user"""
        role = Role(name="AssignErrRole", description="Assign Error", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.post("/api/v1/admin/users/99999/roles", json={
            "role_id": role.id
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_assign_nonexistent_role_to_user(self, client, admin_token_headers, test_db, regular_user):
        """Test assigning non-existent role to user"""
        response = client.post(f"/api/v1/admin/users/{regular_user.id}/roles", json={
            "role_id": 99999
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_create_catalogue_with_config(self, client, admin_token_headers, test_db):
        """Test creating catalogue with config"""
        category = CatalogueCategory(name="configcat", description="Config", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        response = client.post("/api/v1/admin/catalogues", json={
            "name": "configcatalogue",
            "description": "Config Catalogue",
            "category_id": category.id,
            "is_active": True,
            "is_enabled": True,
            "display_order": 1,
            "config": {"key": "value"}
        }, headers=admin_token_headers)
        assert response.status_code == 201
    
    def test_create_catalogue_duplicate(self, client, admin_token_headers, test_db):
        """Test creating duplicate catalogue"""
        category = CatalogueCategory(name="dupcat", description="Dup", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="dupcatalogue",
            description="Dup",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.post("/api/v1/admin/catalogues", json={
            "name": "dupcatalogue",
            "description": "Duplicate",
            "category_id": category.id,
            "is_active": True,
            "is_enabled": True,
            "display_order": 1
        }, headers=admin_token_headers)
        assert response.status_code == 400
    
    def test_update_catalogue_not_found(self, client, admin_token_headers):
        """Test updating non-existent catalogue"""
        response = client.put("/api/v1/admin/catalogues/99999", json={
            "description": "Updated"
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_delete_catalogue_not_found(self, client, admin_token_headers):
        """Test deleting non-existent catalogue"""
        response = client.delete("/api/v1/admin/catalogues/99999", headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_create_category_duplicate(self, client, admin_token_headers, test_db):
        """Test creating duplicate category"""
        category = CatalogueCategory(name="dupcat2", description="Dup", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        response = client.post("/api/v1/admin/categories", json={
            "name": "dupcat2",
            "description": "Duplicate",
            "is_active": True,
            "display_order": 1
        }, headers=admin_token_headers)
        assert response.status_code == 400
    
    def test_update_category_not_found(self, client, admin_token_headers):
        """Test updating non-existent category"""
        response = client.put("/api/v1/admin/categories/99999", json={
            "description": "Updated"
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_delete_category_not_found(self, client, admin_token_headers):
        """Test deleting non-existent category"""
        response = client.delete("/api/v1/admin/categories/99999", headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_reorder_category_not_found(self, client, admin_token_headers):
        """Test reordering non-existent category"""
        response = client.put("/api/v1/admin/categories/99999/reorder", json={
            "display_order": 5
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_reorder_catalogue_not_found(self, client, admin_token_headers):
        """Test reordering non-existent catalogue"""
        response = client.put("/api/v1/admin/catalogues/99999/reorder", json={
            "display_order": 5
        }, headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_reorder_category_missing_order(self, client, admin_token_headers, test_db):
        """Test reordering category without display_order"""
        category = CatalogueCategory(name="missingorder", description="Missing", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        response = client.put(f"/api/v1/admin/categories/{category.id}/reorder", json={}, headers=admin_token_headers)
        assert response.status_code == 400
    
    def test_reorder_catalogue_missing_order(self, client, admin_token_headers, test_db):
        """Test reordering catalogue without display_order"""
        category = CatalogueCategory(name="missingorder2", description="Missing", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="missingordercatalogue",
            description="Missing",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        response = client.put(f"/api/v1/admin/catalogues/{catalogue.id}/reorder", json={}, headers=admin_token_headers)
        assert response.status_code == 400
    
    def test_get_user_roles_not_found(self, client, admin_token_headers):
        """Test getting roles for non-existent user"""
        response = client.get("/api/v1/admin/users/99999/roles", headers=admin_token_headers)
        assert response.status_code == 404
    
    def test_remove_role_not_found(self, client, admin_token_headers, test_db, regular_user):
        """Test removing non-existent role assignment"""
        response = client.delete(
            f"/api/v1/admin/users/{regular_user.id}/roles/99999",
            headers=admin_token_headers
        )
        assert response.status_code == 404
    
    def test_remove_permission_not_found(self, client, admin_token_headers, test_db):
        """Test removing non-existent permission"""
        role = Role(name="RemovePerm", description="Remove", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        response = client.delete(
            f"/api/v1/admin/roles/{role.id}/catalogue-permissions/99999",
            headers=admin_token_headers
        )
        assert response.status_code == 404
    
    def test_assign_permission_update_existing(self, client, admin_token_headers, test_db):
        """Test updating existing permission"""
        role = Role(name="UpdatePerm", description="Update", is_active=True)
        test_db.add(role)
        test_db.commit()
        
        category = CatalogueCategory(name="updateperm", description="Update", is_active=True, display_order=1)
        test_db.add(category)
        test_db.commit()
        
        catalogue = Catalogue(
            name="updatepermcat",
            description="Update",
            category_id=category.id,
            is_active=True,
            is_enabled=True,
            display_order=1
        )
        test_db.add(catalogue)
        test_db.commit()
        
        # Create initial permission
        perm = CatalogueRolePermission(
            role_id=role.id,
            catalogue_id=catalogue.id,
            permission_type="read"
        )
        test_db.add(perm)
        test_db.commit()
        
        # Update to admin permission
        response = client.post(f"/api/v1/admin/roles/{role.id}/catalogue-permissions", json={
            "catalogue_id": catalogue.id,
            "permission_type": "admin"
        }, headers=admin_token_headers)
        assert response.status_code == 201
