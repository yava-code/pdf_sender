import os
from unittest.mock import patch

import pytest

from config import Config


class TestConfig:
    def test_config_with_valid_env(self):
        """Test config with valid environment variables"""
        with patch.dict(
            os.environ,
            {
                "BOT_TOKEN": "test_token_123",
                "PAGES_PER_SEND": "5",
                "SCHEDULE_TIME": "10:30",
                "PDF_PATH": "test.pdf",
                "OUTPUT_DIR": "test_output",
                "DATABASE_PATH": "test_db.json",
            },
        ):
            # Reload config
            from importlib import reload

            import config

            reload(config)

            assert config.Config.BOT_TOKEN == "test_token_123"
            assert config.Config.PAGES_PER_SEND == 5
            assert config.Config.SCHEDULE_TIME == "10:30"
            assert config.Config.PDF_PATH == "test.pdf"
            assert config.Config.OUTPUT_DIR == "test_output"
            assert config.Config.DATABASE_PATH == "test_db.json"

    def test_config_with_defaults(self):
        """Test config with default values"""
        with patch.dict(
            os.environ,
            {
                "BOT_TOKEN": "test_token_123",
                "PAGES_PER_SEND": "3",
                "SCHEDULE_TIME": "09:00",
                "PDF_PATH": "book.pdf",
                "OUTPUT_DIR": "output",
                "DATABASE_PATH": "database.json",
            },
            clear=True,
        ):
            from importlib import reload

            import config

            reload(config)

            assert config.Config.BOT_TOKEN == "test_token_123"
            assert config.Config.PAGES_PER_SEND == 3
            assert config.Config.SCHEDULE_TIME == "09:00"
            assert config.Config.PDF_PATH == "book.pdf"
            assert config.Config.OUTPUT_DIR == "output"
            assert config.Config.DATABASE_PATH == "database.json"

    @patch.object(Config, "BOT_TOKEN", None)
    def test_validate_missing_token(self):
        """Test validation fails when BOT_TOKEN is missing."""
        with pytest.raises(
            ValueError, match="BOT_TOKEN environment variable is required"
        ):
            Config.validate()

    def test_validate_missing_pdf(self):
        """Test validation no longer checks for PDF file since app supports
        per-user uploads"""
        with patch.dict(
            os.environ, {"BOT_TOKEN": "test_token_123", "PDF_PATH": "nonexistent.pdf"}
        ):
            from importlib import reload

            import config

            reload(config)

            # Should not raise an error as PDF validation is removed
            # for per-user support
            config.Config.validate()
