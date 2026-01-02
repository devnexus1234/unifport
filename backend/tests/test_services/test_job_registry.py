
import pytest
from unittest.mock import patch, MagicMock
from app.services.job_registry import parse_schedule, register_all_jobs
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

@pytest.mark.unit
class TestJobRegistryUnit:
    
    def test_parse_schedule_cron_full(self):
        """Test parsing full cron expression"""
        schedule = "0 2 * * *"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, CronTrigger)
    
    def test_parse_schedule_cron_simple(self):
        """Test parsing simple hour minute format"""
        schedule = "2 0"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, CronTrigger)
        
    def test_parse_schedule_cron_day_hour_min(self):
        """Test parsing day hour minute format"""
        schedule = "mon 9 0"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, CronTrigger)
        
    def test_parse_schedule_interval_hours(self):
        """Test parsing interval in hours"""
        schedule = "6 hours"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, IntervalTrigger)
        assert trigger.interval.seconds == 6 * 3600
        
    def test_parse_schedule_interval_minutes(self):
        """Test parsing interval in minutes"""
        schedule = "30 minutes"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, IntervalTrigger)
        assert trigger.interval.seconds == 30 * 60
        
    def test_parse_schedule_interval_seconds(self):
        """Test parsing interval in seconds"""
        schedule = "60 seconds"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, IntervalTrigger)
        assert trigger.interval.seconds == 60

    def test_parse_schedule_invalid(self):
        """Test invalid schedule format fallback"""
        schedule = "invalid format"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, CronTrigger)

    @patch("app.services.job_registry.add_job")
    @patch("app.services.job_registry.settings")
    def test_register_all_jobs(self, mock_settings, mock_add_job):
        """Test registering all jobs calls add_job correctly"""
        mock_settings.JOB_TOKEN_CLEANER_SCHEDULE = "0 2 * * *"
        mock_settings.JOB_DAILY_CHECKLIST_SCHEDULE = "0 6 * * *"
        mock_settings.JOB_STATUS_CHECKER_SCHEDULE = "5 minutes"
        mock_settings.JOB_MORNING_CHECKLIST_DIFF_CAL_SCHEDULE = "30 minutes"
        mock_settings.JOB_MORNING_CHECKLIST_EMAIL_SCHEDULE = "0 4 * * *"
        mock_settings.JOB_IPAM_SYNC_SCHEDULE = "0 3 * * *"
        
        register_all_jobs()
        
        assert mock_add_job.call_count == 6
        
        ids = [call.kwargs['id'] for call in mock_add_job.call_args_list]
        assert "token_cleaner_daily" in ids
        assert "daily_checklist_emails" in ids
        assert "status_checker_interval" in ids
        assert "mc_diff_calculator" in ids
        assert "mc_email_report" in ids
        assert "ipam_segment_sync" in ids

    @patch("app.services.job_registry.CronTrigger.from_crontab")
    def test_parse_schedule_cron_fallback(self, mock_from_crontab):
        """Test cron fallback when from_crontab fails - covers lines 56-74"""
        mock_from_crontab.side_effect = Exception("Invalid cron")
        
        # This will trigger the except block and manual parsing
        # Lines 68, 70, 72 are the if statements for day, month, day_of_week
        schedule = "0 2 15 6 mon"  # minute hour day month day_of_week
        trigger = parse_schedule(schedule)
        
        assert isinstance(trigger, CronTrigger)

    def test_parse_schedule_simple_invalid(self):
        """Test simple format with non-integers"""
        schedule = "hour minute"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, CronTrigger)

    def test_parse_schedule_day_hour_invalid(self):
        """Test day hour format with non-integers"""
        schedule = "mon hour minute"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, CronTrigger)

    def test_parse_schedule_unknown_format(self):
        """Test unknown schedule format - covers lines 94-95"""
        # 4 parts - not a valid format
        schedule = "0 2 * *"
        trigger = parse_schedule(schedule)
        assert isinstance(trigger, CronTrigger)

    @patch("app.services.job_registry.add_job")
    def test_register_job(self, mock_add_job):
        """Test register_job helper"""
        from app.services.job_registry import register_job
        from app.services.workers.base import BaseWorker
        
        class TestWorker(BaseWorker):
            async def execute(self):
                pass
        
        trigger = IntervalTrigger(minutes=1)
        register_job(
            worker_class=TestWorker,
            trigger=trigger,
            job_id="test_id",
            job_name="Test Job"
        )
        
        mock_add_job.assert_called_once()
        assert mock_add_job.call_args.kwargs['id'] == "test_id"
        assert mock_add_job.call_args.kwargs['name'] == "Test Job"
