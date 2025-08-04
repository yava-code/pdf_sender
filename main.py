import asyncio
import logging
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database_manager import DatabaseManager
from pdf_reader import PDFReader
from scheduler import PDFScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define FSM states for PDF upload
class UploadPDF(StatesGroup):
    waiting_for_file = State()


class PDFSenderBot:
    def __init__(self):
        Config.validate()
        self.bot = Bot(token=Config.BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.db = DatabaseManager()
        self.pdf_reader = PDFReader(output_dir=Config.OUTPUT_DIR, db=self.db)
        self.scheduler = PDFScheduler(self)

        # Create upload directory if it doesn't exist
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
        
        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all bot handlers"""
        self.dp.message.register(self.start_handler, Command("start"))
        self.dp.message.register(self.help_handler, Command("help"))
        self.dp.message.register(self.status_handler, Command("status"))
        self.dp.message.register(self.next_pages_handler, Command("next"))
        self.dp.message.register(self.current_page_handler, Command("current"))
        self.dp.message.register(self.goto_page_handler, Command("goto"))
        self.dp.message.register(self.book_command, Command("book"))
        self.dp.message.register(self.upload_command, Command("upload"))
        
        # Upload PDF handlers
        self.dp.message.register(
            self.process_pdf_upload,
            UploadPDF.waiting_for_file
        )

    async def start_handler(self, message: types.Message):
        """Handle /start command"""
        if message.from_user is None:
            return
        
        user_id = message.from_user.id
        username = message.from_user.username

        # Add user to database
        self.db.add_user(user_id, username)

        welcome_text = (
            "📚 Welcome to PDF Sender Bot!\n\n"
            "I help you read books by sending PDF pages daily.\n\n"
            "Available commands:\n"
            "/help - Show this help message\n"
            "/status - Show current reading progress\n"
            "/next - Get next 3 pages manually\n"
            "/current - Get current page\n"
            "/goto <page> - Jump to specific page\n\n"
            "📖 Happy reading!"
        )

        await message.answer(welcome_text)
        logger.info(f"New user started: {user_id} (@{username})")

    async def help_handler(self, message: types.Message):
        """Handle /help command"""
        help_text = (
            "📚 PDF Sender Bot Help\n\n"
            "🤖 Commands:\n"
            "/start - Start using the bot\n"
            "/help - Show this help message\n"
            "/upload - Upload a new PDF book\n"
            "/book - Show information about your current book\n"
            "/status - Show current reading progress\n"
            "/next - Get next 3 pages manually\n"
            "/current - Get current page\n"
            "/goto <page> - Jump to specific page\n\n"
            "📅 The bot automatically sends pages according to schedule.\n"
            "📖 Use /next to get additional pages anytime!"
        )

        await message.answer(help_text)

    async def status_handler(self, message: types.Message):
        """Handle /status command"""
        user_id = message.from_user.id
        
        # Check if user exists
        if not self.db.get_user(user_id):
            await message.answer("You need to /start the bot first!")
            return
            
        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.answer("You need to upload a PDF book first! Use /upload command.")
            return

        current_page = self.db.get_current_page(user_id)
        total_pages = self.db.get_total_pages(user_id)
        progress = (current_page / total_pages) * 100 if total_pages > 0 else 0
        
        # Get last sent time
        last_sent = self.db.get_last_sent(user_id)
        if last_sent:
            last_sent_str = last_sent.strftime("%Y-%m-%d %H:%M:%S")
            # Calculate next send time based on interval
            next_send = last_sent + timedelta(hours=Config.INTERVAL_HOURS)
            next_send_str = next_send.strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_sent_str = "Never"
            next_send_str = "Soon"

        status_text = (
            f"📊 Reading Progress\n\n"
            f"📖 Current page: {current_page}\n"
            f"📚 Total pages: {total_pages}\n"
            f"📈 Progress: {progress:.1f}%\n"
            f"⏰ Last sent: {last_sent_str}\n"
            f"⏭️ Next send: {next_send_str}\n"
            f"📄 Pages per send: {Config.PAGES_PER_SEND}"
        )

        await message.answer(status_text)

    async def next_pages_handler(self, message: types.Message):
        """Handle /next command - send next 3 pages"""
        if message.from_user is None:
            return
        
        user_id = message.from_user.id
            
        # Check if user exists
        if not self.db.get_user(user_id):
            await message.answer("You need to /start the bot first!")
            return
            
        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.answer("You need to upload a PDF book first! Use /upload command.")
            return
            
        try:
            current_page = self.db.get_current_page(user_id)
            await self.send_pages_to_user(user_id, current_page)

            # Update current page
            new_page = self.db.increment_page(user_id)

            await message.answer(
                f"📖 Sent pages {current_page}-{current_page + Config.PAGES_PER_SEND - 1}\n"
                f"📍 Current page is now: {new_page}"
            )

        except Exception as e:
            logger.error(f"Error in next_pages_handler: {e}")
            await message.answer("❌ Error sending pages. Please try again later.")

    async def current_page_handler(self, message: types.Message):
        """Handle /current command - send current page"""
        if message.from_user is None:
            return
        
        user_id = message.from_user.id
            
        # Check if user exists
        if not self.db.get_user(user_id):
            await message.answer("You need to /start the bot first!")
            return
            
        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.answer("You need to upload a PDF book first! Use /upload command.")
            return
            
        try:
            current_page = self.db.get_current_page(user_id)
            # Override pages_per_send to just get one page
            pdf_reader = PDFReader(user_id=user_id, output_dir=Config.OUTPUT_DIR, db=self.db)
            image_paths = pdf_reader.extract_pages_as_images(current_page, 1)
            
            if image_paths:
                photo = FSInputFile(image_paths[0])
                await self.bot.send_photo(
                    chat_id=user_id, 
                    photo=photo, 
                    caption=f"📖 Current page: {current_page}"
                )
                pdf_reader.cleanup_images()
            else:
                await message.answer(f"📖 Current page: {current_page} (could not render image)")

        except Exception as e:
            logger.error(f"Error in current_page_handler: {e}")
            await message.answer(
                "❌ Error sending current page. Please try again later."
            )

    async def goto_page_handler(self, message: types.Message):
        """Handle /goto command - jump to specific page"""
        if message.from_user is None or message.text is None:
            return
        
        user_id = message.from_user.id
            
        # Check if user exists
        if not self.db.get_user(user_id):
            await message.answer("You need to /start the bot first!")
            return
            
        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.answer("You need to upload a PDF book first! Use /upload command.")
            return
            
        try:
            # Extract page number from command
            args = message.text.split()
            if len(args) != 2:
                await message.answer("❌ Usage: /goto <page_number>")
                return

            try:
                target_page = int(args[1])
            except ValueError:
                await message.answer("❌ Please provide a valid page number.")
                return

            total_pages = self.db.get_total_pages(user_id)
            if target_page < 1 or target_page > total_pages:
                await message.answer(f"❌ Page must be between 1 and {total_pages}.")
                return

            # Set new current page
            self.db.set_current_page(user_id, target_page)

            # Send the target page
            # Override pages_per_send to just get one page
            pdf_reader = PDFReader(user_id=user_id, output_dir=Config.OUTPUT_DIR, db=self.db)
            image_paths = pdf_reader.extract_pages_as_images(target_page, 1)
            
            if image_paths:
                photo = FSInputFile(image_paths[0])
                await self.bot.send_photo(
                    chat_id=user_id, 
                    photo=photo, 
                    caption=f"📖 Jumped to page {target_page}"
                )
                pdf_reader.cleanup_images()
            else:
                await message.answer(f"📖 Jumped to page {target_page} (could not render image)")

        except Exception as e:
            logger.error(f"Error in goto_page_handler: {e}")
            await message.answer("❌ Error jumping to page. Please try again later.")

    async def send_pages_to_user(self, user_id: int, page_number: int):
        """Send PDF pages to a user"""
        try:
            # Create a PDFReader instance for this user
            pdf_reader = PDFReader(user_id=user_id, output_dir=Config.OUTPUT_DIR, db=self.db)
            
            # Extract pages as images
            pages_per_send = Config.PAGES_PER_SEND
            image_paths = pdf_reader.extract_pages_as_images(
                page_number, pages_per_send
            )

            if not image_paths:
                await self.bot.send_message(user_id, "❌ No pages to send.")
                return

            # Send a message with the page number
            total_pages = self.db.get_total_pages(user_id)
            await self.bot.send_message(
                user_id,
                f"📖 Page {page_number} of {total_pages} 📖"
            )

            # Send each page as a photo
            for i, image_path in enumerate(image_paths):
                # Create caption
                caption = f"📖 Page {page_number + i}"

                # Send photo
                photo = FSInputFile(image_path)
                await self.bot.send_photo(chat_id=user_id, photo=photo, caption=caption)

            # Update last sent time
            self.db.update_last_sent(user_id)
            
            # Cleanup old images
            pdf_reader.cleanup_images()

            logger.info(f"Sent {len(image_paths)} pages to user {user_id}")

        except Exception as e:
            logger.error(f"Error sending pages to user {user_id}: {e}")
            await self.bot.send_message(
                user_id, "❌ Error sending pages. Please try again later."
            )

    async def check_and_send_pages(self):
        """Check and send pages to users based on interval"""
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
                    
                    # Check if user has a PDF
                    pdf_path = self.db.get_pdf_path(user_id)
                    if not pdf_path or not os.path.exists(pdf_path):
                        logger.info(f"User {user_id} has no PDF, skipping")
                        continue
                    
                    # Get last sent time
                    last_sent = self.db.get_last_sent(user_id)
                    
                    # If never sent or interval has passed
                    if not last_sent or (now - last_sent).total_seconds() >= Config.INTERVAL_HOURS * 3600:
                        # Get current page
                        current_page = self.db.get_current_page(user_id)
                        
                        # Increment page for next time
                        next_page = self.db.increment_page(user_id)
                        logger.info(f"User {user_id}: Incremented page from {current_page} to {next_page}")
                        
                        # Send pages
                        await self.send_pages_to_user(user_id, current_page)
                        logger.info(f"Sent scheduled pages to user {user_id}")
                    else:
                        # Calculate time until next send
                        next_send = last_sent + timedelta(hours=Config.INTERVAL_HOURS)
                        time_until = next_send - now
                        logger.info(f"User {user_id}: Next send in {time_until}")
                        
                except Exception as e:
                    logger.error(f"Error processing user {user_id}: {e}")

        except Exception as e:
            logger.error(f"Error in check_and_send_pages: {e}")

    async def upload_command(self, message: types.Message, state: FSMContext):
        """Handle /upload command"""
        user_id = message.from_user.id
        
        # Check if user exists
        if not self.db.get_user(user_id):
            await message.reply("You need to /start the bot first!")
            return
            
        await message.reply(
            "Please send me your PDF file. I'll use it for your reading."
        )
        
        # Set state to waiting for file
        await state.set_state(UploadPDF.waiting_for_file)
        
    async def process_pdf_upload(self, message: types.Message, state: FSMContext):
        """Process uploaded PDF file"""
        user_id = message.from_user.id
        
        try:
            # Check if message contains a document
            if not message.document:
                await message.reply("Please send a PDF file.")
                return
                
            # Check if the file is a PDF
            if not message.document.mime_type == 'application/pdf':
                await message.reply("Please send a PDF file.")
                return
                
            # Download the file
            file_id = message.document.file_id
            file_info = await self.bot.get_file(file_id)
            file_path = file_info.file_path
            
            # Create user directory if it doesn't exist
            user_upload_dir = os.path.join(Config.UPLOAD_DIR, str(user_id))
            os.makedirs(user_upload_dir, exist_ok=True)
            
            # Generate a filename based on the original filename or a default
            filename = message.document.file_name or f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            local_file_path = os.path.join(user_upload_dir, filename)
            
            # Download the file
            await self.bot.download_file(file_path, local_file_path)
            
            # Create a PDFReader instance to validate and set the PDF
            pdf_reader = PDFReader(user_id=user_id, output_dir=Config.OUTPUT_DIR, db=self.db)
            success = pdf_reader.set_pdf_for_user(user_id, local_file_path)
            
            if success:
                total_pages = self.db.get_total_pages(user_id)
                await message.reply(
                    f"✅ PDF successfully uploaded!\n\n"
                    f"📚 Book: {filename}\n"
                    f"📄 Total pages: {total_pages}\n\n"
                    f"Your reading starts from page 1. Use /next to get the first page."
                )
            else:
                await message.reply("❌ There was a problem with your PDF file. Please try another one.")
                # Clean up the file if there was an error
                if os.path.exists(local_file_path):
                    os.remove(local_file_path)
                    
        except Exception as e:
            logger.error(f"Error processing PDF upload: {e}")
            await message.reply("❌ An error occurred while processing your PDF. Please try again.")
        finally:
            # Reset the state
            await state.clear()
            
    async def book_command(self, message: types.Message):
        """Handle /book command to show current book info"""
        user_id = message.from_user.id
        
        # Check if user exists
        if not self.db.get_user(user_id):
            await message.reply("You need to /start the bot first!")
            return
            
        # Check if user has a PDF
        pdf_path = self.db.get_pdf_path(user_id)
        if not pdf_path or not os.path.exists(pdf_path):
            await message.reply("You haven't uploaded a book yet! Use /upload command to add a book.")
            return
            
        # Get book info
        filename = os.path.basename(pdf_path)
        current_page = self.db.get_current_page(user_id)
        total_pages = self.db.get_total_pages(user_id)
        
        # Format book info
        book_info = (
            f"📚 *Your Current Book* 📚\n\n"
            f"Title: {filename}\n"
            f"Current page: {current_page} of {total_pages}\n"
            f"Progress: {current_page/total_pages*100:.1f}%\n\n"
            f"Use /upload to change your book."
        )
        
        await message.reply(book_info)
    
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
