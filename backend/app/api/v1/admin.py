from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from app.core.database import get_db
from app.models.user import User
from app.models.rbac import (
    Role as RoleModel, 
    CataloguePermission as CataloguePermissionModel,
    CatalogueRolePermission as CatalogueRolePermissionModel,
    UserRole as UserRoleModel
)
from app.models.catalogue import Catalogue, CatalogueCategory
from app.api.v1.auth import get_current_active_user
from app.utils.rbac import is_admin_user
from app.schemas.rbac import (
    RoleCreate, RoleUpdate, Role, RoleWithPermissions,
    CatalogueRolePermissionCreate, CatalogueRolePermission,
    UserRoleCreate, UserRole
)
from app.schemas.catalogue import CatalogueCreate, CatalogueUpdate, CatalogueResponse

router = APIRouter(prefix="/admin", tags=["admin"])

def _parse_config(config_value):
    """Parse config JSON string to dict, handling errors gracefully"""
    if not config_value:
        return None
    try:
        if isinstance(config_value, str):
            return json.loads(config_value)
        elif isinstance(config_value, dict):
            return config_value
        return None
    except (json.JSONDecodeError, TypeError):
        return None

def require_admin(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Dependency to require admin access
    
    Checks if user has admin privileges via:
    1. is_admin flag, OR
    2. "Admin" role assignment
    """
    if not is_admin_user(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/")
async def admin_root(current_user: User = Depends(require_admin)):
    """Admin endpoint placeholder"""
    return {"message": "Admin API", "status": "available"}

# Role Management Endpoints
@router.get("/roles", response_model=List[Role])
async def get_roles(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all roles"""
    try:
        roles = db.query(RoleModel).filter(RoleModel.is_active == True).all()
        # Convert to dict to avoid relationship serialization issues
        return [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "is_active": role.is_active
            }
            for role in roles
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching roles: {str(e)}"
        )

@router.get("/roles/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get a specific role with its permissions"""
    try:
        role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        catalogue_perms = db.query(CatalogueRolePermissionModel).filter(
            CatalogueRolePermissionModel.role_id == role_id
        ).all()
        
        # Convert permissions to dicts to avoid relationship serialization issues
        catalogue_perms_dict = [
            {
                "id": perm.id,
                "role_id": perm.role_id,
                "catalogue_id": perm.catalogue_id,
                "permission_type": perm.permission_type
            }
            for perm in catalogue_perms
        ]
        
        role_dict = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
            "catalogue_permissions": catalogue_perms_dict
        }
        return role_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching role: {str(e)}"
        )

@router.post("/roles", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new role"""
    try:
        # Check if role with same name exists
        existing = db.query(RoleModel).filter(RoleModel.name == role_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Role with this name already exists")
        
        # Use model_dump for Pydantic v2, fallback to dict for v1
        role_data_dict = role_data.model_dump() if hasattr(role_data, 'model_dump') else role_data.dict()
        role = RoleModel(**role_data_dict)
        db.add(role)
        db.commit()
        db.refresh(role)
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating role: {str(e)}"
        )

@router.put("/roles/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a role"""
    try:
        role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Use model_dump for Pydantic v2, fallback to dict for v1
        update_data = role_data.model_dump(exclude_unset=True) if hasattr(role_data, 'model_dump') else role_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
        
        db.commit()
        db.refresh(role)
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating role: {str(e)}"
        )

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete (deactivate) a role"""
    try:
        role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        role.is_active = False
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting role: {str(e)}"
        )



# Catalogue Permission Management
@router.post("/roles/{role_id}/catalogue-permissions", response_model=CatalogueRolePermission, status_code=status.HTTP_201_CREATED)
async def assign_catalogue_permission(
    role_id: int,
    perm_data: CatalogueRolePermissionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign catalogue permission to a role"""
    try:
        # Verify role exists
        role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Verify catalogue exists
        catalogue = db.query(Catalogue).filter(Catalogue.id == perm_data.catalogue_id).first()
        if not catalogue:
            raise HTTPException(status_code=404, detail="Catalogue not found")
        
        # Check if permission already exists
        existing = db.query(CatalogueRolePermissionModel).filter(
            CatalogueRolePermissionModel.role_id == role_id,
            CatalogueRolePermissionModel.catalogue_id == perm_data.catalogue_id
        ).first()
        if existing:
            existing.permission_type = perm_data.permission_type
            db.commit()
            db.refresh(existing)
            return {
                "id": existing.id,
                "role_id": existing.role_id,
                "catalogue_id": existing.catalogue_id,
                "permission_type": existing.permission_type
            }
        
        perm = CatalogueRolePermissionModel(
            role_id=role_id,
            catalogue_id=perm_data.catalogue_id,
            permission_type=perm_data.permission_type
        )
        db.add(perm)
        db.commit()
        db.refresh(perm)
        return {
            "id": perm.id,
            "role_id": perm.role_id,
            "catalogue_id": perm.catalogue_id,
            "permission_type": perm.permission_type
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning catalogue permission: {str(e)}"
        )

@router.delete("/roles/{role_id}/catalogue-permissions/{catalogue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_catalogue_permission(
    role_id: int,
    catalogue_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove catalogue permission from a role"""
    perm = db.query(CatalogueRolePermissionModel).filter(
        CatalogueRolePermissionModel.role_id == role_id,
        CatalogueRolePermissionModel.catalogue_id == catalogue_id
    ).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    db.delete(perm)
    db.commit()
    return None



@router.put("/categories/{category_id}/reorder", status_code=status.HTTP_200_OK)
async def reorder_category(
    category_id: int,
    order_data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update display order of a category"""
    try:
        category = db.query(CatalogueCategory).filter(CatalogueCategory.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        new_order = order_data.get("display_order")
        if new_order is None:
            raise HTTPException(status_code=400, detail="display_order is required")
        
        category.display_order = new_order
        db.commit()
        db.refresh(category)
        return {"id": category.id, "display_order": category.display_order}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating category order: {str(e)}"
        )

@router.put("/catalogues/{catalogue_id}/reorder", status_code=status.HTTP_200_OK)
async def reorder_catalogue(
    catalogue_id: int,
    order_data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update display order of a catalogue"""
    try:
        catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
        if not catalogue:
            raise HTTPException(status_code=404, detail="Catalogue not found")
        
        new_order = order_data.get("display_order")
        if new_order is None:
            raise HTTPException(status_code=400, detail="display_order is required")
        
        catalogue.display_order = new_order
        db.commit()
        db.refresh(catalogue)
        return {"id": catalogue.id, "display_order": catalogue.display_order}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating catalogue order: {str(e)}"
        )

@router.get("/catalogues")
async def get_all_catalogues(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all catalogues for admin panel"""
    try:
        catalogues = db.query(Catalogue).filter(Catalogue.is_active == True).order_by(Catalogue.display_order).all()
        # Convert to dict to avoid relationship serialization issues
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "category_id": cat.category_id,
                "icon": cat.icon,
                "frontend_route": cat.frontend_route,
                "api_endpoint": cat.api_endpoint,
                "display_order": cat.display_order,
                "is_enabled": cat.is_enabled,
                "is_active": cat.is_active,
                "config": json.loads(cat.config) if cat.config else None
            }
            for cat in catalogues
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching catalogues: {str(e)}"
        )

# Catalogue Management Endpoints
@router.post("/catalogues", response_model=CatalogueResponse, status_code=status.HTTP_201_CREATED)
async def create_catalogue(
    catalogue_data: CatalogueCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new catalogue"""
    
    # Check if catalogue with same name exists
    existing = db.query(Catalogue).filter(Catalogue.name == catalogue_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Catalogue with this name already exists")
    
    try:
        # Use model_dump for Pydantic v2, fallback to dict for v1
        catalogue_data_dict = catalogue_data.model_dump() if hasattr(catalogue_data, 'model_dump') else catalogue_data.dict()
        
        # Handle config field (convert dict to JSON string for database storage)
        if 'config' in catalogue_data_dict and catalogue_data_dict['config'] is not None:
            if isinstance(catalogue_data_dict['config'], dict):
                catalogue_data_dict['config'] = json.dumps(catalogue_data_dict['config'])
            elif isinstance(catalogue_data_dict['config'], str):
                # Already a string, keep as is
                pass
        
        catalogue = Catalogue(**catalogue_data_dict)
        db.add(catalogue)
        db.commit()
        db.refresh(catalogue)
        
        # Get category if exists
        category_data = None
        if catalogue.category_id:
            category = db.query(CatalogueCategory).filter(CatalogueCategory.id == catalogue.category_id).first()
            if category:
                category_data = {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "icon": category.icon,
                    "display_order": category.display_order,
                    "is_active": category.is_active,
                    "created_at": category.created_at.isoformat() if category.created_at else None
                }
        
        # Return as dict to avoid relationship serialization issues
        return {
            "id": catalogue.id,
            "name": catalogue.name,
            "description": catalogue.description,
            "category_id": catalogue.category_id,
            "icon": catalogue.icon,
            "frontend_route": catalogue.frontend_route,
            "api_endpoint": catalogue.api_endpoint,
            "display_order": catalogue.display_order,
            "is_enabled": catalogue.is_enabled,
            "is_active": catalogue.is_active,
            "config": _parse_config(catalogue.config),
            "created_at": catalogue.created_at.isoformat() if catalogue.created_at else None,
            "updated_at": catalogue.updated_at.isoformat() if catalogue.updated_at else None,
            "category": category_data
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating catalogue: {str(e)}"
        )

@router.put("/catalogues/{catalogue_id}", response_model=CatalogueResponse)
async def update_catalogue(
    catalogue_id: int,
    catalogue_data: CatalogueUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a catalogue"""
    try:
        catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
        if not catalogue:
            raise HTTPException(status_code=404, detail="Catalogue not found")
        
        # Use model_dump for Pydantic v2, fallback to dict for v1
        update_data = catalogue_data.model_dump(exclude_unset=True) if hasattr(catalogue_data, 'model_dump') else catalogue_data.dict(exclude_unset=True)
        
        # Handle config field (JSON string conversion)
        if 'config' in update_data and update_data['config'] is not None:
            if isinstance(update_data['config'], dict):
                update_data['config'] = json.dumps(update_data['config'])
        
        # Update catalogue fields
        for field, value in update_data.items():
            if hasattr(catalogue, field):
                setattr(catalogue, field, value)
        
        db.commit()
        db.refresh(catalogue)
        
        # Get category if exists
        category_data = None
        if catalogue.category_id:
            category = db.query(CatalogueCategory).filter(CatalogueCategory.id == catalogue.category_id).first()
            if category:
                category_data = {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "icon": category.icon,
                    "display_order": category.display_order,
                    "is_active": category.is_active,
                    "created_at": category.created_at.isoformat() if category.created_at else None
                }
        
        # Return as dict to avoid relationship serialization issues
        return {
            "id": catalogue.id,
            "name": catalogue.name,
            "description": catalogue.description,
            "category_id": catalogue.category_id,
            "icon": catalogue.icon,
            "frontend_route": catalogue.frontend_route,
            "api_endpoint": catalogue.api_endpoint,
            "display_order": catalogue.display_order,
            "is_enabled": catalogue.is_enabled,
            "is_active": catalogue.is_active,
            "config": _parse_config(catalogue.config),
            "created_at": catalogue.created_at.isoformat() if catalogue.created_at else None,
            "updated_at": catalogue.updated_at.isoformat() if catalogue.updated_at else None,
            "category": category_data
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating catalogue: {str(e)}"
        )

@router.delete("/catalogues/{catalogue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalogue(
    catalogue_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a catalogue from the database"""
    try:
        catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
        if not catalogue:
            raise HTTPException(status_code=404, detail="Catalogue not found")
        
        # Delete related permissions first (if cascade doesn't work due to DB constraints)
        # The cascade relationships should handle this, but we'll do it explicitly to be safe
        
        # Delete catalogue permissions
        db.query(CataloguePermissionModel).filter(
            CataloguePermissionModel.catalogue_id == catalogue_id
        ).delete(synchronize_session=False)
        
        # Delete catalogue role permissions
        db.query(CatalogueRolePermissionModel).filter(
            CatalogueRolePermissionModel.catalogue_id == catalogue_id
        ).delete(synchronize_session=False)
        
        # Now delete the catalogue itself
        db.delete(catalogue)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting catalogue: {str(e)}"
        )

# Category Management Endpoints
@router.get("/categories")
async def get_all_categories(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all categories for admin panel (including inactive ones)"""
    try:
        categories = db.query(CatalogueCategory).order_by(CatalogueCategory.display_order).all()
        # Convert to dict to avoid relationship serialization issues
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "icon": cat.icon,
                "display_order": cat.display_order,
                "is_enabled": cat.is_enabled,
                "is_active": cat.is_active
            }
            for cat in categories
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )

@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new category"""
    # Check if category with same name exists
    existing = db.query(CatalogueCategory).filter(CatalogueCategory.name == category_data.get('name')).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category = CatalogueCategory(**category_data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    category_data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a category"""
    category = db.query(CatalogueCategory).filter(CatalogueCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = {k: v for k, v in category_data.items() if v is not None}
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a category - removes it completely from the database"""
    try:
        category = db.query(CatalogueCategory).filter(CatalogueCategory.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Set category_id to NULL for all catalogues associated with this category
        # This allows us to delete the category even if it has associated catalogues
        db.query(Catalogue).filter(Catalogue.category_id == category_id).update(
            {Catalogue.category_id: None},
            synchronize_session=False
        )
        
        # Hard delete: remove the category from the database
        db.delete(category)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )

# User-Role Assignment Management
@router.get("/users")
async def get_all_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users with their roles"""
    try:
        users = db.query(User).filter(User.is_active == True).all()
        result = []
        for user in users:
            user_roles = db.query(UserRoleModel).filter(UserRoleModel.user_id == user.id).all()
            role_ids = [ur.role_id for ur in user_roles]
            roles = db.query(RoleModel).filter(RoleModel.id.in_(role_ids)).all() if role_ids else []
            
            result.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
                "roles": [{"id": r.id, "name": r.name} for r in roles]
            })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all roles assigned to a user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_roles = db.query(UserRoleModel).filter(UserRoleModel.user_id == user_id).all()
        role_ids = [ur.role_id for ur in user_roles]
        roles = db.query(RoleModel).filter(RoleModel.id.in_(role_ids)).all() if role_ids else []
        
        return {
            "user_id": user.id,
            "username": user.username,
            "roles": [{"id": r.id, "name": r.name, "description": r.description} for r in roles]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user roles: {str(e)}"
        )

@router.post("/users/{user_id}/roles", response_model=UserRole, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    user_id: int,
    role_data: UserRoleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign a role to a user"""
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify role exists
        role = db.query(RoleModel).filter(RoleModel.id == role_data.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if assignment already exists
        existing = db.query(UserRoleModel).filter(
            UserRoleModel.user_id == user_id,
            UserRoleModel.role_id == role_data.role_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Role already assigned to user")
        
        # Use user_id from URL, not from request body
        user_role = UserRoleModel(
            user_id=user_id,
            role_id=role_data.role_id,
            is_dl=role_data.is_dl if role_data.is_dl is not None else False,
            dl_name=role_data.dl_name
        )
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        
        return {
            "id": user_role.id,
            "user_id": user_role.user_id,
            "role_id": user_role.role_id,
            "is_dl": user_role.is_dl,
            "dl_name": user_role.dl_name
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning role to user: {str(e)}"
        )

@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove a role from a user"""
    try:
        user_role = db.query(UserRoleModel).filter(
            UserRoleModel.user_id == user_id,
            UserRoleModel.role_id == role_id
        ).first()
        if not user_role:
            raise HTTPException(status_code=404, detail="Role assignment not found")
        
        db.delete(user_role)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing role from user: {str(e)}"
        )

@router.put("/users/{user_id}/status", status_code=status.HTTP_200_OK)
async def update_user_status(
    user_id: int,
    status_data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user status (is_admin, is_active)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if "is_admin" in status_data:
            user.is_admin = status_data["is_admin"]
            
        if "is_active" in status_data:
            user.is_active = status_data["is_active"]
            
        db.commit()
        db.refresh(user)
        
        return {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user status: {str(e)}"
        )

