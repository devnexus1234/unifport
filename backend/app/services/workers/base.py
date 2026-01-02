"""
Base Worker Class

All background workers should inherit from this base class.
"""
from abc import ABC, abstractmethod
from app.core.logging_config import get_logger
from app.core.database import get_session_local
from sqlalchemy.orm import Session
from typing import Optional
import traceback


class BaseWorker(ABC):
    """
    Base class for all background workers
    
    Example:
        class MyWorker(BaseWorker):
            name = "my_worker"
            
            async def execute(self):
                # Your worker logic here
                self.logger.info("Worker executed")
    """
    
    name: str = "base_worker"
    description: str = "Base worker class"
    
    def __init__(self):
        self.logger = get_logger(f"worker.{self.name}")
        self.db: Optional[Session] = None
    
    def get_db(self):
        """Get database session"""
        if self.db is None:
            session_maker = get_session_local()
            if session_maker:
                self.db = session_maker()
        return self.db
    
    def close_db(self):
        """Close database session"""
        if self.db:
            self.db.close()
            self.db = None
    
    @abstractmethod
    async def execute(self):
        """
        Execute the worker task
        
        This method must be implemented by all workers.
        """
        pass
    
    async def run(self):
        """
        Run the worker with error handling and database management
        """
        try:
            self.logger.info(f"Starting worker: {self.name}")
            await self.execute()
            self.logger.info(f"Completed worker: {self.name}")
        except Exception as e:
            self.logger.error(
                f"Worker {self.name} failed: {e}",
                exc_info=True,
                extra={"traceback": traceback.format_exc()}
            )
            raise
        finally:
            self.close_db()
    
    def __call__(self):
        """Allow worker to be called directly"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.run())
