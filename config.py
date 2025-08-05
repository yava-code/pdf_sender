import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    PAGES_PER_SEND = int(os.getenv("PAGES_PER_SEND", 3))
    INTERVAL_HOURS = int(os.getenv("INTERVAL_HOURS", 6))
    SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")
    PDF_PATH = os.getenv("PDF_PATH", "book.pdf")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "database.json")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

    # File validation settings
    MAX_FILE_SIZE_MB = int(
        os.getenv("MAX_FILE_SIZE_MB", 50)
    )  # Maximum PDF file size in MB
    IMAGE_RETENTION_DAYS = int(
        os.getenv("IMAGE_RETENTION_DAYS", 7)
    )  # Days to keep generated images
    IMAGE_QUALITY = int(
        os.getenv("IMAGE_QUALITY", 85)
    )  # JPEG quality for generated images (1-100)

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        # Note: PDF_PATH validation removed as the app now supports per-user PDF uploads
