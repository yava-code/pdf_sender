import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """Application configuration using Pydantic settings."""
    
    # Bot configuration
    bot_token: str = Field(..., description="Telegram bot token")
    
    # Database configuration
    database_path: str = Field("pdf_sender.json", description="Path to JSON database file")
    
    # PDF configuration
    pdf_path: str = Field("book.pdf", description="Default PDF file path")
    pages_per_send: int = Field(3, ge=1, description="Number of pages to send at once")
    
    # Scheduler configuration
    interval_hours: int = Field(6, ge=1, le=168, description="Hours between scheduled sends")
    schedule_time: str = Field("14:00", description="Time to send scheduled messages")
    
    # Upload configuration
    upload_dir: str = Field("uploads", description="Directory for uploaded files")
    output_dir: str = Field("output", description="Output directory for processed files")
    max_file_size: int = Field(50 * 1024 * 1024, description="Maximum file size in bytes")
    
    # Admin configuration
    admin_ids: List[int] = Field(default_factory=list, description="List of admin user IDs")
    
    # Logging configuration
    log_level: str = Field("INFO", description="Logging level")
    log_dir: str = Field("logs", description="Directory for log files")
    
    # Cleanup configuration
    cleanup_interval_hours: int = Field(24, ge=1, description="Hours between cleanup runs")
    cleanup_older_than_days: int = Field(7, ge=1, description="Delete files older than N days")
    
    # Performance configuration
    max_concurrent_uploads: int = Field(5, ge=1, le=20, description="Max concurrent file uploads")
    request_timeout: int = Field(30, ge=5, le=300, description="HTTP request timeout in seconds")
    image_quality: int = Field(85, ge=1, le=100, description="JPEG image quality for PDF page extraction")
    
    # Security configuration
    allowed_file_types: List[str] = Field(
        default_factory=lambda: [".pdf", ".epub", ".txt", ".docx"],
        description="Allowed file extensions"
    )
    enable_rate_limiting: bool = Field(True, description="Enable rate limiting")
    max_requests_per_minute: int = Field(60, ge=1, description="Max requests per user per minute")
    
    # Monitoring configuration
    enable_metrics: bool = Field(False, description="Enable Prometheus metrics")
    metrics_port: int = Field(8000, ge=1024, le=65535, description="Metrics server port")
    
    @validator('admin_ids', pre=True)
    def parse_admin_ids(cls, v):
        """Parse admin IDs from string or list."""
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(id.strip()) for id in v.split(",") if id.strip().isdigit()]
        return v
    
    @validator('upload_dir')
    def create_upload_dir(cls, v):
        """Ensure upload directory exists."""
        Path(v).mkdir(exist_ok=True)
        return v
    
    @validator('log_dir')
    def create_log_dir(cls, v):
        """Ensure log directory exists."""
        Path(v).mkdir(exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Map environment variables to field names
        fields = {
            'bot_token': {'env': 'BOT_TOKEN'},
            'database_path': {'env': 'DATABASE_PATH'},
            'pdf_path': {'env': 'PDF_PATH'},
            'pages_per_send': {'env': 'PAGES_PER_SEND'},
            'interval_hours': {'env': 'INTERVAL_HOURS'},
            'schedule_time': {'env': 'SCHEDULE_TIME'},
            'upload_dir': {'env': 'UPLOAD_DIR'},
            'output_dir': {'env': 'OUTPUT_DIR'},
            'max_file_size': {'env': 'MAX_FILE_SIZE'},
            'admin_ids': {'env': 'ADMIN_IDS'},
            'log_level': {'env': 'LOG_LEVEL'},
            'log_dir': {'env': 'LOG_DIR'},
            'cleanup_interval_hours': {'env': 'CLEANUP_INTERVAL_HOURS'},
            'cleanup_older_than_days': {'env': 'CLEANUP_OLDER_THAN_DAYS'},
            'max_concurrent_uploads': {'env': 'MAX_CONCURRENT_UPLOADS'},
            'request_timeout': {'env': 'REQUEST_TIMEOUT'},
            'image_quality': {'env': 'IMAGE_QUALITY'},
            'allowed_file_types': {'env': 'ALLOWED_FILE_TYPES'},
            'enable_rate_limiting': {'env': 'ENABLE_RATE_LIMITING'},
            'max_requests_per_minute': {'env': 'MAX_REQUESTS_PER_MINUTE'},
            'enable_metrics': {'env': 'ENABLE_METRICS'},
            'metrics_port': {'env': 'METRICS_PORT'},
        }

# Global configuration instance
config = Config()

# Legacy compatibility - maintain old attribute names
class LegacyConfig:
    """Legacy configuration wrapper for backward compatibility."""
    
    @property
    def BOT_TOKEN(self) -> str:
        return config.bot_token
    
    @property
    def DATABASE_PATH(self) -> str:
        return config.database_path
    
    @property
    def PDF_PATH(self) -> str:
        return config.pdf_path
    
    @property
    def INTERVAL_HOURS(self) -> int:
        return config.interval_hours
    
    @property
    def UPLOAD_DIR(self) -> Path:
        return Path(config.upload_dir)
    
    @property
    def MAX_FILE_SIZE(self) -> int:
        return config.max_file_size
    
    @property
    def ADMIN_IDS(self) -> List[int]:
        return config.admin_ids
    
    @property
    def LOG_LEVEL(self) -> str:
        return config.log_level
    
    @property
    def CLEANUP_INTERVAL_HOURS(self) -> int:
        return config.cleanup_interval_hours
    
    @property
    def CLEANUP_OLDER_THAN_DAYS(self) -> int:
        return config.cleanup_older_than_days

# Create legacy instance for backward compatibility
# Create legacy config instance for backward compatibility
legacy_config = LegacyConfig()
