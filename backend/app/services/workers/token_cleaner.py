"""
Token Cleaner Worker

Cleans up expired refresh tokens from the database.
"""
from app.services.workers.base import BaseWorker
from app.models.user import User
from sqlalchemy import text
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.time_utils import get_ist_time


class TokenCleanerWorker(BaseWorker):
    """Worker to clean expired tokens"""
    
    name = "token_cleaner"
    description = "Cleans expired refresh tokens from the database"
    
    async def execute(self):
        """Clean expired tokens"""
        db = self.get_db()
        try:
            # Calculate expiration threshold (tokens older than refresh token expiry)
            threshold = get_ist_time() - timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS + 7)
            
            # Note: In a real implementation, you would have a tokens table
            # For now, this is a placeholder that logs the action
            self.logger.info(f"Token cleaner executed. Threshold: {threshold}")
            self.logger.info("Token cleanup completed (no token table implemented yet)")
            
            # Example query if you have a tokens table:
            # expired_count = db.query(Token).filter(Token.expires_at < threshold).count()
            # db.query(Token).filter(Token.expires_at < threshold).delete()
            # db.commit()
            # self.logger.info(f"Cleaned {expired_count} expired tokens")
            
        except Exception as e:
            self.logger.error(f"Error cleaning tokens: {e}", exc_info=True)
            db.rollback()
            raise
