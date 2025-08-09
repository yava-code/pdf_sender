"""Metrics and monitoring system for PDF Sender Bot."""

import time
import psutil
from typing import Dict, Optional, Any
from functools import wraps
from contextlib import contextmanager
from prometheus_client import (
    Counter, Histogram, Gauge, Info, CollectorRegistry,
    generate_latest, CONTENT_TYPE_LATEST, start_http_server
)
import structlog
from .config import config
from .exceptions import PDFSenderError

logger = structlog.get_logger(__name__)

# Create custom registry for better control
registry = CollectorRegistry()

# Bot metrics
bot_info = Info('pdf_sender_bot_info', 'Bot information', registry=registry)
messages_total = Counter(
    'pdf_sender_messages_total',
    'Total number of messages processed',
    ['message_type', 'status'],
    registry=registry
)
commands_total = Counter(
    'pdf_sender_commands_total',
    'Total number of commands executed',
    ['command', 'status'],
    registry=registry
)
command_duration = Histogram(
    'pdf_sender_command_duration_seconds',
    'Time spent executing commands',
    ['command'],
    registry=registry
)

# File processing metrics
files_processed_total = Counter(
    'pdf_sender_files_processed_total',
    'Total number of files processed',
    ['file_type', 'status'],
    registry=registry
)
file_processing_duration = Histogram(
    'pdf_sender_file_processing_duration_seconds',
    'Time spent processing files',
    ['file_type'],
    registry=registry
)
file_size_bytes = Histogram(
    'pdf_sender_file_size_bytes',
    'Size of processed files in bytes',
    ['file_type'],
    buckets=[1024, 10240, 102400, 1048576, 10485760, 52428800, float('inf')],
    registry=registry
)

# PDF metrics
pdf_pages_sent_total = Counter(
    'pdf_sender_pdf_pages_sent_total',
    'Total number of PDF pages sent',
    ['user_type'],
    registry=registry
)
pdf_generation_duration = Histogram(
    'pdf_sender_pdf_generation_duration_seconds',
    'Time spent generating PDF pages',
    registry=registry
)

# User metrics
active_users = Gauge(
    'pdf_sender_active_users',
    'Number of active users',
    registry=registry
)
user_sessions_total = Counter(
    'pdf_sender_user_sessions_total',
    'Total number of user sessions',
    ['session_type'],
    registry=registry
)
user_errors_total = Counter(
    'pdf_sender_user_errors_total',
    'Total number of user errors',
    ['error_type'],
    registry=registry
)

# System metrics
system_memory_usage = Gauge(
    'pdf_sender_system_memory_usage_bytes',
    'System memory usage in bytes',
    ['type'],
    registry=registry
)
system_disk_usage = Gauge(
    'pdf_sender_system_disk_usage_bytes',
    'System disk usage in bytes',
    ['type', 'path'],
    registry=registry
)
system_cpu_usage = Gauge(
    'pdf_sender_system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=registry
)

# Database metrics
database_operations_total = Counter(
    'pdf_sender_database_operations_total',
    'Total number of database operations',
    ['operation', 'status'],
    registry=registry
)
database_operation_duration = Histogram(
    'pdf_sender_database_operation_duration_seconds',
    'Time spent on database operations',
    ['operation'],
    registry=registry
)
database_size_bytes = Gauge(
    'pdf_sender_database_size_bytes',
    'Database file size in bytes',
    registry=registry
)

# Scheduler metrics
scheduled_jobs_total = Counter(
    'pdf_sender_scheduled_jobs_total',
    'Total number of scheduled jobs',
    ['job_type', 'status'],
    registry=registry
)
job_execution_duration = Histogram(
    'pdf_sender_job_execution_duration_seconds',
    'Time spent executing scheduled jobs',
    ['job_type'],
    registry=registry
)

# Error metrics
errors_total = Counter(
    'pdf_sender_errors_total',
    'Total number of errors',
    ['error_type', 'component'],
    registry=registry
)

# Rate limiting metrics
rate_limit_hits_total = Counter(
    'pdf_sender_rate_limit_hits_total',
    'Total number of rate limit hits',
    ['user_type'],
    registry=registry
)


class MetricsCollector:
    """Centralized metrics collection and management."""
    
    def __init__(self):
        self.start_time = time.time()
        self._update_bot_info()
        
        # Start metrics server if enabled
        if config.enable_metrics:
            self.start_metrics_server()
    
    def _update_bot_info(self):
        """Update bot information metrics."""
        bot_info.info({
            'version': '1.0.0',
            'python_version': f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}",
            'start_time': str(int(self.start_time))
        })
    
    def start_metrics_server(self):
        """Start Prometheus metrics HTTP server."""
        try:
            start_http_server(config.metrics_port, registry=registry)
            logger.info(f"Metrics server started on port {config.metrics_port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
    
    def update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            system_memory_usage.labels(type='used').set(memory.used)
            system_memory_usage.labels(type='available').set(memory.available)
            system_memory_usage.labels(type='total').set(memory.total)
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Disk metrics
            disk = psutil.disk_usage('.')
            system_disk_usage.labels(type='used', path='.').set(disk.used)
            system_disk_usage.labels(type='free', path='.').set(disk.free)
            system_disk_usage.labels(type='total', path='.').set(disk.total)
            
        except Exception as e:
            logger.error(f"Failed to update system metrics: {e}")
    
    def record_message(self, message_type: str, status: str = 'success'):
        """Record message processing metrics."""
        messages_total.labels(message_type=message_type, status=status).inc()
    
    def record_command(self, command: str, status: str = 'success', duration: Optional[float] = None):
        """Record command execution metrics."""
        commands_total.labels(command=command, status=status).inc()
        if duration is not None:
            command_duration.labels(command=command).observe(duration)
    
    def record_file_processing(self, file_type: str, status: str = 'success', 
                             duration: Optional[float] = None, size: Optional[int] = None):
        """Record file processing metrics."""
        files_processed_total.labels(file_type=file_type, status=status).inc()
        if duration is not None:
            file_processing_duration.labels(file_type=file_type).observe(duration)
        if size is not None:
            file_size_bytes.labels(file_type=file_type).observe(size)
    
    def record_pdf_pages_sent(self, count: int, user_type: str = 'regular'):
        """Record PDF pages sent metrics."""
        pdf_pages_sent_total.labels(user_type=user_type).inc(count)
    
    def record_pdf_generation(self, duration: float):
        """Record PDF generation metrics."""
        pdf_generation_duration.observe(duration)
    
    def record_database_operation(self, operation: str, status: str = 'success', 
                                duration: Optional[float] = None):
        """Record database operation metrics."""
        database_operations_total.labels(operation=operation, status=status).inc()
        if duration is not None:
            database_operation_duration.labels(operation=operation).observe(duration)
    
    def record_scheduled_job(self, job_type: str, status: str = 'success', 
                           duration: Optional[float] = None):
        """Record scheduled job metrics."""
        scheduled_jobs_total.labels(job_type=job_type, status=status).inc()
        if duration is not None:
            job_execution_duration.labels(job_type=job_type).observe(duration)
    
    def record_error(self, error_type: str, component: str = 'general'):
        """Record error metrics."""
        errors_total.labels(error_type=error_type, component=component).inc()
    
    def record_rate_limit_hit(self, user_type: str = 'regular'):
        """Record rate limit hit metrics."""
        rate_limit_hits_total.labels(user_type=user_type).inc()
    
    def update_active_users(self, count: int):
        """Update active users count."""
        active_users.set(count)
    
    def record_user_session(self, session_type: str = 'new'):
        """Record user session metrics."""
        user_sessions_total.labels(session_type=session_type).inc()
    
    def record_user_error(self, error_type: str):
        """Record user error metrics."""
        user_errors_total.labels(error_type=error_type).inc()
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(registry)


# Global metrics collector instance
metrics = MetricsCollector()


def track_time(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator to track execution time of functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record based on metric type
                if 'command' in metric_name:
                    metrics.record_command(func.__name__, 'success', duration)
                elif 'file' in metric_name:
                    metrics.record_file_processing('unknown', 'success', duration)
                elif 'database' in metric_name:
                    metrics.record_database_operation(func.__name__, 'success', duration)
                elif 'job' in metric_name:
                    metrics.record_scheduled_job(func.__name__, 'success', duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error based on metric type
                if 'command' in metric_name:
                    metrics.record_command(func.__name__, 'error', duration)
                elif 'file' in metric_name:
                    metrics.record_file_processing('unknown', 'error', duration)
                elif 'database' in metric_name:
                    metrics.record_database_operation(func.__name__, 'error', duration)
                elif 'job' in metric_name:
                    metrics.record_scheduled_job(func.__name__, 'error', duration)
                
                # Record general error
                error_type = type(e).__name__
                if isinstance(e, PDFSenderError):
                    error_type = e.error_code or error_type
                metrics.record_error(error_type, metric_name)
                
                raise
        return wrapper
    return decorator


@contextmanager
def track_operation(operation_type: str, operation_name: str):
    """Context manager to track operation metrics."""
    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        
        if operation_type == 'command':
            metrics.record_command(operation_name, 'success', duration)
        elif operation_type == 'file':
            metrics.record_file_processing(operation_name, 'success', duration)
        elif operation_type == 'database':
            metrics.record_database_operation(operation_name, 'success', duration)
        elif operation_type == 'job':
            metrics.record_scheduled_job(operation_name, 'success', duration)
            
    except Exception as e:
        duration = time.time() - start_time
        
        if operation_type == 'command':
            metrics.record_command(operation_name, 'error', duration)
        elif operation_type == 'file':
            metrics.record_file_processing(operation_name, 'error', duration)
        elif operation_type == 'database':
            metrics.record_database_operation(operation_name, 'error', duration)
        elif operation_type == 'job':
            metrics.record_scheduled_job(operation_name, 'error', duration)
        
        # Record general error
        error_type = type(e).__name__
        if isinstance(e, PDFSenderError):
            error_type = e.error_code or error_type
        metrics.record_error(error_type, operation_type)
        
        raise


def get_health_status() -> Dict[str, Any]:
    """Get application health status."""
    try:
        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Calculate health scores
        memory_health = 'healthy' if memory.percent < 80 else 'warning' if memory.percent < 95 else 'critical'
        disk_health = 'healthy' if disk.percent < 80 else 'warning' if disk.percent < 95 else 'critical'
        cpu_health = 'healthy' if cpu_percent < 80 else 'warning' if cpu_percent < 95 else 'critical'
        
        # Overall health
        health_scores = [memory_health, disk_health, cpu_health]
        if 'critical' in health_scores:
            overall_health = 'critical'
        elif 'warning' in health_scores:
            overall_health = 'warning'
        else:
            overall_health = 'healthy'
        
        return {
            'status': overall_health,
            'timestamp': time.time(),
            'uptime': time.time() - metrics.start_time,
            'system': {
                'memory': {
                    'status': memory_health,
                    'used_percent': memory.percent,
                    'used_bytes': memory.used,
                    'total_bytes': memory.total
                },
                'disk': {
                    'status': disk_health,
                    'used_percent': (disk.used / disk.total) * 100,
                    'used_bytes': disk.used,
                    'total_bytes': disk.total
                },
                'cpu': {
                    'status': cpu_health,
                    'usage_percent': cpu_percent
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get health status: {e}")
        return {
            'status': 'unknown',
            'error': str(e),
            'timestamp': time.time()
        }