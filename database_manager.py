import json
import os
from typing import Dict, Any
from config import Config

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database file if it doesn't exist"""
        if not os.path.exists(self.db_path):
            initial_data = {
                "current_page": 1,
                "total_pages": 0,
                "last_sent": None,
                "users": []
            }
            self.save_data(initial_data)
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON database"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_database_exists()
            return self.load_data()
    
    def save_data(self, data: Dict[str, Any]):
        """Save data to JSON database"""
        with open(self.db_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    
    def get_current_page(self) -> int:
        """Get current page number"""
        data = self.load_data()
        return data.get('current_page', 1)
    
    def set_current_page(self, page: int):
        """Set current page number"""
        data = self.load_data()
        data['current_page'] = page
        self.save_data(data)
    
    def increment_page(self, increment: int = 1) -> int:
        """Increment current page and return new page number"""
        current = self.get_current_page()
        new_page = current + increment
        self.set_current_page(new_page)
        return new_page
    
    def get_total_pages(self) -> int:
        """Get total pages count"""
        data = self.load_data()
        return data.get('total_pages', 0)
    
    def set_total_pages(self, total: int):
        """Set total pages count"""
        data = self.load_data()
        data['total_pages'] = total
        self.save_data(data)
    
    def add_user(self, user_id: int, username: str = None):
        """Add user to database"""
        data = self.load_data()
        users = data.get('users', [])
        
        # Check if user already exists
        for user in users:
            if user['id'] == user_id:
                return
        
        users.append({
            'id': user_id,
            'username': username,
            'joined_at': None  # You can add timestamp here
        })
        
        data['users'] = users
        self.save_data(data)
    
    def get_users(self) -> list:
        """Get all users"""
        data = self.load_data()
        return data.get('users', [])