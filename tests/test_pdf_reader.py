import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from pdf_reader import PDFReader


class TestPDFReader:
    @pytest.fixture
    def mock_pdf_path(self):
        """Create a mock PDF path"""
        return "test_book.pdf"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def pdf_reader(self, mock_pdf_path, temp_output_dir):
        """Create a PDFReader instance with mocked dependencies"""
        with patch("pdf_reader.DatabaseManager"):
            return PDFReader(pdf_path=mock_pdf_path, output_dir=temp_output_dir)

    @patch("os.path.exists")
    @patch("fitz.open")
    def test_get_total_pages(self, mock_fitz_open, mock_path_exists, pdf_reader):
        """Test getting total pages from PDF"""
        # Mock file existence and PDF document
        mock_path_exists.return_value = True
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=50)
        mock_fitz_open.return_value = mock_doc

        total_pages = pdf_reader.get_total_pages()

        assert total_pages == 50
        mock_fitz_open.assert_called_once_with(pdf_reader.pdf_path)
        mock_doc.close.assert_called_once()
        # Don't expect set_total_pages call since no user_id is provided

    @patch("os.path.exists")
    @patch("fitz.open")
    def test_get_total_pages_error(self, mock_fitz_open, mock_path_exists, pdf_reader):
        """Test error handling when getting total pages"""
        mock_path_exists.return_value = True
        mock_fitz_open.side_effect = Exception("PDF read error")

        # Should return 0 on error, not raise exception
        total_pages = pdf_reader.get_total_pages()
        assert total_pages == 0

    @patch("os.path.exists")
    @patch("fitz.open")
    def test_extract_page_as_image(self, mock_fitz_open, mock_path_exists, pdf_reader):
        """Test extracting a single page as image"""
        # Mock file existence and PDF document and page
        mock_path_exists.return_value = True
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=100)
        mock_page = Mock()
        mock_pix = Mock()

        mock_doc.load_page.return_value = mock_page
        mock_page.get_pixmap.return_value = mock_pix
        mock_fitz_open.return_value = mock_doc

        page_number = 5
        result_path = pdf_reader.extract_page_as_image(page_number)

        expected_path = os.path.join(pdf_reader.output_dir, f"page_{page_number}.png")
        assert result_path == expected_path

        mock_doc.load_page.assert_called_once_with(page_number - 1)  # 0-based indexing
        mock_page.get_pixmap.assert_called_once_with(dpi=150)
        mock_pix.save.assert_called_once_with(expected_path)
        mock_doc.close.assert_called_once()

    @patch("os.path.exists")
    @patch("fitz.open")
    def test_extract_page_out_of_range(self, mock_fitz_open, mock_path_exists, pdf_reader):
        """Test extracting page that's out of range"""
        mock_path_exists.return_value = True
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=10)
        mock_fitz_open.return_value = mock_doc

        # Test with a page number beyond the total pages
        out_of_range_page = 15

        # Should return None for out of range pages, not raise exception
        result = pdf_reader.extract_page_as_image(out_of_range_page)
        assert result is None
        mock_doc.close.assert_called_once()

    @patch("pdf_reader.PDFReader.extract_page_as_image")
    @patch("pdf_reader.PDFReader.get_total_pages")
    def test_extract_pages_as_images(
        self, mock_get_total, mock_extract_page, pdf_reader
    ):
        """Test extracting multiple pages as images"""
        mock_get_total.return_value = 100
        mock_extract_page.side_effect = lambda page, dpi: f"page_{page}.png"

        start_page = 5
        num_pages = 3

        result_paths = pdf_reader.extract_pages_as_images(start_page, num_pages)

        expected_paths = ["page_5.png", "page_6.png", "page_7.png"]
        assert result_paths == expected_paths
        assert mock_extract_page.call_count == 3

    @patch("pdf_reader.PDFReader.extract_page_as_image")
    @patch("pdf_reader.PDFReader.get_total_pages")
    def test_extract_pages_beyond_total(
        self, mock_get_total, mock_extract_page, pdf_reader
    ):
        """Test extracting pages when some are beyond total pages"""
        mock_get_total.return_value = 10
        mock_extract_page.side_effect = lambda page, dpi: f"page_{page}.png"

        start_page = 9
        num_pages = 5  # Would go beyond page 10

        result_paths = pdf_reader.extract_pages_as_images(start_page, num_pages)

        # Should only extract pages 9 and 10
        expected_paths = ["page_9.png", "page_10.png"]
        assert result_paths == expected_paths
        assert mock_extract_page.call_count == 2

    @patch("os.path.exists")
    @patch("fitz.open")
    def test_get_page_info(self, mock_fitz_open, mock_path_exists, pdf_reader):
        """Test getting page information"""
        # Mock file existence and PDF document and page
        mock_path_exists.return_value = True
        mock_doc = Mock()
        mock_doc.__len__ = Mock(return_value=100)
        mock_page = Mock()
        mock_rect = Mock()
        mock_rect.width = 595.0
        mock_rect.height = 842.0

        mock_page.rect = mock_rect
        mock_page.rotation = 0
        mock_doc.load_page.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        page_number = 5
        info = pdf_reader.get_page_info(page_number)

        expected_info = {
            "page_number": 5,
            "width": 595.0,
            "height": 842.0,
            "rotation": 0,
        }

        assert info == expected_info
        mock_doc.load_page.assert_called_once_with(page_number - 1)
        mock_doc.close.assert_called_once()

    def test_cleanup_images(self, pdf_reader):
        """Test cleaning up old image files"""
        # Create some test image files
        test_files = [
            "page_1.png",
            "page_2.png",
            "page_3.png",
            "page_4.png",
            "page_5.png",
            "other_file.txt",
        ]

        for filename in test_files:
            filepath = os.path.join(pdf_reader.output_dir, filename)
            with open(filepath, "w") as f:
                f.write("test")

        # Keep only latest 3 files
        pdf_reader.cleanup_images(keep_latest=3)

        # Check remaining files
        remaining_files = os.listdir(pdf_reader.output_dir)

        # Should keep page_3.png, page_4.png, page_5.png, and other_file.txt
        assert "page_3.png" in remaining_files
        assert "page_4.png" in remaining_files
        assert "page_5.png" in remaining_files
        assert "other_file.txt" in remaining_files  # Non-page file should remain
        assert "page_1.png" not in remaining_files
        assert "page_2.png" not in remaining_files

    def test_ensure_output_dir(self, mock_pdf_path):
        """Test output directory creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "new_output")

            # Directory shouldn't exist initially
            assert not os.path.exists(output_dir)

            # Create PDFReader - should create the directory
            with patch("pdf_reader.DatabaseManager"):
                pdf_reader = PDFReader(pdf_path=mock_pdf_path, output_dir=output_dir)

            # Directory should now exist
            assert os.path.exists(output_dir)
            assert os.path.isdir(output_dir)
