import json
import logging
from datetime import datetime, time
from pathlib import Path
from typing import Any, Dict, Optional

from config import Config

logger = logging.getLogger(__name__)


class UserSettings:
    """Управление персональными настройками пользователей"""

    def __init__(self, settings_file: str = "user_settings.json"):
        self.settings_file = Path(settings_file)
        self.settings: Dict[str, Dict[str, Any]] = {}
        self.load_settings()

    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
                logger.info(
                    f"Загружены настройки для {len(self.settings)} пользователей"
                )
            else:
                self.settings = {}
                logger.info("Создан новый файл настроек")
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
            self.settings = {}

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info("Настройки сохранены")
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")

    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Получение настроек пользователя"""
        user_key = str(user_id)
        if user_key not in self.settings:
            # Создаем настройки по умолчанию
            self.settings[user_key] = {
                "pages_per_send": Config.PAGES_PER_SEND,
                "schedule_time": Config.SCHEDULE_TIME,
                "interval_hours": Config.INTERVAL_HOURS,
                "auto_send_enabled": True,
                "timezone": "UTC",
                "image_quality": Config.IMAGE_QUALITY,
                "notifications_enabled": True,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            }
            self.save_settings()

        return self.settings[user_key].copy()

    def update_user_setting(self, user_id: int, setting_name: str, value: Any) -> bool:
        """Обновление конкретной настройки пользователя"""
        try:
            user_key = str(user_id)
            user_settings = self.get_user_settings(user_id)

            # Валидация значений
            if not self._validate_setting(setting_name, value):
                return False

            user_settings[setting_name] = value
            user_settings["last_updated"] = datetime.now().isoformat()

            self.settings[user_key] = user_settings
            self.save_settings()

            logger.info(
                f"Обновлена настройка {setting_name} для "
                f"пользователя {user_id}: {value}"
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления настройки: {e}")
            return False

    def _validate_setting(self, setting_name: str, value: Any) -> bool:
        """Валидация значений настроек"""
        validators = {
            "pages_per_send": lambda x: isinstance(x, int) and 1 <= x <= 10,
            "schedule_time": lambda x: self._validate_time_format(x),
            "interval_hours": lambda x: isinstance(x, int) and 1 <= x <= 24,
            "auto_send_enabled": lambda x: isinstance(x, bool),
            "timezone": lambda x: isinstance(x, str) and len(x) <= 50,
            "image_quality": lambda x: isinstance(x, int) and 1 <= x <= 100,
            "notifications_enabled": lambda x: isinstance(x, bool),
        }

        validator = validators.get(setting_name)
        if validator:
            return validator(value)
        return False

    def _validate_time_format(self, time_str: str) -> bool:
        """Валидация формата времени HH:MM"""
        try:
            time.fromisoformat(time_str)
            return True
        except ValueError:
            return False

    def get_all_users_with_auto_send(self) -> list:
        """Получение всех пользователей с включенной автоотправкой"""
        users = []
        for user_id, settings in self.settings.items():
            if settings.get("auto_send_enabled", True):
                users.append(
                    {
                        "user_id": int(user_id),
                        "schedule_time": settings.get(
                            "schedule_time", Config.SCHEDULE_TIME
                        ),
                        "pages_per_send": settings.get(
                            "pages_per_send", Config.PAGES_PER_SEND
                        ),
                        "interval_hours": settings.get(
                            "interval_hours", Config.INTERVAL_HOURS
                        ),
                    }
                )
        return users

    def delete_user_settings(self, user_id: int) -> bool:
        """Удаление настроек пользователя"""
        try:
            user_key = str(user_id)
            if user_key in self.settings:
                del self.settings[user_key]
                self.save_settings()
                logger.info(f"Удалены настройки пользователя {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка удаления настроек: {e}")
            return False

    def get_settings_summary(self, user_id: int) -> str:
        """Получение краткой сводки настроек пользователя"""
        settings = self.get_user_settings(user_id)

        status = "🟢 Включена" if settings["auto_send_enabled"] else "🔴 Выключена"

        summary = f"""📋 **Ваши настройки:**

📄 Страниц за раз: {settings['pages_per_send']}
⏰ Время отправки: {settings['schedule_time']}
🔄 Интервал (часы): {settings['interval_hours']}
🤖 Автоотправка: {status}
🖼️ Качество изображений: {settings['image_quality']}%
🔔 Уведомления: {'🟢 Включены' if settings['notifications_enabled'] else '🔴 Выключены'}

📅 Последнее обновление: {settings['last_updated'][:19].replace('T', ' ')}"""

        return summary
