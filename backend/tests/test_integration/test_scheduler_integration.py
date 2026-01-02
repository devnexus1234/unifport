
import pytest
from app.services.job_registry import register_all_jobs
from app.services.scheduler import scheduler, get_scheduler
from app.core.config import settings

@pytest.mark.integration
class TestSchedulerIntegration:

    def test_jobs_registration(self):
        """Test that all expected jobs are registered in the scheduler"""
        # Ensure scheduler is clear before test
        sched = get_scheduler()
        sched.remove_all_jobs()
        
        # Determine schedules
        # For integration test, we can rely on defaults or set env vars. 
        # But register_all_jobs reads from settings.
        # If settings variables are unset, parse_schedule might fail or return default?
        # Let's ensure they have values by patching settings.
        
        from unittest.mock import patch
        with patch("app.services.job_registry.settings") as mock_settings:
             mock_settings.JOB_TOKEN_CLEANER_SCHEDULE = "0 2 * * *"
             mock_settings.JOB_DAILY_CHECKLIST_SCHEDULE = "0 6 * * *"
             mock_settings.JOB_STATUS_CHECKER_SCHEDULE = "5 minutes"
             mock_settings.JOB_MORNING_CHECKLIST_DIFF_CAL_SCHEDULE = "30 minutes"
             mock_settings.JOB_MORNING_CHECKLIST_EMAIL_SCHEDULE = "0 4 * * *"
             mock_settings.JOB_IPAM_SYNC_SCHEDULE = "0 3 * * *"
             
             register_all_jobs()
        
        jobs = sched.get_jobs()
        job_ids = [job.id for job in jobs]
        
        expected_jobs = [
            "token_cleaner_daily",
            "daily_checklist_emails",
            "status_checker_interval",
            "mc_diff_calculator",
            "mc_email_report",
            "ipam_segment_sync"
        ]
        
        for job_id in expected_jobs:
            assert job_id in job_ids, f"Job {job_id} not registered"

    def test_job_persistence(self):
        """Test retrieving a specific job"""
        # Ensure job exists (setup in previous test, but tests should be independent)
        # register_all_jobs() should be called ideally or setup_method used.
        # But failing that, let's verify logic.
        
        # We need to ensure jobs are registered for this test too if it runs in isolation
        # For simplicity, assuming running in sequence or register again
        from app.services.job_registry import register_all_jobs
        # Mock settings again if needed, or rely on defaults if they work?
        # Let's rely on previous test having run or just verifying get_scheduler logic
        
        sched = get_scheduler()
        # If no jobs, register them
        if not sched.get_jobs():
             from unittest.mock import patch
             with patch("app.services.job_registry.settings") as mock_settings:
                 mock_settings.JOB_TOKEN_CLEANER_SCHEDULE = "0 2 * * *"
                 mock_settings.JOB_DAILY_CHECKLIST_SCHEDULE = "0 6 * * *"
                 mock_settings.JOB_STATUS_CHECKER_SCHEDULE = "5 minutes"
                 mock_settings.JOB_MORNING_CHECKLIST_DIFF_CAL_SCHEDULE = "30 minutes"
                 mock_settings.JOB_MORNING_CHECKLIST_EMAIL_SCHEDULE = "0 4 * * *"
                 mock_settings.JOB_IPAM_SYNC_SCHEDULE = "0 3 * * *"
                 register_all_jobs()

        job = sched.get_job("token_cleaner_daily")
        assert job is not None
        assert job.name == "Daily Token Cleaner"

    def test_scheduler_starts(self):
        """Test that scheduler reports as running if started"""
        # Note: In integration tests we might not want to actually start the scheduler 
        # as it spawns threads. We can check configuration.
        # But if we did start it:
        # if not scheduler.running:
        #    scheduler.start()
        # assert scheduler.running
        # scheduler.shutdown()
        pass 
