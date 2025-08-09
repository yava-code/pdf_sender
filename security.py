"""Security module for PDF Sender Bot."""

import hashlib
import hmac
import secrets
import time
import re
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog
from pathlib import Path
from .config import config
from .exceptions import UserPermissionError, FileValidationError, ValidationError
from .metrics import metrics

logger = structlog.get_logger(__name__)


class Permission(Enum):
    """User permissions."""
    READ = "read"
    WRITE = "write"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    ADMIN = "admin"
    SYSTEM = "system"
    DELETE = "delete"
    STATS = "stats"
    LOGS = "logs"
    BACKUP = "backup"
    CLEANUP = "cleanup"


class UserRole(Enum):
    """User roles with associated permissions."""
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class SecurityEvent:
    """Security event for logging and monitoring."""
    event_type: str
    user_id: int
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None


class SecurityManager:
    """Comprehensive security management system."""
    
    def __init__(self):
        self.role_permissions = {
            UserRole.GUEST: {Permission.READ},
            UserRole.USER: {Permission.READ, Permission.UPLOAD, Permission.DOWNLOAD},
            UserRole.PREMIUM: {
                Permission.READ, Permission.UPLOAD, Permission.DOWNLOAD,
                Permission.WRITE, Permission.STATS
            },
            UserRole.MODERATOR: {
                Permission.READ, Permission.UPLOAD, Permission.DOWNLOAD,
                Permission.WRITE, Permission.STATS, Permission.DELETE
            },
            UserRole.ADMIN: {
                Permission.READ, Permission.UPLOAD, Permission.DOWNLOAD,
                Permission.WRITE, Permission.STATS, Permission.DELETE,
                Permission.ADMIN, Permission.LOGS, Permission.BACKUP, Permission.CLEANUP
            },
            UserRole.SUPER_ADMIN: set(Permission)  # All permissions
        }
        
        self.user_roles: Dict[int, UserRole] = {}
        self.security_events: List[SecurityEvent] = []
        self.blocked_users: Set[int] = set()
        self.suspicious_activities: Dict[int, List[float]] = {}
        
        # Initialize admin users
        for admin_id in config.admin_ids:
            self.user_roles[admin_id] = UserRole.ADMIN
        
        # Security patterns
        self.malicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'shell_exec\s*\(',
            r'passthru\s*\(',
            r'\.\.[\/\\]',  # Path traversal
            r'\x00',  # Null bytes
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.malicious_patterns]
    
    def get_user_role(self, user_id: int) -> UserRole:
        """Get user role."""
        return self.user_roles.get(user_id, UserRole.USER)
    
    def set_user_role(self, user_id: int, role: UserRole, admin_id: int):
        """Set user role (admin only)."""
        if not self.has_permission(admin_id, Permission.ADMIN):
            raise UserPermissionError(
                "Only admins can change user roles",
                user_id=admin_id,
                required_permission=Permission.ADMIN.value
            )
        
        old_role = self.get_user_role(user_id)
        self.user_roles[user_id] = role
        
        self.log_security_event(
            "role_changed",
            admin_id,
            {
                "target_user": user_id,
                "old_role": old_role.value,
                "new_role": role.value
            },
            "info"
        )
        
        logger.info(f"User role changed", user_id=user_id, old_role=old_role.value, new_role=role.value, admin_id=admin_id)
    
    def has_permission(self, user_id: int, permission: Permission) -> bool:
        """Check if user has specific permission."""
        if user_id in self.blocked_users:
            return False
        
        role = self.get_user_role(user_id)
        return permission in self.role_permissions.get(role, set())
    
    def require_permission(self, user_id: int, permission: Permission):
        """Require permission or raise exception."""
        if not self.has_permission(user_id, permission):
            self.log_security_event(
                "permission_denied",
                user_id,
                {"required_permission": permission.value},
                "warning"
            )
            
            raise UserPermissionError(
                f"Permission denied: {permission.value} required",
                user_id=user_id,
                required_permission=permission.value
            )
    
    def validate_file_path(self, file_path: str) -> bool:
        """Validate file path for security issues."""
        try:
            # Normalize path
            normalized_path = Path(file_path).resolve()
            
            # Check for path traversal
            if '..' in file_path or file_path.startswith('/'):
                return False
            
            # Check for null bytes
            if '\x00' in file_path:
                return False
            
            # Check file extension
            if normalized_path.suffix.lower() not in config.allowed_file_types:
                return False
            
            return True
            
        except Exception:
            return False
    
    def validate_file_content(self, file_path: str, content: bytes) -> Tuple[bool, Optional[str]]:
        """Validate file content for security issues."""
        try:
            # Check file size
            if len(content) > config.max_file_size:
                return False, f"File too large: {len(content)} bytes (max: {config.max_file_size})"
            
            # Check for malicious patterns in text files
            if file_path.lower().endswith(('.txt', '.md', '.json', '.xml', '.html')):
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    for pattern in self.compiled_patterns:
                        if pattern.search(text_content):
                            return False, f"Malicious pattern detected in file content"
                except UnicodeDecodeError:
                    pass
            
            # Check PDF magic bytes
            if file_path.lower().endswith('.pdf'):
                if not content.startswith(b'%PDF-'):
                    return False, "Invalid PDF file format"
            
            # Check for embedded executables
            executable_signatures = [
                b'MZ',  # Windows PE
                b'\x7fELF',  # Linux ELF
                b'\xca\xfe\xba\xbe',  # Mach-O
                b'PK\x03\x04',  # ZIP (could contain executables)
            ]
            
            for signature in executable_signatures:
                if signature in content[:1024]:  # Check first 1KB
                    return False, "Potentially dangerous file content detected"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating file content: {e}")
            return False, f"File validation error: {str(e)}"
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input."""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Limit length
        max_length = 10000
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    def validate_user_input(self, text: str, field_name: str = "input") -> str:
        """Validate and sanitize user input."""
        if not text:
            return ""
        
        # Check for malicious patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                self.log_security_event(
                    "malicious_input_detected",
                    0,  # Unknown user
                    {
                        "field": field_name,
                        "pattern": pattern.pattern,
                        "input_preview": text[:100]
                    },
                    "warning"
                )
                raise ValidationError(
                    f"Invalid input detected in {field_name}",
                    field=field_name,
                    value=text[:100]
                )
        
        return self.sanitize_input(text)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token."""
        return secrets.token_urlsafe(length)
    
    def hash_data(self, data: str, salt: Optional[str] = None) -> str:
        """Hash data with optional salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        return hashlib.pbkdf2_hmac(
            'sha256',
            data.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        ).hex()
    
    def verify_hash(self, data: str, hashed: str, salt: str) -> bool:
        """Verify hashed data."""
        return hmac.compare_digest(
            self.hash_data(data, salt),
            hashed
        )
    
    def detect_suspicious_activity(self, user_id: int, activity_type: str) -> bool:
        """Detect suspicious user activity."""
        current_time = time.time()
        
        # Initialize user activity tracking
        if user_id not in self.suspicious_activities:
            self.suspicious_activities[user_id] = []
        
        activities = self.suspicious_activities[user_id]
        
        # Clean old activities (last hour)
        activities[:] = [t for t in activities if current_time - t < 3600]
        
        # Add current activity
        activities.append(current_time)
        
        # Check for suspicious patterns
        suspicious = False
        
        # Too many activities in short time
        if len(activities) > 100:  # More than 100 activities per hour
            suspicious = True
        
        # Rapid succession activities
        if len(activities) >= 10:
            recent_activities = [t for t in activities if current_time - t < 60]  # Last minute
            if len(recent_activities) > 20:  # More than 20 activities per minute
                suspicious = True
        
        if suspicious:
            self.log_security_event(
                "suspicious_activity",
                user_id,
                {
                    "activity_type": activity_type,
                    "activities_last_hour": len(activities),
                    "activities_last_minute": len([t for t in activities if current_time - t < 60])
                },
                "warning"
            )
        
        return suspicious
    
    def block_user(self, user_id: int, admin_id: int, reason: str):
        """Block user (admin only)."""
        if not self.has_permission(admin_id, Permission.ADMIN):
            raise UserPermissionError(
                "Only admins can block users",
                user_id=admin_id,
                required_permission=Permission.ADMIN.value
            )
        
        self.blocked_users.add(user_id)
        
        self.log_security_event(
            "user_blocked",
            admin_id,
            {
                "blocked_user": user_id,
                "reason": reason
            },
            "warning"
        )
        
        logger.warning(f"User blocked", user_id=user_id, admin_id=admin_id, reason=reason)
    
    def unblock_user(self, user_id: int, admin_id: int):
        """Unblock user (admin only)."""
        if not self.has_permission(admin_id, Permission.ADMIN):
            raise UserPermissionError(
                "Only admins can unblock users",
                user_id=admin_id,
                required_permission=Permission.ADMIN.value
            )
        
        self.blocked_users.discard(user_id)
        
        self.log_security_event(
            "user_unblocked",
            admin_id,
            {"unblocked_user": user_id},
            "info"
        )
        
        logger.info(f"User unblocked", user_id=user_id, admin_id=admin_id)
    
    def log_security_event(self, event_type: str, user_id: int, details: Dict[str, Any], 
                          severity: str = "info", source_ip: Optional[str] = None):
        """Log security event."""
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            timestamp=time.time(),
            details=details,
            severity=severity,
            source_ip=source_ip
        )
        
        self.security_events.append(event)
        
        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
        
        # Log to structured logger
        log_func = getattr(logger, severity, logger.info)
        log_func(
            f"Security event: {event_type}",
            user_id=user_id,
            event_type=event_type,
            **details
        )
        
        # Record metrics
        metrics.record_error(event_type, "security")
    
    def get_security_events(self, user_id: Optional[int] = None, 
                           event_type: Optional[str] = None,
                           limit: int = 100) -> List[SecurityEvent]:
        """Get security events with optional filtering."""
        events = self.security_events
        
        if user_id is not None:
            events = [e for e in events if e.user_id == user_id]
        
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-limit:]
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary statistics."""
        current_time = time.time()
        
        # Events in last 24 hours
        recent_events = [e for e in self.security_events if current_time - e.timestamp < 86400]
        
        # Group by severity
        severity_counts = {}
        for event in recent_events:
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
        
        # Group by event type
        event_type_counts = {}
        for event in recent_events:
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
        
        return {
            "total_events_24h": len(recent_events),
            "severity_breakdown": severity_counts,
            "event_type_breakdown": event_type_counts,
            "blocked_users_count": len(self.blocked_users),
            "total_users_with_roles": len(self.user_roles),
            "suspicious_users_count": len(self.suspicious_activities)
        }
    
    def audit_permissions(self) -> Dict[str, Any]:
        """Audit user permissions and roles."""
        role_counts = {}
        for role in self.user_roles.values():
            role_counts[role.value] = role_counts.get(role.value, 0) + 1
        
        admin_users = [uid for uid, role in self.user_roles.items() if role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]]
        
        return {
            "role_distribution": role_counts,
            "admin_users": admin_users,
            "blocked_users": list(self.blocked_users),
            "total_users": len(self.user_roles)
        }


# Global security manager instance
security = SecurityManager()


# Decorator for permission checking
def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Try to extract user_id from various sources
            user_id = None
            
            if args and hasattr(args[0], 'from_user'):
                user_id = args[0].from_user.id
            elif 'user_id' in kwargs:
                user_id = kwargs['user_id']
            elif 'message' in kwargs and hasattr(kwargs['message'], 'from_user'):
                user_id = kwargs['message'].from_user.id
            
            if user_id:
                security.require_permission(user_id, permission)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Decorator for input validation
def validate_input(field_name: str = "input"):
    """Decorator to validate user input."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Validate string arguments
            for i, arg in enumerate(args):
                if isinstance(arg, str) and i > 0:  # Skip first arg (usually self/message)
                    args = list(args)
                    args[i] = security.validate_user_input(arg, f"{field_name}_{i}")
                    args = tuple(args)
            
            # Validate string keyword arguments
            for key, value in kwargs.items():
                if isinstance(value, str):
                    kwargs[key] = security.validate_user_input(value, key)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator