from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.app_config import app_config
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import RequestIDMiddleware, LoggingMiddleware
from app.core.database import get_engine
from app.api.v1 import api_router
from app.services.scheduler import start_scheduler, shutdown_scheduler
from app.services.job_registry import register_all_jobs
import logging
import sys
import os
import time

from contextlib import asynccontextmanager


# Setup logging first
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup logic
    try:
        db_url = settings.get_database_url()
        # Mask password in log
        if "@" in db_url:
            parts = db_url.split("@")
            if "://" in parts[0]:
                protocol_user = parts[0].split("://")
                if len(protocol_user) == 2:
                    protocol = protocol_user[0]
                    user_pass = protocol_user[1].split(":")
                    if len(user_pass) >= 2:
                        user = user_pass[0]
                        masked_url = f"{protocol}://{user}:***@{parts[1]}"
                    else:
                        masked_url = db_url
                else:
                    masked_url = db_url
            else:
                masked_url = db_url
        else:
            masked_url = db_url
        
        logger.info(f"Database connection: {masked_url}")
        logger.info(f"Database host: {settings.ORACLE_HOST}:{settings.ORACLE_PORT}")
        logger.info(f"Database service: {settings.ORACLE_SERVICE}")
        # Extract user from DATABASE_URL if available, otherwise use ORACLE_USER
        if settings.DATABASE_URL and "@" in settings.DATABASE_URL:
            try:
                url_parts = settings.DATABASE_URL.split("@")[0].split("://")[1]
                db_user = url_parts.split(":")[0]
                logger.info(f"Database user: {db_user} (from DATABASE_URL)")
            except:
                logger.info(f"Database user: {settings.ORACLE_USER}")
        else:
            logger.info(f"Database user: {settings.ORACLE_USER}")
        
        # Test connection strictly (no retries)
        try:
            engine = get_engine(fail_fast=True)
            if engine:
                from sqlalchemy import text
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1 FROM DUAL"))
                    logger.info("Database connection test: SUCCESS")
            else:
                logger.critical("Database engine currently not available. Service shutting down.")
                os._exit(1)
            
        except Exception as e:
            logger.critical(f"Database connectivity error: {e}. Service shutting down.")
            os._exit(1)

        # Start background job scheduler
        start_scheduler()
        register_all_jobs()
        logger.info("Background job scheduler initialized and jobs registered")
    except Exception as e:
        logger.error(f"Unexpected startup error: {e}", exc_info=True)
        sys.exit(1)
    
    yield
    
    # Shutdown logic
    shutdown_scheduler()
    logger.info("Application shutdown complete")

app = FastAPI(
    title=app_config.app_title,
    description=app_config.app_description,
    version=app_config.app_version,
    lifespan=lifespan
)

# Request ID middleware (should be first to set context)
app.add_middleware(RequestIDMiddleware)

# Logging middleware (after request ID is set)
app.add_middleware(LoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Unified Portal API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint with database status"""
    db_status = "unknown"
    db_info = {}
    try:
        from sqlalchemy import text
        engine = get_engine()
        if engine:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 FROM DUAL"))
                db_status = "connected"
                db_info = {
                    "host": settings.ORACLE_HOST,
                    "port": settings.ORACLE_PORT,
                    "service": settings.ORACLE_SERVICE,
                    "user": settings.ORACLE_USER
                }
        else:
            db_status = "not_available"
    except Exception as e:
        db_status = "error"
        db_info = {"error": str(e)}
    
    return {
        "status": "healthy",
        "database": {
            "status": db_status,
            **db_info
        }
    }

