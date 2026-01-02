from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class Role(RoleBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class PermissionBase(BaseModel):
    resource_type: str
    resource_id: Optional[int] = None
    action: str

class PermissionCreate(PermissionBase):
    role_id: int

class Permission(PermissionBase):
    id: int
    role_id: int
    
    model_config = ConfigDict(from_attributes=True)

class UserRoleBase(BaseModel):
    role_id: int
    is_dl: bool = False
    dl_name: Optional[str] = None

class UserRoleCreate(UserRoleBase):
    pass  # user_id comes from URL parameter in the endpoint

class UserRole(UserRoleBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

class CatalogueRolePermissionBase(BaseModel):
    catalogue_id: int
    permission_type: str  # 'read', 'write', 'admin'

class CatalogueRolePermissionCreate(CatalogueRolePermissionBase):
    role_id: int

class CatalogueRolePermission(CatalogueRolePermissionBase):
    id: int
    role_id: int
    
    model_config = ConfigDict(from_attributes=True)

class RoleWithPermissions(Role):
    catalogue_permissions: List[CatalogueRolePermission] = []

class CatalogueRolePermissionBase(BaseModel):
    catalogue_id: int
    permission_type: str = "read"

class CatalogueRolePermissionCreate(CatalogueRolePermissionBase):
    pass

class CatalogueRolePermission(CatalogueRolePermissionBase):
    id: int
    role_id: int
    
    model_config = ConfigDict(from_attributes=True)

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[Permission] = []
    catalogue_permissions: List[CatalogueRolePermission] = []
    
    model_config = ConfigDict(from_attributes=True)
