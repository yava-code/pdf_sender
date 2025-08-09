import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config import config


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.database_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Create database file if it doesn't exist"""
        if not os.path.exists(self.db_path):
            initial_data = {
                "users": [],
                "leaderboard": [],
                "achievements": self._get_default_achievements(),
                "reading_sessions": []
            }
            self.save_data(initial_data)
    
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

    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON database"""
        try:
            with open(self.db_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_database_exists()
            return self.load_data()

    def save_data(self, data: Dict[str, Any]):
        """Save data to JSON database"""
        with open(self.db_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user data from database"""
        data = self.load_data()
        users = data.get("users", [])

        for user in users:
            if user["id"] == user_id:
                return user

        # If user not found, create default user data
        return {
            "id": user_id,
            "username": None,
            "joined_at": None,
            "current_page": 1,
            "total_pages": 0,
            "pdf_path": config.pdf_path,  # Default PDF path
            "last_sent": None,
            "total_points": 0,
            "pages_read": 0,
            "books_completed": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "last_read_date": None,
            "achievements": [],
            "reading_sessions": [],
            "level": 1,
            "experience": 0
        }

    def get_current_page(self, user_id: int) -> int:
        """Get current page number for a user"""
        user_data = self.get_user_data(user_id)
        return user_data.get("current_page", 1)

    def set_current_page(self, user_id: int, page: int):
        """Set current page number for a user"""
        data = self.load_data()
        users = data.get("users", [])

        for user in users:
            if user["id"] == user_id:
                user["current_page"] = page
                self.save_data(data)
                return

        # If user not found, add them with the specified page
        self.add_user(user_id, None, pdf_path=config.pdf_path, current_page=page)

    def increment_page(self, user_id: int, increment: int = 1) -> int:
        """Increment current page for a user and return new page number"""
        current = self.get_current_page(user_id)
        new_page = current + increment
        self.set_current_page(user_id, new_page)
        return new_page

    def get_total_pages(self, user_id: int) -> int:
        """Get total pages count for a user's PDF"""
        user_data = self.get_user_data(user_id)
        return user_data.get("total_pages", 0)

    def set_total_pages(self, user_id: int, total: int):
        """Set total pages count for a user's PDF"""
        data = self.load_data()
        users = data.get("users", [])

        for user in users:
            if user["id"] == user_id:
                user["total_pages"] = total
                self.save_data(data)
                return

        # If user not found, add them with the specified total pages
        self.add_user(user_id, None, pdf_path=config.pdf_path, total_pages=total)

    def add_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        pdf_path: Optional[str] = None,
        current_page: int = 1,
        total_pages: int = 0,
    ):
        """Add user to database or update existing user"""
        data = self.load_data()
        users = data.get("users", [])

        # Check if user already exists
        for user in users:
            if user["id"] == user_id:
                # Update existing user data if provided
                if username is not None:
                    user["username"] = username
                if pdf_path is not None:
                    user["pdf_path"] = pdf_path
                user["current_page"] = current_page
                user["total_pages"] = total_pages
                self.save_data(data)
                return

        # Add new user
        users.append(
            {
                "id": user_id,
                "username": username,
                "joined_at": datetime.now().isoformat(),
                "current_page": current_page,
                "total_pages": total_pages,
                "pdf_path": pdf_path or config.pdf_path,
                "last_sent": None,
                "total_points": 0,
                "pages_read": 0,
                "books_completed": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "last_read_date": None,
                "achievements": [],
                "reading_sessions": [],
                "level": 1,
                "experience": 0
            }
        )

        data["users"] = users
        self.save_data(data)

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        data = self.load_data()
        return data.get("users", [])

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID, returns None if not found"""
        data = self.load_data()
        users = data.get("users", [])

        for user in users:
            if user["id"] == user_id:
                return user

        return None
    
    # Gamification methods
    def add_points(self, user_id: int, points: int, reason: str = ""):
        """Add points to user and update level"""
        data = self.load_data()
        users = data.get("users", [])
        
        for user in users:
            if user["id"] == user_id:
                user["total_points"] = user.get("total_points", 0) + points
                user["experience"] = user.get("experience", 0) + points
                
                # Calculate level (every 100 points = 1 level)
                new_level = (user["experience"] // 100) + 1
                if new_level > user.get("level", 1):
                    user["level"] = new_level
                
                self.save_data(data)
                return user["total_points"]
        
        return 0
    
    def mark_page_read(self, user_id: int, pages_count: int = 1):
        """Mark pages as read and award points"""
        data = self.load_data()
        users = data.get("users", [])
        
        for user in users:
            if user["id"] == user_id:
                user["pages_read"] = user.get("pages_read", 0) + pages_count
                
                # Update reading streak
                today = datetime.now().date().isoformat()
                last_read = user.get("last_read_date")
                
                if last_read != today:
                    if last_read == (datetime.now().date() - timedelta(days=1)).isoformat():
                        user["current_streak"] = user.get("current_streak", 0) + 1
                    else:
                        user["current_streak"] = 1
                    
                    user["last_read_date"] = today
                    
                    if user["current_streak"] > user.get("longest_streak", 0):
                        user["longest_streak"] = user["current_streak"]
                
                # Award points for reading
                points_per_page = 5
                self.add_points(user_id, pages_count * points_per_page, f"Read {pages_count} pages")
                
                # Check for achievements
                self._check_achievements(user_id)
                
                self.save_data(data)
                break
    
    def complete_book(self, user_id: int):
        """Mark book as completed"""
        data = self.load_data()
        users = data.get("users", [])
        
        for user in users:
            if user["id"] == user_id:
                user["books_completed"] = user.get("books_completed", 0) + 1
                self.add_points(user_id, 300, "Completed a book")
                self._unlock_achievement(user_id, "book_complete")
                self.save_data(data)
                break
    
    def _check_achievements(self, user_id: int):
        """Check and unlock achievements for user"""
        user_data = self.get_user_data(user_id)
        pages_read = user_data.get("pages_read", 0)
        current_streak = user_data.get("current_streak", 0)
        
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
        current_hour = datetime.now().hour
        if current_hour >= 22:  # After 10 PM
            self._unlock_achievement(user_id, "night_owl")
    
    def _unlock_achievement(self, user_id: int, achievement_id: str):
        """Unlock achievement for user"""
        data = self.load_data()
        users = data.get("users", [])
        achievements = data.get("achievements", [])
        
        # Find achievement details
        achievement = next((a for a in achievements if a["id"] == achievement_id), None)
        if not achievement:
            return False
        
        for user in users:
            if user["id"] == user_id:
                user_achievements = user.get("achievements", [])
                if achievement_id not in user_achievements:
                    user_achievements.append(achievement_id)
                    user["achievements"] = user_achievements
                    self.add_points(user_id, achievement["points"], f"Achievement: {achievement['name']}")
                    self.save_data(data)
                    return True
        
        return False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        user_data = self.get_user_data(user_id)
        data = self.load_data()
        achievements = data.get("achievements", [])
        
        user_achievements = []
        for ach_id in user_data.get("achievements", []):
            ach = next((a for a in achievements if a["id"] == ach_id), None)
            if ach:
                user_achievements.append(ach)
        
        return {
            "total_points": user_data.get("total_points", 0),
            "pages_read": user_data.get("pages_read", 0),
            "books_completed": user_data.get("books_completed", 0),
            "current_streak": user_data.get("current_streak", 0),
            "longest_streak": user_data.get("longest_streak", 0),
            "level": user_data.get("level", 1),
            "experience": user_data.get("experience", 0),
            "achievements": user_achievements,
            "next_level_exp": (user_data.get("level", 1) * 100) - user_data.get("experience", 0)
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard of top users"""
        data = self.load_data()
        users = data.get("users", [])
        
        # Sort by total points
        sorted_users = sorted(users, key=lambda x: x.get("total_points", 0), reverse=True)
        
        leaderboard = []
        for i, user in enumerate(sorted_users[:limit]):
            leaderboard.append({
                "rank": i + 1,
                "username": user.get("username", f"User {user['id']}"),
                "total_points": user.get("total_points", 0),
                "level": user.get("level", 1),
                "pages_read": user.get("pages_read", 0),
                "books_completed": user.get("books_completed", 0)
            })
        
        return leaderboard
    
    def get_available_achievements(self) -> List[Dict[str, Any]]:
        """Get all available achievements"""
        data = self.load_data()
        return data.get("achievements", [])
    
    def add_reading_session(self, user_id: int, pages_read: int, duration_minutes: int):
        """Add a reading session record"""
        data = self.load_data()
        sessions = data.get("reading_sessions", [])
        
        session = {
            "user_id": user_id,
            "pages_read": pages_read,
            "duration_minutes": duration_minutes,
            "timestamp": datetime.now().isoformat(),
            "points_earned": pages_read * 5
        }
        
        sessions.append(session)
        data["reading_sessions"] = sessions
        
        # Check for speed reading achievement
        if pages_read >= 20:
            self._unlock_achievement(user_id, "speed_reader")
        
        self.save_data(data)

    def set_pdf_path(self, user_id: int, pdf_path: str):
        """Set PDF path for a user"""
        data = self.load_data()
        users = data.get("users", [])

        for user in users:
            if user["id"] == user_id:
                user["pdf_path"] = pdf_path
                self.save_data(data)
                return

        # If user not found, add them with the specified PDF path
        self.add_user(user_id, None, pdf_path=pdf_path)

    def get_pdf_path(self, user_id: int) -> str:
        """Get PDF path for a user"""
        user_data = self.get_user_data(user_id)
        return user_data.get("pdf_path", config.pdf_path)

    def update_last_sent(self, user_id: int):
        """Update last sent timestamp for a user"""
        data = self.load_data()
        users = data.get("users", [])

        for user in users:
            if user["id"] == user_id:
                user["last_sent"] = datetime.now().isoformat()
                self.save_data(data)
                return

    def get_last_sent(self, user_id: int) -> Optional[datetime]:
        """Get last sent timestamp for a user"""
        user_data = self.get_user_data(user_id)
        last_sent = user_data.get("last_sent")

        if last_sent:
            try:
                return datetime.fromisoformat(last_sent)
            except (ValueError, TypeError):
                return None

        return None
