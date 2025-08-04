import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    PAGES_PER_SEND = int(os.getenv("PAGES_PER_SEND", 3))
    INTERVAL_HOURS = int(os.getenv("INTERVAL_HOURS", 6))
    PDF_PATH = os.getenv("PDF_PATH", "book.pdf")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "database.json")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        if not os.path.exists(cls.PDF_PATH):
            raise FileNotFoundError(f"PDF file not found: {cls.PDF_PATH}")
