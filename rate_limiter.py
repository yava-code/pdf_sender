"""Rate limiting system for PDF Sender Bot."""

import time
import asyncio
from typing import Dict, Optional, Tuple, Any
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
import structlog
from .config import config
from .exceptions import RateLimitError
from .metrics import metrics

logger = structlog.get_logger(__name__)


class RateLimitType(Enum):
    """Types of rate limits."""
    MESSAGES = "messages"
    COMMANDS = "commands"
    FILE_UPLOADS = "file_uploads"
    PDF_REQUESTS = "pdf_requests"
    API_CALLS = "api_calls"


@dataclass
class RateLimit:
    """Rate limit configuration."""
    max_requests: int
    window_seconds: int
    burst_allowance: int = 0
    cooldown_seconds: int = 0
    
    def __post_init__(self):
        if self.burst_allowance == 0:
            self.burst_allowance = max(1, self.max_requests // 4)


@dataclass
class UserRateState:
    """Rate limiting state for a user."""
    requests: deque = field(default_factory=deque)
    last_request: float = 0
    violation_count: int = 0
    cooldown_until: float = 0
    burst_tokens: int = 0
    
    def __post_init__(self):
        if not hasattr(self, 'requests'):
            self.requests = deque()


class RateLimiter:
    """Advanced rate limiter with multiple strategies."""
    
    def __init__(self):
        self.enabled = config.enable_rate_limiting
        self.user_states: Dict[int, Dict[RateLimitType, UserRateState]] = defaultdict(
            lambda: defaultdict(UserRateState)
        )
        
        # Default rate limits
        self.rate_limits = {
            RateLimitType.MESSAGES: RateLimit(
                max_requests=config.max_requests_per_minute,
                window_seconds=60,
                burst_allowance=10,
                cooldown_seconds=30
            ),
            RateLimitType.COMMANDS: RateLimit(
                max_requests=20,
                window_seconds=60,
                burst_allowance=5,
                cooldown_seconds=60
            ),
            RateLimitType.FILE_UPLOADS: RateLimit(
                max_requests=5,
                window_seconds=300,  # 5 minutes
                burst_allowance=2,
                cooldown_seconds=120
            ),
            RateLimitType.PDF_REQUESTS: RateLimit(
                max_requests=10,
                window_seconds=60,
                burst_allowance=3,
                cooldown_seconds=30
            ),
            RateLimitType.API_CALLS: RateLimit(
                max_requests=100,
                window_seconds=60,
                burst_allowance=20,
                cooldown_seconds=10
            )
        }
        
        # Admin users get higher limits
        self.admin_multiplier = 5
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_task())
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in config.admin_ids
    
    def get_rate_limit(self, limit_type: RateLimitType, user_id: int) -> RateLimit:
        """Get rate limit for user and type."""
        base_limit = self.rate_limits[limit_type]
        
        if self.is_admin(user_id):
            return RateLimit(
                max_requests=base_limit.max_requests * self.admin_multiplier,
                window_seconds=base_limit.window_seconds,
                burst_allowance=base_limit.burst_allowance * self.admin_multiplier,
                cooldown_seconds=base_limit.cooldown_seconds // 2
            )
        
        return base_limit
    
    def _cleanup_old_requests(self, user_state: UserRateState, window_seconds: int):
        """Remove old requests outside the time window."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        while user_state.requests and user_state.requests[0] < cutoff_time:
            user_state.requests.popleft()
    
    def _is_in_cooldown(self, user_state: UserRateState) -> Tuple[bool, float]:
        """Check if user is in cooldown period."""
        current_time = time.time()
        if user_state.cooldown_until > current_time:
            return True, user_state.cooldown_until - current_time
        return False, 0
    
    def _apply_cooldown(self, user_state: UserRateState, cooldown_seconds: int):
        """Apply cooldown to user."""
        user_state.cooldown_until = time.time() + cooldown_seconds
        user_state.violation_count += 1
        
        # Exponential backoff for repeated violations
        if user_state.violation_count > 3:
            additional_cooldown = min(300, cooldown_seconds * (2 ** (user_state.violation_count - 3)))
            user_state.cooldown_until += additional_cooldown
    
    def _refill_burst_tokens(self, user_state: UserRateState, rate_limit: RateLimit):
        """Refill burst tokens based on time elapsed."""
        current_time = time.time()
        time_since_last = current_time - user_state.last_request
        
        if time_since_last > 0:
            # Refill rate: 1 token per (window_seconds / max_requests)
            refill_rate = rate_limit.max_requests / rate_limit.window_seconds
            tokens_to_add = int(time_since_last * refill_rate)
            
            user_state.burst_tokens = min(
                rate_limit.burst_allowance,
                user_state.burst_tokens + tokens_to_add
            )
    
    async def check_rate_limit(self, user_id: int, limit_type: RateLimitType, 
                             cost: int = 1) -> Tuple[bool, Optional[str], float]:
        """Check if request is within rate limits.
        
        Returns:
            Tuple of (allowed, error_message, retry_after_seconds)
        """
        if not self.enabled:
            return True, None, 0
        
        rate_limit = self.get_rate_limit(limit_type, user_id)
        user_state = self.user_states[user_id][limit_type]
        current_time = time.time()
        
        # Check cooldown
        in_cooldown, cooldown_remaining = self._is_in_cooldown(user_state)
        if in_cooldown:
            metrics.record_rate_limit_hit('admin' if self.is_admin(user_id) else 'regular')
            return False, f"Rate limit exceeded. Try again in {int(cooldown_remaining)} seconds.", cooldown_remaining
        
        # Clean up old requests
        self._cleanup_old_requests(user_state, rate_limit.window_seconds)
        
        # Refill burst tokens
        self._refill_burst_tokens(user_state, rate_limit)
        
        # Check if we can use burst tokens
        if user_state.burst_tokens >= cost:
            user_state.burst_tokens -= cost
            user_state.last_request = current_time
            user_state.requests.append(current_time)
            return True, None, 0
        
        # Check regular rate limit
        if len(user_state.requests) + cost <= rate_limit.max_requests:
            # Add requests to the window
            for _ in range(cost):
                user_state.requests.append(current_time)
            user_state.last_request = current_time
            return True, None, 0
        
        # Rate limit exceeded
        self._apply_cooldown(user_state, rate_limit.cooldown_seconds)
        metrics.record_rate_limit_hit('admin' if self.is_admin(user_id) else 'regular')
        
        error_msg = (
            f"Rate limit exceeded for {limit_type.value}. "
            f"Max {rate_limit.max_requests} requests per {rate_limit.window_seconds} seconds. "
            f"Cooldown: {rate_limit.cooldown_seconds} seconds."
        )
        
        return False, error_msg, rate_limit.cooldown_seconds
    
    async def consume_rate_limit(self, user_id: int, limit_type: RateLimitType, cost: int = 1):
        """Consume rate limit or raise exception."""
        allowed, error_msg, retry_after = await self.check_rate_limit(user_id, limit_type, cost)
        
        if not allowed:
            raise RateLimitError(
                error_msg or "Rate limit exceeded",
                user_id=user_id,
                retry_after=int(retry_after)
            )
    
    def get_user_status(self, user_id: int, limit_type: RateLimitType) -> Dict[str, Any]:
        """Get current rate limit status for user."""
        rate_limit = self.get_rate_limit(limit_type, user_id)
        user_state = self.user_states[user_id][limit_type]
        current_time = time.time()
        
        # Clean up old requests
        self._cleanup_old_requests(user_state, rate_limit.window_seconds)
        
        # Check cooldown
        in_cooldown, cooldown_remaining = self._is_in_cooldown(user_state)
        
        # Refill burst tokens
        self._refill_burst_tokens(user_state, rate_limit)
        
        return {
            'limit_type': limit_type.value,
            'max_requests': rate_limit.max_requests,
            'window_seconds': rate_limit.window_seconds,
            'current_requests': len(user_state.requests),
            'remaining_requests': max(0, rate_limit.max_requests - len(user_state.requests)),
            'burst_tokens': user_state.burst_tokens,
            'max_burst_tokens': rate_limit.burst_allowance,
            'in_cooldown': in_cooldown,
            'cooldown_remaining': cooldown_remaining,
            'violation_count': user_state.violation_count,
            'window_reset_in': rate_limit.window_seconds - (current_time - (user_state.requests[0] if user_state.requests else current_time)),
            'is_admin': self.is_admin(user_id)
        }
    
    def get_all_user_status(self, user_id: int) -> Dict[str, Any]:
        """Get rate limit status for all limit types for a user."""
        return {
            limit_type.value: self.get_user_status(user_id, limit_type)
            for limit_type in RateLimitType
        }
    
    def reset_user_limits(self, user_id: int, limit_type: Optional[RateLimitType] = None):
        """Reset rate limits for a user."""
        if limit_type:
            if user_id in self.user_states and limit_type in self.user_states[user_id]:
                del self.user_states[user_id][limit_type]
        else:
            if user_id in self.user_states:
                del self.user_states[user_id]
        
        logger.info(f"Reset rate limits for user {user_id}", limit_type=limit_type.value if limit_type else "all")
    
    def update_rate_limit(self, limit_type: RateLimitType, **kwargs):
        """Update rate limit configuration."""
        current_limit = self.rate_limits[limit_type]
        
        # Update only provided parameters
        new_limit = RateLimit(
            max_requests=kwargs.get('max_requests', current_limit.max_requests),
            window_seconds=kwargs.get('window_seconds', current_limit.window_seconds),
            burst_allowance=kwargs.get('burst_allowance', current_limit.burst_allowance),
            cooldown_seconds=kwargs.get('cooldown_seconds', current_limit.cooldown_seconds)
        )
        
        self.rate_limits[limit_type] = new_limit
        logger.info(f"Updated rate limit for {limit_type.value}", **kwargs)
    
    async def _cleanup_task(self):
        """Periodic cleanup of old rate limit data."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                current_time = time.time()
                
                # Clean up old user states
                users_to_remove = []
                for user_id, limit_states in self.user_states.items():
                    limits_to_remove = []
                    
                    for limit_type, user_state in limit_states.items():
                        rate_limit = self.get_rate_limit(limit_type, user_id)
                        
                        # Clean up old requests
                        self._cleanup_old_requests(user_state, rate_limit.window_seconds)
                        
                        # Remove if no recent activity and not in cooldown
                        if (not user_state.requests and 
                            user_state.cooldown_until < current_time and
                            current_time - user_state.last_request > 3600):  # 1 hour
                            limits_to_remove.append(limit_type)
                    
                    # Remove empty limit states
                    for limit_type in limits_to_remove:
                        del limit_states[limit_type]
                    
                    # Remove user if no limit states
                    if not limit_states:
                        users_to_remove.append(user_id)
                
                # Remove empty user states
                for user_id in users_to_remove:
                    del self.user_states[user_id]
                
                logger.debug(f"Rate limiter cleanup completed. Active users: {len(self.user_states)}")
                
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")


# Decorator for rate limiting
def rate_limit(limit_type: RateLimitType, cost: int = 1):
    """Decorator to apply rate limiting to functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Try to extract user_id from various sources
            user_id = None
            
            # Check function arguments
            if args and hasattr(args[0], 'from_user'):
                user_id = args[0].from_user.id
            elif 'user_id' in kwargs:
                user_id = kwargs['user_id']
            elif 'message' in kwargs and hasattr(kwargs['message'], 'from_user'):
                user_id = kwargs['message'].from_user.id
            
            if user_id:
                await rate_limiter.consume_rate_limit(user_id, limit_type, cost)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Global rate limiter instance
rate_limiter = RateLimiter()