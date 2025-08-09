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
        ) as mock_scheduler:

            # Setup mocks
            mock_bot_instance = Mock()
            mock_dp_instance = Mock()
            mock_db_instance = Mock()
            mock_pdf_reader_instance = Mock()
            mock_scheduler_instance = Mock()

            mock_bot.return_value = mock_bot_instance
            mock_dp.return_value = mock_dp_instance
            mock_db.return_value = mock_db_instance
            mock_pdf_reader.return_value = mock_pdf_reader_instance
            mock_scheduler.return_value = mock_scheduler_instance

            yield {
                "bot": mock_bot_instance,
                "dp": mock_dp_instance,
                "db": mock_db_instance,
                "pdf_reader": mock_pdf_reader_instance,
                "scheduler": mock_scheduler_instance,
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

    @pytest.fixture
    def complete_user_settings(self):
        """A complete user settings dictionary for mocking."""
        return {
            "auto_send_enabled": True,
            "schedule_time": "09:00",
            "pages_per_send": 3,
            "interval_hours": 6,
            "image_quality": 85,
            "notifications_enabled": True,
        }

    @pytest.mark.asyncio
    async def test_start_handler(self, pdf_bot, mock_message, mock_dependencies):
        """Test /start command handler"""
        await pdf_bot.start_handler(mock_message)

        # Check that user was added to database
        mock_dependencies["db"].add_user.assert_called_once_with(12345, "test_user")

        # Check that welcome message was sent
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Добро пожаловать в PDF Sender Bot" in call_args

    @pytest.mark.asyncio
    async def test_help_handler(self, pdf_bot, mock_message):
        """Test /help command handler"""
        await pdf_bot.help_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Справка по боту" in call_args
        assert "/start" in call_args
        assert "/next" in call_args

    @pytest.mark.asyncio
    async def test_status_handler(
        self, pdf_bot, mock_message, mock_dependencies, complete_user_settings
    ):
        """Test /status command handler"""
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_current_page.return_value = 10
        mock_dependencies["db"].get_total_pages.return_value = 100
        mock_dependencies["db"].get_last_sent.return_value = None

        with patch.object(
            pdf_bot.user_settings, "get_user_settings", return_value=complete_user_settings
        ), patch("main.os.path.exists", return_value=True):
            await pdf_bot.status_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]

        # Use line-by-line check for robustness
        lines = [line.strip() for line in call_args.split('\n')]
        assert "📊 **Статус чтения** 📊" in lines
        assert "📖 **Текущая страница:** 10" in lines
        assert "📄 **Всего страниц:** 100" in lines
        assert "📈 **Прогресс:** 10.0%" in lines
        assert "🔄 **Автоотправка:** ✅ Включена" in call_args # Check in raw string for compound line
        assert "🕐 **Время отправки:** 09:00" in call_args # Check in raw string for compound line


    @pytest.mark.asyncio
    async def test_next_pages_handler(
        self, pdf_bot, mock_message, mock_dependencies, complete_user_settings
    ):
        """Test /next command handler"""
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_current_page.side_effect = [5, 8]
        mock_dependencies["db"].get_total_pages.return_value = 100

        pdf_bot.send_pages_to_user = AsyncMock()

        with patch.object(
            pdf_bot.user_settings, "get_user_settings", return_value=complete_user_settings
        ), patch("main.os.path.exists", return_value=True):
            await pdf_bot.next_pages_handler(mock_message)

        pdf_bot.send_pages_to_user.assert_called_once_with(12345, 5)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Отправлены страницы 5-7" in call_args
        assert "Текущая страница: 8 из 100" in call_args

    @pytest.mark.asyncio
    async def test_current_page_handler(
        self, pdf_bot, mock_message, mock_dependencies, complete_user_settings
    ):
        """Test /current command handler"""
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_current_page.return_value = 15
        mock_dependencies["db"].get_total_pages.return_value = 100

        mock_pdf_reader_instance = Mock()
        mock_pdf_reader_instance.extract_pages_as_images.return_value = ["page_15.png"]
        mock_pdf_reader_instance.cleanup_images.return_value = None

        mock_dependencies["bot"].send_photo = AsyncMock()

        with patch.object(
            pdf_bot.user_settings, "get_user_settings", return_value=complete_user_settings
        ), patch("main.os.path.exists", return_value=True), patch(
            "main.PDFReader", return_value=mock_pdf_reader_instance
        ):
            await pdf_bot.current_page_handler(mock_message)

        mock_dependencies["bot"].send_photo.assert_called_once()
        call_args = mock_dependencies["bot"].send_photo.call_args
        assert call_args[1]["chat_id"] == 12345
        assert "Текущая страница: 15 из 100" in call_args[1]["caption"]

    @pytest.mark.asyncio
    async def test_goto_page_handler_valid(
        self, pdf_bot, mock_message, mock_dependencies, complete_user_settings
    ):
        """Test /goto command handler with valid page"""
        mock_message.text = "/goto 25"
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_total_pages.return_value = 100

        pdf_bot._send_single_page = AsyncMock()

        with patch.object(
            pdf_bot.user_settings, "get_user_settings", return_value=complete_user_settings
        ), patch("main.os.path.exists", return_value=True):
            await pdf_bot.goto_page_handler(mock_message)

        mock_dependencies["db"].set_current_page.assert_called_once_with(12345, 25)
        pdf_bot._send_single_page.assert_called_once_with(12345, 25)

    @pytest.mark.asyncio
    async def test_goto_page_handler_invalid_format(
        self, pdf_bot, mock_message, mock_dependencies
    ):
        """Test /goto command handler with invalid format"""
        mock_message.text = "/goto"
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"

        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.goto_page_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Неверный формат команды" in call_args

    @pytest.mark.asyncio
    async def test_goto_page_handler_invalid_number(
        self, pdf_bot, mock_message, mock_dependencies
    ):
        """Test /goto command handler with invalid page number"""
        mock_message.text = "/goto abc"
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"

        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.goto_page_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Неверный формат команды" in call_args

    @pytest.mark.asyncio
    async def test_goto_page_handler_out_of_range(
        self, pdf_bot, mock_message, mock_dependencies
    ):
        """Test /goto command handler with page out of range"""
        mock_message.text = "/goto 150"
        mock_dependencies["db"].get_user.return_value = {"id": 12345}
        mock_dependencies["db"].get_pdf_path.return_value = "test.pdf"
        mock_dependencies["db"].get_total_pages.return_value = 100

        with patch("main.os.path.exists", return_value=True):
            await pdf_bot.goto_page_handler(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "Страница вне диапазона" in call_args

    @pytest.mark.asyncio
    async def test_send_pages_to_user(
        self, pdf_bot, mock_dependencies, complete_user_settings
    ):
        """Test sending pages to user"""
        mock_pdf_reader_instance = Mock()
        mock_pdf_reader_instance.extract_pages_as_images.return_value = [
            "page_1.png",
            "page_2.png",
            "page_3.png",
        ]
        mock_pdf_reader_instance.cleanup_images.return_value = None

        mock_dependencies["db"].get_total_pages.return_value = 100
        mock_dependencies["db"].get_user.return_value = {"username": "test_user"}

        mock_dependencies["bot"].send_message = AsyncMock()
        mock_dependencies["bot"].send_photo = AsyncMock()

        with patch.object(
            pdf_bot.user_settings, "get_user_settings", return_value=complete_user_settings
        ), patch("main.PDFReader", return_value=mock_pdf_reader_instance):
            await pdf_bot.send_pages_to_user(12345, 1)

        mock_dependencies["bot"].send_message.assert_called()
        send_message_calls = mock_dependencies["bot"].send_message.call_args_list
        assert any("Страница 1 из 100" in str(call) for call in send_message_calls)

        assert mock_dependencies["bot"].send_photo.call_count == 3
        mock_dependencies["db"].update_last_sent.assert_called_once_with(12345)
        mock_dependencies["db"].set_current_page.assert_called_once_with(12345, 4)

    @pytest.mark.asyncio
    async def test_send_pages_to_user_no_pages(
        self, pdf_bot, mock_dependencies, complete_user_settings
    ):
        """Test sending pages when no pages are available"""
        mock_pdf_reader_instance = Mock()
        mock_pdf_reader_instance.extract_pages_as_images.return_value = []

        mock_dependencies["bot"].send_message = AsyncMock()
        mock_dependencies["db"].get_user.return_value = {"username": "test_user"}

        with patch.object(
            pdf_bot.user_settings, "get_user_settings", return_value=complete_user_settings
        ), patch("main.PDFReader", return_value=mock_pdf_reader_instance):
            await pdf_bot.send_pages_to_user(12345, 1)

        mock_dependencies["bot"].send_message.assert_called_once_with(
            12345, "❌ Нет страниц для отправки."
        )

    @pytest.mark.asyncio
    async def test_check_and_send_pages(
        self, pdf_bot, mock_dependencies, complete_user_settings
    ):
        """Test checking and sending pages to all users"""
        mock_dependencies["db"].get_users.return_value = [
            {"id": 123, "username": "user1"},
            {"id": 456, "username": "user2"},
        ]
        mock_dependencies["db"].get_total_pages.return_value = 100

        def mock_get_pdf_path(user_id):
            return "test.pdf"

        def mock_get_last_sent(user_id):
            return None

        def mock_get_current_page(user_id):
            return 10

        mock_dependencies["db"].get_pdf_path.side_effect = mock_get_pdf_path
        mock_dependencies["db"].get_last_sent.side_effect = mock_get_last_sent
        mock_dependencies["db"].get_current_page.side_effect = mock_get_current_page

        pdf_bot.send_pages_to_user = AsyncMock()

        settings = complete_user_settings.copy()
        settings["auto_send_enabled"] = True
        settings["schedule_time"] = "disabled"
        settings["interval_hours"] = 1

        with patch.object(
            pdf_bot.user_settings, "get_user_settings", return_value=settings
        ), patch("main.os.path.exists", return_value=True):
            await pdf_bot.check_and_send_pages()

        assert pdf_bot.send_pages_to_user.call_count == 2
        pdf_bot.send_pages_to_user.assert_any_call(123, 10)
        pdf_bot.send_pages_to_user.assert_any_call(456, 10)

    @pytest.mark.asyncio
    async def test_check_and_send_pages_no_users(self, pdf_bot, mock_dependencies):
        """Test checking and sending pages when no users exist"""
        mock_dependencies["db"].get_users.return_value = []
        await pdf_bot.check_and_send_pages()
        mock_dependencies["db"].increment_page.assert_not_called()
