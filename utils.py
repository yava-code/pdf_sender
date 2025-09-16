# some utility functions that are used across the project
# not the cleanest code but it works

import os
import re
from typing import List, Optional

def clean_filename(filename: str) -> str:
    """clean up filename by removing bad characters"""
    # remove dangerous chars
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # remove extra spaces
    filename = re.sub(r'\s+', ' ', filename).strip()
    return filename

def get_file_size_mb(file_path: str) -> float:
    """get file size in mb - returns 0 if file doesnt exist"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0.0

def format_duration(seconds: int) -> str:
    """format seconds into readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def truncate_text(text: str, max_length: int = 100) -> str:
    """truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

# some constants that are used in multiple places
SUPPORTED_FORMATS = ['.pdf', '.epub']
MAX_FILENAME_LENGTH = 255
DEFAULT_PAGE_LIMIT = 1000

class SimpleValidator:
    """basic validation functions"""
    
    @staticmethod
    def is_valid_page_number(page: int, total_pages: int) -> bool:
        return 1 <= page <= total_pages
    
    @staticmethod  
    def is_valid_user_id(user_id: int) -> bool:
        return user_id > 0
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """check if filename is safe to use"""
        if not filename or len(filename) > MAX_FILENAME_LENGTH:
            return False
        
        dangerous_patterns = ['..', '~', '$']
        for pattern in dangerous_patterns:
            if pattern in filename:
                return False
                
        return True

# quick helper to check if running in debug mode
def is_debug_mode() -> bool:
    return os.getenv('DEBUG', '').lower() in ['1', 'true', 'yes']