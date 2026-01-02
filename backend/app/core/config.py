from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    APP_NAME: str = "Unified Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database Configuration
    ORACLE_USER: str = "umduser"
    ORACLE_PASSWORD: str = "umd123"
    ORACLE_HOST: str = "localhost"
    ORACLE_PORT: int = 1521
    ORACLE_SERVICE: str = "XEPDB1"
    DATABASE_URL: str = ""
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True
    DB_RECONNECT_RETRIES: int = 5
    DB_RECONNECT_DELAY: int = 2  # seconds
    DB_RECONNECT_BACKOFF: float = 1.5  # exponential backoff multiplier
    
    # LDAP Configuration
    LDAP_SERVER: str = "ldap://ldap.example.com:389"
    LDAP_BASE_DN: str = "dc=example,dc=com"
    LDAP_USER_DN: str = "cn=users,dc=example,dc=com"
    LDAP_GROUP_DN: str = "cn=groups,dc=example,dc=com"
    LDAP_ENABLED: bool = False
    
    # JWT Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "unified-portal"
    JWT_AUDIENCE: str = "unified-portal-users"
    
    # Debug Mode (bypass LDAP and password check)
    DEBUG_MODE: bool = True
    
    # CORS - handle both string (comma-separated) and list
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:4200,http://localhost:3000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Application Settings (same across environments but configurable)
    APP_TITLE: str = "Unified Portal"
    APP_DESCRIPTION: str = "Unified automation portal with multiple catalogues"
    PAGE_SIZE: int = 20
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    SESSION_TIMEOUT_MINUTES: int = 30
    ENABLE_AUDIT_LOGGING: bool = True
    ENABLE_RATE_LIMITING: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Feature Flags
    ENABLE_REGISTRATION: bool = False
    ENABLE_PASSWORD_RESET: bool = True
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    
    # SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@example.com"
    SMTP_FROM_NAME: str = "Unified Portal"
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    SMTP_TIMEOUT: int = 10
    
    # Email Recipients (comma-separated for multiple recipients)
    # These are used as defaults in DEBUG_MODE. In production, recipients should be explicitly provided.
    EMAIL_ADMIN_RECIPIENTS: str = "admin@example.com"
    EMAIL_ADMIN_CC: str = ""
    EMAIL_ADMIN_BCC: str = ""
    
    # Background Job Schedules
    # Cron format: "hour minute" or "day_of_week hour minute" or full cron expression
    # Interval format: "hours", "minutes", or "seconds" (e.g., "6 hours", "30 minutes")
    JOB_TOKEN_CLEANER_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM (cron format)
    JOB_DAILY_CHECKLIST_SCHEDULE: str = "0 8 * * *"  # Daily at 8 AM (cron format)
    JOB_STATUS_CHECKER_SCHEDULE: str = "6 hours"  # Every 6 hours (interval format)
    JOB_MORNING_CHECKLIST_DIFF_CAL_SCHEDULE: str = "30 minutes" # Every 30 minutes (interval format)
    JOB_MORNING_CHECKLIST_EMAIL_SCHEDULE: str = "0 4 * * *" # Daily at 4 AM (cron format)
    JOB_MORNING_CHECKLIST_EMAIL_TO: str = "" # Comma-separated list of recipients
    JOB_MORNING_CHECKLIST_EMAIL_CC: str = "" # Comma-separated list of CC recipients
    
    # Audit Log Email
    JOB_AUDIT_LOG_EMAIL_SCHEDULE: str = "0 6 * * *" # Daily at 6 AM
    JOB_AUDIT_LOG_EMAIL_RECIPIENTS: str = "" # Comma-separated list of recipients
    
    # IPAM Sync
    SNOW_API_URL: str = ""
    SNOW_USER: str = ""
    SNOW_PASSWORD: str = ""
    SNOW_IPAM_TABLE: str = "cmdb_ci_ip_network" # Default table
    JOB_IPAM_SYNC_SCHEDULE: str = "0 3 * * *" # Daily at 3 AM
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8"
    )

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    def get_database_url(self) -> str:
        """Build database URL if not provided"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Use Easy Connect Plus format with service_name parameter for pluggable databases
        # This ensures Oracle interprets it as a service name, not a SID
        return f"oracle+oracledb://{self.ORACLE_USER}:{self.ORACLE_PASSWORD}@{self.ORACLE_HOST}:{self.ORACLE_PORT}/?service_name={self.ORACLE_SERVICE}"
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"

# Load environment-specific config
def load_settings() -> Settings:
    """Load settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    # Determine which .env file to use
    env_file_map = {
        "development": ".env.dev",
        "staging": ".env.staging",
        "production": ".env.prod"
    }
    
    env_file = env_file_map.get(env, ".env")
    
    # Check if environment-specific file exists, fallback to .env
    env_path = Path(env_file)
    if not env_path.exists():
        env_file = ".env"
    
    # Create settings with environment-specific file
    settings = Settings(_env_file=env_file if env_file != ".env" else None)
    
    # Override with environment variables
    settings.ENVIRONMENT = env
    
    return settings

settings = load_settings()

# Build database URL
if not settings.DATABASE_URL:
    settings.DATABASE_URL = settings.get_database_url()
