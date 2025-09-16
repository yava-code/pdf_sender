import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from functools import lru_cache

class Config(BaseSettings):
    """Application configuration using Pydantic settings."""
    
# bot configuration
    bot_token: str = Field(default="dummy_token", description="Telegram bot token", alias="BOT_TOKEN")
    
    # Database configuration
    database_path: str = Field("pdf_sender.json", description="Path to JSON database file", alias="DATABASE_PATH")
    
    # PDF configuration
    pdf_path: str = Field("book.pdf", description="Default PDF file path", alias="PDF_PATH")
    pages_per_send: int = Field(3, ge=1, description="Number of pages to send at once", alias="PAGES_PER_SEND")
    
    # Scheduler configuration
    interval_hours: int = Field(6, ge=1, le=168, description="Hours between scheduled sends", alias="INTERVAL_HOURS")
    schedule_time: str = Field("14:00", description="Time to send scheduled messages", alias="SCHEDULE_TIME")
    
    # Upload configuration
    upload_dir: str = Field("uploads", description="Directory for uploaded files", alias="UPLOAD_DIR")
    output_dir: str = Field("output", description="Output directory for processed files", alias="OUTPUT_DIR")
    max_file_size: int = Field(50 * 1024 * 1024, description="Maximum file size in bytes", alias="MAX_FILE_SIZE")
    
    # Admin configuration
    admin_ids: List[int] = Field(default_factory=list, description="List of admin user IDs", alias="ADMIN_IDS")
    
    # Logging configuration
    log_level: str = Field("INFO", description="Logging level", alias="LOG_LEVEL")
    log_dir: str = Field("logs", description="Directory for log files", alias="LOG_DIR")
    
    # Cleanup configuration
    cleanup_interval_hours: int = Field(24, ge=1, description="Hours between cleanup runs", alias="CLEANUP_INTERVAL_HOURS")
    cleanup_older_than_days: int = Field(7, ge=1, description="Delete files older than N days", alias="CLEANUP_OLDER_THAN_DAYS")
    
    # Performance configuration
    max_concurrent_uploads: int = Field(5, ge=1, le=20, description="Max concurrent file uploads", alias="MAX_CONCURRENT_UPLOADS")
    request_timeout: int = Field(30, ge=5, le=300, description="HTTP request timeout in seconds", alias="REQUEST_TIMEOUT")
    image_quality: int = Field(85, ge=1, le=100, description="JPEG image quality for PDF page extraction", alias="IMAGE_QUALITY")
    
    # Security configuration
    allowed_file_types: List[str] = Field(
        default_factory=lambda: [".pdf", ".epub", ".txt", ".docx"],
        description="Allowed file extensions",
        alias="ALLOWED_FILE_TYPES"
    )
    enable_rate_limiting: bool = Field(True, description="Enable rate limiting", alias="ENABLE_RATE_LIMITING")
    max_requests_per_minute: int = Field(60, ge=1, description="Max requests per user per minute", alias="MAX_REQUESTS_PER_MINUTE")
    
    # Monitoring configuration
    enable_metrics: bool = Field(False, description="Enable Prometheus metrics", alias="ENABLE_METRICS")
    metrics_port: int = Field(8000, ge=1024, le=65535, description="Metrics server port", alias="METRICS_PORT")
    
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

# global config instance - yeah i know singleton pattern but whatever
config = Config()

# some legacy stuff for backwards compatibility... dont judge me
class LegacyConfig:
    """legacy wrapper - keeping this cuz too lazy to refactor everything"""
    
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
    
    @property
    def OUTPUT_DIR(self) -> str:
        return config.output_dir
    
    @property
    def MAX_FILE_SIZE_MB(self) -> int:
        return config.max_file_size // (1024 * 1024)  # bytes to MB
    
    @property
    def IMAGE_RETENTION_DAYS(self) -> int:
        return config.cleanup_older_than_days
    
    @property
    def IMAGE_QUALITY(self) -> int:
        return config.image_quality
    
    @property
    def PAGES_PER_SEND(self) -> int:
        return config.pages_per_send
    
    @property
    def SCHEDULE_TIME(self) -> str:
        return config.schedule_time
    
    @property
    def LOG_DIR(self) -> str:
        return config.log_dir
    
    @property
    def MAX_CONCURRENT_UPLOADS(self) -> int:
        return config.max_concurrent_uploads
    
    @property
    def REQUEST_TIMEOUT(self) -> int:
        return config.request_timeout
    
    @property
    def ALLOWED_FILE_TYPES(self) -> List[str]:
        return config.allowed_file_types
    
    @property
    def ENABLE_RATE_LIMITING(self) -> bool:
        return config.enable_rate_limiting
    
    @property
    def MAX_REQUESTS_PER_MINUTE(self) -> int:
        return config.max_requests_per_minute
    
    @property
    def ENABLE_METRICS(self) -> bool:
        return config.enable_metrics
    
    @property
    def METRICS_PORT(self) -> int:
        return config.metrics_port

# legacy config instance
legacy_config = LegacyConfig()

@lru_cache()
def get_config() -> Config:
    """returns cached config instance"""
    return Config()
