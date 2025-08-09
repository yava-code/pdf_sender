import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import TYPE_CHECKING

from keyboards import BotKeyboards
from user_settings import UserSettings
from logger_config import BotLogger

if TYPE_CHECKING:
    from main import PDFSenderBot

logger = logging.getLogger(__name__)


class SettingsStates(StatesGroup):
    """States for setting parameters"""
    waiting_for_custom_time = State()
    waiting_for_page_number = State()


class CallbackHandler:
    """Handles callback queries from inline keyboards"""
    
    def __init__(self, bot_instance: 'PDFSenderBot'):
        self.bot = bot_instance
        self.user_settings = UserSettings()
        self.keyboards = BotKeyboards()
    
    async def handle_callback(self, callback: types.CallbackQuery, state: FSMContext):
        """Main handler for callback queries"""
        try:
            data = callback.data
            user_id = callback.from_user.id
            username = callback.from_user.username or "unknown"
            
            # Log user action
            BotLogger.log_user_action(user_id, username, f"callback: {data}")
            
            # Route callback queries
            if data == "main_menu":
                await self._show_main_menu(callback)
            elif data == "settings_menu":
                await self._show_settings_menu(callback)
            elif data == "show_settings":
                await self._show_user_settings(callback)
            elif data == "set_pages_per_send":
                await self._show_pages_per_send_menu(callback)
            elif data.startswith("pages_per_send_"):
                await self._set_pages_per_send(callback, data)
            elif data == "set_schedule_time":
                await self._show_schedule_time_menu(callback)
            elif data.startswith("schedule_time_"):
                await self._set_schedule_time(callback, data)
            elif data == "custom_schedule_time":
                await self._request_custom_time(callback, state)
            elif data == "set_interval_hours":
                await self._show_interval_hours_menu(callback)
            elif data.startswith("interval_hours_"):
                await self._set_interval_hours(callback, data)
            elif data == "set_image_quality":
                await self._show_image_quality_menu(callback)
            elif data.startswith("image_quality_"):
                await self._set_image_quality(callback, data)
            elif data == "toggle_auto_send":
                await self._toggle_auto_send(callback)
            elif data == "toggle_notifications":
                await self._toggle_notifications(callback)
            elif data == "books_menu":
                await self._show_books_menu(callback)
            elif data == "next_pages":
                await self._send_next_pages(callback)
            elif data == "current_page":
                await self._show_current_page(callback)
            elif data == "goto_page":
                await self._request_page_number(callback, state)
            elif data.startswith("goto_page_"):
                await self._goto_specific_page(callback, data)
            elif data == "stats":
                await self._show_stats(callback)
            elif data == "help":
                await self._show_help(callback)
            # Gamification callbacks
            elif data == "leaderboard":
                await self._show_leaderboard(callback)
            elif data == "achievements":
                await self._show_achievements(callback)
            elif data == "mark_page_read":
                await self._mark_page_read(callback)
            # Administrative callbacks
            elif data == "stats":
                await self._show_stats(callback)
            elif data == "admin_menu":
                await self._show_admin_menu(callback)
            elif data == "admin_users":
                await self._handle_admin_users(callback)
            elif data == "admin_system":
                await self._handle_admin_system(callback)
            elif data == "admin_logs":
                await self._handle_admin_logs(callback)
            elif data == "admin_backup":
                await self._handle_admin_backup(callback)
            elif data == "admin_cleanup":
                await self._handle_admin_cleanup(callback)
            elif data == "system_refresh":
                await self._handle_system_refresh(callback)
            elif data == "logs_refresh":
                await self._handle_logs_refresh(callback)
            elif data == "backup_create":
                await self._handle_backup_create(callback)
            elif data == "cleanup_run":
                await self._handle_cleanup_run(callback)
            else:
                await callback.answer("Unknown command", show_alert=True)
            
        except Exception as e:
            logger.error(f"Error processing callback {callback.data}: {e}")
            await callback.answer("An error occurred. Please try again.", show_alert=True)
    
    async def _show_main_menu(self, callback: types.CallbackQuery):
        """Show main menu"""
        await callback.message.edit_text(
            "🏠 **Main Menu**\n\nSelect an action:",
            reply_markup=self.keyboards.main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _show_admin_menu(self, callback: types.CallbackQuery):
        """Show admin menu"""
        admin_text = (
            "🔧 **Admin Panel** 🔧\n\n"
            "📊 **Available commands:**\n"
            "/users - User management\n"
            "/system - System information\n"
            "/logs - View logs\n"
            "/backup - Backup\n"
            "/cleanup - Clean up files\n\n"
            "⚙️ **Quick actions:**"
        )
        
        await callback.message.edit_text(
            admin_text,
            reply_markup=self.keyboards.admin_menu(),
            parse_mode="Markdown"
        )
    
    async def _handle_admin_users(self, callback: types.CallbackQuery):
        """Handle user management button"""
        await self.bot.users_command(callback.message)
    
    async def _handle_admin_system(self, callback: types.CallbackQuery):
        """Handle system information button"""
        await self.bot.system_command(callback.message)
    
    async def _handle_admin_logs(self, callback: types.CallbackQuery):
        """Handle view logs button"""
        await self.bot.logs_command(callback.message)
    
    async def _handle_admin_backup(self, callback: types.CallbackQuery):
        """Handle backup button"""
        await self.bot.backup_command(callback.message)
    
    async def _handle_admin_cleanup(self, callback: types.CallbackQuery):
        """Handle cleanup button"""
        await self.bot.cleanup_command(callback.message)
    
    async def _handle_system_refresh(self, callback: types.CallbackQuery):
        """Refresh system information"""
        await self.bot.system_command(callback.message)
    
    async def _handle_logs_refresh(self, callback: types.CallbackQuery):
        """Refresh logs"""
        await self.bot.logs_command(callback.message)
    
    async def _handle_backup_create(self, callback: types.CallbackQuery):
        """Create backup"""
        await self.bot.backup_command(callback.message)
    
    async def _handle_cleanup_run(self, callback: types.CallbackQuery):
        """Run cleanup"""
        await self.bot.cleanup_command(callback.message)
    
    async def _show_settings_menu(self, callback: types.CallbackQuery):
        """Show settings menu"""
        await callback.message.edit_text(
            "⚙️ **Bot Settings**\n\nSelect a parameter to change:",
            reply_markup=self.keyboards.settings_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _show_user_settings(self, callback: types.CallbackQuery):
        """Show current user settings"""
        user_id = callback.from_user.id
        settings_text = self.user_settings.get_settings_summary(user_id)
        
        await callback.message.edit_text(
            settings_text,
            reply_markup=self.keyboards.settings_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _show_pages_per_send_menu(self, callback: types.CallbackQuery):
        """Показать меню выбора количества страниц"""
        user_settings = self.user_settings.get_user_settings(callback.from_user.id)
        current_pages = user_settings["pages_per_send"]
        
        await callback.message.edit_text(
            f"📄 **Количество страниц за раз**\n\nТекущее значение: {current_pages}\nВыберите новое значение:",
            reply_markup=self.keyboards.pages_per_send_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _set_pages_per_send(self, callback: types.CallbackQuery, data: str):
        """Установить количество страниц за раз"""
        try:
            pages = int(data.split("_")[-1])
            user_id = callback.from_user.id
            
            if self.user_settings.update_user_setting(user_id, "pages_per_send", pages):
                await callback.message.edit_text(
                    f"✅ Количество страниц за раз установлено: **{pages}**",
                    reply_markup=self.keyboards.settings_menu(),
                    parse_mode="Markdown"
                )
                await callback.answer("Настройка сохранена!")
            else:
                await callback.answer("Ошибка сохранения настройки", show_alert=True)
        except ValueError:
            await callback.answer("Неверное значение", show_alert=True)
    
    async def _show_schedule_time_menu(self, callback: types.CallbackQuery):
        """Показать меню выбора времени отправки"""
        user_settings = self.user_settings.get_user_settings(callback.from_user.id)
        current_time = user_settings["schedule_time"]
        
        await callback.message.edit_text(
            f"⏰ **Время отправки**\n\nТекущее время: {current_time}\nВыберите новое время:",
            reply_markup=self.keyboards.schedule_time_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _set_schedule_time(self, callback: types.CallbackQuery, data: str):
        """Установить время отправки"""
        time_value = data.split("_")[-1]
        user_id = callback.from_user.id
        
        if self.user_settings.update_user_setting(user_id, "schedule_time", time_value):
            await callback.message.edit_text(
                f"✅ Время отправки установлено: **{time_value}**",
                reply_markup=self.keyboards.settings_menu(),
                parse_mode="Markdown"
            )
            await callback.answer("Настройка сохранена!")
        else:
            await callback.answer("Ошибка сохранения настройки", show_alert=True)
    
    async def _request_custom_time(self, callback: types.CallbackQuery, state: FSMContext):
        """Запросить ввод пользовательского времени"""
        await callback.message.edit_text(
            "⏰ **Введите время в формате HH:MM**\n\nНапример: 09:30 или 14:15",
            parse_mode="Markdown"
        )
        await state.set_state(SettingsStates.waiting_for_custom_time)
        await callback.answer()
    
    async def _show_interval_hours_menu(self, callback: types.CallbackQuery):
        """Показать меню выбора интервала"""
        user_settings = self.user_settings.get_user_settings(callback.from_user.id)
        current_interval = user_settings["interval_hours"]
        
        await callback.message.edit_text(
            f"🔄 **Интервал отправки**\n\nТекущий интервал: {current_interval} ч.\nВыберите новый интервал:",
            reply_markup=self.keyboards.interval_hours_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _set_interval_hours(self, callback: types.CallbackQuery, data: str):
        """Установить интервал в часах"""
        try:
            hours = int(data.split("_")[-1])
            user_id = callback.from_user.id
            
            if self.user_settings.update_user_setting(user_id, "interval_hours", hours):
                await callback.message.edit_text(
                    f"✅ Интервал отправки установлен: **{hours} ч.**",
                    reply_markup=self.keyboards.settings_menu(),
                    parse_mode="Markdown"
                )
                await callback.answer("Настройка сохранена!")
            else:
                await callback.answer("Ошибка сохранения настройки", show_alert=True)
        except ValueError:
            await callback.answer("Неверное значение", show_alert=True)
    
    async def _show_image_quality_menu(self, callback: types.CallbackQuery):
        """Показать меню выбора качества изображений"""
        user_settings = self.user_settings.get_user_settings(callback.from_user.id)
        current_quality = user_settings["image_quality"]
        
        await callback.message.edit_text(
            f"🖼️ **Качество изображений**\n\nТекущее качество: {current_quality}%\nВыберите новое качество:",
            reply_markup=self.keyboards.image_quality_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _set_image_quality(self, callback: types.CallbackQuery, data: str):
        """Установить качество изображений"""
        try:
            quality = int(data.split("_")[-1])
            user_id = callback.from_user.id
            
            if self.user_settings.update_user_setting(user_id, "image_quality", quality):
                await callback.message.edit_text(
                    f"✅ Качество изображений установлено: **{quality}%**",
                    reply_markup=self.keyboards.settings_menu(),
                    parse_mode="Markdown"
                )
                await callback.answer("Настройка сохранена!")
            else:
                await callback.answer("Ошибка сохранения настройки", show_alert=True)
        except ValueError:
            await callback.answer("Неверное значение", show_alert=True)
    
    async def _toggle_auto_send(self, callback: types.CallbackQuery):
        """Переключить автоотправку"""
        user_id = callback.from_user.id
        current_settings = self.user_settings.get_user_settings(user_id)
        current_value = current_settings["auto_send_enabled"]
        new_value = not current_value
        
        if self.user_settings.update_user_setting(user_id, "auto_send_enabled", new_value):
            status = "включена" if new_value else "выключена"
            await callback.message.edit_text(
                f"✅ Автоотправка **{status}**",
                reply_markup=self.keyboards.settings_menu(),
                parse_mode="Markdown"
            )
            await callback.answer(f"Автоотправка {status}!")
        else:
            await callback.answer("Ошибка сохранения настройки", show_alert=True)
    
    async def _toggle_notifications(self, callback: types.CallbackQuery):
        """Переключить уведомления"""
        user_id = callback.from_user.id
        current_settings = self.user_settings.get_user_settings(user_id)
        current_value = current_settings["notifications_enabled"]
        new_value = not current_value
        
        if self.user_settings.update_user_setting(user_id, "notifications_enabled", new_value):
            status = "включены" if new_value else "выключены"
            await callback.message.edit_text(
                f"✅ Уведомления **{status}**",
                reply_markup=self.keyboards.settings_menu(),
                parse_mode="Markdown"
            )
            await callback.answer(f"Уведомления {status}!")
        else:
            await callback.answer("Ошибка сохранения настройки", show_alert=True)
    
    async def _show_books_menu(self, callback: types.CallbackQuery):
        """Показать меню управления книгами"""
        await callback.message.edit_text(
            "📚 **Управление книгами**\n\nВыберите действие:",
            reply_markup=self.keyboards.books_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _send_next_pages(self, callback: types.CallbackQuery):
        """Отправить следующие страницы"""
        user_id = callback.from_user.id
        user_settings = self.user_settings.get_user_settings(user_id)
        pages_per_send = user_settings["pages_per_send"]
        
        # Получаем текущую страницу из базы данных
        user_data = self.bot.db.get_user_data(user_id)
        current_page = user_data.get("current_page", 1)
        
        await self.bot.send_pages_to_user(user_id, current_page)
        await callback.answer(f"Отправлено {pages_per_send} страниц!")
    
    async def _show_current_page(self, callback: types.CallbackQuery):
        """Показать текущую страницу"""
        user_id = callback.from_user.id
        user_data = self.bot.db.get_user_data(user_id)
        current_page = user_data.get("current_page", 1)
        total_pages = self.bot.pdf_reader.get_total_pages()
        
        await callback.message.edit_text(
            f"📄 **Текущая страница: {current_page} из {total_pages}**\n\nВыберите действие:",
            reply_markup=self.keyboards.navigation_menu(current_page, total_pages),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _request_page_number(self, callback: types.CallbackQuery, state: FSMContext):
        """Запросить номер страницы для перехода"""
        total_pages = self.bot.pdf_reader.get_total_pages()
        await callback.message.edit_text(
            f"🔍 **Переход к странице**\n\nВведите номер страницы (1-{total_pages}):",
            parse_mode="Markdown"
        )
        await state.set_state(SettingsStates.waiting_for_page_number)
        await callback.answer()
    
    async def _goto_specific_page(self, callback: types.CallbackQuery, data: str):
        """Перейти к конкретной странице"""
        try:
            page_number = int(data.split("_")[-1])
            user_id = callback.from_user.id
            
            # Обновляем текущую страницу в базе данных
            self.bot.db.set_current_page(user_id, page_number)
            
            await callback.answer(f"Переход к странице {page_number}")
            await self._show_current_page(callback)
        except ValueError:
            await callback.answer("Неверный номер страницы", show_alert=True)
    
    async def _show_stats(self, callback: types.CallbackQuery):
        """Показать статистику"""
        user_id = callback.from_user.id
        user_data = self.bot.db.get_user_data(user_id)
        current_page = user_data.get("current_page", 1)
        total_pages = self.bot.pdf_reader.get_total_pages()
        progress = (current_page / total_pages) * 100 if total_pages > 0 else 0
        
        stats_text = f"""📊 **Статистика чтения**

📄 Текущая страница: {current_page}
📚 Всего страниц: {total_pages}
📈 Прогресс: {progress:.1f}%
📅 Последнее обновление: {user_data.get('last_sent', 'Никогда')}
"""
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=self.keyboards.main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _show_help(self, callback: types.CallbackQuery):
        """Показать справку"""
        help_text = """ℹ️ **Справка по боту**

🤖 **Основные функции:**
• Автоматическая отправка страниц книги по расписанию
• Ручной запрос следующих страниц
• Переход к любой странице
• Персональные настройки для каждого пользователя

⚙️ **Настройки:**
• Количество страниц за раз (1-10)
• Время автоотправки
• Интервал между отправками
• Качество изображений
• Включение/выключение автоотправки

📱 **Основные команды:**
/start - Запуск бота
/help - Справка
/settings - Настройки
/status - Текущий статус
/next - Следующие страницы
/upload - Загрузить PDF
/book - Информация о книге
/stats - Статистика

🔧 **Административные команды:**
/admin - Панель администратора
/users - Управление пользователями
/system - Системная информация
/logs - Просмотр логов
/backup - Резервное копирование
/cleanup - Очистка файлов

💡 **Совет:** Используйте кнопки для удобной навигации!"""
        
        await callback.message.edit_text(
            help_text,
            reply_markup=self.keyboards.main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
    
    async def _show_leaderboard(self, callback: types.CallbackQuery):
        """Show leaderboard"""
        try:
            leaderboard = self.bot.db_manager.get_leaderboard(limit=10)
            
            if not leaderboard:
                text = "📊 **Таблица лидеров**\n\n🤷‍♂️ Пока никто не читал страницы!"
            else:
                text = "📊 **Таблица лидеров**\n\n"
                for i, user in enumerate(leaderboard, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    username = user.get('username', 'Неизвестный')
                    points = user.get('total_points', 0)
                    level = user.get('level', 1)
                    text += f"{medal} **{username}** - {points} очков (Уровень {level})\n"
            
            await callback.message.edit_text(
                text,
                reply_markup=self.keyboards.main_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error showing leaderboard: {e}")
            await callback.message.edit_text(
                "❌ Ошибка при загрузке таблицы лидеров",
                reply_markup=self.keyboards.main_menu()
            )
        await callback.answer()
    
    async def _show_achievements(self, callback: types.CallbackQuery):
        """Show user achievements"""
        try:
            user_id = callback.from_user.id
            user_data = self.bot.db_manager.get_user(user_id)
            
            if not user_data:
                await callback.message.edit_text(
                    "❌ Пользователь не найден",
                    reply_markup=self.keyboards.main_menu()
                )
                return
            
            user_achievements = user_data.get('achievements', [])
            all_achievements = self.bot.db_manager.get_available_achievements()
            
            text = "🏆 **Ваши достижения**\n\n"
            
            unlocked_count = 0
            for achievement_id, achievement in all_achievements.items():
                if achievement_id in user_achievements:
                    text += f"✅ {achievement['icon']} **{achievement['name']}** - {achievement['description']} (+{achievement['points']} очков)\n"
                    unlocked_count += 1
                else:
                    text += f"🔒 {achievement['icon']} **{achievement['name']}** - {achievement['description']} (+{achievement['points']} очков)\n"
            
            text += f"\n📈 **Прогресс:** {unlocked_count}/{len(all_achievements)} достижений разблокировано"
            
            await callback.message.edit_text(
                text,
                reply_markup=self.keyboards.main_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Error showing achievements: {e}")
            await callback.message.edit_text(
                "❌ Ошибка при загрузке достижений",
                reply_markup=self.keyboards.main_menu()
            )
        await callback.answer()
    
    async def _mark_page_read(self, callback: types.CallbackQuery):
        """Mark current page as read and award points"""
        try:
            user_id = callback.from_user.id
            username = callback.from_user.username or "unknown"
            
            # Get current user data
            user_data = self.bot.db_manager.get_user(user_id)
            if not user_data:
                await callback.answer("❌ Пользователь не найден", show_alert=True)
                return
            
            current_page = user_data.get('current_page', 1)
            total_pages = user_data.get('total_pages', 0)
            
            if current_page >= total_pages:
                await callback.answer("📚 Вы уже прочитали всю книгу!", show_alert=True)
                return
            
            # Mark page as read and get results
            result = self.bot.db_manager.mark_page_read(user_id)
            
            # Increment current page
            self.bot.db_manager.increment_page(user_id)
            
            # Prepare response message
            points_earned = result.get('points_earned', 0)
            new_achievements = result.get('new_achievements', [])
            level_up = result.get('level_up', False)
            
            response_text = f"✅ Страница {current_page} отмечена как прочитанная!\n"
            response_text += f"🎯 +{points_earned} очков\n"
            
            if level_up:
                new_level = result.get('new_level', 1)
                response_text += f"🎉 Поздравляем! Вы достигли {new_level} уровня!\n"
            
            if new_achievements:
                response_text += "\n🏆 Новые достижения:\n"
                all_achievements = self.bot.db_manager.get_available_achievements()
                for achievement_id in new_achievements:
                    if achievement_id in all_achievements:
                        ach = all_achievements[achievement_id]
                        response_text += f"• {ach['icon']} {ach['name']}\n"
            
            # Update the message with reading progress
            updated_user_data = self.bot.db_manager.get_user(user_id)
            new_current_page = updated_user_data.get('current_page', 1)
            progress_percent = int((new_current_page / total_pages) * 100) if total_pages > 0 else 0
            
            progress_text = f"📖 **Прогресс чтения**\n\n"
            progress_text += f"📄 Страница: {new_current_page}/{total_pages}\n"
            progress_text += f"📊 Прогресс: {progress_percent}%\n\n"
            progress_text += response_text
            
            await callback.message.edit_text(
                progress_text,
                reply_markup=self.keyboards.reading_progress_menu(new_current_page, total_pages),
                parse_mode="Markdown"
            )
            
            await callback.answer(f"🎯 +{points_earned} очков!", show_alert=True)
            
        except Exception as e:
            logger.error(f"Error marking page as read: {e}")
            await callback.answer("❌ Ошибка при отметке страницы", show_alert=True)