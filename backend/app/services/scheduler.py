"""
Background Job Scheduler Service

This service manages all scheduled background jobs and workers using APScheduler.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from app.core.logging_config import get_logger
from typing import Optional, Callable, Any
import asyncio

logger = get_logger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance"""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


def start_scheduler():
    """Start the scheduler"""
    sched = get_scheduler()
    if not sched.running:
        sched.start()
        logger.info("Background job scheduler started")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Background job scheduler stopped")


def add_job(
    func: Callable,
    trigger: Any,
    id: Optional[str] = None,
    name: Optional[str] = None,
    replace_existing: bool = True,
    **kwargs
):
    """
    Add a job to the scheduler
    
    Args:
        func: The function to execute
        trigger: Trigger for the job (CronTrigger, IntervalTrigger, etc.)
        id: Unique identifier for the job
        name: Human-readable name for the job
        replace_existing: Whether to replace existing job with same id
        **kwargs: Additional arguments to pass to the job
    """
    sched = get_scheduler()
    sched.add_job(
        func=func,
        trigger=trigger,
        id=id,
        name=name,
        replace_existing=replace_existing,
        **kwargs
    )
    logger.info(f"Added job: {name or id} (trigger: {trigger})")


def remove_job(job_id: str):
    """Remove a job from the scheduler"""
    sched = get_scheduler()
    try:
        sched.remove_job(job_id)
        logger.info(f"Removed job: {job_id}")
    except Exception as e:
        logger.error(f"Failed to remove job {job_id}: {e}")


def get_jobs():
    """Get all scheduled jobs"""
    sched = get_scheduler()
    return sched.get_jobs()


def pause_job(job_id: str):
    """Pause a job"""
    sched = get_scheduler()
    try:
        sched.pause_job(job_id)
        logger.info(f"Paused job: {job_id}")
    except Exception as e:
        logger.error(f"Failed to pause job {job_id}: {e}")


def resume_job(job_id: str):
    """Resume a paused job"""
    sched = get_scheduler()
    try:
        sched.resume_job(job_id)
        logger.info(f"Resumed job: {job_id}")
    except Exception as e:
        logger.error(f"Failed to resume job {job_id}: {e}")
