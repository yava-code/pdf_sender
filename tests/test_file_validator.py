"""
Tests for file validation functionality
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import fitz as pymupdf

from file_validator import FileValidator


class TestFileValidator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = FileValidator()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_mock_pdf(
        self, filename: str, pages: int = 5, needs_password: bool = False
    ) -> str:
        """Create a mock PDF file for testing"""
        filepath = os.path.join(self.temp_dir, filename)

        # Create a simple PDF with specified number of pages
        doc = pymupdf.open()
        for i in range(pages):
            page = doc.new_page()
            # Add some content to make it a valid page
            page.insert_text((50, 50), f"Page {i + 1}")

        if needs_password:
            # Set password protection
            doc.save(filepath, encryption=pymupdf.PDF_ENCRYPT_AES_256, user_pw="test")
        else:
            doc.save(filepath)

        doc.close()
        return filepath

    def test_validate_pdf_file_valid(self):
        """Test validation of a valid PDF file"""
        pdf_path = self.create_mock_pdf("test.pdf")

        is_valid, message = self.validator.validate_pdf_file(pdf_path)

        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid PDF file")

    def test_validate_pdf_file_not_found(self):
        """Test validation when file doesn't exist"""
        is_valid, message = self.validator.validate_pdf_file("nonexistent.pdf")

        self.assertFalse(is_valid)
        self.assertEqual(message, "File not found")

    def test_validate_pdf_file_too_large(self):
        """Test validation when file is too large"""
        pdf_path = self.create_mock_pdf("large.pdf", pages=10)  # Create a PDF

        # Make file appear larger than limit by passing large file_size
        file_size = 2 * 1024 * 1024  # 2MB
        
        # Create validator with smaller max file size
        self.validator.config.max_file_size = 1024 * 1024  # 1MB limit
        is_valid, message = self.validator.validate_pdf_file(pdf_path, file_size)

        self.assertFalse(is_valid)
        self.assertIn("File too large", message)

    def test_validate_pdf_file_empty(self):
        """Test validation of an empty PDF"""
        # Create a text file disguised as PDF instead of actual empty PDF
        fake_pdf = os.path.join(self.temp_dir, "empty.pdf")
        with open(fake_pdf, "w") as f:
            f.write("")  # Empty file

        is_valid, message = self.validator.validate_pdf_file(fake_pdf)

        self.assertFalse(is_valid)
        self.assertEqual(message, "Invalid or corrupted PDF file")

    def test_validate_pdf_file_password_protected(self):
        """Test validation of password-protected PDF"""
        pdf_path = self.create_mock_pdf("protected.pdf", needs_password=True)

        is_valid, message = self.validator.validate_pdf_file(pdf_path)

        self.assertFalse(is_valid)
        self.assertEqual(message, "Password-protected PDFs are not supported")

    def test_validate_pdf_file_too_many_pages(self):
        """Test validation of PDF with too many pages"""
        # Mock the PDF to appear to have too many pages
        with patch("file_validator.os.path.exists", return_value=True), patch(
            "file_validator.os.path.getsize", return_value=1024
        ), patch(
            "file_validator.mimetypes.guess_type",
            return_value=("application/pdf", None),
        ), patch(
            "file_validator.pymupdf.open"
        ) as mock_open:

            mock_doc = Mock()
            mock_doc.__len__ = Mock(return_value=15000)  # Use Mock() for __len__
            mock_doc.needs_pass = False
            mock_doc.close = Mock()
            mock_open.return_value = mock_doc

            is_valid, message = self.validator.validate_pdf_file("fake.pdf")

            self.assertFalse(is_valid)
            self.assertEqual(message, "PDF has too many pages (maximum: 10,000)")

    def test_validate_pdf_file_corrupted(self):
        """Test validation of corrupted PDF"""
        # Create a file that's not a valid PDF
        fake_pdf = os.path.join(self.temp_dir, "fake.pdf")
        with open(fake_pdf, "w") as f:
            f.write("This is not a PDF file")

        is_valid, message = self.validator.validate_pdf_file(fake_pdf)

        self.assertFalse(is_valid)
        self.assertEqual(message, "Invalid or corrupted PDF file")

    def test_validate_file_name_valid(self):
        """Test filename validation with valid name"""
        is_valid, sanitized = self.validator.validate_file_name("book.pdf")

        self.assertTrue(is_valid)
        self.assertEqual(sanitized, "book.pdf")

    def test_validate_file_name_no_extension(self):
        """Test filename validation without PDF extension"""
        is_valid, sanitized = self.validator.validate_file_name("book")

        self.assertTrue(is_valid)
        self.assertEqual(sanitized, "book.pdf")

    def test_validate_file_name_dangerous_chars(self):
        """Test filename validation with dangerous characters"""
        is_valid, sanitized = self.validator.validate_file_name(
            "../../../etc/passwd.pdf"
        )

        self.assertTrue(is_valid)
        self.assertEqual(
            sanitized, "passwd.pdf"
        )  # os.path.basename removes path components

    def test_validate_file_name_empty(self):
        """Test filename validation with empty name"""
        is_valid, sanitized = self.validator.validate_file_name("")

        self.assertFalse(is_valid)
        self.assertEqual(sanitized, "book.pdf")

    def test_validate_file_name_too_long(self):
        """Test filename validation with very long name"""
        long_name = "a" * 200 + ".pdf"
        is_valid, sanitized = self.validator.validate_file_name(long_name)

        self.assertTrue(is_valid)
        self.assertTrue(len(sanitized) <= 100)
        self.assertTrue(sanitized.endswith(".pdf"))

    def test_validate_file_name_only_special_chars(self):
        """Test filename validation with only special characters"""
        is_valid, sanitized = self.validator.validate_file_name(
            "@#$%^&*()!+={}[]|\\:;\"'<>,.?/~`"
        )

        self.assertTrue(is_valid)  # Function will sanitize it
        self.assertEqual(
            sanitized, "book.pdf"
        )  # Should become default after sanitization


if __name__ == "__main__":
    unittest.main()
