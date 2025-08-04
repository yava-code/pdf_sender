import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from config import Config
from database_manager import DatabaseManager
from pdf_reader import PDFReader
from scheduler import PDFScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFSenderBot:
    def __init__(self):
        Config.validate()
        self.bot = Bot(token=Config.BOT_TOKEN)
        self.dp = Dispatcher()
        self.db = DatabaseManager()
        self.pdf_reader = PDFReader()
        self.scheduler = PDFScheduler(self)
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all bot handlers"""
        self.dp.message.register(self.start_handler, Command('start'))
        self.dp.message.register(self.help_handler, Command('help'))
        self.dp.message.register(self.status_handler, Command('status'))
        self.dp.message.register(self.next_pages_handler, Command('next'))
        self.dp.message.register(self.current_page_handler, Command('current'))
        self.dp.message.register(self.goto_page_handler, Command('goto'))
    
    async def start_handler(self, message: types.Message):
        """Handle /start command"""
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
            "/status - Show current reading progress\n"
            "/next - Get next 3 pages manually\n"
            "/current - Get current page\n"
            "/goto <page> - Jump to specific page\n\n"
            "📅 The bot automatically sends pages daily according to schedule.\n"
            "📖 Use /next to get additional pages anytime!"
        )
        
        await message.answer(help_text)
    
    async def status_handler(self, message: types.Message):
        """Handle /status command"""
        current_page = self.db.get_current_page()
        total_pages = self.pdf_reader.get_total_pages()
        progress = (current_page / total_pages) * 100 if total_pages > 0 else 0
        
        status_text = (
            f"📊 Reading Progress\n\n"
            f"📖 Current page: {current_page}\n"
            f"📚 Total pages: {total_pages}\n"
            f"📈 Progress: {progress:.1f}%\n"
            f"⏰ Schedule: {Config.SCHEDULE_TIME}\n"
            f"📄 Pages per send: {Config.PAGES_PER_SEND}"
        )
        
        await message.answer(status_text)
    
    async def next_pages_handler(self, message: types.Message):
        """Handle /next command - send next 3 pages"""
        try:
            current_page = self.db.get_current_page()
            await self.send_pages_to_user(message.from_user.id, current_page, Config.PAGES_PER_SEND)
            
            # Update current page
            new_page = self.db.increment_page(Config.PAGES_PER_SEND)
            
            await message.answer(
                f"📖 Sent pages {current_page}-{current_page + Config.PAGES_PER_SEND - 1}\n"
                f"📍 Current page is now: {new_page}"
            )
            
        except Exception as e:
            logger.error(f"Error in next_pages_handler: {e}")
            await message.answer("❌ Error sending pages. Please try again later.")
    
    async def current_page_handler(self, message: types.Message):
        """Handle /current command - send current page"""
        try:
            current_page = self.db.get_current_page()
            await self.send_pages_to_user(message.from_user.id, current_page, 1)
            
            await message.answer(f"📖 Current page: {current_page}")
            
        except Exception as e:
            logger.error(f"Error in current_page_handler: {e}")
            await message.answer("❌ Error sending current page. Please try again later.")
    
    async def goto_page_handler(self, message: types.Message):
        """Handle /goto command - jump to specific page"""
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
            
            total_pages = self.pdf_reader.get_total_pages()
            if target_page < 1 or target_page > total_pages:
                await message.answer(f"❌ Page must be between 1 and {total_pages}.")
                return
            
            # Set new current page
            self.db.set_current_page(target_page)
            
            # Send the target page
            await self.send_pages_to_user(message.from_user.id, target_page, 1)
            
            await message.answer(f"📖 Jumped to page {target_page}")
            
        except Exception as e:
            logger.error(f"Error in goto_page_handler: {e}")
            await message.answer("❌ Error jumping to page. Please try again later.")
    
    async def send_pages_to_user(self, user_id: int, start_page: int, num_pages: int):
        """Send PDF pages as images to a user"""
        try:
            # Extract pages as images
            image_paths = self.pdf_reader.extract_pages_as_images(start_page, num_pages)
            
            if not image_paths:
                await self.bot.send_message(user_id, "❌ No pages to send.")
                return
            
            # Send each page as photo
            for i, image_path in enumerate(image_paths):
                page_number = start_page + i
                
                # Create caption
                caption = f"📖 Page {page_number}"
                
                # Send photo
                photo = FSInputFile(image_path)
                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=caption
                )
            
            logger.info(f"Sent {len(image_paths)} pages to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending pages to user {user_id}: {e}")
            await self.bot.send_message(user_id, "❌ Error sending pages. Please try again later.")
    
    async def send_daily_pages(self):
        """Send daily pages to all users"""
        try:
            users = self.db.get_users()
            if not users:
                logger.info("No users to send pages to")
                return
            
            current_page = self.db.get_current_page()
            
            # Send pages to all users
            for user in users:
                try:
                    await self.send_pages_to_user(user['id'], current_page, Config.PAGES_PER_SEND)
                except Exception as e:
                    logger.error(f"Error sending daily pages to user {user['id']}: {e}")
            
            # Update current page
            new_page = self.db.increment_page(Config.PAGES_PER_SEND)
            logger.info(f"Daily pages sent. Current page updated to: {new_page}")
            
        except Exception as e:
            logger.error(f"Error in send_daily_pages: {e}")
    
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

if __name__ == '__main__':
    asyncio.run(main())