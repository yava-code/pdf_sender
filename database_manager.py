import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from config import Config


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Create database file if it doesn't exist"""
        if not os.path.exists(self.db_path):
            initial_data = {
                "users": [],
            }
            self.save_data(initial_data)

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
            "pdf_path": Config.PDF_PATH,  # Default PDF path
            "last_sent": None
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
        self.add_user(user_id, None, pdf_path=Config.PDF_PATH, current_page=page)

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
        self.add_user(user_id, None, pdf_path=Config.PDF_PATH, total_pages=total)

    def add_user(self, user_id: int, username: Optional[str] = None, pdf_path: Optional[str] = None, 
               current_page: int = 1, total_pages: int = 0):
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
                "pdf_path": pdf_path or Config.PDF_PATH,
                "last_sent": None
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
        return user_data.get("pdf_path", Config.PDF_PATH)
    
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
