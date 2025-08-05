"""
Cleanup manager for removing old generated images and temporary files
"""

import logging
import os
import time

from config import Config

logger = logging.getLogger(__name__)


class CleanupManager:
    """Manages cleanup of old generated images and temporary files"""

    @staticmethod
    def cleanup_old_images(output_dir: str = None, retention_days: int = None) -> int:
        """
        Clean up old generated images

        Args:
            output_dir: Directory containing generated images
                (defaults to Config.OUTPUT_DIR)
            retention_days: Number of days to retain images
                (defaults to Config.IMAGE_RETENTION_DAYS)

        Returns:
            Number of files deleted
        """
        if output_dir is None:
            output_dir = Config.OUTPUT_DIR

        if retention_days is None:
            retention_days = Config.IMAGE_RETENTION_DAYS

        if not os.path.exists(output_dir):
            return 0

        deleted_count = 0
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)

        try:
            # Walk through all subdirectories (user-specific directories)
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Only process image files
                    if file.lower().endswith((".png", ".jpg", ".jpeg")):
                        try:
                            # Check file modification time
                            if os.path.getmtime(file_path) < cutoff_time:
                                os.remove(file_path)
                                deleted_count += 1
                                logger.debug(f"Deleted old image: {file_path}")
                        except OSError as e:
                            logger.warning(f"Could not delete file {file_path}: {e}")

                # Remove empty user directories
                if root != output_dir and not os.listdir(root):
                    try:
                        os.rmdir(root)
                        logger.debug(f"Removed empty directory: {root}")
                    except OSError as e:
                        logger.warning(f"Could not remove directory {root}: {e}")

            if deleted_count > 0:
                logger.info(
                    f"Cleanup completed: deleted {deleted_count} old image files"
                )

        except Exception as e:
            logger.error(f"Error during image cleanup: {e}")

        return deleted_count

    @staticmethod
    def cleanup_orphaned_uploads(
        upload_dir: str = None, max_age_hours: int = 24
    ) -> int:
        """
        Clean up orphaned upload files (uploads that weren't properly processed)

        Args:
            upload_dir: Directory containing uploads (defaults to Config.UPLOAD_DIR)
            max_age_hours: Maximum age in hours for unprocessed uploads

        Returns:
            Number of files deleted
        """
        if upload_dir is None:
            upload_dir = Config.UPLOAD_DIR

        if not os.path.exists(upload_dir):
            return 0

        deleted_count = 0
        cutoff_time = time.time() - (max_age_hours * 60 * 60)

        try:
            for root, dirs, files in os.walk(upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)

                    try:
                        # Check file modification time
                        if os.path.getmtime(file_path) < cutoff_time:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.debug(f"Deleted orphaned upload: {file_path}")
                    except OSError as e:
                        logger.warning(f"Could not delete file {file_path}: {e}")

                # Remove empty user directories
                if root != upload_dir and not os.listdir(root):
                    try:
                        os.rmdir(root)
                        logger.debug(f"Removed empty directory: {root}")
                    except OSError as e:
                        logger.warning(f"Could not remove directory {root}: {e}")

            if deleted_count > 0:
                logger.info(f"Orphaned uploads cleanup: deleted {deleted_count} files")

        except Exception as e:
            logger.error(f"Error during orphaned uploads cleanup: {e}")

        return deleted_count

    @staticmethod
    def get_storage_usage() -> dict:
        """
        Get storage usage statistics

        Returns:
            Dictionary with storage usage information
        """
        stats = {
            "output_dir_size": 0,
            "output_dir_files": 0,
            "upload_dir_size": 0,
            "upload_dir_files": 0,
            "total_size": 0,
            "total_files": 0,
        }

        try:
            # Check output directory
            if os.path.exists(Config.OUTPUT_DIR):
                for root, dirs, files in os.walk(Config.OUTPUT_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            stats["output_dir_size"] += size
                            stats["output_dir_files"] += 1
                        except OSError:
                            pass

            # Check upload directory
            if os.path.exists(Config.UPLOAD_DIR):
                for root, dirs, files in os.walk(Config.UPLOAD_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            stats["upload_dir_size"] += size
                            stats["upload_dir_files"] += 1
                        except OSError:
                            pass

            stats["total_size"] = stats["output_dir_size"] + stats["upload_dir_size"]
            stats["total_files"] = stats["output_dir_files"] + stats["upload_dir_files"]

        except Exception as e:
            logger.error(f"Error calculating storage usage: {e}")

        return stats

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"
