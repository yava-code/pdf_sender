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
    """Handles text messages"""
    
    def __init__(self, bot_instance: 'PDFSenderBot'):
        self.bot = bot_instance
        self.user_settings = UserSettings()
        self.keyboards = BotKeyboards()
    
    async def handle_custom_time(self, message: types.Message, state: FSMContext):
        """Handles user's custom time input"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "unknown"
            time_text = message.text.strip()
            
            # Log user action
            BotLogger.log_user_action(user_id, username, f"custom_time_input: {time_text}")
            
            # Validate time format (HH:MM)
            time_pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$'
            if not re.match(time_pattern, time_text):
                await message.reply(
                    "❌ **Invalid time format!**\n\n"
                    "Please enter time in HH:MM format\n"
                    "For example: 09:30 or 14:15",
                    parse_mode="Markdown"
                )
                return
            
            # Save setting
            if self.user_settings.update_user_setting(user_id, "schedule_time", time_text):
                await message.reply(
                    f"✅ **Send time set to: {time_text}**\n\n"
                    "Setting saved!",
                    reply_markup=self.keyboards.settings_menu(),
                    parse_mode="Markdown"
                )
                await state.clear()
            else:
                await message.reply(
                    "❌ Error saving setting. Please try again.",
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            logger.error(f"Error handling custom time: {e}")
            await message.reply(
                "❌ An error occurred. Please try again.",
                parse_mode="Markdown"
            )
    
    async def handle_page_number(self, message: types.Message, state: FSMContext):
        """Handles page number input"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "unknown"
            page_text = message.text.strip()
            
            # Log user action
            BotLogger.log_user_action(user_id, username, f"page_number_input: {page_text}")
            
            # Check if input is a number
            try:
                page_number = int(page_text)
            except ValueError:
                await message.reply(
                    "❌ **Invalid format!**\n\n"
                    "Please enter a page number (a digit)",
                    parse_mode="Markdown"
                )
                return
            
            # Check page range
            total_pages = self.bot.pdf_reader.get_total_pages()
            if page_number < 1 or page_number > total_pages:
                await message.reply(
                    f"❌ **Invalid page number!**\n\n"
                    f"Please enter a number from 1 to {total_pages}",
                    parse_mode="Markdown"
                )
                return
            
            # Update current page in database
            self.bot.db.set_current_page(user_id, page_number)
            
            # Get data for display
            user_data = self.bot.db.get_user_data(user_id)
            current_page = user_data.get("current_page", 1) if user_data else page_number
            
            await message.reply(
                f"✅ **Navigated to page {page_number}**\n\n"
                f"📄 Current page: {current_page} of {total_pages}",
                reply_markup=self.keyboards.navigation_menu(current_page, total_pages),
                parse_mode="Markdown"
            )
            await state.clear()
                
        except Exception as e:
            logger.error(f"Error handling page number: {e}")
            await message.reply(
                "❌ An error occurred. Please try again.",
                parse_mode="Markdown"
            )
    
    async def handle_regular_message(self, message: types.Message):
        """Handles regular text messages"""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "unknown"
            text = message.text
            
            # Log user message
            BotLogger.log_user_action(user_id, username, f"message: {text[:50]}...")
            
            # Check if the message is a command
            if text.startswith('/'):
                # Commands are handled by separate handlers
                return
            
            # For regular messages, show the main menu
            await message.reply(
                "🤖 **Hello!**\n\n"
                "I am a bot for sending PDF book pages.\n"
                "Use the buttons below for navigation:",
                reply_markup=self.keyboards.main_menu(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error handling regular message: {e}")
            await message.reply(
                "❌ An error occurred. Please try again.",
                parse_mode="Markdown"
            )
    
    async def handle_state_message(self, message: types.Message, state: FSMContext):
        """Handles messages based on FSM state"""
        try:
            current_state = await state.get_state()
            
            if current_state == SettingsStates.waiting_for_custom_time.state:
                await self.handle_custom_time(message, state)
            elif current_state == SettingsStates.waiting_for_page_number.state:
                await self.handle_page_number(message, state)
            else:
                await self.handle_regular_message(message)
                
        except Exception as e:
            logger.error(f"Error handling state message: {e}")
            await message.reply(
                "❌ An error occurred. Please try again.",
                parse_mode="Markdown"
            )