import json
import logging
from datetime import datetime, time
from pathlib import Path
from typing import Dict, Optional, Any

from config import Config

logger = logging.getLogger(__name__)


class UserSettings:
    """Manages personal user settings"""
    
    def __init__(self, settings_file: str = "user_settings.json"):
        self.settings_file = Path(settings_file)
        self.settings: Dict[str, Dict[str, Any]] = {}
        self.load_settings()
    
    def load_settings(self):
        """Loads settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logger.info(f"Settings loaded for {len(self.settings)} users")
            else:
                self.settings = {}
                logger.info("New settings file created")
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self.settings = {}
    
    def save_settings(self):
        """Saves settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info("Settings saved")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Gets user settings"""
        user_key = str(user_id)
        if user_key not in self.settings:
            # Create default settings
            self.settings[user_key] = {
                "pages_per_send": Config.PAGES_PER_SEND,
                "schedule_time": Config.SCHEDULE_TIME,
                "interval_hours": Config.INTERVAL_HOURS,
                "auto_send_enabled": True,
                "timezone": "UTC",
                "image_quality": Config.IMAGE_QUALITY,
                "notifications_enabled": True,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self.save_settings()
        
        return self.settings[user_key].copy()
    
    def update_user_setting(self, user_id: int, setting_name: str, value: Any) -> bool:
        """Updates a specific user setting"""
        try:
            user_key = str(user_id)
            user_settings = self.get_user_settings(user_id)
            
            # Validate values
            if not self._validate_setting(setting_name, value):
                return False
            
            user_settings[setting_name] = value
            user_settings["last_updated"] = datetime.now().isoformat()
            
            self.settings[user_key] = user_settings
            self.save_settings()
            
            logger.info(f"Setting {setting_name} updated for user {user_id}: {value}")
            return True
        except Exception as e:
            logger.error(f"Error updating setting: {e}")
            return False
    
    def _validate_setting(self, setting_name: str, value: Any) -> bool:
        """Validates setting values"""
        validators = {
            "pages_per_send": lambda x: isinstance(x, int) and 1 <= x <= 10,
            "schedule_time": lambda x: self._validate_time_format(x),
            "interval_hours": lambda x: isinstance(x, int) and 1 <= x <= 24,
            "auto_send_enabled": lambda x: isinstance(x, bool),
            "timezone": lambda x: isinstance(x, str) and len(x) <= 50,
            "image_quality": lambda x: isinstance(x, int) and 1 <= x <= 100,
            "notifications_enabled": lambda x: isinstance(x, bool)
        }
        
        validator = validators.get(setting_name);
        if validator:
            return validator(value)
        return False
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validates HH:MM time format"""
        try:
            time.fromisoformat(time_str)
            return True
        except ValueError:
            return False
    
    def get_all_users_with_auto_send(self) -> list:
        """Gets all users with auto-send enabled"""
        users = []
        for user_id, settings in self.settings.items():
            if settings.get("auto_send_enabled", True):
                users.append({
                    "user_id": int(user_id),
                    "schedule_time": settings.get("schedule_time", Config.SCHEDULE_TIME),
                    "pages_per_send": settings.get("pages_per_send", Config.PAGES_PER_SEND),
                    "interval_hours": settings.get("interval_hours", Config.INTERVAL_HOURS)
                })
        return users
    
    def delete_user_settings(self, user_id: int) -> bool:
        """Deletes user settings"""
        try:
            user_key = str(user_id)
            if user_key in self.settings:
                del self.settings[user_key]
                self.save_settings()
                logger.info(f"User settings deleted for {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting settings: {e}")
            return False
    
    def get_settings_summary(self, user_id: int) -> str:
        """Gets a brief summary of user settings"""
        settings = self.get_user_settings(user_id)
        
        status = "🟢 Enabled" if settings["auto_send_enabled"] else "🔴 Disabled"
        
        summary = f"""📋 **Your settings:**

📄 Pages per send: {settings['pages_per_send']}
⏰ Send time: {settings['schedule_time']}
🔄 Interval (hours): {settings['interval_hours']}
🤖 Auto-send: {status}
🖼️ Image quality: {settings['image_quality']}
%🔔 Notifications: {'🟢 Enabled' if settings['notifications_enabled'] else '🔴 Disabled'}

📅 Last updated: {settings['last_updated'][:19].replace('T', ' ')}"""
        
        return summary