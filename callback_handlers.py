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
    """Состояния для настройки параметров"""
    waiting_for_custom_time = State()
    waiting_for_page_number = State()


class CallbackHandler:
    """Обработчик callback запросов от inline клавиатур"""

    def __init__(self, bot_instance: 'PDFSenderBot'):
        self.bot = bot_instance
        self.user_settings = UserSettings()
        self.keyboards = BotKeyboards()

    async def handle_callback(self, callback: types.CallbackQuery, state: FSMContext):
        """Основной обработчик callback запросов"""
        try:
            data = callback.data
            user_id = callback.from_user.id
            username = callback.from_user.username or "unknown"

            # Логируем действие пользователя
            BotLogger.log_user_action(user_id, username, f"callback: {data}")

            # Маршрутизация callback запросов
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
            # Administrative callbacks
            elif data == "stats":
                await self._show_stats(callback)
            elif data == "help":
                await self._show_help(callback)
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
            elif data.startswith("mark_as_read_"):
                await self._mark_as_read(callback, data)
            elif data == "leaderboard":
                await self._show_leaderboard(callback)
            else:
                await callback.answer("Неизвестная команда", show_alert=True)

        except Exception as e:
            logger.error(f"Ошибка обработки callback {callback.data}: {e}")
            await callback.answer("Произошла ошибка. Попробуйте еще раз.", show_alert=True)

    async def _show_main_menu(self, callback: types.CallbackQuery):
        """Показать главное меню"""
        await callback.message.edit_text(
            "🏠 **Главное меню**\n\nВыберите действие:",
            reply_markup=self.keyboards.main_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()

    async def _show_admin_menu(self, callback: types.CallbackQuery):
        """Показать административное меню"""
        admin_text = (
            "🔧 **Панель администратора** 🔧\n\n"
            "📊 **Доступные команды:**\n"
            "/users - Управление пользователями\n"
            "/system - Системная информация\n"
            "/logs - Просмотр логов\n"
            "/backup - Резервное копирование\n"
            "/cleanup - Очистка файлов\n\n"
            "⚙️ **Быстрые действия:**"
        )

        await callback.message.edit_text(
            admin_text,
            reply_markup=self.keyboards.admin_menu(),
            parse_mode="Markdown"
        )

    async def _handle_admin_users(self, callback: types.CallbackQuery):
        """Обработка кнопки управления пользователями"""
        await self.bot.users_command(callback.message)

    async def _handle_admin_system(self, callback: types.CallbackQuery):
        """Обработка кнопки системной информации"""
        await self.bot.system_command(callback.message)

    async def _handle_admin_logs(self, callback: types.CallbackQuery):
        """Обработка кнопки просмотра логов"""
        await self.bot.logs_command(callback.message)

    async def _handle_admin_backup(self, callback: types.CallbackQuery):
        """Обработка кнопки резервного копирования"""
        await self.bot.backup_command(callback.message)

    async def _handle_admin_cleanup(self, callback: types.CallbackQuery):
        """Обработка кнопки очистки"""
        await self.bot.cleanup_command(callback.message)

    async def _handle_system_refresh(self, callback: types.CallbackQuery):
        """Обновить системную информацию"""
        await self.bot.system_command(callback.message)

    async def _handle_logs_refresh(self, callback: types.CallbackQuery):
        """Обновить логи"""
        await self.bot.logs_command(callback.message)

    async def _handle_backup_create(self, callback: types.CallbackQuery):
        """Создать резервную копию"""
        await self.bot.backup_command(callback.message)

    async def _handle_cleanup_run(self, callback: types.CallbackQuery):
        """Запустить очистку"""
        await self.bot.cleanup_command(callback.message)

    async def _show_settings_menu(self, callback: types.CallbackQuery):
        """Показать меню настроек"""
        await callback.message.edit_text(
            "⚙️ **Настройки бота**\n\nВыберите параметр для изменения:",
            reply_markup=self.keyboards.settings_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()

    async def _show_user_settings(self, callback: types.CallbackQuery):
        """Показать текущие настройки пользователя"""
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

    async def _mark_as_read(self, callback: types.CallbackQuery, data: str):
        """Отметить страницу как прочитанную"""
        try:
            page_number = int(data.split("_")[-1])
            user_id = callback.from_user.id

            self.bot.db.mark_page_as_read(user_id, page_number)
            self.bot.db.add_points(user_id, 1)

            BotLogger.log_user_action(user_id, callback.from_user.username, f"mark_as_read: {page_number}")

            await callback.answer(f"Страница {page_number} отмечена как прочитанная! +1 очко!", show_alert=True)

        except (IndexError, ValueError) as e:
            logger.error(f"Ошибка в _mark_as_read: {e}")
            await callback.answer("Ошибка обработки запроса.", show_alert=True)

    async def _show_leaderboard(self, callback: types.CallbackQuery):
        """Показать таблицу лидеров"""
        await self.bot.leaderboard_command(callback.message)
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