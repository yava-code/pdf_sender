import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

class BotLogger:
    """Logger for bot actions and events"""
    
    LOG_FILE = "bot_logs.json"
    
    @classmethod
    def _ensure_log_file(cls):
        """Ensure log file exists"""
        if not os.path.exists(cls.LOG_FILE):
            with open(cls.LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump({"logs": []}, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def _load_logs(cls) -> Dict[str, List[Dict]]:
        """Load logs from file"""
        cls._ensure_log_file()
        try:
            with open(cls.LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"logs": []}
    
    @classmethod
    def _save_logs(cls, data: Dict[str, List[Dict]]):
        """Save logs to file"""
        try:
            with open(cls.LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving logs: {e}")
    
    @classmethod
    def log_user_action(cls, user_id: int, username: str, action: str):
        """Log user action"""
        try:
            data = cls._load_logs()
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "type": "user_action",
                "user_id": user_id,
                "username": username,
                "action": action,
                "message": f"User {username} ({user_id}) performed action: {action}"
            }
            
            data["logs"].append(log_entry)
            
            # Keep only last 1000 logs
            if len(data["logs"]) > 1000:
                data["logs"] = data["logs"][-1000:]
            
            cls._save_logs(data)
            
        except Exception as e:
            logging.error(f"Error logging user action: {e}")
    
    @classmethod
    def log_error(cls, message: str, error: Exception):
        """Log error"""
        try:
            data = cls._load_logs()
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "type": "error",
                "message": message,
                "error": str(error),
                "error_type": type(error).__name__
            }
            
            data["logs"].append(log_entry)
            
            # Keep only last 1000 logs
            if len(data["logs"]) > 1000:
                data["logs"] = data["logs"][-1000:]
            
            cls._save_logs(data)
            
        except Exception as e:
            logging.error(f"Error logging error: {e}")
    
    @classmethod
    def log_system_event(cls, event: str, details: str = ""):
        """Log system event"""
        try:
            data = cls._load_logs()
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "type": "system_event",
                "event": event,
                "details": details,
                "message": f"System event: {event} - {details}"
            }
            
            data["logs"].append(log_entry)
            
            # Keep only last 1000 logs
            if len(data["logs"]) > 1000:
                data["logs"] = data["logs"][-1000:]
            
            cls._save_logs(data)
            
        except Exception as e:
            logging.error(f"Error logging system event: {e}")
    
    @classmethod
    def get_recent_logs(cls, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent log entries"""
        try:
            data = cls._load_logs()
            logs = data.get("logs", [])
            return logs[-count:] if logs else []
        except Exception as e:
            logging.error(f"Error getting recent logs: {e}")
            return []
    
    @classmethod
    def get_logs_by_level(cls, level: str, count: int = 50) -> List[Dict[str, Any]]:
        """Get logs by level (ERROR, WARNING, INFO, DEBUG)"""
        try:
            data = cls._load_logs()
            logs = data.get("logs", [])
            filtered_logs = [log for log in logs if log.get("level") == level.upper()]
            return filtered_logs[-count:] if filtered_logs else []
        except Exception as e:
            logging.error(f"Error getting logs by level: {e}")
            return []
    
    @classmethod
    def get_user_logs(cls, user_id: int, count: int = 50) -> List[Dict[str, Any]]:
        """Get logs for specific user"""
        try:
            data = cls._load_logs()
            logs = data.get("logs", [])
            user_logs = [log for log in logs if log.get("user_id") == user_id]
            return user_logs[-count:] if user_logs else []
        except Exception as e:
            logging.error(f"Error getting user logs: {e}")
            return []
    
    @classmethod
    def clear_logs(cls):
        """Clear all logs"""
        try:
            cls._save_logs({"logs": []})
            cls.log_system_event("logs_cleared", "All logs have been cleared")
        except Exception as e:
            logging.error(f"Error clearing logs: {e}")
    
    @classmethod
    def get_logs_stats(cls) -> Dict[str, Any]:
        """Get logs statistics"""
        try:
            data = cls._load_logs()
            logs = data.get("logs", [])
            
            stats = {
                "total_logs": len(logs),
                "error_count": len([log for log in logs if log.get("level") == "ERROR"]),
                "warning_count": len([log for log in logs if log.get("level") == "WARNING"]),
                "info_count": len([log for log in logs if log.get("level") == "INFO"]),
                "debug_count": len([log for log in logs if log.get("level") == "DEBUG"]),
                "user_actions": len([log for log in logs if log.get("type") == "user_action"]),
                "system_events": len([log for log in logs if log.get("type") == "system_event"])
            }
            
            if logs:
                stats["oldest_log"] = logs[0].get("timestamp", "Unknown")
                stats["newest_log"] = logs[-1].get("timestamp", "Unknown")
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting logs stats: {e}")
            return {}