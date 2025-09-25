"""
Tests for cleanup manager functionality
"""

import os
import tempfile
import time
import unittest
from unittest.mock import patch

from cleanup_manager import CleanupManager


class TestCleanupManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        self.upload_dir = os.path.join(self.temp_dir, "uploads")
        os.makedirs(self.output_dir)
        os.makedirs(self.upload_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(
        self, directory: str, filename: str, age_hours: int = 0
    ) -> str:
        """Create a test file with specified age"""
        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as f:
            f.write("test content")

        # Modify file time if age is specified
        if age_hours > 0:
            old_time = time.time() - (age_hours * 3600)
            os.utime(filepath, (old_time, old_time))

        return filepath

    def test_cleanup_old_images_removes_old_files(self):
        """Test that cleanup removes old image files"""
        # Create old and new image files
        self.create_test_file(
            self.output_dir, "page_1.jpg", age_hours=24 * 8
        )  # 8 days old
        self.create_test_file(
            self.output_dir, "page_2.png", age_hours=24 * 8
        )  # 8 days old
        self.create_test_file(self.output_dir, "page_3.jpg", age_hours=1)  # 1 hour old
        self.create_test_file(
            self.output_dir, "other.txt", age_hours=24 * 8
        )  # Not an image

        deleted_count = CleanupManager.cleanup_old_images(
            self.output_dir, retention_days=7
        )

        self.assertEqual(deleted_count, 2)  # Should delete 2 old image files
        self.assertFalse(os.path.exists(os.path.join(self.output_dir, "page_1.jpg")))
        self.assertFalse(os.path.exists(os.path.join(self.output_dir, "page_2.png")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "page_3.jpg")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "other.txt")))

    def test_cleanup_old_images_with_subdirectories(self):
        """Test cleanup with user-specific subdirectories"""
        user_dir = os.path.join(self.output_dir, "123")
        os.makedirs(user_dir)

        # Create old files in subdirectory
        self.create_test_file(user_dir, "page_1.jpg", age_hours=24 * 8)
        self.create_test_file(user_dir, "page_2.jpg", age_hours=1)

        deleted_count = CleanupManager.cleanup_old_images(
            self.output_dir, retention_days=7
        )

        self.assertEqual(deleted_count, 1)
        self.assertFalse(os.path.exists(os.path.join(user_dir, "page_1.jpg")))
        self.assertTrue(os.path.exists(os.path.join(user_dir, "page_2.jpg")))

    def test_cleanup_old_images_removes_empty_directories(self):
        """Test that cleanup removes empty user directories"""
        user_dir = os.path.join(self.output_dir, "456")
        os.makedirs(user_dir)

        # Create old file that will be deleted
        self.create_test_file(user_dir, "page_1.jpg", age_hours=24 * 8)

        CleanupManager.cleanup_old_images(self.output_dir, retention_days=7)

        # Directory should be removed since it's empty now
        self.assertFalse(os.path.exists(user_dir))

    def test_cleanup_old_images_nonexistent_directory(self):
        """Test cleanup with non-existent directory"""
        deleted_count = CleanupManager.cleanup_old_images("/nonexistent/dir")

        self.assertEqual(deleted_count, 0)

    def test_cleanup_orphaned_uploads(self):
        """Test cleanup of orphaned upload files"""
        # Create old and new upload files
        self.create_test_file(
            self.upload_dir, "old.pdf", age_hours=25
        )  # Older than 24 hours
        self.create_test_file(self.upload_dir, "new.pdf", age_hours=1)  # Recent

        deleted_count = CleanupManager.cleanup_orphaned_uploads(
            self.upload_dir, max_age_hours=24
        )

        self.assertEqual(deleted_count, 1)
        self.assertFalse(os.path.exists(os.path.join(self.upload_dir, "old.pdf")))
        self.assertTrue(os.path.exists(os.path.join(self.upload_dir, "new.pdf")))

    def test_cleanup_orphaned_uploads_with_subdirectories(self):
        """Test cleanup of uploads in user subdirectories"""
        user_dir = os.path.join(self.upload_dir, "789")
        os.makedirs(user_dir)

        self.create_test_file(user_dir, "old.pdf", age_hours=25)
        self.create_test_file(user_dir, "new.pdf", age_hours=1)

        deleted_count = CleanupManager.cleanup_orphaned_uploads(
            self.upload_dir, max_age_hours=24
        )

        self.assertEqual(deleted_count, 1)
        self.assertFalse(os.path.exists(os.path.join(user_dir, "old.pdf")))
        self.assertTrue(os.path.exists(os.path.join(user_dir, "new.pdf")))

    def test_get_storage_usage(self):
        """Test storage usage calculation"""
        mock_config = unittest.mock.Mock()
        mock_config.output_dir = self.output_dir
        mock_config.upload_dir = self.upload_dir
        with patch("cleanup_manager.get_config", return_value=mock_config):
            # Create test files
            self.create_test_file(self.output_dir, "page_1.jpg")
            self.create_test_file(self.output_dir, "page_2.png")
            self.create_test_file(self.upload_dir, "book.pdf")

            stats = CleanupManager.get_storage_usage()

            self.assertGreater(stats["output_dir_files"], 0)
            self.assertGreater(stats["upload_dir_files"], 0)
            self.assertGreater(stats["output_dir_size"], 0)
            self.assertGreater(stats["upload_dir_size"], 0)
            self.assertEqual(
                stats["total_files"],
                stats["output_dir_files"] + stats["upload_dir_files"],
            )
            self.assertEqual(
                stats["total_size"], stats["output_dir_size"] + stats["upload_dir_size"]
            )

    def test_get_storage_usage_nonexistent_dirs(self):
        """Test storage usage with non-existent directories"""
        mock_config = unittest.mock.Mock()
        mock_config.output_dir = "/nonexistent1"
        mock_config.upload_dir = "/nonexistent2"
        with patch("cleanup_manager.get_config", return_value=mock_config):
            stats = CleanupManager.get_storage_usage()

            self.assertEqual(stats["output_dir_files"], 0)
            self.assertEqual(stats["upload_dir_files"], 0)
            self.assertEqual(stats["output_dir_size"], 0)
            self.assertEqual(stats["upload_dir_size"], 0)

    def test_format_file_size(self):
        """Test file size formatting"""
        self.assertEqual(CleanupManager.format_file_size(0), "0 B")
        self.assertEqual(CleanupManager.format_file_size(512), "512.0 B")
        self.assertEqual(CleanupManager.format_file_size(1024), "1.0 KB")
        self.assertEqual(CleanupManager.format_file_size(1024 * 1024), "1.0 MB")
        self.assertEqual(CleanupManager.format_file_size(1024 * 1024 * 1024), "1.0 GB")
        self.assertEqual(CleanupManager.format_file_size(1536), "1.5 KB")  # 1.5 KB


if __name__ == "__main__":
    unittest.main()
