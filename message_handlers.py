import logging
import re
from aiogram import types
from aiogram.fsm.context import FSMContext
from typing import TYPE_CHECKING

from callback_handlers import SettingsStates
from keyboards import BotKeyboards
from user_settings import UserSettings
from logger_config import BotLogger

if TYPE_CHECKING:
    from main import PDFSenderBot

logger = logging.getLogger(__name__)


class MessageHandler:
    """Обработчик текстовых сообщений"""

    def __init__(self, bot_instance: 'PDFSenderBot'):
        self.bot = bot_instance
        self.user_settings = UserSettings()
        self.keyboards = BotKeyboards()

    async def handle_custom_time(self, message: types.Message, state: FSMContext):
        """Обработка ввода пользовательского времени"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "unknown"
            time_text = message.text.strip()

            # Логируем действие пользователя
            BotLogger.log_user_action(user_id, username, f"custom_time_input: {time_text}")

            # Проверяем формат времени (HH:MM)
            time_pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$'
            if not re.match(time_pattern, time_text):
                await message.reply(
                    "❌ **Неверный формат времени!**\n\n"
                    "Пожалуйста, введите время в формате HH:MM\n"
                    "Например: 09:30 или 14:15",
                    parse_mode="Markdown"
                )
                return

            # Сохраняем настройку
            if self.user_settings.update_user_setting(user_id, "schedule_time", time_text):
                await message.reply(
                    f"✅ **Время отправки установлено: {time_text}**\n\n"
                    "Настройка сохранена!",
                    reply_markup=self.keyboards.settings_menu(),
                    parse_mode="Markdown"
                )
                await state.clear()
            else:
                await message.reply(
                    "❌ Ошибка сохранения настройки. Попробуйте еще раз.",
                    parse_mode="Markdown"
                )

        except Exception as e:
            logger.error(f"Ошибка обработки пользовательского времени: {e}")
            await message.reply(
                "❌ Произошла ошибка. Попробуйте еще раз.",
                parse_mode="Markdown"
            )

    async def handle_page_number(self, message: types.Message, state: FSMContext):
        """Обработка ввода номера страницы"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "unknown"
            page_text = message.text.strip()

            # Логируем действие пользователя
            BotLogger.log_user_action(user_id, username, f"page_number_input: {page_text}")

            # Проверяем, что введено число
            try:
                page_number = int(page_text)
            except ValueError:
                await message.reply(
                    "❌ **Неверный формат!**\n\n"
                    "Пожалуйста, введите номер страницы (число)",
                    parse_mode="Markdown"
                )
                return

            # Проверяем диапазон страниц
            total_pages = self.bot.pdf_reader.get_total_pages()
            if page_number < 1 or page_number > total_pages:
                await message.reply(
                    f"❌ **Неверный номер страницы!**\n\n"
                    f"Введите номер от 1 до {total_pages}",
                    parse_mode="Markdown"
                )
                return

            # Обновляем текущую страницу в базе данных
            self.bot.db.set_current_page(user_id, page_number)

            # Получаем данные для отображения
            user_data = self.bot.db.get_user_data(user_id)
            current_page = user_data.get("current_page", 1)

            await message.reply(
                f"✅ **Переход к странице {page_number}**\n\n"
                f"📄 Текущая страница: {current_page} из {total_pages}",
                reply_markup=self.keyboards.navigation_menu(current_page, total_pages),
                parse_mode="Markdown"
            )
            await state.clear()

        except Exception as e:
            logger.error(f"Ошибка обработки номера страницы: {e}")
            await message.reply(
                "❌ Произошла ошибка. Попробуйте еще раз.",
                parse_mode="Markdown"
            )

    async def handle_regular_message(self, message: types.Message):
        """Обработка обычных текстовых сообщений"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "unknown"
            text = message.text

            # Логируем сообщение пользователя
            BotLogger.log_user_action(user_id, username, f"message: {text[:50]}...")

            # Проверяем, является ли сообщение командой
            if text.startswith('/'):
                # Команды обрабатываются отдельными хендлерами
                return

            # Для обычных сообщений показываем главное меню
            await message.reply(
                "🤖 **Привет!**\n\n"
                "Я бот для отправки страниц PDF книг.\n"
                "Используйте кнопки ниже для навигации:",
                reply_markup=self.keyboards.main_menu(),
                parse_mode="Markdown"
            )

        except Exception as e:
            logger.error(f"Ошибка обработки обычного сообщения: {e}")
            await message.reply(
                "❌ Произошла ошибка. Попробуйте еще раз.",
                parse_mode="Markdown"
            )

    async def handle_state_message(self, message: types.Message, state: FSMContext):
        """Обработка сообщений в зависимости от состояния FSM"""
        try:
            current_state = await state.get_state()

            if current_state == SettingsStates.waiting_for_custom_time.state:
                await self.handle_custom_time(message, state)
            elif current_state == SettingsStates.waiting_for_page_number.state:
                await self.handle_page_number(message, state)
            else:
                await self.handle_regular_message(message)

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения с состоянием: {e}")
            await message.reply(
                "❌ Произошла ошибка. Попробуйте еще раз.",
                parse_mode="Markdown"
            )