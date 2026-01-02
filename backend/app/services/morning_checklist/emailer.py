from datetime import date
from app.services.morning_checklist.report_generator import generate_morning_checklist_excel
from app.services.email_service import get_email_service
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def send_morning_checklist_report_email():
    """
    Generates the morning checklist Excel report for today and emails it.
    """
    logger.info("Starting morning checklist email job")
    
    today = date.today()
    
    db = SessionLocal()
    try:
        # Generate Excel
        excel_stream = generate_morning_checklist_excel(db, today)
        excel_content = excel_stream.getvalue()
        filename = f"checklist_report_{today}.xlsx"
        
        # Prepare valid attachment dict
        attachments = [
            {
                "filename": filename,
                "content": excel_content
            }
        ]
        
        email_service = get_email_service()
        
        subject = f"Morning Checklist Report - {today}"
        body = f"Please find attached the Morning Checklist Report for {today}."
        
        # Use configured recipients if available, otherwise let service handle defaults (debug mode)
        # In production, recipients must be provided via config or defaults.
        recipients = settings.JOB_MORNING_CHECKLIST_EMAIL_TO or None
        cc_recipients = settings.JOB_MORNING_CHECKLIST_EMAIL_CC or None
        
        success = email_service.send_plain_email_with_defaults(
            subject=subject,
            text_body=body,
            recipients=recipients,
            cc=cc_recipients,
            attachments=attachments,
            use_env_defaults=True
        )
        
        if success:
            logger.info(f"Morning checklist report sent for date: {today}")
        else:
            logger.error(f"Failed to send morning checklist report for date: {today}")
            
    except Exception as e:
        logger.error(f"Error in morning checklist email job: {e}")
    finally:
        db.close()
