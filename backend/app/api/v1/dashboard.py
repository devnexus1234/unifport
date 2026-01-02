"""
Dashboard API endpoints for application summary and health details
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.user import User
from app.models.catalogue import Catalogue, CatalogueCategory
from app.models.rbac import Role, UserRole
from typing import Dict, Any
from datetime import datetime, timezone

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get application summary statistics"""
    try:
        # Count total users (all users)
        total_users = db.query(func.count(User.id)).scalar() or 0
        
        # Count active users (users who have logged in recently or are active)
        active_users = db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar() or 0
        
        # Count total catalogues (only active catalogues)
        total_catalogues = db.query(func.count(Catalogue.id)).filter(
            Catalogue.is_active == True
        ).scalar() or 0
        
        # Count enabled catalogues (active and enabled)
        enabled_catalogues = db.query(func.count(Catalogue.id)).filter(
            Catalogue.is_enabled == True,
            Catalogue.is_active == True
        ).scalar() or 0
        
        # Count total categories (only active categories)
        total_categories = db.query(func.count(CatalogueCategory.id)).filter(
            CatalogueCategory.is_active == True
        ).scalar() or 0
        
        # Count active categories (same as total for active categories)
        active_categories = total_categories
        
        # Count total roles (only active roles)
        total_roles = db.query(func.count(Role.id)).filter(
            Role.is_active == True
        ).scalar() or 0
        
        # Count active roles (same as total for active roles)
        active_roles = total_roles
        
        # Count role assignments
        total_role_assignments = db.query(func.count(UserRole.id)).scalar() or 0
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "catalogues": {
                "total": total_catalogues,
                "enabled": enabled_catalogues,
                "disabled": total_catalogues - enabled_catalogues
            },
            "categories": {
                "total": total_categories,
                "active": active_categories,
                "inactive": total_categories - active_categories
            },
            "roles": {
                "total": total_roles,
                "active": active_roles,
                "inactive": total_roles - active_roles,
                "assignments": total_role_assignments
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "users": {"total": 0, "active": 0, "inactive": 0},
            "catalogues": {"total": 0, "enabled": 0, "disabled": 0},
            "categories": {"total": 0, "active": 0, "inactive": 0},
            "roles": {"total": 0, "active": 0, "inactive": 0, "assignments": 0},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/health")
async def get_dashboard_health(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed health information for the application"""
    health_status = {
        "overall": "healthy",
        "components": {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Database health
    db_health = {
        "status": "unknown",
        "response_time_ms": None,
        "error": None
    }
    
    try:
        from app.core.database import get_engine
        from app.core.config import settings
        import time
        
        start_time = time.time()
        engine = get_engine()
        
        if engine:
            with engine.connect() as conn:
                # Try Oracle-specific query first, fallback to generic query
                try:
                    result = conn.execute(text("SELECT 1 FROM DUAL"))
                except Exception:
                    # For non-Oracle databases (e.g., SQLite in tests)
                    result = conn.execute(text("SELECT 1"))
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                db_health = {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "host": getattr(settings, 'ORACLE_HOST', None),
                    "port": getattr(settings, 'ORACLE_PORT', None),
                    "service": getattr(settings, 'ORACLE_SERVICE', None)
                }
        else:
            db_health = {
                "status": "degraded",
                "response_time_ms": None,
                "error": "Database engine not available (debug mode)"
            }
    except Exception as e:
        db_health = {
            "status": "unhealthy",
            "response_time_ms": None,
            "error": str(e)
        }
        health_status["overall"] = "degraded"
    
    health_status["components"]["database"] = db_health
    
    # API health (basic check)
    api_health = {
        "status": "healthy",
        "response_time_ms": None
    }
    try:
        import time
        start_time = time.time()
        # Simple check - if we got here, API is responding
        api_health["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    except Exception as e:
        api_health = {
            "status": "degraded",
            "response_time_ms": None,
            "error": str(e)
        }
        health_status["overall"] = "degraded"
    
    health_status["components"]["api"] = api_health
    
    # System health (basic info)
    system_health = {
        "status": "unknown",
        "error": "System metrics not available"
    }
    
    try:
        import psutil
        import platform
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        system_health = {
            "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "degraded",
            "cpu": {
                "usage_percent": round(cpu_percent, 2),
                "cores": psutil.cpu_count()
            },
            "memory": {
                "usage_percent": round(memory.percent, 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2)
            },
            "platform": platform.system(),
            "platform_version": platform.version()
        }
        
        if system_health["status"] == "degraded":
            health_status["overall"] = "degraded"
            
    except ImportError:
        # psutil not available, skip system metrics
        pass
    except Exception as e:
        system_health = {
            "status": "unknown",
            "error": str(e)
        }
    
    health_status["components"]["system"] = system_health
    
    return health_status
