"""
File validation utilities for PDF uploads
"""

import logging
import mimetypes
import os
from typing import Optional, Tuple

import fitz as pymupdf

from config import get_config, Config

logger = logging.getLogger(__name__)


class FileValidator:
    """Validates uploaded files for security and compatibility"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize FileValidator with config"""
        self.config = config or get_config()

    def validate_pdf_file(
        self, file_path: str, file_size: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Validate a PDF file for upload

        Args:
            file_path: Path to the PDF file
            file_size: Size of the file in bytes (optional)

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, "File not found"

            # Get file size if not provided
            if file_size is None:
                file_size = os.path.getsize(file_path)

            # Check file size limit
            max_size_bytes = self.config.max_file_size
            if file_size > max_size_bytes:
                max_size_mb = max_size_bytes // (1024 * 1024)
                return (
                    False,
                    f"File too large. Maximum size: {max_size_mb}MB",
                )

            # Check MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type != "application/pdf":
                return False, "Invalid file type. Only PDF files are supported"

            # Try to open and validate PDF content
            try:
                doc = pymupdf.open(file_path)
                page_count = len(doc)

                # Check if PDF has pages
                if page_count == 0:
                    doc.close()
                    return False, "PDF file is empty or corrupted"

                # Check if PDF is encrypted
                if doc.needs_pass:
                    doc.close()
                    return False, "Password-protected PDFs are not supported"

                # Check page count limit (reasonable upper bound)
                if page_count > 10000:
                    doc.close()
                    return False, "PDF has too many pages (maximum: 10,000)"

                # Try to extract a page to ensure PDF is readable
                try:
                    page = doc[0]
                    _ = page.get_pixmap()
                except Exception as e:
                    doc.close()
                    logger.warning(f"PDF validation failed during page extraction: {e}")
                    return False, "PDF file appears to be corrupted or unreadable"

                doc.close()
                logger.info(
                    f"PDF validation successful: {page_count} pages, {file_size} bytes"
                )
                return True, "Valid PDF file"

            except Exception as e:
                logger.error(f"Error validating PDF content: {e}")
                return False, "Invalid or corrupted PDF file"

        except Exception as e:
            logger.error(f"Error during file validation: {e}")
            return False, "Error validating file"

    def validate_file_name(self, filename: str) -> Tuple[bool, str]:
        """
        Validate filename for security

        Args:
            filename: The filename to validate

        Returns:
            Tuple of (is_valid, sanitized_filename)
        """
        if not filename:
            return False, "book.pdf"

        # Remove path separators and other dangerous characters
        sanitized = os.path.basename(filename)
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "._-")

        # Ensure it ends with .pdf
        if not sanitized.lower().endswith(".pdf"):
            sanitized += ".pdf"

        # Ensure it's not empty after sanitization
        if len(sanitized) <= 4:  # Just ".pdf"
            sanitized = "book.pdf"

        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:96] + ".pdf"

        return True, sanitized
