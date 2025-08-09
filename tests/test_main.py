from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiogram import types

from main import PDFSenderBot


class TestPDFSenderBot:
    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        with patch("main.Config") as mock_config:
            mock_config.BOT_TOKEN = "test_token"
            mock_config.PAGES_PER_SEND = 3
            mock_config.INTERVAL_HOURS = 6
            mock_config.UPLOAD_DIR = "test_uploads"
            mock_config.validate.return_value = None
            yield mock_config

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies"""
        with patch("main.Bot") as mock_bot, patch("main.Dispatcher") as mock_dp, patch(
            "main.DatabaseManager"
        ) as mock_db, patch("main.PDFReader") as mock_pdf_reader, patch(
            "main.PDFScheduler"
        ) as mock_scheduler, patch("main.UserSettings") as mock_user_settings:

            # Setup mocks
            mock_bot_instance = Mock()
            mock_dp_instance = Mock()
            mock_db_instance = Mock()
            mock_pdf_reader_instance = Mock()
            mock_scheduler_instance = Mock()
            mock_user_settings_instance = Mock()

            mock_bot.return_value = mock_bot_instance
            mock_dp.return_value = mock_dp_instance
            mock_db.return_value = mock_db_instance
            mock_pdf_reader.return_value = mock_pdf_reader_instance
            mock_scheduler.return_value = mock_scheduler_instance
            mock_user_settings.return_value = mock_user_settings_instance

            yield {
                "bot": mock_bot_instance,
                "dp": mock_dp_instance,
                "db": mock_db_instance,
                "pdf_reader": mock_pdf_reader_instance,
                "scheduler": mock_scheduler_instance,
                "user_settings": mock_user_settings_instance,
            }

    @pytest.fixture
    def pdf_bot(self, mock_config, mock_dependencies):
        """Create PDFSenderBot instance with mocked dependencies"""
        return PDFSenderBot()

    @pytest.fixture
    def mock_message(self):
        """Create a mock message"""
        message = Mock(spec=types.Message)
        message.from_user = Mock()
        message.from_user.id = 12345
        message.from_user.username = "test_user"
        message.answer = AsyncMock()
        message.text = "/start"
        return message

    @pytest.mark.asyncio
    async def test_start_handler(self, pdf_bot, mock_message, mock_dependencies):
        """Test /start command handler"""
        await pdf_bot.start_handler(mock_message)

        # Check that user was added to database
        mock_dependencies["db"].add_user.assert_called_once_with(12345, "test_user")

        # Check that welcome message was sent
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Welcome to PDF Sender Bot" in call_args

    @pytest.mark.asyncio
    async def test_help_handler(self, pdf_bot, mock_message):
        """Test /help command handler"""
        await pdf_bot.help_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "PDF Sender Bot Help" in call_args
        assert "/start" in call_args
        assert "/next" in call_args

    @pytest.mark.asyncio
    async def test_status_handler(self, pdf_bot, mock_message, mock_dependencies):
        """Test /status command handler"""
        # Setup mock returns
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_current_page.return_value = 10
        mock_dependencies["db"].get_total_pages.return_value = 100
        mock_dependencies["db"].get_last_sent.return_value = None

        # Mock os.path.exists to return True for the PDF path
        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.status_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Reading Progress" in call_args
        assert "Current page: 10" in call_args
        assert "Total pages: 100" in call_args
        assert "Progress: 10.0%" in call_args

    @pytest.mark.asyncio
    async def test_next_pages_handler(self, pdf_bot, mock_message, mock_dependencies):
        """Test /next command handler"""
        # Setup mock returns
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_current_page.return_value = 5
        mock_dependencies["db"].get_total_pages.return_value = 100
        mock_dependencies["db"].increment_page.return_value = 8

        # Mock send_pages_to_user method
        pdf_bot.send_pages_to_user = AsyncMock()

        # Mock user settings
        mock_dependencies["user_settings"].get_user_settings.return_value = {
            "pages_per_send": 3
        }

        # Mock os.path.exists to return True for the PDF path
        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.next_pages_handler(mock_message)

        # Check that pages were sent
        pdf_bot.send_pages_to_user.assert_called_once_with(12345, 5)

        # Check that page was incremented
        mock_dependencies["db"].increment_page.assert_called_once_with(12345, 3)

        # Check response message
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Sent pages 5-7" in call_args
        assert "Current page is now: 8" in call_args

    @pytest.mark.asyncio
    async def test_current_page_handler(self, pdf_bot, mock_message, mock_dependencies):
        """Test /current command handler"""
        # Setup mock returns
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_current_page.return_value = 15

        # Mock PDFReader instance
        mock_pdf_reader_instance = Mock()
        mock_pdf_reader_instance.extract_pages_as_images.return_value = ["page_15.png"]
        mock_pdf_reader_instance.cleanup_images.return_value = None

        # Mock bot send_photo method
        mock_dependencies["bot"].send_photo = AsyncMock()

        # Mock os.path.exists to return True for the PDF path
        with patch("main.os.path.exists", return_value=True), patch(
            "main.PDFReader", return_value=mock_pdf_reader_instance
        ):
            await pdf_bot.current_page_handler(mock_message)

        # Check that send_photo was called
        mock_dependencies["bot"].send_photo.assert_called_once()
        call_args = mock_dependencies["bot"].send_photo.call_args
        assert call_args[1]["chat_id"] == 12345
        assert "Current page: 15" in call_args[1]["caption"]

    @pytest.mark.asyncio
    async def test_goto_page_handler_valid(
        self, pdf_bot, mock_message, mock_dependencies
    ):
        """Test /goto command handler with valid page"""
        # Setup message text
        mock_message.text = "/goto 25"

        # Setup mock returns
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_total_pages.return_value = 100

        # Mock _send_single_page method
        pdf_bot._send_single_page = AsyncMock()

        # Mock os.path.exists to return True for the PDF path
        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.goto_page_handler(mock_message)

        # Check that page was set
        mock_dependencies["db"].set_current_page.assert_called_once_with(12345, 25)

        # Check that page was sent
        pdf_bot._send_single_page.assert_called_once_with(12345, 25)

    @pytest.mark.asyncio
    async def test_goto_page_handler_invalid_format(
        self, pdf_bot, mock_message, mock_dependencies
    ):
        """Test /goto command handler with invalid format"""
        mock_message.text = "/goto"

        # Setup mock returns
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"

        # Mock os.path.exists to return True for the PDF path
        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.goto_page_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Usage: /goto <page_number>" in call_args

    @pytest.mark.asyncio
    async def test_goto_page_handler_invalid_number(
        self, pdf_bot, mock_message, mock_dependencies
    ):
        """Test /goto command handler with invalid page number"""
        mock_message.text = "/goto abc"

        # Setup mock returns
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"

        # Mock os.path.exists to return True for the PDF path
        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.goto_page_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Usage: /goto <page_number>" in call_args

    @pytest.mark.asyncio
    async def test_goto_page_handler_out_of_range(
        self, pdf_bot, mock_message, mock_dependencies
    ):
        """Test /goto command handler with page out of range"""
        mock_message.text = "/goto 150"

        # Setup mock returns
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_total_pages.return_value = 100

        # Mock os.path.exists to return True for the PDF path
        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.goto_page_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Page must be between 1 and 100" in call_args

    @pytest.mark.asyncio
    async def test_send_pages_to_user(self, pdf_bot, mock_dependencies):
        """Test sending pages to user"""
        # Setup mock PDFReader instance
        mock_pdf_reader_instance = Mock()
        mock_pdf_reader_instance.extract_pages_as_images.return_value = [
            "page_1.png",
            "page_2.png",
            "page_3.png",
        ]
        mock_pdf_reader_instance.cleanup_images.return_value = None

        # Setup mock database returns
        mock_dependencies["db"].get_total_pages.return_value = 100

        # Mock bot methods
        mock_dependencies["bot"].send_message = AsyncMock()
        mock_dependencies["bot"].send_photo = AsyncMock()

        # Patch PDFReader constructor
        with patch("main.PDFReader", return_value=mock_pdf_reader_instance):
            await pdf_bot.send_pages_to_user(12345, 1)

        # Check that initial message was sent
        mock_dependencies["bot"].send_message.assert_called()
        send_message_calls = mock_dependencies["bot"].send_message.call_args_list
        assert any("Page 1 of 100" in str(call) for call in send_message_calls)

        # Check that photos were sent
        assert mock_dependencies["bot"].send_photo.call_count == 3

        # Check that database was updated
        mock_dependencies["db"].update_last_sent.assert_called_once_with(12345)

    @pytest.mark.asyncio
    async def test_send_pages_to_user_no_pages(self, pdf_bot, mock_dependencies):
        """Test sending pages when no pages are available"""
        # Setup mock PDFReader instance that returns no pages
        mock_pdf_reader_instance = Mock()
        mock_pdf_reader_instance.extract_pages_as_images.return_value = []

        # Mock bot methods
        mock_dependencies["bot"].send_message = AsyncMock()

        # Patch PDFReader constructor
        with patch("main.PDFReader", return_value=mock_pdf_reader_instance):
            await pdf_bot.send_pages_to_user(12345, 1)

        # Check that error message was sent
        mock_dependencies["bot"].send_message.assert_called_once_with(
            12345, "❌ No pages to send."
        )

    @pytest.mark.asyncio
    async def test_check_and_send_pages(self, pdf_bot, mock_dependencies):
        """Test checking and sending pages to all users"""
        # Setup mock returns
        mock_dependencies["db"].get_users.return_value = [
            {"id": 123, "username": "user1"},
            {"id": 456, "username": "user2"},
        ]

        # Mock per-user database calls
        def mock_get_pdf_path(user_id):
            return "test.pdf"

        def mock_get_last_sent(user_id):
            return None  # Never sent before

        def mock_get_current_page(user_id):
            return 10

        def mock_increment_page(user_id, increment):
            assert increment == 3
            return 13

        def mock_get_total_pages(user_id):
            return 100

        mock_dependencies["db"].get_pdf_path.side_effect = mock_get_pdf_path
        mock_dependencies["db"].get_last_sent.side_effect = mock_get_last_sent
        mock_dependencies["db"].get_current_page.side_effect = mock_get_current_page
        mock_dependencies["db"].get_total_pages.side_effect = mock_get_total_pages
        mock_dependencies["db"].increment_page.side_effect = mock_increment_page

        # Mock send_pages_to_user method
        pdf_bot.send_pages_to_user = AsyncMock()

        # Mock user settings to enable auto-send and use interval-based sending
        def mock_get_user_settings(user_id):
            return {
                "auto_send_enabled": True,
                "schedule_time": "disabled",
                "interval_hours": 6,
                "pages_per_send": 3
            }
        
        mock_dependencies["user_settings"].get_user_settings.side_effect = mock_get_user_settings

        # Mock os.path.exists to return True for all PDF paths
        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.check_and_send_pages()

        # Check that pages were sent to all users
        assert pdf_bot.send_pages_to_user.call_count == 2
        pdf_bot.send_pages_to_user.assert_any_call(123, 10)
        pdf_bot.send_pages_to_user.assert_any_call(456, 10)

    @pytest.mark.asyncio
    async def test_check_and_send_pages_no_users(self, pdf_bot, mock_dependencies):
        """Test checking and sending pages when no users exist"""
        mock_dependencies["db"].get_users.return_value = []

        await pdf_bot.check_and_send_pages()

        # Should not increment page when no users
        mock_dependencies["db"].increment_page.assert_not_called()
