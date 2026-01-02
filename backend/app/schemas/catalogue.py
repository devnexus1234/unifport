from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.catalogue import CatalogueCategoryEnum

class CatalogueCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0
    is_enabled: bool = True

class CatalogueCategoryCreate(CatalogueCategoryBase):
    pass

class CatalogueCategory(CatalogueCategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CatalogueBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int  # Required: category is main grouping
    api_endpoint: Optional[str] = None
    frontend_route: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0
    config: Optional[Dict[str, Any]] = None

class CatalogueCreate(CatalogueBase):
    pass

class CatalogueUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    api_endpoint: Optional[str] = None
    frontend_route: Optional[str] = None
    icon: Optional[str] = None
    is_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    config: Optional[Dict[str, Any]] = None

class CatalogueResponse(CatalogueBase):
    id: int
    is_enabled: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CatalogueCategory] = None
    
    model_config = ConfigDict(from_attributes=True)

class Catalogue(CatalogueResponse):
    pass

