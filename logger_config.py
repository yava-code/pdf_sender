import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

from config import Config


class BotLogger:
    """Настройка логирования для бота с ротацией файлов"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
    def setup_logging(self):
        """Настройка системы логирования"""
        # Создаем основной логгер
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Очищаем существующие обработчики
        logger.handlers.clear()
        
        # Форматтер для логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Файловый обработчик с ротацией
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "bot.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Отдельный файл для ошибок
        error_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        # Логгер для пользовательских действий
        user_logger = logging.getLogger('user_actions')
        user_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "user_actions.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        user_handler.setFormatter(formatter)
        user_logger.addHandler(user_handler)
        user_logger.setLevel(logging.INFO)
        
        return logger
    
    @staticmethod
    def log_user_action(user_id: int, username: str, action: str, details: str = ""):
        """Логирование действий пользователей"""
        user_logger = logging.getLogger('user_actions')
        user_logger.info(
            f"User {user_id} (@{username}) - {action} - {details}"
        )
    
    @staticmethod
    def log_error(error: Exception, context: str = ""):
        """Логирование ошибок с контекстом"""
        logger = logging.getLogger()
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    
    @staticmethod
    def get_recent_logs(count: int = 50):
        """Retrieves recent log entries from the log file"""
        log_file = Path("logs") / "bot.log"
        logs = []
        
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # Get the last lines
                recent_lines = lines[-count:] if len(lines) > count else lines
                
                for line in recent_lines:
                    line = line.strip()
                    if line:
                        # Parse the log line
                        parts = line.split(' - ', 3)
                        if len(parts) >= 4:
                            timestamp = parts[0]
                            name = parts[1]
                            level = parts[2]
                            message = parts[3]
                            
                            logs.append({
                                'timestamp': timestamp,
                                'name': name,
                                'level': level,
                                'message': message
                            })
                        else:
                            # If parsing fails, add as is
                            logs.append({
                                'timestamp': 'Unknown',
                                'name': 'Unknown',
                                'level': 'INFO',
                                'message': line
                            })
        except Exception as e:
            logging.error(f"Error reading log file: {e}")
        
        return logs
    
    @staticmethod
    def get_logs_by_level(level: str, count: int = 50):
        """Получить логи определенного уровня"""
        all_logs = BotLogger.get_recent_logs(count * 2)  # Берем больше, чтобы отфильтровать
        filtered_logs = [log for log in all_logs if log.get('level', '').upper() == level.upper()]
        return filtered_logs[-count:] if len(filtered_logs) > count else filtered_logs
    
    @staticmethod
    def clear_logs():
        """Очистить лог файлы"""
        log_dir = Path("logs")
        try:
            for log_file in log_dir.glob("*.log*"):
                if log_file.is_file():
                    log_file.unlink()
                    logging.info(f"Cleared log file: {log_file}")
        except Exception as e:
            logging.error(f"Error clearing logs: {e}")


# Инициализация логирования
def init_logging():
    """Инициализация системы логирования"""
    bot_logger = BotLogger()
    return bot_logger.setup_logging()