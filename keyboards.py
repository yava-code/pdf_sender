from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Dict, Any


class BotKeyboards:
    """Класс для создания inline клавиатур бота"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Главное меню бота"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📄 Следующие страницы", callback_data="next_pages"),
            InlineKeyboardButton(text="📍 Текущая страница", callback_data="current_page")
        )
        builder.row(
            InlineKeyboardButton(text="🔍 Перейти к странице", callback_data="goto_page"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
        )
        builder.row(
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings_menu"),
            InlineKeyboardButton(text="📚 Управление книгами", callback_data="books_menu")
        )
        builder.row(
            InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"),
            InlineKeyboardButton(text="🔧 Админ панель", callback_data="admin_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Меню настроек"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📄 Страниц за раз", callback_data="set_pages_per_send"),
            InlineKeyboardButton(text="⏰ Время отправки", callback_data="set_schedule_time")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Интервал отправки", callback_data="set_interval_hours"),
            InlineKeyboardButton(text="🖼️ Качество изображений", callback_data="set_image_quality")
        )
        builder.row(
            InlineKeyboardButton(text="🤖 Автоотправка", callback_data="toggle_auto_send"),
            InlineKeyboardButton(text="🔔 Уведомления", callback_data="toggle_notifications")
        )
        builder.row(
            InlineKeyboardButton(text="📋 Показать настройки", callback_data="show_settings")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def pages_per_send_menu() -> InlineKeyboardMarkup:
        """Меню выбора количества страниц"""
        builder = InlineKeyboardBuilder()
        
        # Кнопки с числами от 1 до 10
        for i in range(1, 11):
            builder.add(InlineKeyboardButton(
                text=str(i), 
                callback_data=f"pages_per_send_{i}"
            ))
        
        # Размещаем по 5 кнопок в ряд
        builder.adjust(5, 5)
        
        builder.row(
            InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def schedule_time_menu() -> InlineKeyboardMarkup:
        """Меню выбора времени отправки"""
        builder = InlineKeyboardBuilder()
        
        # Популярные времена
        times = [
            ("🌅 06:00", "06:00"), ("🌄 07:00", "07:00"), ("☀️ 08:00", "08:00"),
            ("🌞 09:00", "09:00"), ("🕙 10:00", "10:00"), ("🕚 11:00", "11:00"),
            ("🕛 12:00", "12:00"), ("🕐 13:00", "13:00"), ("🕑 14:00", "14:00"),
            ("🕒 15:00", "15:00"), ("🕓 16:00", "16:00"), ("🕔 17:00", "17:00"),
            ("🕕 18:00", "18:00"), ("🕖 19:00", "19:00"), ("🕗 20:00", "20:00"),
            ("🕘 21:00", "21:00"), ("🕙 22:00", "22:00"), ("🕚 23:00", "23:00")
        ]
        
        for text, time_val in times:
            builder.add(InlineKeyboardButton(
                text=text, 
                callback_data=f"schedule_time_{time_val}"
            ))
        
        # Размещаем по 3 кнопки в ряд
        builder.adjust(3)
        
        builder.row(
            InlineKeyboardButton(text="✏️ Ввести свое время", callback_data="custom_schedule_time")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def interval_hours_menu() -> InlineKeyboardMarkup:
        """Меню выбора интервала в часах"""
        builder = InlineKeyboardBuilder()
        
        intervals = [
            ("1 час", 1), ("2 часа", 2), ("3 часа", 3),
            ("4 часа", 4), ("6 часов", 6), ("8 часов", 8),
            ("12 часов", 12), ("24 часа", 24)
        ]
        
        for text, hours in intervals:
            builder.add(InlineKeyboardButton(
                text=text, 
                callback_data=f"interval_hours_{hours}"
            ))
        
        builder.adjust(2)
        
        builder.row(
            InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def image_quality_menu() -> InlineKeyboardMarkup:
        """Меню выбора качества изображений"""
        builder = InlineKeyboardBuilder()
        
        qualities = [
            ("🔴 Низкое (50%)", 50),
            ("🟡 Среднее (70%)", 70),
            ("🟢 Хорошее (85%)", 85),
            ("🔵 Высокое (95%)", 95),
            ("⭐ Максимальное (100%)", 100)
        ]
        
        for text, quality in qualities:
            builder.add(InlineKeyboardButton(
                text=text, 
                callback_data=f"image_quality_{quality}"
            ))
        
        builder.adjust(1)
        
        builder.row(
            InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def books_menu() -> InlineKeyboardMarkup:
        """Меню управления книгами"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📤 Загрузить книгу", callback_data="upload_book"),
            InlineKeyboardButton(text="📚 Список книг", callback_data="list_books")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Сменить книгу", callback_data="change_book"),
            InlineKeyboardButton(text="📊 Прогресс чтения", callback_data="reading_progress")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def confirmation_menu(action: str) -> InlineKeyboardMarkup:
        """Меню подтверждения действия"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel_action")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def navigation_menu(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
        """Меню навигации по страницам"""
        builder = InlineKeyboardBuilder()
        
        # Кнопки навигации
        nav_buttons = []
        
        if current_page > 1:
            nav_buttons.append(InlineKeyboardButton(text="⏮️ Первая", callback_data="goto_page_1"))
            nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"goto_page_{current_page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(
            text=f"📄 {current_page}/{total_pages}", 
            callback_data="current_page_info"
        ))
        
        if current_page < total_pages:
            nav_buttons.append(InlineKeyboardButton(text="▶️ Вперед", callback_data=f"goto_page_{current_page+1}"))
            nav_buttons.append(InlineKeyboardButton(text="⏭️ Последняя", callback_data=f"goto_page_{total_pages}"))
        
        # Добавляем кнопки навигации
        for button in nav_buttons:
            builder.add(button)
        
        builder.adjust(2 if len(nav_buttons) <= 4 else 3)
        
        # Дополнительные действия
        builder.row(
            InlineKeyboardButton(text="🔍 Перейти к странице", callback_data="goto_page"),
            InlineKeyboardButton(text="📄 Следующие страницы", callback_data="next_pages")
        )
        
        builder.row(
            InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def toggle_button(setting_name: str, current_value: bool) -> InlineKeyboardMarkup:
        """Кнопка переключения настройки"""
        builder = InlineKeyboardBuilder()
        
        status_text = "🟢 Включено" if current_value else "🔴 Выключено"
        action = "disable" if current_value else "enable"
        
        builder.row(
            InlineKeyboardButton(
                text=f"{status_text} (нажмите для изменения)", 
                callback_data=f"toggle_{setting_name}_{action}"
            )
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Назад к настройкам", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Меню администратора"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="🖥️ Система", callback_data="admin_system")
        )
        builder.row(
            InlineKeyboardButton(text="📝 Логи", callback_data="admin_logs"),
            InlineKeyboardButton(text="📦 Backup", callback_data="admin_backup")
        )
        builder.row(
            InlineKeyboardButton(text="🧹 Очистка", callback_data="admin_cleanup"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def users_management_menu() -> InlineKeyboardMarkup:
        """Меню управления пользователями"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📊 Статистика", callback_data="users_stats"),
            InlineKeyboardButton(text="👤 Список", callback_data="users_list")
        )
        builder.row(
            InlineKeyboardButton(text="🔍 Поиск", callback_data="users_search"),
            InlineKeyboardButton(text="📈 Активность", callback_data="users_activity")
        )
        builder.row(
            InlineKeyboardButton(text="🚫 Заблокированные", callback_data="users_blocked"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="users_settings")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Админ панель", callback_data="admin_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def system_menu() -> InlineKeyboardMarkup:
        """Меню системы"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🔄 Обновить", callback_data="system_refresh"),
            InlineKeyboardButton(text="📊 Мониторинг", callback_data="system_monitoring")
        )
        builder.row(
            InlineKeyboardButton(text="🗂️ Хранилище", callback_data="system_storage"),
            InlineKeyboardButton(text="⚡ Производительность", callback_data="system_performance")
        )
        builder.row(
            InlineKeyboardButton(text="🔧 Конфигурация", callback_data="system_config"),
            InlineKeyboardButton(text="🔄 Перезапуск", callback_data="system_restart")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Админ панель", callback_data="admin_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def logs_menu() -> InlineKeyboardMarkup:
        """Меню логов"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🔄 Обновить", callback_data="logs_refresh"),
            InlineKeyboardButton(text="📄 Полные логи", callback_data="logs_full")
        )
        builder.row(
            InlineKeyboardButton(text="🔴 Ошибки", callback_data="logs_errors"),
            InlineKeyboardButton(text="🟡 Предупреждения", callback_data="logs_warnings")
        )
        builder.row(
            InlineKeyboardButton(text="📊 Статистика", callback_data="logs_stats"),
            InlineKeyboardButton(text="🗑️ Очистить", callback_data="logs_clear")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Админ панель", callback_data="admin_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def backup_menu() -> InlineKeyboardMarkup:
        """Меню резервного копирования"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📦 Создать backup", callback_data="backup_create"),
            InlineKeyboardButton(text="📋 Список backup'ов", callback_data="backup_list")
        )
        builder.row(
            InlineKeyboardButton(text="📥 Восстановить", callback_data="backup_restore"),
            InlineKeyboardButton(text="🗑️ Удалить старые", callback_data="backup_cleanup")
        )
        builder.row(
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="backup_settings"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="backup_stats")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Админ панель", callback_data="admin_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def cleanup_menu() -> InlineKeyboardMarkup:
        """Меню очистки"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🧹 Запустить очистку", callback_data="cleanup_run"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="cleanup_stats")
        )
        builder.row(
            InlineKeyboardButton(text="🖼️ Изображения", callback_data="cleanup_images"),
            InlineKeyboardButton(text="📁 Загрузки", callback_data="cleanup_uploads")
        )
        builder.row(
            InlineKeyboardButton(text="🗑️ Логи", callback_data="cleanup_logs"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="cleanup_settings")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Админ панель", callback_data="admin_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def page_navigation() -> InlineKeyboardMarkup:
        """Простая навигационная клавиатура"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        )
        
        return builder.as_markup()