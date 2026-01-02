import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from app.services.scheduler import (
    start_scheduler, 
    shutdown_scheduler,
    add_job,
    remove_job,
    get_jobs,
    pause_job,
    resume_job,
    get_scheduler
)
# app.services.scheduler uses a global 'scheduler' variable and get_scheduler function

@pytest.mark.unit
def test_start_scheduler():
    """Test starting the scheduler"""
    mock_sched_instance = MagicMock()
    # Mock 'running' property behavior is tricky on MagicMock unless configured
    type(mock_sched_instance).running = PropertyMock(return_value=False)
    
    with patch('app.services.scheduler.AsyncIOScheduler', return_value=mock_sched_instance):
        # Force reset of global scheduler if needed, but get_scheduler creates it
        with patch('app.services.scheduler.scheduler', None):
             start_scheduler()
             mock_sched_instance.start.assert_called_once()

@pytest.mark.unit
def test_start_scheduler_already_running():
    """Test starting scheduler when already running"""
    mock_sched_instance = MagicMock()
    type(mock_sched_instance).running = PropertyMock(return_value=True)
    
    with patch('app.services.scheduler.AsyncIOScheduler', return_value=mock_sched_instance):
        with patch('app.services.scheduler.scheduler', None): 
             start_scheduler()
             mock_sched_instance.start.assert_not_called()

@pytest.mark.unit
def test_shutdown_scheduler():
    """Test shutting down the scheduler"""
    mock_sched_instance = MagicMock()
    type(mock_sched_instance).running = PropertyMock(return_value=True)
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        shutdown_scheduler()
        mock_sched_instance.shutdown.assert_called_once_with(wait=True)

@pytest.mark.unit
def test_shutdown_scheduler_not_running():
    """Test shutting down when not running"""
    mock_sched_instance = MagicMock()
    type(mock_sched_instance).running = PropertyMock(return_value=False)
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        shutdown_scheduler()
        mock_sched_instance.shutdown.assert_not_called()

@pytest.mark.unit
def test_add_job():
    """Test adding a job"""
    mock_sched_instance = MagicMock()
    
    with patch('app.services.scheduler.AsyncIOScheduler', return_value=mock_sched_instance):
        with patch('app.services.scheduler.scheduler', None): 
            # First call creates scheduler
            add_job(lambda: None, 'interval', id='test_job')
            mock_sched_instance.add_job.assert_called_once()
            
            # Verify args
            args, kwargs = mock_sched_instance.add_job.call_args
            assert kwargs['id'] == 'test_job'

@pytest.mark.unit
def test_remove_job():
    """Test removing a job"""
    mock_sched_instance = MagicMock()
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        remove_job('test_job')
        mock_sched_instance.remove_job.assert_called_once_with('test_job')

@pytest.mark.unit
def test_remove_job_error():
    """Test removing a job with error"""
    mock_sched_instance = MagicMock()
    mock_sched_instance.remove_job.side_effect = Exception("Job not found")
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        # Should catch exception and log error, not raise
        remove_job('test_job')
        mock_sched_instance.remove_job.assert_called_once()

@pytest.mark.unit
def test_get_jobs():
    """Test getting jobs"""
    mock_sched_instance = MagicMock()
    mock_sched_instance.get_jobs.return_value = []
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        jobs = get_jobs()
        assert jobs == []
        mock_sched_instance.get_jobs.assert_called_once()

@pytest.mark.unit
def test_pause_job():
    """Test pausing a job"""
    mock_sched_instance = MagicMock()
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        pause_job('test_job')
        mock_sched_instance.pause_job.assert_called_once_with('test_job')

@pytest.mark.unit
def test_pause_job_error():
    """Test pausing a job with error"""
    mock_sched_instance = MagicMock()
    mock_sched_instance.pause_job.side_effect = Exception("Error")
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        pause_job('test_job')
        mock_sched_instance.pause_job.assert_called_once()

@pytest.mark.unit
def test_resume_job():
    """Test resuming a job"""
    mock_sched_instance = MagicMock()
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        resume_job('test_job')
        mock_sched_instance.resume_job.assert_called_once_with('test_job')

@pytest.mark.unit
def test_resume_job_error():
    """Test resuming a job with error"""
    mock_sched_instance = MagicMock()
    mock_sched_instance.resume_job.side_effect = Exception("Error")
    
    with patch('app.services.scheduler.scheduler', mock_sched_instance):
        resume_job('test_job')
        mock_sched_instance.resume_job.assert_called_once()
