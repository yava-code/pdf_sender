"""Custom exceptions for the PDF Sender Bot."""

from typing import Optional, Any, Dict


class PDFSenderError(Exception):
    """Base exception for PDF Sender Bot."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(PDFSenderError):
    """Raised when there's a configuration issue."""
    pass


class DatabaseError(PDFSenderError):
    """Raised when there's a database operation issue."""
    pass


class FileError(PDFSenderError):
    """Base class for file-related errors."""
    pass


class FileNotFoundError(FileError):
    """Raised when a required file is not found."""
    pass


class FileValidationError(FileError):
    """Raised when file validation fails."""
    pass


class FileSizeError(FileValidationError):
    """Raised when file size exceeds limits."""
    
    def __init__(self, message: str, file_size: int, max_size: int, **kwargs):
        super().__init__(message, **kwargs)
        self.file_size = file_size
        self.max_size = max_size
        self.details.update({
            'file_size': file_size,
            'max_size': max_size,
            'size_mb': round(file_size / (1024 * 1024), 2),
            'max_size_mb': round(max_size / (1024 * 1024), 2)
        })


class FileTypeError(FileValidationError):
    """Raised when file type is not allowed."""
    
    def __init__(self, message: str, file_type: str, allowed_types: list, **kwargs):
        super().__init__(message, **kwargs)
        self.file_type = file_type
        self.allowed_types = allowed_types
        self.details.update({
            'file_type': file_type,
            'allowed_types': allowed_types
        })


class PDFError(FileError):
    """Base class for PDF-related errors."""
    pass


class PDFCorruptedError(PDFError):
    """Raised when PDF file is corrupted or unreadable."""
    pass


class PDFPasswordProtectedError(PDFError):
    """Raised when PDF is password protected."""
    pass


class PDFProcessingError(PDFError):
    """Raised when PDF processing fails."""
    pass


class UserError(PDFSenderError):
    """Base class for user-related errors."""
    pass


class UserNotFoundError(UserError):
    """Raised when user is not found in database."""
    
    def __init__(self, message: str, user_id: int, **kwargs):
        super().__init__(message, **kwargs)
        self.user_id = user_id
        self.details.update({'user_id': user_id})


class UserPermissionError(UserError):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str, user_id: int, required_permission: str, **kwargs):
        super().__init__(message, **kwargs)
        self.user_id = user_id
        self.required_permission = required_permission
        self.details.update({
            'user_id': user_id,
            'required_permission': required_permission
        })


class RateLimitError(UserError):
    """Raised when user exceeds rate limits."""
    
    def __init__(self, message: str, user_id: int, retry_after: int, **kwargs):
        super().__init__(message, **kwargs)
        self.user_id = user_id
        self.retry_after = retry_after
        self.details.update({
            'user_id': user_id,
            'retry_after': retry_after
        })


class TelegramError(PDFSenderError):
    """Base class for Telegram API related errors."""
    pass


class MessageSendError(TelegramError):
    """Raised when message sending fails."""
    
    def __init__(self, message: str, user_id: int, telegram_error: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.user_id = user_id
        self.telegram_error = telegram_error
        self.details.update({
            'user_id': user_id,
            'telegram_error': telegram_error
        })


class FileSendError(TelegramError):
    """Raised when file sending fails."""
    
    def __init__(self, message: str, user_id: int, file_path: str, **kwargs):
        super().__init__(message, **kwargs)
        self.user_id = user_id
        self.file_path = file_path
        self.details.update({
            'user_id': user_id,
            'file_path': file_path
        })


class SchedulerError(PDFSenderError):
    """Raised when scheduler operations fail."""
    pass


class JobError(SchedulerError):
    """Raised when job execution fails."""
    
    def __init__(self, message: str, job_id: str, **kwargs):
        super().__init__(message, **kwargs)
        self.job_id = job_id
        self.details.update({'job_id': job_id})


class ValidationError(PDFSenderError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str, value: Any, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        self.details.update({
            'field': field,
            'value': str(value)
        })


class NetworkError(PDFSenderError):
    """Raised when network operations fail."""
    pass


class TimeoutError(NetworkError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str, timeout_seconds: int, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.details.update({'timeout_seconds': timeout_seconds})


class ResourceError(PDFSenderError):
    """Raised when system resources are insufficient."""
    pass


class DiskSpaceError(ResourceError):
    """Raised when disk space is insufficient."""
    
    def __init__(self, message: str, available_space: int, required_space: int, **kwargs):
        super().__init__(message, **kwargs)
        self.available_space = available_space
        self.required_space = required_space
        self.details.update({
            'available_space': available_space,
            'required_space': required_space,
            'available_mb': round(available_space / (1024 * 1024), 2),
            'required_mb': round(required_space / (1024 * 1024), 2)
        })


class MemoryError(ResourceError):
    """Raised when memory is insufficient."""
    pass


# Error code mappings for structured error handling
ERROR_CODES = {
    # Configuration errors
    'CONFIG_MISSING_TOKEN': 'BOT_TOKEN environment variable is required',
    'CONFIG_INVALID_VALUE': 'Invalid configuration value',
    
    # File errors
    'FILE_NOT_FOUND': 'File not found',
    'FILE_TOO_LARGE': 'File size exceeds maximum allowed size',
    'FILE_INVALID_TYPE': 'File type not allowed',
    'FILE_CORRUPTED': 'File is corrupted or unreadable',
    'FILE_PASSWORD_PROTECTED': 'File is password protected',
    
    # User errors
    'USER_NOT_FOUND': 'User not found in database',
    'USER_PERMISSION_DENIED': 'User lacks required permissions',
    'USER_RATE_LIMITED': 'User has exceeded rate limits',
    
    # Telegram errors
    'TELEGRAM_MESSAGE_FAILED': 'Failed to send message via Telegram',
    'TELEGRAM_FILE_FAILED': 'Failed to send file via Telegram',
    
    # System errors
    'SYSTEM_DISK_FULL': 'Insufficient disk space',
    'SYSTEM_MEMORY_LOW': 'Insufficient memory',
    'SYSTEM_TIMEOUT': 'Operation timed out',
}


def get_error_message(error_code: str, **kwargs) -> str:
    """Get formatted error message for error code."""
    template = ERROR_CODES.get(error_code, 'Unknown error')
    try:
        return template.format(**kwargs)
    except KeyError:
        return template