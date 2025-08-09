import os
from unittest.mock import patch

import pytest

from config import get_config


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
            # Clear cache and get new config
            get_config.cache_clear()
            config_instance = get_config()

            assert config_instance.bot_token == "test_token_123"
            assert config_instance.pages_per_send == 5
            assert config_instance.schedule_time == "10:30"
            assert config_instance.pdf_path == "test.pdf"
            assert config_instance.output_dir == "test_output"
            assert config_instance.database_path == "test_db.json"

    def test_config_with_defaults(self):
        """Test config with default values"""
        with patch.dict(
            os.environ,
            {
                "BOT_TOKEN": "test_token_123",
            },
            clear=True,
        ):
            # Clear cache and get new config
            get_config.cache_clear()
            config_instance = get_config()

            assert config_instance.bot_token == "test_token_123"
            assert config_instance.pages_per_send == 3
            assert config_instance.schedule_time == "14:00"
            assert config_instance.pdf_path == "book.pdf"
            assert config_instance.output_dir == "output"
            assert config_instance.database_path == "pdf_sender.json"


    def test_validate_missing_pdf(self):
        """Test validation no longer checks for PDF file since app supports
        per-user uploads"""
        with patch.dict(
            os.environ, {"BOT_TOKEN": "test_token_123", "PDF_PATH": "nonexistent.pdf"}
        ):
            # Clear cache and get new config
            get_config.cache_clear()
            config_instance = get_config()

            # Should not raise an error as PDF validation is removed
            # for per-user support
            # Config creation should succeed even with nonexistent PDF
            assert config_instance.pdf_path == "nonexistent.pdf"
