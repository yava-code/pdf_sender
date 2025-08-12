import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile

from cleanup_manager import CleanupManager
<<<<<<< HEAD
from config import config, legacy_config
=======
from config import get_config, Config
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc
from database_manager import DatabaseManager
from file_validator import FileValidator
from pdf_reader import PDFReader
from scheduler import PDFScheduler
from logger_config import BotLogger, init_logging
from user_settings import UserSettings
from keyboards import BotKeyboards
from callback_handlers import CallbackHandler
from message_handlers import MessageHandler

# Configure logging using our custom logger
init_logging()
logger = logging.getLogger(__name__)


# Define FSM states for PDF upload
class UploadPDF(StatesGroup):
    waiting_for_file = State()


class PDFSenderBot:
    def __init__(self):
<<<<<<< HEAD
=======
        config = get_config()
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc
        self.bot = Bot(token=config.bot_token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.db = DatabaseManager()
        self.pdf_reader = PDFReader(output_dir=config.output_dir, db=self.db)
        self.scheduler = PDFScheduler(self)
        
        # Initialize new components
        self.user_settings = UserSettings()
        self.keyboards = BotKeyboards()
        self.callback_handler = CallbackHandler(self)
        self.message_handler = MessageHandler(self)

        # Create upload directory if it doesn't exist
<<<<<<< HEAD
        os.makedirs(legacy_config.UPLOAD_DIR, exist_ok=True)
=======
        os.makedirs(config.upload_dir, exist_ok=True)
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc

        # Register handlers
        self._register_handlers()
    
    @property
    def db_manager(self):
        """Property to access database manager"""
        return self.db

    def _register_handlers(self):
        """Register all bot handlers"""
        # Command handlers
        self.dp.message.register(self.start_handler, Command("start"))
        self.dp.message.register(self.help_handler, Command("help"))
        self.dp.message.register(self.settings_handler, Command("settings"))
        self.dp.message.register(self.status_handler, Command("status"))
        self.dp.message.register(self.next_pages_handler, Command("next"))
        self.dp.message.register(self.current_page_handler, Command("current"))
        self.dp.message.register(self.goto_page_handler, Command("goto"))
        self.dp.message.register(self.book_command, Command("book"))
        self.dp.message.register(self.upload_command, Command("upload"))
        self.dp.message.register(self.stats_command, Command("stats"))
        self.dp.message.register(self.leaderboard_command, Command("leaderboard"))
        self.dp.message.register(self.achievements_command, Command("achievements"))
        self.dp.message.register(self.admin_command, Command("admin"))
        self.dp.message.register(self.logs_command, Command("logs"))
        self.dp.message.register(self.users_command, Command("users"))
        self.dp.message.register(self.system_command, Command("system"))
        self.dp.message.register(self.backup_command, Command("backup"))
        self.dp.message.register(self.cleanup_command, Command("cleanup"))

        # Callback query handlers
        self.dp.callback_query.register(self.callback_handler.handle_callback)
        
        # State-based message handlers
        self.dp.message.register(self.message_handler.handle_state_message)
        
        # Upload PDF handlers
        self.dp.message.register(self.process_pdf_upload, UploadPDF.waiting_for_file)

    async def start_handler(self, message: types.Message):
        """Handle /start command"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"

        # Add user to database
        self.db.add_user(user_id, username)
        
        # Log user action
        BotLogger.log_user_action(user_id, username, "start_command")

        welcome_text = (
            "📚 **Welcome to PDF Sender Bot!**\n\n"
            "I help you read books by sending PDF pages on schedule.\n\n"
            "🎯 **Main features:**\n"
            "• Automatic page sending on schedule\n"
            "• Personal settings for each user\n"
            "• Convenient control through buttons\n"
            "• Jump to any page\n"
            "• Reading statistics\n\n"
            "📱 Use the buttons below for navigation:"
        )

        await message.answer(
            welcome_text,
            reply_markup=self.keyboards.main_menu(),
            parse_mode="Markdown"
        )
        logger.info(f"New user started: {user_id} (@{username})")

    async def settings_handler(self, message: types.Message):
        """Handle /settings command"""
        if message.from_user is None:
            return
            
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        # Log user action
        BotLogger.log_user_action(user_id, username, "settings_command")
        
        # Get current user settings
        settings_text = self.user_settings.get_settings_summary(user_id)
        
        await message.answer(
            settings_text,
            reply_markup=self.keyboards.settings_menu(),
            parse_mode="Markdown"
        )

    async def help_handler(self, message: types.Message):
        """Handle /help command"""
        if message.from_user is None:
            return
            
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        # Log user action
        BotLogger.log_user_action(user_id, username, "help_command")
        
        help_text = (
            "ℹ️ **PDF Sender Bot Help**\n\n"
            "🤖 **Main functions:**\n"
            "• Automatic page sending on schedule\n"
            "• Manually request next pages\n"
            "• Jump to any page\n"
            "• Personal settings for each user\n\n"
            "⚙️ **Settings:**\n"
            "• Number of pages at once (1-10)\n"
            "• Auto-send time\n"
            "• Interval between sends\n"
            "• Image quality\n"
            "• Enable/disable auto-send\n\n"
            "📱 **Main commands:**\n"
            "/start - Start bot\n"
            "/help - Help\n"
            "/settings - Settings\n"
            "/status - Current status\n"
            "/next - Next pages\n"
            "/upload - Upload PDF\n"
            "/book - Book information\n"
            "/stats - Statistics\n\n"
            "🔧 **Admin commands:**\n"
            "/admin - Admin panel\n"
            "/users - User management\n"
            "/system - System info\n"
            "/logs - View logs\n"
            "/backup - Backup\n"
            "/cleanup - Cleanup files\n\n"
            "💡 **Tip:** Use buttons for easy navigation!"
        )
        
        await message.answer(
            help_text,
            reply_markup=self.keyboards.main_menu(),
            parse_mode="Markdown"
        )

    async def status_handler(self, message: types.Message):
        """Handle /status command"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "status_command")

        # Check if user exists
        if not self.db.get_user(user_id):
            await message.answer(
                "❌ **Need to start bot**\n\n"
                "Use /start command",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )
            return

        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.answer(
                "❌ **Book not uploaded**\n\n"
                "First upload a PDF book using /upload command",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )
            return

        # Get user settings
        settings = self.user_settings.get_user_settings(user_id)
        
        current_page = self.db.get_current_page(user_id)
        total_pages = self.db.get_total_pages(user_id)
        progress = (current_page / total_pages) * 100 if total_pages > 0 else 0
        filename = os.path.basename(pdf_path)

        # Get last sent time
        last_sent = self.db.get_last_sent(user_id)
        if last_sent:
            last_sent_str = last_sent.strftime("%d.%m.%Y %H:%M")
            # Calculate next send time based on user's interval
            next_send = last_sent + timedelta(hours=settings['interval_hours'])
            next_send_str = next_send.strftime("%d.%m.%Y %H:%M")
        else:
            last_sent_str = "Never"
            next_send_str = "Soon" if settings['auto_send_enabled'] else "Disabled"

        # Auto-send status
        auto_send_status = "✅ Enabled" if settings['auto_send_enabled'] else "❌ Disabled"
        
        # Schedule info
        schedule_info = ""
        if settings['schedule_time']:
            schedule_info = f"\n🕐 **Send time:** {settings['schedule_time']}"

        status_text = (
            f"📊 **Reading Progress** 📊\n\n"
            f"📚 **Book:** {filename}\n"
            f"📖 **Current page:** {current_page}\n"
            f"📄 **Total pages:** {total_pages}\n"
            f"📈 **Progress:** {progress:.1f}%\n\n"
            f"⏰ **Last sent:** {last_sent_str}\n"
            f"⏭️ **Next send:** {next_send_str}\n"
            f"🔄 **Auto-send:** {auto_send_status}{schedule_info}\n\n"
            f"📄 **Pages per send:** {settings['pages_per_send']}\n"
            f"⏱️ **Interval:** {settings['interval_hours']} h\n"
            f"🖼️ **Quality:** {settings['image_quality']}"
        )

        await message.answer(
            status_text,
            parse_mode="Markdown",
            reply_markup=self.keyboards.status_menu()
        )

    async def next_pages_handler(self, message: types.Message):
        """Handle /next command - send next pages"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        # Log user action
        BotLogger.log_user_action(user_id, username, "next_pages")

        # Check if user exists
        if not self.db.get_user(user_id):
            await message.answer("You need to start the bot first with /start!", 
                               reply_markup=self.keyboards.main_menu())
            return

        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.answer(
                "You need to upload a PDF book first! Use /upload.",
                reply_markup=self.keyboards.main_menu()
            )
            return

        try:
            # Get user settings
            user_settings = self.user_settings.get_user_settings(user_id)
            pages_per_send = user_settings["pages_per_send"]
            
            current_page = self.db.get_current_page(user_id)
            total_pages = self.db.get_total_pages(user_id)
            
            # Check if we've reached the end
            if current_page >= total_pages:
                await message.answer(
                    "📖 You have already finished the book! 🎉",
                    reply_markup=self.keyboards.main_menu()
                )
                return
            
            await self.send_pages_to_user(user_id, current_page)

            # Explicitly increment page as expected by tests
            new_page = self.db.increment_page(user_id, pages_per_send)
            
            end_page = min(current_page + pages_per_send - 1, total_pages)
            await message.answer(
                f"📖 **Sent pages {current_page}-{end_page}**\n"
                f"📍 Current page is now: {new_page}",
                parse_mode="Markdown",
                reply_markup=self.keyboards.reading_progress_menu(new_page, total_pages)
            )

        except Exception as e:
            BotLogger.log_error(e, f"next_pages_handler for user {user_id}")
            await message.answer("❌ Error sending pages. Try again later.", 
                               reply_markup=self.keyboards.main_menu())

    async def current_page_handler(self, message: types.Message):
        """Handle /current command - send current page"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        # Log user action
        BotLogger.log_user_action(user_id, username, "current_page")

        # Check if user exists
        if not self.db.get_user(user_id):
            await message.answer("Вам нужно сначала запустить бота командой /start!",
                               reply_markup=self.keyboards.main_menu())
            return

        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.answer(
                "Вам нужно сначала загрузить PDF книгу! Используйте команду /upload.",
                reply_markup=self.keyboards.main_menu()
            )
            return

        try:
            # Get user settings
            user_settings = self.user_settings.get_user_settings(user_id)
            image_quality = user_settings["image_quality"]
            
            current_page = self.db.get_current_page(user_id)
            total_pages = self.db.get_total_pages(user_id)
            
            # Create PDFReader instance
            pdf_reader = PDFReader(
                user_id=user_id, output_dir=legacy_config.OUTPUT_DIR, db=self.db
            )
            image_paths = pdf_reader.extract_pages_as_images(
                current_page, 1
            )

            if image_paths:
                photo = FSInputFile(image_paths[0])
                progress_percent = int((current_page / total_pages) * 100) if total_pages > 0 else 0
                caption = f"📖 **Прогресс чтения**\n\n"
                caption += f"📄 Страница: {current_page}/{total_pages}\n"
                caption += f"📊 Прогресс: {progress_percent}%"
                
                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=self.keyboards.reading_progress_menu(current_page, total_pages)
                )
                pdf_reader.cleanup_images()
            else:
                progress_percent = int((current_page / total_pages) * 100) if total_pages > 0 else 0
                text = f"📖 **Прогресс чтения**\n\n"
                text += f"📄 Страница: {current_page}/{total_pages}\n"
                text += f"📊 Прогресс: {progress_percent}%\n\n"
                text += "(Не удалось отобразить изображение)"
                
                await message.answer(
                    text,
                    parse_mode="Markdown",
                    reply_markup=self.keyboards.reading_progress_menu(current_page, total_pages)
                )

        except Exception as e:
            logger.error(f"Error in current_page_handler: {e}")
            await message.answer(
                "❌ Error sending current page. Please try again later."
            )

    def _parse_page_number(self, message_text: str) -> Optional[int]:
        """Parse page number from goto command text"""
        args = message_text.split()
        if len(args) != 2:
            return None

        try:
            return int(args[1])
        except ValueError:
            return None

    async def _send_single_page(self, user_id: int, page_number: int):
        """Send a single page to user"""
        pdf_reader = PDFReader(
            user_id=user_id, output_dir=legacy_config.OUTPUT_DIR, db=self.db
        )
        image_paths = pdf_reader.extract_pages_as_images(page_number, 1)

        if image_paths:
            photo = FSInputFile(image_paths[0])
            await self.bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=f"📖 Jumped to page {page_number}",
            )
            pdf_reader.cleanup_images()
        else:
            await self.bot.send_message(
                user_id, f"📖 Jumped to page {page_number} (could not render image)"
            )

    async def goto_page_handler(self, message: types.Message):
        """Handle /goto command - jump to specific page"""
        if message.from_user is None or message.text is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "goto_page_command")

        # Check if user exists
        if not self.db.get_user(user_id):
            await message.answer(
                "❌ **Need to start bot**\n\n"
                "Use /start command",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )
            return

        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.answer(
                "❌ **Book not uploaded**\n\n"
                "First upload a PDF book using /upload command",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )
            return

        try:
            # Extract page number from command
            target_page = self._parse_page_number(message.text)
            if target_page is None:
                await message.answer(
                    "❌ **Invalid command format**\n\n"
                    "Usage: /goto <page_number>\n"
                    "Example: /goto 15",
                    parse_mode="Markdown",
                    reply_markup=self.keyboards.page_navigation()
                )
                return

            total_pages = self.db.get_total_pages(user_id)
            if target_page < 1 or target_page > total_pages:
                await message.answer(
                    f"❌ **Page out of range**\n\n"
                    f"Page must be between 1 and {total_pages}",
                    parse_mode="Markdown",
                    reply_markup=self.keyboards.page_navigation()
                )
                return

            # Set new current page
            self.db.set_current_page(user_id, target_page)
            
            # Get user settings for image quality
            settings = self.user_settings.get_user_settings(user_id)
            
            # Send the target page
            await self._send_single_page(user_id, target_page)
            
            BotLogger.log_user_action(user_id, username, f"goto_page: {target_page}")

        except Exception as e:
            BotLogger.log_error(e, f"goto_page_handler for user {user_id}")
            await message.answer(
                "❌ **Jump error**\n\n"
                "An error occurred when jumping to page. "
                "Try again.",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )

    async def send_pages_to_user(self, user_id: int, page_number: int):
        """Send PDF pages to a user"""
        try:
            # Get user settings
            user_settings = self.user_settings.get_user_settings(user_id)
            pages_per_send = user_settings["pages_per_send"]
            image_quality = user_settings["image_quality"]
            notifications_enabled = user_settings["notifications_enabled"]
            
            # Log user action
            username = self.db.get_user(user_id).get("username", "unknown")
            BotLogger.log_user_action(user_id, username, f"send_pages: {page_number}")
            
            # Create a PDFReader instance for this user
            pdf_reader = PDFReader(
                user_id=user_id, output_dir=legacy_config.OUTPUT_DIR, db=self.db
            )

            # Extract pages as images
            image_paths = pdf_reader.extract_pages_as_images(
                page_number, pages_per_send
            )

            if not image_paths:
                if notifications_enabled:
                    await self.bot.send_message(user_id, "❌ No pages to send.")
                return

            # Send a message with the page number
            total_pages = self.db.get_total_pages(user_id)
            if notifications_enabled:
                await self.bot.send_message(
                    user_id, 
                    f"📖 **Page {page_number} of {total_pages}**",
                    parse_mode="Markdown"
                )

            # Send each page as a photo
            for i, image_path in enumerate(image_paths):
                # Create caption
                caption = f"📖 Page {page_number + i}"

                # Send photo
                photo = FSInputFile(image_path)
                await self.bot.send_photo(chat_id=user_id, photo=photo, caption=caption)

            # Update last sent time and current page
            self.db.update_last_sent(user_id)
            self.db.set_current_page(user_id, page_number + pages_per_send)

            # Cleanup old images
            pdf_reader.cleanup_images()

            logger.info(f"Sent {len(image_paths)} pages to user {user_id}")

        except Exception as e:
            BotLogger.log_error(e, f"sending pages to user {user_id}")
            if user_settings.get("notifications_enabled", True):
                await self.bot.send_message(
                    user_id, "❌ Error sending pages. Try again later."
                )

    async def check_and_send_pages(self):
        """Check and send pages to users based on their personal settings"""
        try:
            # Get all users
            users = self.db.get_users()
            logger.info(f"Checking {len(users)} users for scheduled sends")

            # Current time
            now = datetime.now()

            # Check each user
            for user in users:
                try:
                    user_id = user["id"]
                    
                    # Get user settings
                    user_settings = self.user_settings.get_user_settings(user_id)
                    
                    # Skip if auto-send is disabled
                    if not user_settings["auto_send_enabled"]:
                        continue

                    # Check if user has a PDF
                    pdf_path = self.db.get_pdf_path(user_id)
                    if not pdf_path or not os.path.exists(pdf_path):
                        logger.info(f"User {user_id} has no PDF, skipping")
                        continue

                    # Get user's schedule settings
                    schedule_time = user_settings["schedule_time"]
                    interval_hours = user_settings["interval_hours"]
                    pages_per_send = user_settings["pages_per_send"]
                    
                    # Check if it's time to send based on schedule
                    should_send = False
                    
                    if schedule_time and schedule_time != "disabled":
                        # Parse schedule time (HH:MM format)
                        try:
                            schedule_hour, schedule_minute = map(int, schedule_time.split(":"))
                            schedule_today = now.replace(hour=schedule_hour, minute=schedule_minute, second=0, microsecond=0)
                            
                            # Check if we should send at this scheduled time
                            last_sent = self.db.get_last_sent(user_id)
                            if not last_sent:
                                # Never sent before, send if it's past schedule time today
                                should_send = now >= schedule_today
                            else:
                                # Check if it's a new day and past schedule time
                                last_sent_date = last_sent.date()
                                today = now.date()
                                if today > last_sent_date and now >= schedule_today:
                                    should_send = True
                        except ValueError:
                            logger.warning(f"Invalid schedule time format for user {user_id}: {schedule_time}")
                    else:
                        # Use interval-based sending
                        last_sent = self.db.get_last_sent(user_id)
                        if (
                            not last_sent
                            or (now - last_sent).total_seconds() >= interval_hours * 3600
                        ):
                            should_send = True
                    
                    if should_send:
                        # Get current page
                        current_page = self.db.get_current_page(user_id)
                        
                        # Check if we've reached the end of the book
                        total_pages = self.db.get_total_pages(user_id)
                        if current_page >= total_pages:
                            logger.info(f"User {user_id} has finished their book")
                            continue

                        # Send pages
                        await self.send_pages_to_user(user_id, current_page)
                        logger.info(f"Sent scheduled pages to user {user_id} (page {current_page})")
                    else:
                        # Log next send time
                        last_sent = self.db.get_last_sent(user_id)
                        if last_sent and schedule_time == "disabled":
                            next_send = last_sent + timedelta(hours=interval_hours)
                            time_until = next_send - now
                            logger.debug(f"User {user_id}: Next send in {time_until}")

                except Exception as e:
                    logger.error(f"Error processing user {user_id}: {e}")

        except Exception as e:
            logger.error(f"Error in check_and_send_pages: {e}")

    async def upload_command(self, message: types.Message, state: FSMContext):
        """Handle /upload command"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        # Log user action
        BotLogger.log_user_action(user_id, username, "upload_command")

        # Check if user exists
        if not self.db.get_user(user_id):
            await message.reply("Вам нужно сначала запустить бота командой /start!",
                               reply_markup=self.keyboards.main_menu())
            return

        await message.reply(
            "📤 **Загрузка PDF книги**\n\n"
            "Отправьте мне PDF файл, который вы хотите читать.\n\n"
            "📋 **Требования:**\n"
<<<<<<< HEAD
            f"• Максимальный размер: {legacy_config.MAX_FILE_SIZE_MB}MB\n"
=======
            f"• Максимальный размер: {get_config().max_file_size // (1024 * 1024)}MB\n"
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc
            "• Только PDF формат\n"
            "• Файл должен содержать текст или изображения",
            parse_mode="Markdown"
        )

        # Set state to waiting for file
        await state.set_state(UploadPDF.waiting_for_file)

    async def process_pdf_upload(self, message: types.Message, state: FSMContext):
        """Process uploaded PDF file"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        
        # Log user action
        BotLogger.log_user_action(user_id, username, "pdf_upload_attempt")

        try:
            # Check if message contains a document
            if not message.document:
                await message.reply("❌ Пожалуйста, отправьте PDF файл.",
                                   reply_markup=self.keyboards.main_menu())
                return

            # Check if the file is a PDF
            if not message.document.mime_type == "application/pdf":
                await message.reply("❌ Пожалуйста, отправьте именно PDF файл.",
                                   reply_markup=self.keyboards.main_menu())
                return

            # Check file size before downloading
            file_size = message.document.file_size
<<<<<<< HEAD
            if file_size and file_size > legacy_config.MAX_FILE_SIZE_MB * 1024 * 1024:
                await message.reply(
                    f"❌ **Файл слишком большой!**\n\n"
                    f"Максимальный размер: {legacy_config.MAX_FILE_SIZE_MB}MB\n"
=======
            if file_size and file_size > get_config().max_file_size:
                await message.reply(
                    f"❌ **Файл слишком большой!**\n\n"
                    f"Максимальный размер: {get_config().max_file_size // (1024 * 1024)}MB\n"
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc
                    f"Размер вашего файла: {file_size / 1024 / 1024:.1f}MB",
                    parse_mode="Markdown",
                    reply_markup=self.keyboards.main_menu()
                )
                return

            # Validate and sanitize filename
            original_filename = message.document.file_name or "book.pdf"
            is_valid_name, sanitized_filename = FileValidator.validate_file_name(
                original_filename
            )

            # Download the file
            file_id = message.document.file_id
            file_info = await self.bot.get_file(file_id)
            file_path = file_info.file_path

            # Create user directory if it doesn't exist
<<<<<<< HEAD
            user_upload_dir = os.path.join(legacy_config.UPLOAD_DIR, str(user_id))
=======
            user_upload_dir = os.path.join(get_config().upload_dir, str(user_id))
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc
            os.makedirs(user_upload_dir, exist_ok=True)

            # Generate local file path with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(sanitized_filename)[0]
            local_file_path = os.path.join(
                user_upload_dir, f"{base_name}_{timestamp}.pdf"
            )

            # Download the file
            await message.reply(
                "📥 **Загружаю и проверяю ваш PDF...**\n\n"
                "⏳ Это может занять несколько секунд",
                parse_mode="Markdown"
            )
            await self.bot.download_file(file_path, local_file_path)

            # Validate the downloaded PDF
            is_valid, validation_message = FileValidator.validate_pdf_file(
                local_file_path, file_size
            )

            if not is_valid:
                # Clean up the downloaded file
                if os.path.exists(local_file_path):
                    os.remove(local_file_path)
                await message.reply(
                    f"❌ **Ошибка валидации PDF**\n\n{validation_message}",
                    parse_mode="Markdown",
                    reply_markup=self.keyboards.main_menu()
                )
                BotLogger.log_error(Exception(validation_message), f"PDF validation failed for user {user_id}")
                return

            # Create a PDFReader instance to validate and set the PDF
            pdf_reader = PDFReader(
                user_id=user_id, output_dir=legacy_config.OUTPUT_DIR, db=self.db
            )
            success = pdf_reader.set_pdf_for_user(user_id, local_file_path)

            if success:
                total_pages = self.db.get_total_pages(user_id)
                file_size_mb = (
                    f"{file_size / 1024 / 1024:.1f}MB" if file_size else "Unknown"
                )
                await message.reply(
                    f"✅ **PDF успешно загружен!**\n\n"
                    f"📚 **Книга:** {sanitized_filename}\n"
                    f"📄 **Всего страниц:** {total_pages}\n"
                    f"💾 **Размер файла:** {file_size_mb}\n\n"
                    f"📖 Чтение начинается с первой страницы.\n"
                    f"Используйте кнопки ниже для навигации.",
                    parse_mode="Markdown",
                    reply_markup=self.keyboards.main_menu()
                )
                BotLogger.log_user_action(
                    user_id, username, 
                    f"pdf_uploaded: {sanitized_filename} ({total_pages} pages)"
                )
            else:
                await message.reply(
                    "❌ **Ошибка обработки PDF**\n\n"
                    "Возникла проблема при обработке вашего файла. "
                    "Попробуйте другой PDF файл.",
                    parse_mode="Markdown",
                    reply_markup=self.keyboards.main_menu()
                )
                # Clean up the file if there was an error
                if os.path.exists(local_file_path):
                    os.remove(local_file_path)
                BotLogger.log_error(Exception("set_pdf_for_user returned False"), f"PDF processing failed for user {user_id}")

        except Exception as e:
            BotLogger.log_error(e, f"processing PDF upload for user {user_id}")
            await message.reply(
                "❌ **Произошла ошибка**\n\n"
                "При обработке вашего PDF произошла ошибка. "
                "Попробуйте еще раз.",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )
        finally:
            # Reset the state
            await state.clear()

    async def book_command(self, message: types.Message):
        """Handle /book command to show current book info"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "book_info_command")

        # Check if user exists
        if not self.db.get_user(user_id):
            await message.reply(
                "❌ **Необходимо запустить бота**\n\n"
                "Используйте команду /start",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )
            return

        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.reply(
                "❌ **Книга не загружена**\n\n"
                "Вы еще не загрузили книгу! "
                "Используйте команду /upload для добавления книги.",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )
            return

        # Get book info
        filename = os.path.basename(pdf_path)
        current_page = self.db.get_current_page(user_id)
        total_pages = self.db.get_total_pages(user_id)
        progress = (current_page / total_pages * 100) if total_pages > 0 else 0

        # Format book info
        book_info = (
            f"📚 **Ваша текущая книга** 📚\n\n"
            f"📖 **Название:** {filename}\n"
            f"📄 **Текущая страница:** {current_page} из {total_pages}\n"
            f"📊 **Прогресс:** {progress:.1f}%\n\n"
            f"💡 Используйте /upload для смены книги."
        )

        await message.reply(
            book_info,
            parse_mode="Markdown",
            reply_markup=self.keyboards.book_management()
        )

    async def leaderboard_command(self, message: types.Message):
        """Handle /leaderboard command"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"

        BotLogger.log_user_action(user_id, username, "leaderboard_command")

        try:
            leaderboard = self.db.get_leaderboard(limit=10)

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

            await message.reply(
                text,
                reply_markup=self.keyboards.leaderboard_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            BotLogger.log_error(e, f"Error showing leaderboard: {e}")
            await message.reply(
                "❌ Ошибка при загрузке таблицы лидеров",
                reply_markup=self.keyboards.main_menu()
            )

    async def achievements_command(self, message: types.Message):
        """Handle /achievements command"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"

        BotLogger.log_user_action(user_id, username, "achievements_command")

        try:
            user_stats = self.db.get_user_stats(user_id)
            user_achievements = [ach['id'] for ach in user_stats['achievements']]
            all_achievements = self.db.get_available_achievements()

            text = "🏆 **Ваши достижения**\n\n"

            unlocked_count = 0
            for achievement in all_achievements:
                if achievement['id'] in user_achievements:
                    text += f"✅ {achievement['icon']} **{achievement['name']}** - {achievement['description']} (+{achievement['points']} очков)\n"
                    unlocked_count += 1
                else:
                    text += f"🔒 {achievement['icon']} **{achievement['name']}** - {achievement['description']} (+{achievement['points']} очков)\n"

            text += f"\n📈 **Прогресс:** {unlocked_count}/{len(all_achievements)} достижений разблокировано"

            await message.reply(
                text,
                reply_markup=self.keyboards.achievements_menu(),
                parse_mode="Markdown"
            )
        except Exception as e:
            BotLogger.log_error(e, f"Error showing achievements: {e}")
            await message.reply(
                "❌ Ошибка при загрузке достижений",
                reply_markup=self.keyboards.main_menu()
            )

    async def stats_command(self, message: types.Message):
        """Handle /stats command to show enhanced reading statistics with gamification"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "stats_command")

        # Check if user exists
        if not self.db.get_user(user_id):
            await message.reply(
                "❌ **Необходимо запустить бота**\n\n"
                "Используйте команду /start",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )
            return

        try:
            # Get user stats with gamification
            user_stats = self.db.get_user_stats(user_id)
            pdf_path = self.db.get_pdf_path(user_id)
            
            # Get user settings
            settings = self.user_settings.get_user_settings(user_id)

            stats_text = "📊 **Ваша статистика** 📊\n\n"

            # Gamification stats
            stats_text += "🎮 **Игровая статистика:**\n"
            stats_text += f"⭐ **Уровень:** {user_stats['level']}\n"

            # Experience progress bar
            exp = user_stats['experience']
            next_level_exp = user_stats['level'] * 100
            exp_percent = (exp % 100) / 100 * 100
            exp_bar = "█" * int(exp_percent / 10) + "░" * (10 - int(exp_percent / 10))
            stats_text += f" XP: {exp % 100}/{next_level_exp} [{exp_bar}]\n"

            stats_text += f"🎯 **Очки:** {user_stats['total_points']}\n"
            stats_text += f"📚 **Прочитано страниц:** {user_stats['pages_read']}\n"
            stats_text += f"📖 **Завершено книг:** {user_stats['books_completed']}\n"
            stats_text += f"🔥 **Текущая серия:** {user_stats['current_streak']} дней\n"
            stats_text += f"🏆 **Лучшая серия:** {user_stats['longest_streak']} дней\n"
            stats_text += f"🏅 **Достижений:** {len(user_stats['achievements'])}/{len(self.db.get_available_achievements())}\n\n"

            # Current book progress
            if pdf_path and os.path.exists(pdf_path):
                current_page = self.db.get_current_page(user_id)
                total_pages = self.db.get_total_pages(user_id)
                progress = (current_page / total_pages) * 100 if total_pages > 0 else 0

                stats_text += "📖 **Текущая книга:**\n"
                stats_text += f"📚 {os.path.basename(pdf_path)}\n"
                stats_text += f"📄 {current_page}/{total_pages} ({progress:.1f}%)\n"

                # Progress bar
                progress_bar_length = 10
                filled_length = int(progress_bar_length * progress / 100)
                progress_bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
                stats_text += f"📊 [{progress_bar}]\n\n"
            else:
                stats_text += "📖 **Книга еще не загружена**\n\n"

            # Reading pace and predictions
            if user_stats['pages_read'] > 0:
                user_data = self.db.get_user_data(user_id)
                join_date = user_data.get("joined_at")
                if join_date:
                    try:
                        join_dt = datetime.fromisoformat(
                            join_date.replace("Z", "+00:00")
                        )
                        days_active = (datetime.now() - join_dt).days + 1
                        pages_per_day = user_stats['pages_read'] / days_active if days_active > 0 else 0
                        
                        stats_text += "📈 **Аналитика чтения:**\n"
                        stats_text += f"⚡ **Темп:** {pages_per_day:.1f} стр/день\n"
                        
                        if pdf_path and os.path.exists(pdf_path):
                            current_page = self.db.get_current_page(user_id)
                            total_pages = self.db.get_total_pages(user_id)
                            if pages_per_day > 0 and total_pages > current_page:
                                estimated_days_left = (total_pages - current_page) / pages_per_day
                                stats_text += f"🏁 **До финиша:** ~{estimated_days_left:.0f} дней\n"
                        
                        stats_text += "\n"
                    except (ValueError, TypeError):
                        pass

            # Recent achievements
            if user_stats['achievements']:
                stats_text += "🏆 **Последние достижения:**\n"
                for achievement in user_stats['achievements'][-3:]:
                    stats_text += f"• {achievement['icon']} **{achievement['name']}**: {achievement['description']} (+{achievement['points']} очков)\n"
                stats_text += "\n"

            await message.reply(
                stats_text, 
                parse_mode="Markdown",
                reply_markup=self.keyboards.stats_menu()
            )

        except Exception as e:
            BotLogger.log_error(e, f"generating stats for user {user_id}")
            await message.reply(
                "❌ **Ошибка генерации статистики**\n\n"
                "Произошла ошибка при создании статистики. "
                "Попробуйте еще раз.",
                parse_mode="Markdown",
                reply_markup=self.keyboards.main_menu()
            )

    async def cleanup_old_files(self):
        """Perform cleanup of old files"""
        try:
            logger.info("Starting automatic cleanup...")

            # Clean up old images
            deleted_images = CleanupManager.cleanup_old_images()

            # Clean up orphaned uploads (older than 24 hours)
            deleted_uploads = CleanupManager.cleanup_orphaned_uploads()

            total_deleted = deleted_images + deleted_uploads
            if total_deleted > 0:
                logger.info(
                    f"Cleanup completed: {deleted_images} images, {deleted_uploads} uploads deleted"
                )

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    async def admin_command(self, message: types.Message):
        """Handle /admin command - administrative panel"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "admin_command")

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

        await message.answer(
            admin_text,
            reply_markup=self.keyboards.admin_menu(),
            parse_mode="Markdown"
        )

    async def users_command(self, message: types.Message):
        """Handle /users command - user management"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "users_command")

        try:
            users = self.db.get_users()
            total_users = len(users)
            
            # Count active users (with PDFs)
            active_users = 0
            users_with_auto_send = 0
            
            for user in users:
                pdf_path = user.get("pdf_path")
                if pdf_path and os.path.exists(pdf_path):
                    active_users += 1
                
                user_settings = self.user_settings.get_user_settings(user["id"])
                if user_settings.get("auto_send_enabled", True):
                    users_with_auto_send += 1

            users_text = (
                f"👥 <b>Управление пользователями</b> 👥\n\n"
                f"📊 <b>Статистика:</b>\n"
                f"👤 Всего пользователей: {total_users}\n"
                f"📚 Активных пользователей: {active_users}\n"
                f"🤖 С автоотправкой: {users_with_auto_send}\n\n"
                f"📋 <b>Последние 10 пользователей:</b>\n"
            )

            # Show last 10 users
            recent_users = sorted(users, key=lambda x: x.get("joined_at") or "", reverse=True)[:10]
            for i, user in enumerate(recent_users, 1):
                user_info = user.get("username", "Без имени")
                # Escape HTML special characters
                user_info = user_info.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                join_date = user.get("joined_at", "Неизвестно")[:10] if user.get("joined_at") else "Неизвестно"
                current_page = user.get("current_page", 1)
                users_text += f"{i}. @{user_info} (стр. {current_page}) - {join_date}\n"

            await message.answer(
                users_text,
                reply_markup=self.keyboards.users_management_menu(),
                parse_mode="HTML"
            )

        except Exception as e:
            BotLogger.log_error(e, f"users_command for user {user_id}")
            await message.answer(
                "❌ <b>Ошибка получения данных пользователей</b>\n\n"
                "Произошла ошибка при загрузке информации о пользователях.",
                parse_mode="HTML"
            )

    async def system_command(self, message: types.Message):
        """Handle /system command - system information"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "system_command")

        try:
            import psutil
            from datetime import timedelta
            
            # System info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            try:
                # Try to get disk usage for current drive
                current_drive = os.path.splitdrive(os.getcwd())[0] + os.sep
                disk = psutil.disk_usage(current_drive)
            except Exception:
                # Fallback to root drive if current path fails
                try:
                    disk = psutil.disk_usage('/')
                except Exception:
                    # If all fails, create dummy disk info
                    disk = type('DiskUsage', (), {'total': 0, 'used': 0, 'free': 0})()
            
            # Bot uptime (approximate)
            uptime = datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Storage stats
            storage_stats = CleanupManager.get_storage_usage()
            
            system_text = (
                f"🖥️ **Системная информация** 🖥️\n\n"
                f"⚡ **Производительность:**\n"
                f"🔥 CPU: {cpu_percent}%\n"
                f"🧠 RAM: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)\n"
                f"💾 Диск: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)\n\n"
                f"📁 **Хранилище бота:**\n"
                f"📸 Изображения: {CleanupManager.format_file_size(storage_stats['output_dir_size'])} ({storage_stats['output_dir_files']} файлов)\n"
                f"📚 PDF файлы: {CleanupManager.format_file_size(storage_stats['upload_dir_size'])} ({storage_stats['upload_dir_files']} файлов)\n"
                f"💿 Общий размер: {CleanupManager.format_file_size(storage_stats['total_size'])}\n\n"
                f"⚙️ **Конфигурация:**\n"
<<<<<<< HEAD
                f"📄 Макс. размер файла: {legacy_config.MAX_FILE_SIZE_MB}MB\n"
                f"🗂️ Хранение изображений: {legacy_config.IMAGE_RETENTION_DAYS} дней\n"
                f"🖼️ Качество по умолчанию: {legacy_config.IMAGE_QUALITY}%"
=======
                f"📄 Макс. размер файла: {get_config().max_file_size // (1024 * 1024)}MB\n"
                f"🗂️ Хранение изображений: {get_config().cleanup_older_than_days} дней\n"
                f"🖼️ Качество по умолчанию: {get_config().image_quality}%"
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc
            )

            await message.answer(
                system_text,
                reply_markup=self.keyboards.system_menu(),
                parse_mode="Markdown"
            )

        except ImportError:
            await message.answer(
                "❌ **Модуль psutil не установлен**\n\n"
                "Для отображения системной информации требуется установить psutil:\n"
                "`pip install psutil`",
                parse_mode="Markdown"
            )
        except Exception as e:
            BotLogger.log_error(e, f"system_command for user {user_id}")
            await message.answer(
                "❌ **Ошибка получения системной информации**\n\n"
                "Произошла ошибка при сборе данных о системе.",
                parse_mode="Markdown"
            )

    async def logs_command(self, message: types.Message):
        """Handle /logs command - view recent logs"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "logs_command")

        try:
            # Get recent log entries (last 20)
            log_entries = BotLogger.get_recent_logs(20)
            
            if not log_entries:
                await message.answer(
                    "📝 <b>Логи пусты</b>\n\n"
                    "Нет доступных записей в логах.",
                    parse_mode="HTML"
                )
                return

            logs_text = "📝 <b>Последние записи логов</b> 📝\n\n"
            
            for entry in log_entries[-10:]:  # Show last 10 entries
                timestamp = entry.get('timestamp', 'Unknown')
                level = entry.get('level', 'INFO')
                message_text = entry.get('message', '')[:100]  # Truncate long messages
                
                # Escape HTML special characters in message text
                message_text = message_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                # Add emoji based on log level
                emoji = {
                    'ERROR': '🔴',
                    'WARNING': '🟡', 
                    'INFO': '🔵',
                    'DEBUG': '⚪'
                }.get(level, '⚪')
                
                logs_text += f"{emoji} <code>{timestamp[:19]}</code> [{level}]\n{message_text}...\n\n"

            await message.answer(
                logs_text,
                reply_markup=self.keyboards.logs_menu(),
                parse_mode="HTML"
            )

        except Exception as e:
            BotLogger.log_error(e, f"logs_command for user {user_id}")
            await message.answer(
                "❌ <b>Ошибка получения логов</b>\n\n"
                "Произошла ошибка при чтении файлов логов.",
                parse_mode="HTML"
            )

    async def backup_command(self, message: types.Message):
        """Handle /backup command - create backup"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "backup_command")

        try:
            import shutil
            import zipfile
            from pathlib import Path
            
            # Create backup directory
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"pdf_sender_backup_{timestamp}.zip"
            backup_path = backup_dir / backup_filename
            
            await message.answer(
                "📦 **Создание резервной копии...**\n\n"
                "⏳ Пожалуйста, подождите...",
                parse_mode="Markdown"
            )
            
            # Create zip backup
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup database
<<<<<<< HEAD
                if os.path.exists(config.database_path):
                    zipf.write(config.database_path, "database.json")
=======
                if os.path.exists(get_config().database_path):
                    zipf.write(get_config().database_path, "database.json")
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc
                
                # Backup user settings
                if os.path.exists("user_settings.json"):
                    zipf.write("user_settings.json", "user_settings.json")
                
                # Backup config (without sensitive data)
                zipf.writestr("config_backup.txt", 
<<<<<<< HEAD
                    f"PAGES_PER_SEND={legacy_config.PAGES_PER_SEND}\n"
                    f"INTERVAL_HOURS={legacy_config.INTERVAL_HOURS}\n"
                    f"SCHEDULE_TIME={legacy_config.SCHEDULE_TIME}\n"
                    f"MAX_FILE_SIZE_MB={legacy_config.MAX_FILE_SIZE_MB}\n"
                    f"IMAGE_RETENTION_DAYS={legacy_config.IMAGE_RETENTION_DAYS}\n"
                    f"IMAGE_QUALITY={legacy_config.IMAGE_QUALITY}\n"
=======
                    f"PAGES_PER_SEND={get_config().pages_per_send}\n"
                    f"INTERVAL_HOURS={get_config().interval_hours}\n"
                    f"SCHEDULE_TIME={get_config().schedule_time}\n"
                    f"MAX_FILE_SIZE_MB={get_config().max_file_size // (1024 * 1024)}\n"
                    f"IMAGE_RETENTION_DAYS={get_config().cleanup_older_than_days}\n"
                    f"IMAGE_QUALITY={get_config().image_quality}\n"
>>>>>>> b55000166c88d8e62842cd6c782225c1545c00cc
                )
            
            backup_size = os.path.getsize(backup_path) / 1024 / 1024  # MB
            
            await message.answer(
                f"✅ **Резервная копия создана!** ✅\n\n"
                f"📁 **Файл:** `{backup_filename}`\n"
                f"📊 **Размер:** {backup_size:.2f} MB\n"
                f"📅 **Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                f"💾 Резервная копия сохранена в папке `backups/`",
                parse_mode="Markdown",
                reply_markup=self.keyboards.backup_menu()
            )
            
            BotLogger.log_user_action(user_id, username, f"backup_created: {backup_filename}")

        except Exception as e:
            BotLogger.log_error(e, f"backup_command for user {user_id}")
            await message.answer(
                "❌ **Ошибка создания резервной копии**\n\n"
                "Произошла ошибка при создании backup файла.",
                parse_mode="Markdown"
            )

    async def cleanup_command(self, message: types.Message):
        """Handle /cleanup command - manual cleanup"""
        if message.from_user is None:
            return

        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        
        BotLogger.log_user_action(user_id, username, "cleanup_command")

        try:
            await message.answer(
                "🧹 **Запуск очистки файлов...**\n\n"
                "⏳ Удаление старых изображений и временных файлов...",
                parse_mode="Markdown"
            )
            
            # Get storage stats before cleanup
            stats_before = CleanupManager.get_storage_usage()
            
            # Perform cleanup
            deleted_images = CleanupManager.cleanup_old_images()
            deleted_uploads = CleanupManager.cleanup_orphaned_uploads()
            
            # Get storage stats after cleanup
            stats_after = CleanupManager.get_storage_usage()
            
            # Calculate freed space
            freed_space = stats_before['total_size'] - stats_after['total_size']
            
            cleanup_text = (
                f"✅ **Очистка завершена!** ✅\n\n"
                f"🗑️ **Удалено:**\n"
                f"📸 Изображений: {deleted_images}\n"
                f"📁 Загрузок: {deleted_uploads}\n\n"
                f"💾 **Освобождено места:** {CleanupManager.format_file_size(freed_space)}\n\n"
                f"📊 **Текущее использование:**\n"
                f"📸 Изображения: {CleanupManager.format_file_size(stats_after['output_dir_size'])} ({stats_after['output_dir_files']} файлов)\n"
                f"📚 PDF файлы: {CleanupManager.format_file_size(stats_after['upload_dir_size'])} ({stats_after['upload_dir_files']} файлов)\n"
                f"💿 Общий размер: {CleanupManager.format_file_size(stats_after['total_size'])}"
            )
            
            await message.answer(
                cleanup_text,
                reply_markup=self.keyboards.cleanup_menu(),
                parse_mode="Markdown"
            )
            
            BotLogger.log_user_action(user_id, username, f"manual_cleanup: {deleted_images + deleted_uploads} files deleted")

        except Exception as e:
            BotLogger.log_error(e, f"cleanup_command for user {user_id}")
            await message.answer(
                "❌ **Ошибка очистки**\n\n"
                "Произошла ошибка при выполнении очистки файлов.",
                parse_mode="Markdown"
            )

    async def start_polling(self):
        """Start the bot"""
        try:
            # Start scheduler
            self.scheduler.start()

            # Start polling
            logger.info("Starting PDF Sender Bot...")
            await self.dp.start_polling(self.bot)

        except Exception as e:
            logger.error(f"Error starting bot: {e}")
        finally:
            # Stop scheduler
            self.scheduler.stop()
            await self.bot.session.close()


async def main():
    bot = PDFSenderBot()
    await bot.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
