"""
Background Jobs API

Endpoints for managing and monitoring background jobs.
"""
from fastapi import APIRouter, HTTPException, status
from app.services.scheduler import (
    get_jobs,
    pause_job,
    resume_job,
    remove_job,
    get_scheduler
)
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["background-jobs"])


@router.get("/")
async def list_jobs() -> List[Dict[str, Any]]:
    """Get list of all scheduled jobs"""
    jobs = get_jobs()
    return [
        {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
            "pending": job.pending
        }
        for job in jobs
    ]


@router.get("/{job_id}")
async def get_job(job_id: str) -> Dict[str, Any]:
    """Get details of a specific job"""
    scheduler = get_scheduler()
    try:
        job = scheduler.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        return {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
            "pending": job.pending
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting job: {str(e)}"
        )


@router.post("/{job_id}/pause")
async def pause_job_endpoint(job_id: str) -> Dict[str, str]:
    """Pause a scheduled job"""
    try:
        pause_job(job_id)
        return {"status": "success", "message": f"Job {job_id} paused"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pausing job: {str(e)}"
        )


@router.post("/{job_id}/resume")
async def resume_job_endpoint(job_id: str) -> Dict[str, str]:
    """Resume a paused job"""
    try:
        resume_job(job_id)
        return {"status": "success", "message": f"Job {job_id} resumed"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resuming job: {str(e)}"
        )


@router.delete("/{job_id}")
async def delete_job(job_id: str) -> Dict[str, str]:
    """Remove a job from the scheduler"""
    try:
        remove_job(job_id)
        return {"status": "success", "message": f"Job {job_id} removed"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing job: {str(e)}"
        )


@router.get("/scheduler/status")
async def scheduler_status() -> Dict[str, Any]:
    """Get scheduler status"""
    scheduler = get_scheduler()
    return {
        "running": scheduler.running if scheduler else False,
        "jobs_count": len(get_jobs()) if scheduler else 0
    }
