from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Dict, Any


class BotKeyboards:
    """Class for creating inline bot keyboards"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main bot menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📄 Next pages", callback_data="next_pages"),
            InlineKeyboardButton(text="📍 Current page", callback_data="current_page")
        )
        builder.row(
            InlineKeyboardButton(text="🔍 Go to page", callback_data="goto_page"),
            InlineKeyboardButton(text="📊 Statistics", callback_data="stats")
        )
        builder.row(
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard"),
            InlineKeyboardButton(text="🎯 Achievements", callback_data="achievements")
        )
        builder.row(
            InlineKeyboardButton(text="⚙️ Settings", callback_data="settings_menu"),
            InlineKeyboardButton(text="📚 Manage books", callback_data="books_menu")
        )
        builder.row(
            InlineKeyboardButton(text="ℹ️ Help", callback_data="help"),
            InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def reading_progress_menu(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
        """Reading progress menu with 'I Read' button"""
        builder = InlineKeyboardBuilder()
        
        # Progress bar
        progress = (current_page / total_pages) * 100 if total_pages > 0 else 0
        progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
        
        builder.row(
            InlineKeyboardButton(
                text=f"✅ I Read This Page (+5 pts)", 
                callback_data="mark_page_read"
            )
        )
        builder.row(
            InlineKeyboardButton(text="📄 Next Page", callback_data="next_pages"),
            InlineKeyboardButton(text="📊 My Stats", callback_data="my_stats")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def leaderboard_menu() -> InlineKeyboardMarkup:
        """Leaderboard menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🏆 Top Points", callback_data="leaderboard_points"),
            InlineKeyboardButton(text="📚 Most Pages", callback_data="leaderboard_pages")
        )
        builder.row(
            InlineKeyboardButton(text="🔥 Longest Streak", callback_data="leaderboard_streak"),
            InlineKeyboardButton(text="📖 Books Completed", callback_data="leaderboard_books")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Refresh", callback_data="leaderboard")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def achievements_menu() -> InlineKeyboardMarkup:
        """Achievements menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🎯 My Achievements", callback_data="my_achievements"),
            InlineKeyboardButton(text="📋 All Achievements", callback_data="all_achievements")
        )
        builder.row(
            InlineKeyboardButton(text="🏅 Recent Unlocks", callback_data="recent_achievements")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """Enhanced statistics menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📊 Reading Stats", callback_data="reading_stats"),
            InlineKeyboardButton(text="🎮 Game Stats", callback_data="game_stats")
        )
        builder.row(
            InlineKeyboardButton(text="📈 Progress Chart", callback_data="progress_chart"),
            InlineKeyboardButton(text="🏆 Achievements", callback_data="achievements")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Back to Menu", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def level_up_menu(new_level: int) -> InlineKeyboardMarkup:
        """Level up celebration menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🎉 Awesome!", callback_data="main_menu")
        )
        builder.row(
            InlineKeyboardButton(text="📊 View Stats", callback_data="my_stats"),
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def achievement_unlocked_menu(achievement_name: str) -> InlineKeyboardMarkup:
        """Achievement unlocked menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="🎯 View All Achievements", callback_data="my_achievements")
        )
        builder.row(
            InlineKeyboardButton(text="📊 My Stats", callback_data="my_stats"),
            InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Continue Reading", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Settings menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📄 Pages per send", callback_data="set_pages_per_send"),
            InlineKeyboardButton(text="⏰ Send time", callback_data="set_schedule_time")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Send interval", callback_data="set_interval_hours"),
            InlineKeyboardButton(text="🖼️ Image quality", callback_data="set_image_quality")
        )
        builder.row(
            InlineKeyboardButton(text="🤖 Auto-send", callback_data="toggle_auto_send"),
            InlineKeyboardButton(text="🔔 Notifications", callback_data="toggle_notifications")
        )
        builder.row(
            InlineKeyboardButton(text="📋 Show settings", callback_data="show_settings")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def pages_per_send_menu() -> InlineKeyboardMarkup:
        """Menu for selecting the number of pages"""
        builder = InlineKeyboardBuilder()
        
        # Buttons with numbers from 1 to 10
        for i in range(1, 11):
            builder.add(InlineKeyboardButton(
                text=str(i), 
                callback_data=f"pages_per_send_{i}"
            ))
        
        # Arrange 5 buttons per row
        builder.adjust(5, 5)
        
        builder.row(
            InlineKeyboardButton(text="🔙 Back to settings", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def schedule_time_menu() -> InlineKeyboardMarkup:
        """Menu for selecting send time"""
        builder = InlineKeyboardBuilder()
        
        # Popular times
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
        
        # Arrange 3 buttons per row
        builder.adjust(3)
        
        builder.row(
            InlineKeyboardButton(text="✏️ Enter custom time", callback_data="custom_schedule_time")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Back to settings", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def interval_hours_menu() -> InlineKeyboardMarkup:
        """Menu for selecting interval in hours"""
        builder = InlineKeyboardBuilder()
        
        intervals = [
            ("1 hour", 1), ("2 hours", 2), ("3 hours", 3),
            ("4 hours", 4), ("6 hours", 6), ("8 hours", 8),
            ("12 hours", 12), ("24 hours", 24)
        ]
        
        for text, hours in intervals:
            builder.add(InlineKeyboardButton(
                text=text, 
                callback_data=f"interval_hours_{hours}"
            ))
        
        builder.adjust(2)
        
        builder.row(
            InlineKeyboardButton(text="🔙 Back to settings", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def image_quality_menu() -> InlineKeyboardMarkup:
        """Menu for selecting image quality"""
        builder = InlineKeyboardBuilder()
        
        qualities = [
            ("🔴 Low (50%)", 50),
            ("🟡 Medium (70%)", 70),
            ("🟢 Good (85%)", 85),
            ("🔵 High (95%)", 95),
            ("⭐ Maximum (100%)", 100)
        ]
        
        for text, quality in qualities:
            builder.add(InlineKeyboardButton(
                text=text, 
                callback_data=f"image_quality_{quality}"
            ))
        
        builder.adjust(1)
        
        builder.row(
            InlineKeyboardButton(text="🔙 Back to settings", callback_data="settings_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def books_menu() -> InlineKeyboardMarkup:
        """Book management menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📤 Upload book", callback_data="upload_book"),
            InlineKeyboardButton(text="📚 Book list", callback_data="list_books")
        )
        builder.row(
            InlineKeyboardButton(text="🔄 Change book", callback_data="change_book"),
            InlineKeyboardButton(text="📊 Reading progress", callback_data="reading_progress")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def confirmation_menu(action: str) -> InlineKeyboardMarkup:
        """Action confirmation menu"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="✅ Yes", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ No", callback_data="cancel_action")
        )
        
        return builder.as_markup()
    
    @staticmethod
    def navigation_menu(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
        """Page navigation menu"""
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
    def status_menu() -> InlineKeyboardMarkup:
        """Меню статуса чтения"""
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="📄 Следующие страницы", callback_data="next_pages"),
            InlineKeyboardButton(text="🔄 Обновить статус", callback_data="status")
        )
        builder.row(
            InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
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