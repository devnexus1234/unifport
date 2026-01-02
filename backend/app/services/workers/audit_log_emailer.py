import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.workers.base import BaseWorker
from app.services.email_service import get_email_service
from app.core.config import settings
from app.models.ipam import IpamAuditLog
from app.models.user import User
from app.core.time_utils import get_ist_time
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font

logger = logging.getLogger(__name__)

class AuditLogEmailWorker(BaseWorker):
    """
    Worker to send daily audit log reports via email.
    """
    name = "audit_log_email_worker"
    
    def __init__(self):
        super().__init__()
    
    async def execute(self):
        """
        Execute the worker task:
        1. Fetch audit logs from the last 24 hours.
        2. Format them into an HTML table.
        3. Generate Excel report.
        4. Send email to configured recipients with attachment.
        """
        logger.info("Starting audit log email worker")
        
        # Check if recipients are configured
        recipients_str = settings.JOB_AUDIT_LOG_EMAIL_RECIPIENTS
        if not recipients_str:
            logger.info("No recipients configured for audit log email. Skipping.")
            return
            
        recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
        if not recipients:
             logger.info("No valid recipients found. Skipping.")
             return

        db = SessionLocal()
        try:
            # Calculate time range (last 24 hours)
            current_time = get_ist_time()
            start_time = current_time - timedelta(days=1)
            
            logger.info(f"Fetching audit logs from {start_time} to {current_time}")
            
            # Query IpamAuditLog
            logs = db.query(IpamAuditLog).filter(
                IpamAuditLog.created_at >= start_time
            ).order_by(IpamAuditLog.created_at.desc()).all()
            
            excel_file = None
            if logs:
                excel_file = self._generate_excel(logs)

            logger.info(f"Found {len(logs)} audit logs. Sending email.")
            self._send_email(recipients, logs, start_time, current_time, excel_file)
            
        except Exception as e:
            logger.error(f"Error in audit log email worker: {e}", exc_info=True)
        finally:
            db.close()
            
    def _send_email(self, recipients: List[str], logs: List[IpamAuditLog], start_time: datetime, end_time: datetime, excel_file: bytes = None):
        """Send the formatted email with optional attachment"""
        date_str = start_time.strftime("%Y-%m-%d")
        subject = f"[{settings.APP_TITLE}] Daily Audit Log Report - {date_str}"
        
        html_content = self._generate_html(logs, start_time, end_time)
        
        attachments = []
        if excel_file:
            attachments.append({
                "filename": f"audit_logs_{date_str}.xlsx",
                "content": excel_file
            })
        
        email_service = get_email_service()
        email_service.send_html_email_with_defaults(
            subject=subject,
            html_body=html_content,
            recipients=recipients,
            attachments=attachments,
            use_env_defaults=True 
        )

    def _extract_details(self, changes: str):
        """Extract RITM, Source, and Comment from changes string"""
        details = {"ritm": "-", "source": "-", "comment": "-"}
        if not changes:
            return details
            
        import re
        def get_val(key):
            # Regex to match "Key: Old -> New" or "Key: Value" and capture the final value
            # Matches Key: followed by optional (stuff -> ), then captures content until comma or end of string
            pattern = f"{key}:\\s*(?:.*?->\\s*)?(.*?)(?:, |$)"
            match = re.search(pattern, changes)
            if match:
                val = match.group(1).strip()
                return val if val != 'None' else '-'
            return "-"
            
        details["ritm"] = get_val("RITM")
        details["source"] = get_val("Source")
        details["comment"] = get_val("Comment")
        
        return details

    def _generate_excel(self, logs: List[IpamAuditLog]) -> bytes:
        """Generate Excel file from logs"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Audit Logs"
        
        # Headers
        headers = ["Timestamp", "User", "Action", "Entity", "RITM", "Source", "Comment", "Full Changes"]
        ws.append(headers)
        
        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            
        # Data
        for log in logs:
            ts = log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "N/A"
            user_name = log.user.username if log.user else f"User ID: {log.user_id}"
            
            entity = "Unknown"
            if log.ip_address:
                entity = f"IP: {log.ip_address}"
            elif log.segment:
                entity = f"Segment: {log.segment.segment}"
            elif log.segment_id:
                    entity = f"Segment ID: {log.segment_id}"
            
            changes = log.changes or "-"
            details = self._extract_details(changes)
            
            ws.append([ts, user_name, log.action, entity, details["ritm"], details["source"], details["comment"], changes])
            
        # Auto-adjust column widths (approximate)
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 50) # Cap width
            
        output = BytesIO()
        wb.save(output)
        return output.getvalue()
        
    def _generate_html(self, logs: List[IpamAuditLog], start_time: datetime, end_time: datetime) -> str:
        """Generate HTML email body"""
        
        style = """
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            h2 { color: #2c3e50; }
            .meta { color: #666; font-size: 0.9em; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.9em; }
            th, td { padding: 8px; border: 1px solid #ddd; text-align: left; vertical-align: top; }
            th { background-color: #f2f2f2; font-weight: bold; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .no-logs { padding: 20px; background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; color: #666; text-align: center; }
            .changes-col { max-width: 300px; word-wrap: break-word; }
        </style>
        """
        
        header = f"""
        <h2>Daily Audit Log Report</h2>
        <div class="meta">
            <strong>Period:</strong> {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} (IST)<br>
            <strong>Total Records:</strong> {len(logs)}
        </div>
        """
        
        if not logs:
            content = """
            <div class="no-logs">
                No audit logs recorded during this period.
            </div>
            """
        else:
            rows = []
            for log in logs:
                # Format timestamp
                ts = log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "N/A"
                
                # Get user name
                user_name = log.user.username if log.user else f"User ID: {log.user_id}"
                
                # Entity info (Segment or IP)
                entity = "Unknown"
                if log.ip_address:
                    entity = f"IP: {log.ip_address}"
                elif log.segment:
                    entity = f"Segment: {log.segment.segment}"
                elif log.segment_id:
                     entity = f"Segment ID: {log.segment_id}"
                
                changes = log.changes or "-"
                details = self._extract_details(changes)
                
                row = f"""
                <tr>
                    <td>{ts}</td>
                    <td>{user_name}</td>
                    <td>{log.action}</td>
                    <td>{entity}</td>
                    <td>{details['ritm']}</td>
                    <td>{details['source']}</td>
                    <td>{details['comment']}</td>
                    <td class="changes-col">{changes}</td>
                </tr>
                """
                rows.append(row)
            
            check_table = f"""
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>User</th>
                        <th>Action</th>
                        <th>Entity</th>
                        <th>RITM</th>
                        <th>Source</th>
                        <th>Comment</th>
                        <th>Full Changes</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
            """
            content = check_table

        return f"""
        <!DOCTYPE html>
        <html>
        <head>{style}</head>
        <body>
            {header}
            {content}
            <p style="margin-top: 30px; font-size: 0.8em; color: #999;">
                This is an automated report from {settings.APP_TITLE}.
            </p>
        </body>
        </html>
        """
