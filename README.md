# PDF Sender Bot

[![Python Package using Conda](https://github.com/yava-code/pdf_sender/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/yourusername/pdf_sender/actions/workflows/python-package-conda.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

telegram bot that sends pdf pages automatically on schedule... pretty useful for reading books i guess

## features

- daily page delivery - sends pages automatically 
- manual requests - get pages whenever you want
- progress tracking - keeps track of where you are
- page jumping - go to any page
- multiple users - works for multiple people (shared progress though)
- basic gamification stuff:
  - points for reading
  - levels 
  - achievements and stuff
  - leaderboards if youre into that
  - reading streaks
- json database (simple file storage)
- some tests
- environment config

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/botfather))
- A PDF file you want to read

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pdf_sender.git
   cd pdf_sender
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   PAGES_PER_SEND=3
   SCHEDULE_TIME=09:00
   PDF_PATH=book.pdf
   OUTPUT_DIR=output
   DATABASE_PATH=database.json
   ```

4. **Add your PDF file**
   
   Place your PDF file in the project directory and name it `book.pdf` (or update `PDF_PATH` in `.env`)

5. **Run the bot**
   ```bash
   python main.py
   ```

## 📋 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Your Telegram bot token | - | ✅ |
| `PAGES_PER_SEND` | Number of pages to send at once | `3` | ❌ |
| `SCHEDULE_TIME` | Daily send time (HH:MM format) | `09:00` | ❌ |
| `PDF_PATH` | Path to your PDF file | `book.pdf` | ❌ |
| `OUTPUT_DIR` | Directory for generated images | `output` | ❌ |
| `DATABASE_PATH` | Path to JSON database file | `database.json` | ❌ |

## 🤖 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start using the bot and get welcome message | `/start` |
| `/help` | Show help message with all commands | `/help` |
| `/status` | Show current reading progress | `/status` |
| `/next` | Get next 3 pages manually | `/next` |
| `/current` | Get the current page | `/current` |
| `/goto <page>` | Jump to a specific page | `/goto 25` |
| `/stats` | Show your reading statistics | `/stats` |
| `/leaderboard` | Show the leaderboard | `/leaderboard` |
| `/achievements`| Show your achievements | `/achievements` |

## 📁 Project Structure

```
pdf_sender/
├── 📄 main.py              # Main bot application
├── ⚙️ config.py            # Configuration management
├── 🗄️ database_manager.py  # JSON database operations
├── 📖 pdf_reader.py        # PDF processing and image extraction
├── ⏰ scheduler.py         # Daily scheduling functionality
├── 📋 requirements.txt     # Python dependencies
├── 🗃️ database.json       # User data and progress storage
├── 📚 README.md           # This file
├── 🧪 pytest.ini         # Test configuration
├── 📁 tests/              # Test suite
│   ├── test_config.py
│   ├── test_database_manager.py
│   ├── test_pdf_reader.py
│   └── test_main.py
├── 📁 .github/
│   └── workflows/
│       └── python-package-conda.yml
└── 📁 output/             # Generated page images (auto-created)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v
```

## 🔧 Development

### Code Quality

This project uses several tools to maintain code quality:

```bash
# Format code with Black
black .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

### Adding New Features

1. Create a new branch for your feature
2. Write tests for your new functionality
3. Implement the feature
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request

## 📊 Database Schema

The bot uses a simple JSON file for data storage. Here is an example of the user object:

```json
{
    "id": 123456789,
    "username": "user123",
    "joined_at": "2023-10-27T10:00:00",
    "current_page": 1,
    "total_pages": 100,
    "pdf_path": "path/to/book.pdf",
    "last_sent": "2023-10-27T10:00:00",
    "total_points": 150,
    "pages_read": 30,
    "books_completed": 0,
    "current_streak": 5,
    "longest_streak": 10,
    "last_read_date": "2023-10-27",
    "achievements": ["first_page", "page_10"],
    "reading_sessions": [],
    "level": 2,
    "experience": 150
}
```

## 🚀 Deployment

### Using Docker (Recommended)

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Using systemd (Linux)

Create a service file `/etc/systemd/system/pdf-sender-bot.service`:

```ini
[Unit]
Description=PDF Sender Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/pdf_sender
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
EnvironmentFile=/path/to/pdf_sender/.env

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable pdf-sender-bot
sudo systemctl start pdf-sender-bot
```

## 🔍 Troubleshooting

### Common Issues

**Bot doesn't respond to commands**
- Check if `BOT_TOKEN` is correctly set
- Verify the bot is running without errors
- Ensure the bot has been started with `/start` command

**PDF pages not generating**
- Check if the PDF file exists at the specified path
- Verify the PDF is not corrupted or password-protected
- Ensure sufficient disk space for image generation

**Scheduled messages not sending**
- Check the `SCHEDULE_TIME` format (must be HH:MM)
- Verify the bot process is running continuously
- Check logs for any scheduler errors

### Logs

The bot provides detailed logging. Check the console output for:
- User interactions
- Scheduled job execution
- Error messages and stack traces
- Database operations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Install development dependencies (`pip install -r requirements.txt`)
4. Make your changes
5. Add tests for your changes
6. Ensure tests pass (`pytest`)
7. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
8. Push to the branch (`git push origin feature/AmazingFeature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [aiogram](https://github.com/aiogram/aiogram) - Modern and fully asynchronous framework for Telegram Bot API
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - Python bindings for MuPDF's rendering capabilities
- [APScheduler](https://github.com/agronholm/apscheduler) - Advanced Python Scheduler

