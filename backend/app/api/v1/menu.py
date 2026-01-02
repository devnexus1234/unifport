from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from app.core.database import get_db
from app.models.user import User
from app.models.catalogue import Catalogue, CatalogueCategory
from app.models.rbac import CatalogueRolePermission, UserRole, CataloguePermission
from app.api.v1.auth import get_current_active_user
from app.utils.rbac import is_admin_user

router = APIRouter(prefix="/menu", tags=["menu"])

def check_catalogue_permission(user: User, catalogue_id: int, db: Session, permission_type: str = "read"):
    """Check if user has permission to access a catalogue (user-based or role-based)"""
    # Admin users have all permissions (via is_admin flag or Admin role)
    if is_admin_user(user, db):
        return True
    
    # Get user's roles
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    
    if not role_ids:
        return False
    
    # Check catalogue-level permissions (Role based)
    catalogue_permission = db.query(CatalogueRolePermission).filter(
        CatalogueRolePermission.catalogue_id == catalogue_id,
        CatalogueRolePermission.role_id.in_(role_ids)
    ).first()
    
    if catalogue_permission:
        if permission_type:
            return catalogue_permission.permission_type == permission_type or catalogue_permission.permission_type == "admin"
        return True
    
    # Check user-specific permissions
    user_permission = db.query(CataloguePermission).filter(
        CataloguePermission.catalogue_id == catalogue_id,
        CataloguePermission.user_id == user.id,
        CataloguePermission.permission_type == permission_type
    ).first()
    
    if user_permission:
        return True
    
    # Check DL-based permissions
    for user_role in user_roles:
        if user_role.is_dl and user_role.dl_name:
            dl_permission = db.query(CataloguePermission).filter(
                CataloguePermission.catalogue_id == catalogue_id,
                CataloguePermission.dl_name == user_role.dl_name,
                CataloguePermission.permission_type == permission_type
            ).first()
            if dl_permission:
                return True
    
    return False

@router.get("/")
async def get_menu(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get side menu structure based on user permissions"""
    # Get all active categories
    categories = db.query(CatalogueCategory).filter(
        CatalogueCategory.is_active == True
    ).order_by(CatalogueCategory.display_order).all()
    
    menu_items = []
    
    for category in categories:
        # Get enabled catalogues in this category
        catalogues = db.query(Catalogue).filter(
            Catalogue.category_id == category.id,
            Catalogue.is_enabled == True,
            Catalogue.is_active == True
        ).order_by(Catalogue.display_order).all()
        
        # Filter catalogues by user permissions
        accessible_catalogues = []
        for catalogue in catalogues:
            if check_catalogue_permission(current_user, catalogue.id, db):
                accessible_catalogues.append({
                    "id": catalogue.id,
                    "name": catalogue.name,
                    "description": catalogue.description,
                    "route": catalogue.frontend_route,
                    "icon": catalogue.icon,
                    "api_endpoint": catalogue.api_endpoint
                })
        
        # Only include category if it has accessible catalogues (Implicit Permission)
        if accessible_catalogues:
            menu_items.append({
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "icon": category.icon,
                "catalogues": accessible_catalogues
            })
    
    return {"menu": menu_items}


