"""
Status Checker Worker

Performs daily status checks on system components and sends email report.
"""
from app.services.workers.base import BaseWorker
from app.core.database import get_engine
from app.core.config import settings
from app.services.email_service import get_email_service
from sqlalchemy import text
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from app.core.time_utils import get_ist_time


class StatusCheckerWorker(BaseWorker):
    """Worker to perform daily status checks and send email report"""
    
    name = "status_checker"
    description = "Performs daily status checks on system components and sends email report"
    
    async def execute(self):
        """Perform status checks and send email report"""
        status_report = {
            "database": False,
            "timestamp": None,
            "checks": []
        }
        
        try:
            # Check database connection
            engine = get_engine()
            if engine:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1 FROM DUAL"))
                    status_report["database"] = True
                    status_report["checks"].append({
                        "component": "database",
                        "status": "healthy",
                        "message": "Database connection successful"
                    })
            else:
                status_report["checks"].append({
                    "component": "database",
                    "status": "unavailable",
                    "message": "Database engine not available"
                })
            
            # Add more checks as needed:
            # - External API health
            # - File system checks
            # - Service availability
            
            status_report["timestamp"] = get_ist_time().isoformat()
            
            self.logger.info(f"Status check completed: {status_report}")
            
            # Send email report
            await self._send_status_email(status_report)
            
            # In production, you might want to:
            # - Store status in database
            # - Send alerts if issues detected
            # - Update monitoring dashboards
            
        except Exception as e:
            self.logger.error(f"Error in status checker: {e}", exc_info=True)
            status_report["checks"].append({
                "component": "status_checker",
                "status": "error",
                "message": str(e)
            })
            # Try to send error email
            try:
                await self._send_status_email(status_report, is_error=True)
            except:
                pass
            raise
    
    async def _send_status_email(
        self, 
        status_report: Dict[str, Any], 
        is_error: bool = False,
        recipients: Optional[Union[str, List[str]]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None
    ):
        """
        Send status check email report
        
        Args:
            status_report: Status report dictionary
            is_error: Whether this is an error report
            recipients: Custom recipients (optional). In debug mode, uses env defaults if not provided.
                       In production, must be provided.
            cc: Custom CC recipients (optional)
            bcc: Custom BCC recipients (optional)
        """
        email_service = get_email_service()
        
        # Determine subject
        if is_error:
            subject = f"[ALERT] {settings.APP_NAME} - Status Check Failed"
        else:
            subject = f"{settings.APP_NAME} - Daily Status Check Report"
        
        # Build HTML email body
        html_body = self._build_status_email_html(status_report, is_error)
        
        # Send email with defaults (uses env in debug mode, requires explicit recipients in production)
        # In debug mode: uses EMAIL_ADMIN_RECIPIENTS from env if recipients not provided
        # In production: recipients must be explicitly provided
        use_env_defaults = settings.DEBUG_MODE
        
        success = email_service.send_html_email_with_defaults(
            subject=subject,
            html_body=html_body,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            use_env_defaults=use_env_defaults
        )
        
        if success:
            final_recipients = recipients if recipients else settings.EMAIL_ADMIN_RECIPIENTS
            self.logger.info(f"Status check email sent to {final_recipients}")
        else:
            self.logger.warning("Failed to send status check email")
    
    def _build_status_email_html(self, status_report: Dict[str, Any], is_error: bool) -> str:
        """Build HTML email body for status report"""
        timestamp = status_report.get("timestamp", get_ist_time().isoformat())
        checks = status_report.get("checks", [])
        
        # Determine overall status
        all_healthy = all(check.get("status") == "healthy" for check in checks)
        status_color = "#d32f2f" if (is_error or not all_healthy) else "#388e3c"
        status_text = "ERROR" if (is_error or not all_healthy) else "HEALTHY"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {status_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .status-badge {{ display: inline-block; padding: 5px 15px; background-color: {status_color}; color: white; border-radius: 3px; font-weight: bold; }}
                .check-item {{ background-color: white; padding: 10px; margin: 10px 0; border-left: 4px solid #ddd; }}
                .check-item.healthy {{ border-left-color: #4caf50; }}
                .check-item.unavailable {{ border-left-color: #ff9800; }}
                .check-item.error {{ border-left-color: #f44336; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{settings.APP_NAME}</h1>
                    <p>Status Check Report</p>
                </div>
                <div class="content">
                    <h2>System Status: <span class="status-badge">{status_text}</span></h2>
                    <p><strong>Timestamp:</strong> {timestamp}</p>
                    <p><strong>Environment:</strong> {settings.ENVIRONMENT}</p>
                    
                    <h3>Component Checks:</h3>
        """
        
        for check in checks:
            component = check.get("component", "unknown")
            status = check.get("status", "unknown")
            message = check.get("message", "")
            status_class = status.lower()
            
            html += f"""
                    <div class="check-item {status_class}">
                        <strong>{component.upper()}</strong>: {status.upper()}<br>
                        <em>{message}</em>
                    </div>
            """
        
        html += f"""
                </div>
                <div class="footer">
                    <p>This is an automated email from {settings.APP_NAME}</p>
                    <p>Environment: {settings.ENVIRONMENT}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
