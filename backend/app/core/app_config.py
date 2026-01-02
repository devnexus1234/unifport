"""
Application-level configuration that is same across environments but configurable.
These are settings that don't change between dev/staging/prod but can be customized.
"""
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional

class AppConfig(BaseModel):
    """Application configuration"""
    # UI Settings
    app_title: str = "Unified Portal"
    app_description: str = "Unified automation portal with multiple catalogues"
    app_version: str = "1.0.0"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # File Upload
    max_upload_size_mb: int = 10
    allowed_file_types: list = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"]
    
    # UI Features
    enable_theme_toggle: bool = True
    default_theme: str = "light"  # light, dark, auto
    enable_notifications: bool = True
    enable_help_tooltips: bool = True
    
    # Catalogue Settings
    default_catalogue_icon: str = "description"
    max_catalogue_name_length: int = 255
    max_catalogue_description_length: int = 1000
    
    # Search & Filter
    enable_global_search: bool = True
    search_min_length: int = 2
    search_max_results: int = 50
    
    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    enable_lazy_loading: bool = True
    
    # Security
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = False
    
    # Notifications
    notification_duration_seconds: int = 5
    enable_sound_notifications: bool = False
    
    # Customizable branding
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: str = "#1976d2"
    secondary_color: str = "#424242"
    
    model_config = ConfigDict(extra="allow")

# Global app config instance
app_config = AppConfig()

def get_app_config() -> AppConfig:
    """Get application configuration"""
    return app_config

def update_app_config(**kwargs) -> AppConfig:
    """Update application configuration"""
    global app_config
    app_config = app_config.copy(update=kwargs)
    return app_config

