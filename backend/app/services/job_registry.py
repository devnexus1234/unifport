"""
Job Registry

Registers and configures all background jobs.
Schedules are read from environment variables for each environment.
"""
from app.services.scheduler import add_job, get_scheduler
from app.services.workers import (
    TokenCleanerWorker,
    DailyChecklistWorker,
    StatusCheckerWorker,
    AuditLogEmailWorker
)
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.core.logging_config import get_logger
from app.core.config import settings
from app.services.morning_checklist.diff_calculator import update_morning_checklist_diffs
from app.services.morning_checklist.diff_calculator import update_morning_checklist_diffs
from app.services.morning_checklist.emailer import send_morning_checklist_report_email
from app.services.ipam_sync import sync_ipam_segments
import re

logger = get_logger(__name__)


def parse_schedule(schedule_str: str):
    """
    Parse schedule string from environment variable
    
    Supports:
    - Cron format: "0 2 * * *" (full cron) or "2 0" (hour minute) or "mon-fri 9 0" (day_of_week hour minute)
    - Interval format: "6 hours", "30 minutes", "60 seconds"
    
    Returns appropriate APScheduler trigger
    """
    schedule_str = schedule_str.strip()
    
    # Check if it's an interval format (e.g., "6 hours", "30 minutes")
    interval_match = re.match(r'^(\d+)\s+(hours?|minutes?|seconds?)$', schedule_str, re.IGNORECASE)
    if interval_match:
        value = int(interval_match.group(1))
        unit = interval_match.group(2).lower()
        
        if unit.startswith('hour'):
            return IntervalTrigger(hours=value)
        elif unit.startswith('minute'):
            return IntervalTrigger(minutes=value)
        elif unit.startswith('second'):
            return IntervalTrigger(seconds=value)
    
    # Check if it's a cron expression
    cron_parts = schedule_str.split()
    if len(cron_parts) == 5:
        # Full cron expression: "minute hour day month day_of_week"
        try:
            return CronTrigger.from_crontab(schedule_str)
        except:
            # Fallback: parse manually
            minute, hour = int(cron_parts[0]), int(cron_parts[1])
            day = cron_parts[2] if cron_parts[2] != '*' else None
            month = cron_parts[3] if cron_parts[3] != '*' else None
            day_of_week = cron_parts[4] if cron_parts[4] != '*' else None
            
            trigger_kwargs = {}
            if minute != '*':
                trigger_kwargs['minute'] = minute
            if hour != '*':
                trigger_kwargs['hour'] = hour
            if day and day != '*':
                trigger_kwargs['day'] = day
            if month and month != '*':
                trigger_kwargs['month'] = month
            if day_of_week and day_of_week != '*':
                trigger_kwargs['day_of_week'] = day_of_week
            
            return CronTrigger(**trigger_kwargs)
    elif len(cron_parts) == 2:
        # Simple format: "hour minute"
        try:
            hour, minute = int(cron_parts[0]), int(cron_parts[1])
            return CronTrigger(hour=hour, minute=minute)
        except ValueError:
            logger.warning(f"Invalid schedule format: {schedule_str}, using default")
            return CronTrigger(hour=0, minute=0)
    elif len(cron_parts) == 3:
        # Format: "day_of_week hour minute"
        try:
            day_of_week = cron_parts[0]
            hour, minute = int(cron_parts[1]), int(cron_parts[2])
            return CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
        except ValueError:
            logger.warning(f"Invalid schedule format: {schedule_str}, using default")
            return CronTrigger(hour=0, minute=0)
    else:
        # Default: try to parse as cron expression
        logger.warning(f"Unknown schedule format: {schedule_str}, using default (daily at midnight)")
        return CronTrigger(hour=0, minute=0)


def register_all_jobs():
    """Register all background jobs with the scheduler"""
    
    # Token Cleaner - Schedule from environment
    token_cleaner_schedule = parse_schedule(settings.JOB_TOKEN_CLEANER_SCHEDULE)
    add_job(
        func=TokenCleanerWorker().run,
        trigger=token_cleaner_schedule,
        id="token_cleaner_daily",
        name="Daily Token Cleaner",
        replace_existing=True
    )
    logger.info(f"Registered Token Cleaner with schedule: {settings.JOB_TOKEN_CLEANER_SCHEDULE}")
    
    # Daily Checklist Emails - Schedule from environment
    checklist_schedule = parse_schedule(settings.JOB_DAILY_CHECKLIST_SCHEDULE)
    add_job(
        func=DailyChecklistWorker().run,
        trigger=checklist_schedule,
        id="daily_checklist_emails",
        name="Daily Checklist Emails",
        replace_existing=True
    )
    logger.info(f"Registered Daily Checklist with schedule: {settings.JOB_DAILY_CHECKLIST_SCHEDULE}")
    
    # Status Checker - Schedule from environment
    status_checker_schedule = parse_schedule(settings.JOB_STATUS_CHECKER_SCHEDULE)
    add_job(
        func=StatusCheckerWorker().run,
        trigger=status_checker_schedule,
        id="status_checker_interval",
        name="System Status Checker",
        replace_existing=True
    )
    logger.info(f"Registered Status Checker with schedule: {settings.JOB_STATUS_CHECKER_SCHEDULE}")

    # Morning Checklist Diff Calculator - Schedule from environment
    diff_calculator_schedule = parse_schedule(settings.JOB_MORNING_CHECKLIST_DIFF_CAL_SCHEDULE)
    add_job(
        func=update_morning_checklist_diffs,
        trigger=diff_calculator_schedule,
        id="mc_diff_calculator",
        name="Morning Checklist Diff Calculator",
        replace_existing=True
    )
    logger.info(f"Registered Morning Checklist Diff Calculator with schedule: {settings.JOB_MORNING_CHECKLIST_DIFF_CAL_SCHEDULE}")
    
    # Daily Morning Checklist Email - Schedule from environment
    email_schedule = parse_schedule(settings.JOB_MORNING_CHECKLIST_EMAIL_SCHEDULE)
    add_job(
        func=send_morning_checklist_report_email,
        trigger=email_schedule,
        id="mc_email_report",
        name="Morning Checklist Email Report",
        replace_existing=True
    )
    logger.info(f"Registered Morning Checklist Email Report with schedule: {settings.JOB_MORNING_CHECKLIST_EMAIL_SCHEDULE}")
    
    # 6. Audit Log Email Report
    audit_scheduler = parse_schedule(settings.JOB_AUDIT_LOG_EMAIL_SCHEDULE)
    if audit_scheduler:
        add_job(
            func=AuditLogEmailWorker().run,
            trigger=audit_scheduler,
            id="audit_log_email_report",
            name="Audit Log Email Report",
            replace_existing=True
        )
        logger.info(f"Registered Audit Log Email Report with schedule: {settings.JOB_AUDIT_LOG_EMAIL_SCHEDULE}")
        
    # 7. IPAM Segment Sync - Schedule from environment
    ipam_sync_schedule = parse_schedule(settings.JOB_IPAM_SYNC_SCHEDULE)
    add_job(
        func=sync_ipam_segments,
        trigger=ipam_sync_schedule,
        id="ipam_segment_sync",
        name="IPAM Segment Sync",
        replace_existing=True
    )
    logger.info(f"Registered IPAM Segment Sync with schedule: {settings.JOB_IPAM_SYNC_SCHEDULE}")

    logger.info("All background jobs registered")


def register_job(
    worker_class,
    trigger,
    job_id: str,
    job_name: str,
    **kwargs
):
    """
    Register a new job
    
    Args:
        worker_class: Worker class (must inherit from BaseWorker)
        trigger: APScheduler trigger (CronTrigger, IntervalTrigger, etc.)
        job_id: Unique job identifier
        job_name: Human-readable job name
        **kwargs: Additional arguments for the job
    """
    worker = worker_class()
    add_job(
        func=worker.run,
        trigger=trigger,
        id=job_id,
        name=job_name,
        replace_existing=True,
        **kwargs
    )
    logger.info(f"Registered job: {job_name} (ID: {job_id})")
