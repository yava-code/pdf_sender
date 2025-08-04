import pytest
import os
from unittest.mock import patch
from config import Config

class TestConfig:
    def test_config_with_valid_env(self):
        """Test config with valid environment variables"""
        with patch.dict(os.environ, {
            'BOT_TOKEN': 'test_token_123',
            'PAGES_PER_SEND': '5',
            'SCHEDULE_TIME': '10:30',
            'PDF_PATH': 'test.pdf',
            'OUTPUT_DIR': 'test_output',
            'DATABASE_PATH': 'test_db.json'
        }):
            # Reload config
            from importlib import reload
            import config
            reload(config)
            
            assert config.Config.BOT_TOKEN == 'test_token_123'
            assert config.Config.PAGES_PER_SEND == 5
            assert config.Config.SCHEDULE_TIME == '10:30'
            assert config.Config.PDF_PATH == 'test.pdf'
            assert config.Config.OUTPUT_DIR == 'test_output'
            assert config.Config.DATABASE_PATH == 'test_db.json'
    
    def test_config_with_defaults(self):
        """Test config with default values"""
        with patch.dict(os.environ, {
            'BOT_TOKEN': 'test_token_123'
        }, clear=True):
            from importlib import reload
            import config
            reload(config)
            
            assert config.Config.BOT_TOKEN == 'test_token_123'
            assert config.Config.PAGES_PER_SEND == 3
            assert config.Config.SCHEDULE_TIME == '09:00'
            assert config.Config.PDF_PATH == 'book.pdf'
            assert config.Config.OUTPUT_DIR == 'output'
            assert config.Config.DATABASE_PATH == 'database.json'
    
    def test_validate_missing_token(self):
        """Test validation fails when BOT_TOKEN is missing."""
        # Save original value
        original_token = os.environ.get("BOT_TOKEN")
        
        try:
            # Remove BOT_TOKEN from environment
            if "BOT_TOKEN" in os.environ:
                del os.environ["BOT_TOKEN"]
            
            # Reload the config module to pick up the environment change
            from importlib import reload
            import config
            reload(config)
            
            with pytest.raises(ValueError, match="BOT_TOKEN environment variable is required"):
                config.Config.validate()
        finally:
            # Restore original value
            if original_token is not None:
                os.environ["BOT_TOKEN"] = original_token
                # Reload again to restore the original state
                import config
                reload(config)
    
    def test_validate_missing_pdf(self):
        """Test validation with missing PDF file"""
        with patch.dict(os.environ, {
            'BOT_TOKEN': 'test_token_123',
            'PDF_PATH': 'nonexistent.pdf'
        }):
            from importlib import reload
            import config
            reload(config)
            
            with pytest.raises(FileNotFoundError, match="PDF file not found"):
                config.Config.validate()