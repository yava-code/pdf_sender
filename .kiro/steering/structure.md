# Project Structure

## Root Directory Layout

```
pdf_sender/
├── main.py                 # Main bot application entry point
├── config.py              # Centralized configuration with Pydantic
├── database_manager.py    # JSON database operations and user management
├── pdf_reader.py          # PDF processing and image extraction
├── scheduler.py           # Daily scheduling functionality
├── user_settings.py       # Individual user preferences management
├── keyboards.py           # Telegram inline keyboard layouts
├── callback_handlers.py   # Telegram callback query handlers
├── message_handlers.py    # Telegram message handlers
├── cleanup_manager.py     # File cleanup and maintenance
├── file_validator.py      # File upload validation
├── logger_config.py       # Logging configuration
├── bot_logger.py          # Bot-specific logging utilities
├── rate_limiter.py        # Rate limiting functionality
├── security.py           # Security utilities
├── metrics.py             # Prometheus metrics collection
├── exceptions.py          # Custom exception classes
└── requirements.txt       # Python dependencies
```

## Key Directories

- **`tests/`**: Comprehensive test suite with pytest
- **`logs/`**: Application logs (bot.log, errors.log, user_actions.log)
- **`uploads/`**: User-uploaded PDF files
- **`output/`**: Generated page images (auto-cleaned)
- **`backups/`**: Database backups
- **`.github/workflows/`**: CI/CD pipeline configuration

## Architecture Patterns

### Main Components
- **PDFSenderBot**: Main bot class orchestrating all functionality
- **DatabaseManager**: Handles all data persistence operations
- **PDFReader**: Manages PDF processing and image generation
- **PDFScheduler**: Handles automated scheduling logic
- **UserSettings**: Manages individual user preferences

### Handler Pattern
- **CallbackHandler**: Processes inline keyboard interactions
- **MessageHandler**: Processes text messages and state-based flows
- **Command handlers**: Individual functions for each bot command

### Configuration
- Single `config.py` with Pydantic models for type safety
- Environment variable support with `.env` files
- Validation and default values built-in

### Database Schema
- JSON file-based storage in `database.json`
- User objects with progress tracking, settings, and gamification data
- Achievements, leaderboards, and reading sessions

### File Organization
- Each major feature has its own module
- Clear separation of concerns
- Async/await pattern throughout for Telegram operations