import uvicorn
import sys
import logging
from app.core.config import settings
from app.core.database import get_engine

# Configure basic logging for startup check
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Pre-flight check: Verify database connectivity before starting server
    # This prevents the reloader from keeping the process alive if DB is down
    try:
        logger.info("Performing startup database connection check...")
        engine = get_engine(fail_fast=True)
        if not engine:
            logger.critical("Startup check failed: Database not available.")
            sys.exit(1)
        logger.info("Startup database check passed.")
    except Exception as e:
        logger.critical(f"Startup check failed with error: {e}")
        sys.exit(1)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

