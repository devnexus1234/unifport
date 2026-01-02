from fastapi import APIRouter, Depends
from app.core.app_config import get_app_config, AppConfig
from app.core.config import settings
from app.api.v1.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/config", tags=["configuration"])

@router.get("/app")
async def get_app_config_endpoint():
    """Get application-level configuration"""
    config = get_app_config()
    return {
        "app_title": config.app_title,
        "app_description": config.app_description,
        "app_version": config.app_version,
        "default_page_size": config.default_page_size,
        "max_upload_size_mb": config.max_upload_size_mb,
        "enable_theme_toggle": config.enable_theme_toggle,
        "default_theme": config.default_theme,
        "primary_color": config.primary_color,
        "secondary_color": config.secondary_color,
        "logo_url": config.logo_url,
        "favicon_url": config.favicon_url
    }

@router.get("/environment")
async def get_environment_config(current_user: User = Depends(get_current_active_user)):
    """Get environment-specific configuration (user must be authenticated)"""
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "enable_registration": settings.ENABLE_REGISTRATION,
        "enable_password_reset": settings.ENABLE_PASSWORD_RESET,
        "enable_email_notifications": settings.ENABLE_EMAIL_NOTIFICATIONS,
        "session_timeout_minutes": settings.SESSION_TIMEOUT_MINUTES,
        "page_size": settings.PAGE_SIZE
    }

