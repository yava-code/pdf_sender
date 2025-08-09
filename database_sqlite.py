import sqlite3
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from config import get_config

logger = logging.getLogger(__name__)

class DatabaseManagerSQLite:
    def __init__(self, db_path: Optional[str] = None):
        config = get_config()
        self.db_path = db_path or config.database_path.replace(".json", ".sqlite")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
        self._populate_achievements()

    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Users table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    joined_at TEXT,
                    current_page INTEGER DEFAULT 1,
                    total_pages INTEGER DEFAULT 0,
                    pdf_path TEXT,
                    last_sent TEXT,
                    total_points INTEGER DEFAULT 0,
                    pages_read INTEGER DEFAULT 0,
                    books_completed INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    last_read_date TEXT,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0
                )
            """)

            # Achievements table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    icon TEXT
                )
            """)

            # User achievements table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    user_id INTEGER,
                    achievement_id TEXT,
                    unlocked_at TEXT,
                    PRIMARY KEY (user_id, achievement_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
                )
            """)

            # Reading sessions table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reading_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    pages_read INTEGER,
                    duration_minutes INTEGER,
                    timestamp TEXT,
                    points_earned INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            self.conn.commit()
            logger.info("Database tables created or already exist.")
        except sqlite3.Error as e:
            logger.error(f"Error creating database tables: {e}")

    def __del__(self):
        """Close the database connection when the object is destroyed"""
        if self.conn:
            self.conn.close()

    def _get_default_achievements(self) -> List[Dict[str, Any]]:
        """Get default achievements list"""
        return [
            {"id": "first_page", "name": "First Steps", "description": "Read your first page", "points": 10, "icon": "🎯"},
            {"id": "page_10", "name": "Getting Started", "description": "Read 10 pages", "points": 50, "icon": "📖"},
            {"id": "page_50", "name": "Bookworm", "description": "Read 50 pages", "points": 100, "icon": "🐛"},
            {"id": "page_100", "name": "Dedicated Reader", "description": "Read 100 pages", "points": 200, "icon": "📚"},
            {"id": "page_500", "name": "Scholar", "description": "Read 500 pages", "points": 500, "icon": "🎓"},
            {"id": "daily_streak_7", "name": "Week Warrior", "description": "Read for 7 days in a row", "points": 150, "icon": "🔥"},
            {"id": "daily_streak_30", "name": "Monthly Master", "description": "Read for 30 days in a row", "points": 1000, "icon": "👑"},
            {"id": "book_complete", "name": "Book Finisher", "description": "Complete your first book", "points": 300, "icon": "🏆"},
            {"id": "speed_reader", "name": "Speed Reader", "description": "Read 20 pages in one session", "points": 100, "icon": "⚡"},
            {"id": "night_owl", "name": "Night Owl", "description": "Read after 10 PM", "points": 25, "icon": "🦉"}
        ]

    def _populate_achievements(self):
        """Populate the achievements table with default achievements"""
        achievements = self._get_default_achievements()
        try:
            self.cursor.executemany("""
                INSERT OR IGNORE INTO achievements (id, name, description, points, icon)
                VALUES (:id, :name, :description, :points, :icon)
            """, achievements)
            self.conn.commit()
            logger.info("Achievements table populated with default achievements.")
        except sqlite3.Error as e:
            logger.error(f"Error populating achievements table: {e}")

    def add_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        pdf_path: Optional[str] = None,
        current_page: int = 1,
        total_pages: int = 0,
    ):
        """Add user to database or update existing user"""
        try:
            from datetime import datetime

            # Check if user exists
            self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            user = self.cursor.fetchone()

            if user:
                # Update existing user
                if username is not None:
                    self.cursor.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
                if pdf_path is not None:
                    self.cursor.execute("UPDATE users SET pdf_path = ? WHERE id = ?", (pdf_path, user_id))
                self.cursor.execute("UPDATE users SET current_page = ?, total_pages = ? WHERE id = ?", (current_page, total_pages, user_id))
                logger.info(f"User {user_id} (@{username}) updated in the database.")
            else:
                # Insert new user
                config = get_config()
                pdf_path = pdf_path or config.pdf_path
                self.cursor.execute("""
                    INSERT INTO users (id, username, joined_at, current_page, total_pages, pdf_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, username, datetime.now().isoformat(), current_page, total_pages, pdf_path))
                logger.info(f"User {user_id} (@{username}) added to the database.")

            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding or updating user {user_id}: {e}")

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID, returns None if not found"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = self.cursor.fetchone()
            return dict(user) if user else None
        except sqlite3.Error as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            self.cursor.execute("SELECT * FROM users")
            users = self.cursor.fetchall()
            return [dict(user) for user in users]
        except sqlite3.Error as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def get_current_page(self, user_id: int) -> int:
        """Get current page number for a user"""
        user = self.get_user(user_id)
        return user.get("current_page", 1) if user else 1

    def set_current_page(self, user_id: int, page: int):
        """Set current page number for a user"""
        try:
            self.cursor.execute("UPDATE users SET current_page = ? WHERE id = ?", (page, user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error setting current page for user {user_id}: {e}")

    def increment_page(self, user_id: int, increment: int = 1) -> int:
        """Increment current page for a user and return new page number"""
        current_page = self.get_current_page(user_id)
        new_page = current_page + increment
        self.set_current_page(user_id, new_page)
        return new_page

    def get_total_pages(self, user_id: int) -> int:
        """Get total pages count for a user's PDF"""
        user = self.get_user(user_id)
        return user.get("total_pages", 0) if user else 0

    def set_total_pages(self, user_id: int, total: int):
        """Set total pages count for a user's PDF"""
        try:
            self.cursor.execute("UPDATE users SET total_pages = ? WHERE id = ?", (total, user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error setting total pages for user {user_id}: {e}")

    def set_pdf_path(self, user_id: int, pdf_path: str):
        """Set PDF path for a user"""
        try:
            self.cursor.execute("UPDATE users SET pdf_path = ? WHERE id = ?", (pdf_path, user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error setting PDF path for user {user_id}: {e}")

    def get_pdf_path(self, user_id: int) -> str:
        """Get PDF path for a user"""
        user = self.get_user(user_id)
        return user.get("pdf_path", get_config().pdf_path) if user else get_config().pdf_path

    def update_last_sent(self, user_id: int):
        """Update last sent timestamp for a user"""
        try:
            from datetime import datetime
            self.cursor.execute("UPDATE users SET last_sent = ? WHERE id = ?", (datetime.now().isoformat(), user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating last sent for user {user_id}: {e}")

    def get_last_sent(self, user_id: int) -> Optional[datetime]:
        """Get last sent timestamp for a user"""
        user = self.get_user(user_id)
        last_sent = user.get("last_sent") if user else None

        if last_sent:
            try:
                from datetime import datetime
                return datetime.fromisoformat(last_sent)
            except (ValueError, TypeError):
                return None
        return None

    def add_points(self, user_id: int, points: int, reason: str = ""):
        """Add points to user and update level"""
        try:
            user = self.get_user(user_id)
            if not user:
                return 0

            new_total_points = user.get("total_points", 0) + points
            new_experience = user.get("experience", 0) + points
            new_level = (new_experience // 100) + 1

            self.cursor.execute("""
                UPDATE users
                SET total_points = ?, experience = ?, level = ?
                WHERE id = ?
            """, (new_total_points, new_experience, new_level, user_id))
            self.conn.commit()

            logger.info(f"Added {points} points to user {user_id} for {reason}. New total: {new_total_points}")
            return new_total_points
        except sqlite3.Error as e:
            logger.error(f"Error adding points to user {user_id}: {e}")
            return 0

    def mark_page_read(self, user_id: int, pages_count: int = 1):
        """Mark pages as read and award points"""
        try:
            from datetime import datetime, timedelta

            user = self.get_user(user_id)
            if not user:
                return

            # Update pages read
            new_pages_read = user.get("pages_read", 0) + pages_count
            self.cursor.execute("UPDATE users SET pages_read = ? WHERE id = ?", (new_pages_read, user_id))

            # Update reading streak
            today = datetime.now().date().isoformat()
            last_read = user.get("last_read_date")
            current_streak = user.get("current_streak", 0)
            longest_streak = user.get("longest_streak", 0)

            if last_read != today:
                if last_read == (datetime.now().date() - timedelta(days=1)).isoformat():
                    current_streak += 1
                else:
                    current_streak = 1

                if current_streak > longest_streak:
                    longest_streak = current_streak

                self.cursor.execute("""
                    UPDATE users
                    SET current_streak = ?, longest_streak = ?, last_read_date = ?
                    WHERE id = ?
                """, (current_streak, longest_streak, today, user_id))

            # Award points for reading
            points_per_page = 5
            self.add_points(user_id, pages_count * points_per_page, f"Read {pages_count} pages")

            # Check for achievements
            self._check_achievements(user_id)

            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error marking page as read for user {user_id}: {e}")

    def complete_book(self, user_id: int):
        """Mark book as completed"""
        try:
            user = self.get_user(user_id)
            if not user:
                return

            new_books_completed = user.get("books_completed", 0) + 1
            self.cursor.execute("UPDATE users SET books_completed = ? WHERE id = ?", (new_books_completed, user_id))

            self.add_points(user_id, 300, "Completed a book")
            self._unlock_achievement(user_id, "book_complete")

            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error completing book for user {user_id}: {e}")

    def _check_achievements(self, user_id: int):
        """Check and unlock achievements for user"""
        user = self.get_user(user_id)
        if not user:
            return

        pages_read = user.get("pages_read", 0)
        current_streak = user.get("current_streak", 0)

        # Page-based achievements
        if pages_read >= 1:
            self._unlock_achievement(user_id, "first_page")
        if pages_read >= 10:
            self._unlock_achievement(user_id, "page_10")
        if pages_read >= 50:
            self._unlock_achievement(user_id, "page_50")
        if pages_read >= 100:
            self._unlock_achievement(user_id, "page_100")
        if pages_read >= 500:
            self._unlock_achievement(user_id, "page_500")

        # Streak-based achievements
        if current_streak >= 7:
            self._unlock_achievement(user_id, "daily_streak_7")
        if current_streak >= 30:
            self._unlock_achievement(user_id, "daily_streak_30")

        # Time-based achievements
        from datetime import datetime
        current_hour = datetime.now().hour
        if current_hour >= 22:  # After 10 PM
            self._unlock_achievement(user_id, "night_owl")

    def _unlock_achievement(self, user_id: int, achievement_id: str):
        """Unlock achievement for user"""
        try:
            from datetime import datetime

            # Check if user already has this achievement
            self.cursor.execute("SELECT achievement_id FROM user_achievements WHERE user_id = ? AND achievement_id = ?", (user_id, achievement_id))
            if self.cursor.fetchone():
                return False

            # Get achievement details
            self.cursor.execute("SELECT points FROM achievements WHERE id = ?", (achievement_id,))
            achievement = self.cursor.fetchone()
            if not achievement:
                return False

            # Unlock achievement
            self.cursor.execute("""
                INSERT INTO user_achievements (user_id, achievement_id, unlocked_at)
                VALUES (?, ?, ?)
            """, (user_id, achievement_id, datetime.now().isoformat()))

            # Add points
            self.add_points(user_id, achievement["points"], f"Achievement: {achievement_id}")

            self.conn.commit()
            logger.info(f"User {user_id} unlocked achievement: {achievement_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error unlocking achievement {achievement_id} for user {user_id}: {e}")
            return False

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        user = self.get_user(user_id)
        if not user:
            return {}

        self.cursor.execute("""
            SELECT a.* FROM achievements a
            JOIN user_achievements ua ON a.id = ua.achievement_id
            WHERE ua.user_id = ?
        """, (user_id,))
        achievements = [dict(row) for row in self.cursor.fetchall()]

        return {
            "total_points": user.get("total_points", 0),
            "pages_read": user.get("pages_read", 0),
            "books_completed": user.get("books_completed", 0),
            "current_streak": user.get("current_streak", 0),
            "longest_streak": user.get("longest_streak", 0),
            "level": user.get("level", 1),
            "experience": user.get("experience", 0),
            "achievements": achievements,
            "next_level_exp": (user.get("level", 1) * 100) - user.get("experience", 0)
        }

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard of top users"""
        try:
            self.cursor.execute("""
                SELECT id, username, total_points, level, pages_read, books_completed
                FROM users
                ORDER BY total_points DESC
                LIMIT ?
            """, (limit,))
            users = self.cursor.fetchall()
            leaderboard = []
            for i, user in enumerate(users):
                leaderboard.append({
                    "rank": i + 1,
                    "username": user["username"],
                    "total_points": user["total_points"],
                    "level": user["level"],
                    "pages_read": user["pages_read"],
                    "books_completed": user["books_completed"]
                })
            return leaderboard
        except sqlite3.Error as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    def get_available_achievements(self) -> List[Dict[str, Any]]:
        """Get all available achievements"""
        try:
            self.cursor.execute("SELECT * FROM achievements")
            achievements = self.cursor.fetchall()
            return [dict(ach) for ach in achievements]
        except sqlite3.Error as e:
            logger.error(f"Error getting available achievements: {e}")
            return []

    def add_reading_session(self, user_id: int, pages_read: int, duration_minutes: int):
        """Add a reading session record"""
        try:
            from datetime import datetime

            points_earned = pages_read * 5
            self.cursor.execute("""
                INSERT INTO reading_sessions (user_id, pages_read, duration_minutes, timestamp, points_earned)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, pages_read, duration_minutes, datetime.now().isoformat(), points_earned))

            # Check for speed reading achievement
            if pages_read >= 20:
                self._unlock_achievement(user_id, "speed_reader")

            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding reading session for user {user_id}: {e}")
