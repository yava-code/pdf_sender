import json
import os
import tempfile

import pytest

from database_sqlite import DatabaseManagerSQLite


class TestDatabaseManagerSQLite:
    @pytest.fixture
    def temp_db_file(self):
        """Create a temporary database file for testing"""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def db_manager(self, temp_db_file):
        """Create a DatabaseManager instance with temporary file"""
        return DatabaseManagerSQLite(temp_db_file)


    def test_get_current_page(self, db_manager):
        """Test getting current page for a user"""
        user_id = 123
        db_manager.add_user(user_id, "test_user")
        page = db_manager.get_current_page(user_id)
        assert isinstance(page, int)
        assert page == 1

    def test_set_current_page(self, db_manager):
        """Test setting current page for a user"""
        user_id = 123
        db_manager.add_user(user_id, "test_user")
        db_manager.set_current_page(user_id, 10)
        assert db_manager.get_current_page(user_id) == 10

    def test_increment_page(self, db_manager):
        """Test incrementing current page for a user"""
        user_id = 123
        db_manager.add_user(user_id, "test_user")
        initial_page = db_manager.get_current_page(user_id)
        new_page = db_manager.increment_page(user_id, 3)

        assert new_page == initial_page + 3
        assert db_manager.get_current_page(user_id) == new_page

    def test_get_set_total_pages(self, db_manager):
        """Test getting and setting total pages for a user"""
        user_id = 123
        db_manager.add_user(user_id, "test_user")
        db_manager.set_total_pages(user_id, 150)
        assert db_manager.get_total_pages(user_id) == 150

    def test_add_user(self, db_manager):
        """Test adding a user"""
        user_id = 12345
        username = "test_user"

        db_manager.add_user(user_id, username)
        users = db_manager.get_users()

        assert len(users) == 1
        assert users[0]["id"] == user_id
        assert users[0]["username"] == username

    def test_add_duplicate_user(self, db_manager):
        """Test adding the same user twice"""
        user_id = 12345
        username = "test_user"

        db_manager.add_user(user_id, username)
        db_manager.add_user(user_id, username)  # Add same user again

        users = db_manager.get_users()
        assert len(users) == 1  # Should not duplicate

    def test_get_users(self, db_manager):
        """Test getting users list"""
        users = db_manager.get_users()
        assert isinstance(users, list)

    def test_ensure_database_exists(self):
        """Test database creation when file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "new_db.sqlite")

            # File shouldn't exist initially
            assert not os.path.exists(db_path)

            # Create DatabaseManager - should create the file
            db_manager = DatabaseManagerSQLite(db_path)

            # File should now exist
            assert os.path.exists(db_path)

            # Should have tables
            db_manager.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            assert db_manager.cursor.fetchone() is not None
