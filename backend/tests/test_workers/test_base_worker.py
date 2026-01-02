
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.workers.base import BaseWorker
from sqlalchemy.orm import Session

class MockWorker(BaseWorker):
    name = "test_worker"
    async def execute(self):
        pass

@pytest.mark.unit
@pytest.mark.asyncio
async def test_base_worker_execution():
    """Test successful worker execution"""
    worker = MockWorker()
    worker.execute = AsyncMock()
    
    await worker.run()
    
    worker.execute.assert_called_once()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_base_worker_error_handling():
    """Test worker handles errors and logs them"""
    worker = MockWorker()
    worker.execute = AsyncMock(side_effect=Exception("Test Error"))
    
    with patch.object(worker.logger, 'error') as mock_error:
        with pytest.raises(Exception):
            await worker.run()
        
        mock_error.assert_called_once()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_base_worker_database_session():
    """Test database session is created and closed"""
    worker = MockWorker()
    
    # Mock get_session_local returning a session maker
    mock_session = MagicMock(spec=Session)
    mock_session_maker = MagicMock(return_value=mock_session)
    
    with patch('app.services.workers.base.get_session_local', return_value=mock_session_maker):
        session = worker.get_db()
        assert session == mock_session
        
        worker.close_db()
        mock_session.close.assert_called_once()
        assert worker.db is None

@pytest.mark.unit
@pytest.mark.asyncio
async def test_base_worker_logging():
    """Test logger initialization"""
    worker = MockWorker()
    # Logger name might be prefixed, e.g. "app.worker.test_worker" or just "worker.test_worker"
    # base.py does: get_logger(f"worker.{self.name}")
    # checking if it ends with correct suffix
    assert worker.logger.name.endswith("worker.test_worker")

@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_close_db_error():
    """Test error when closing DB"""
    from app.services.workers.base import BaseWorker
    class MockWorker(BaseWorker):
        async def execute(self):
            pass

    worker = MockWorker()
    mock_db = MagicMock()
    worker.get_db = MagicMock(return_value=mock_db)
    
    # Mock close_db to log error but not raise
    def close_with_error():
        worker.logger.error("Error closing DB")
    
    worker.close_db = MagicMock(side_effect=close_with_error)
    
    # Run should succeed despite close error
    await worker.run()
    
    # Verify close_db was called
    worker.close_db.assert_called_once()

@pytest.mark.unit
def test_worker_call_method():
    """Test worker __call__ method for direct invocation"""
    from app.services.workers.base import BaseWorker
    
    class CallableWorker(BaseWorker):
        name = "callable_worker"
        
        async def execute(self):
            self.logger.info("Executed via __call__")
    
    worker = CallableWorker()
    
    # Call the worker directly (synchronous)
    # This will use the event loop
    result = worker()
    
    # Should complete without error
    assert result is None

@pytest.mark.unit
@pytest.mark.asyncio
async def test_worker_call_method_new_event_loop():
    """Test worker __call__ creates new event loop if needed"""
    from app.services.workers.base import BaseWorker
    import asyncio
    
    class LoopWorker(BaseWorker):
        name = "loop_worker"
        
        async def execute(self):
            pass
    
    worker = LoopWorker()
    
    # Mock get_event_loop to raise RuntimeError
    with patch('asyncio.get_event_loop', side_effect=RuntimeError("No loop")):
        with patch('asyncio.new_event_loop') as mock_new_loop:
            with patch('asyncio.set_event_loop'):
                mock_loop = MagicMock()
                mock_loop.run_until_complete = MagicMock(return_value=None)
                mock_new_loop.return_value = mock_loop
                
                result = worker()
                
                # Should have created new loop
                mock_new_loop.assert_called_once()
