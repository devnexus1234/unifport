"""
FastAPI middleware for request tracking and logging.
"""
import time
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import StreamingResponse

from app.core.logging_config import (
    get_logger,
    set_request_id,
    set_user,
    clear_context,
    get_request_id
)
from app.core.security import verify_token
from app.core.time_utils import get_ist_time

logger = get_logger("middleware")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Set in context for logging
        set_request_id(request_id)
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


def extract_user_from_token(request: Request) -> Optional[Dict[str, Any]]:
    """Extract user information from JWT token in Authorization header."""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = verify_token(token, token_type="access")
        
        if payload:
            return {
                "user_id": payload.get("user_id"),
                "username": payload.get("sub"),
                "email": payload.get("email")
            }
    except Exception:
        # Silently fail if token extraction fails
        pass
    return None


def parse_request_body(body_bytes: bytes, content_type: str) -> Optional[Dict[str, Any]]:
    """Parse request body bytes into a dictionary for logging."""
    if not body_bytes:
        return None
    
    try:
        # Only parse JSON bodies
        if "application/json" in content_type:
            try:
                body_dict = json.loads(body_bytes)
                # Mask sensitive fields
                sensitive_fields = ["password", "old_password", "new_password", "access_token", "refresh_token"]
                if isinstance(body_dict, dict):
                    masked_body = body_dict.copy()
                    for field in sensitive_fields:
                        if field in masked_body:
                            masked_body[field] = "***REDACTED***"
                    return masked_body
                return body_dict
            except json.JSONDecodeError:
                # If not valid JSON, return as string (truncated)
                body_str = body_bytes.decode("utf-8", errors="ignore")
                return {"raw": body_str[:500]}  # Limit to 500 chars
        elif "application/x-www-form-urlencoded" in content_type:
            # For form data, return type indicator
            return {"type": "form_data", "size": len(body_bytes)}
        elif "multipart/form-data" in content_type:
            # For multipart, return type indicator
            return {"type": "multipart_form_data", "size": len(body_bytes)}
    except Exception as e:
        logger.debug(f"Error parsing request body: {e}")
    
    return None


def get_query_params(request: Request) -> Optional[Dict[str, Any]]:
    """Extract query parameters from request."""
    if not request.url.query:
        return None
    
    try:
        query_params = {}
        for key, value in request.query_params.multi_items():
            if key not in query_params:
                query_params[key] = value
            else:
                # Handle multiple values for same key
                if isinstance(query_params[key], list):
                    query_params[key].append(value)
                else:
                    query_params[key] = [query_params[key], value]
        return query_params
    except Exception:
        return None


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with comprehensive details."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = get_request_id()
        timestamp = get_ist_time().isoformat()
        
        # Extract user information from JWT token
        user_info = extract_user_from_token(request)
        user_id = None
        username = None
        
        if user_info:
            user_id = user_info.get("user_id")
            username = user_info.get("username")
            if user_id:
                set_user(str(user_id))
        
        # Extract request details
        method = request.method
        path = str(request.url.path)
        query_params = get_query_params(request)
        
        # Read request body (this consumes it, so we need to cache it)
        request_body = None
        body_bytes = None
        
        if method in ["POST", "PUT", "PATCH"]:
            try:
                # Limit body size for logging (10MB default)
                max_body_size = 10 * 1024 * 1024  # 10MB
                content_length = request.headers.get("content-length")
                
                # Skip reading body if too large
                if content_length and int(content_length) > max_body_size:
                    request_body = {"size": int(content_length), "truncated": True}
                else:
                    # Read and cache the body
                    body_bytes = await request.body()
                    if body_bytes:
                        # Parse body for logging
                        content_type = request.headers.get("content-type", "")
                        request_body = parse_request_body(body_bytes, content_type)
                        
                        # Store body in a closure-safe way for the receive function
                        # Starlette caches the body after first read, but we need to provide it
                        # back to FastAPI since we read it first
                        cached_body = [body_bytes]  # Use list to allow modification in closure
                        
                        # Recreate request receive function to provide cached body
                        # This is needed because reading the body consumes the stream
                        original_receive = getattr(request, '_receive', None)
                        
                        async def receive():
                            # Return cached body on first call
                            if cached_body:
                                body = cached_body[0]
                                cached_body.clear()  # Clear after first use
                                return {"type": "http.request", "body": body}
                            # If body already consumed, return empty
                            return {"type": "http.request", "body": b""}
                        
                        request._receive = receive
            except Exception as e:
                logger.debug(f"Error reading request body: {e}")
        
        # Extract other standard parameters
        client_host = request.client.host if request.client else None
        client_port = request.client.port if request.client else None
        user_agent = request.headers.get("user-agent")
        referer = request.headers.get("referer")
        content_type = request.headers.get("content-type")
        accept = request.headers.get("accept")
        
        # Build comprehensive log data
        log_data: Dict[str, Any] = {
            "timestamp": timestamp,
            "request_id": request_id,
            "api_endpoint": f"{method} {path}",
            "method": method,
            "path": path,
            "status_code": None,  # Will be set after response
            "user_id": user_id,
            "username": username,
            "client_ip": client_host,
            "client_port": client_port,
            "user_agent": user_agent,
            "referer": referer,
            "content_type": content_type,
            "accept": accept,
        }
        
        # Add query parameters if present
        if query_params:
            log_data["query_params"] = query_params
        
        # Add request body if present
        if request_body:
            log_data["request_body"] = request_body
        
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Get response status code
            status_code = response.status_code
            log_data["status_code"] = status_code
            log_data["duration_ms"] = round(duration_ms, 2)
            log_data["duration_seconds"] = round(duration_ms / 1000, 3)
            
            # Add response size if available
            if hasattr(response, "body"):
                try:
                    if isinstance(response, StreamingResponse):
                        log_data["response_size"] = "streaming"
                    else:
                        # Try to get content length
                        content_length = response.headers.get("content-length")
                        if content_length:
                            log_data["response_size"] = int(content_length)
                except Exception:
                    pass
            
            # Log the complete API call
            logger.info(
                f"API Call: {method} {path} - Status: {status_code}",
                extra=log_data
            )
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Update log data with error information
            log_data["status_code"] = 500
            log_data["duration_ms"] = round(duration_ms, 2)
            log_data["duration_seconds"] = round(duration_ms / 1000, 3)
            log_data["error_type"] = type(e).__name__
            log_data["error_message"] = str(e)
            
            # Log the failed API call
            logger.error(
                f"API Call Failed: {method} {path} - Error: {type(e).__name__}",
                extra=log_data,
                exc_info=True
            )
            
            raise
        
        finally:
            # Clear context after request
            clear_context()
