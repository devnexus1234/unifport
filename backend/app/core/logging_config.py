"""
Structured JSON logging configuration for Unified Portal.

Provides JSON-based logging with standard keys for production and development environments.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path
import traceback
from contextvars import ContextVar

from app.core.config import settings

# Context variable for request ID (set by middleware)
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_var: ContextVar[Optional[str]] = ContextVar('user', default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log structure with standard keys
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "environment": settings.ENVIRONMENT,
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
        }
        
        # Add request context if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        user = user_var.get()
        if user:
            log_data["user"] = user
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info else None
            }
        
        # Add all custom extra fields directly to log_data (flattened)
        # This includes all fields from middleware like api_endpoint, user_id, query_params, etc.
        excluded_keys = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'message', 'pathname', 'process', 'processName', 'relativeCreated',
            'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
            'taskName'
        }
        
        # Add any custom extra fields passed to logger directly to log_data
        for key, value in record.__dict__.items():
            if key not in excluded_keys:
                log_data[key] = value
        
        # Add standard metadata fields if include_extra is True
        if self.include_extra:
            log_data["process_id"] = record.process
            log_data["thread_id"] = record.thread
            log_data["thread_name"] = record.threadName
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class StandardFormatter(logging.Formatter):
    """Standard text formatter for development (more readable)."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as readable text."""
        # Build base message
        parts = [
            f"[{datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')}]",
            f"{record.levelname:8s}",
            f"{record.name}:{record.funcName}:{record.lineno}",
        ]
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            parts.append(f"[req:{request_id}]")
        
        # Add user if available
        user = user_var.get()
        if user:
            parts.append(f"[user:{user}]")
        
        parts.append(f"- {record.getMessage()}")
        
        # Add exception if present
        if record.exc_info:
            parts.append(f"\n{self.formatException(record.exc_info)}")
        
        return " ".join(parts)


def setup_logging() -> None:
    """Configure logging for the application."""
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Always use JSON formatter for structured logging
    use_json = True
    formatter = JSONFormatter(include_extra=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if configured
    if settings.LOG_FILE:
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Application logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    
    logging.info(
        "Logging configured",
        extra={
            "environment": settings.ENVIRONMENT,
            "log_level": settings.LOG_LEVEL,
            "log_format": "JSON",
            "log_file": settings.LOG_FILE or "console only"
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(f"app.{name}")


# Context managers for request/user tracking
def set_request_id(request_id: str) -> None:
    """Set request ID in context."""
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Get current request ID from context."""
    return request_id_var.get()


def set_user(user: str) -> None:
    """Set user in context."""
    user_var.set(user)


def get_user() -> Optional[str]:
    """Get current user from context."""
    return user_var.get()


def clear_context() -> None:
    """Clear request context."""
    request_id_var.set(None)
    user_var.set(None)
