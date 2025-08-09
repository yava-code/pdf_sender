import json
import sqlite3
from pathlib import Path
import logging

from database_sqlite import DatabaseManagerSQLite
from database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrate data from JSON database to SQLite database"""
    json_db_path = "database.json"
    sqlite_db_path = "database.sqlite"

    if not Path(json_db_path).exists():
        logger.info("JSON database not found. No migration needed.")
        return

    # Initialize both database managers
    json_db = DatabaseManager(db_path=json_db_path)
    sqlite_db = DatabaseManagerSQLite(db_path=sqlite_db_path)

    # Migrate users
    users = json_db.get_users()
    for user in users:
        sqlite_db.add_user(
            user_id=user["id"],
            username=user.get("username"),
            pdf_path=user.get("pdf_path"),
            current_page=user.get("current_page", 1),
            total_pages=user.get("total_pages", 0)
        )
        # Update other fields
        sqlite_db.cursor.execute("""
            UPDATE users
            SET joined_at = ?, last_sent = ?, total_points = ?, pages_read = ?,
                books_completed = ?, current_streak = ?, longest_streak = ?,
                last_read_date = ?, level = ?, experience = ?
            WHERE id = ?
        """, (
            user.get("joined_at"), user.get("last_sent"), user.get("total_points", 0),
            user.get("pages_read", 0), user.get("books_completed", 0),
            user.get("current_streak", 0), user.get("longest_streak", 0),
            user.get("last_read_date"), user.get("level", 1), user.get("experience", 0),
            user["id"]
        ))

        # Migrate user achievements
        for achievement_id in user.get("achievements", []):
            sqlite_db._unlock_achievement(user["id"], achievement_id)

    # Migrate reading sessions
    json_data = json_db.load_data()
    reading_sessions = json_data.get("reading_sessions", [])
    for session in reading_sessions:
        sqlite_db.add_reading_session(
            user_id=session["user_id"],
            pages_read=session["pages_read"],
            duration_minutes=session["duration_minutes"]
        )

    sqlite_db.conn.commit()
    logger.info("Database migration completed successfully.")

if __name__ == "__main__":
    migrate_database()
