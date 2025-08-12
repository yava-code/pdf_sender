# Technology Stack

## Core Technologies

- **Python 3.8+**: Main programming language
- **aiogram 3.10+**: Async Telegram Bot API framework
- **PyMuPDF (fitz)**: PDF processing and image extraction
- **APScheduler**: Task scheduling for automated page delivery
- **Pydantic**: Configuration management and data validation
- **JSON**: File-based database storage

## Key Libraries

- `python-dotenv`: Environment variable management
- `aiofiles`: Async file operations
- `psutil`: System monitoring
- `structlog`: Structured logging
- `prometheus-client`: Metrics collection
- `typing-extensions`: Enhanced type hints

## Development Tools

- **pytest**: Testing framework with async support
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking
- **bandit**: Security analysis

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
pytest --cov=. --cov-report=html
pytest -v

# Code quality
black .
isort .
flake8 .
mypy .
```

### Running
```bash
# Start bot
python main.py

# With environment file
python main.py  # Automatically loads .env
```

### Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f pdf-sender-bot

# Stop
docker-compose down
```

## Configuration

Uses Pydantic settings with `.env` file support. All configuration is centralized in `config.py` with type validation and default values.