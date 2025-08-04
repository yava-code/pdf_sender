import os
import logging
from typing import List, Optional, Tuple

import fitz as pymupdf

from config import Config
from database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class PDFReader:
    def __init__(self, user_id: Optional[int] = None, pdf_path: Optional[str] = None, output_dir: Optional[str] = None, db: Optional[DatabaseManager] = None):
        self.db = db or DatabaseManager(Config.DATABASE_PATH)
        self.user_id = user_id
        
        # If user_id is provided, get PDF path from database
        if user_id is not None:
            self.pdf_path = pdf_path or self.db.get_pdf_path(user_id)
            if not self.pdf_path or not os.path.exists(self.pdf_path):
                logger.warning(f"No valid PDF path found for user {user_id}")
        else:
            self.pdf_path = pdf_path or Config.PDF_PATH
            
        # Create user-specific output directory if user_id is provided
        if user_id is not None:
            self.output_dir = output_dir or os.path.join(Config.OUTPUT_DIR, str(user_id))
        else:
            self.output_dir = output_dir or Config.OUTPUT_DIR
            
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)

    def get_total_pages(self) -> int:
        """Get total number of pages in PDF"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            logger.error(f"PDF file not found: {self.pdf_path}")
            return 0
            
        try:
            doc = pymupdf.open(self.pdf_path)
            total_pages = len(doc)
            doc.close()

            # Update database with total pages if user_id is provided
            if self.user_id is not None:
                self.db.set_total_pages(self.user_id, total_pages)
            return total_pages
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return 0

    def extract_page_as_image(self, page_number: int, dpi: int = 150) -> Optional[str]:
        """Extract a single page as image and return file path"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            logger.error(f"PDF file not found: {self.pdf_path}")
            return None
            
        try:
            doc = pymupdf.open(self.pdf_path)

            if page_number < 1 or page_number > len(doc):
                doc.close()
                logger.warning(f"Page {page_number} is out of range (1-{len(doc)})")
                return None

            page = doc.load_page(page_number - 1)  # pymupdf uses 0-based indexing
            pix = page.get_pixmap(dpi=dpi)

            output_path = os.path.join(self.output_dir, f"page_{page_number}.png")
            pix.save(output_path)

            doc.close()
            return output_path
        except Exception as e:
            logger.error(f"Error extracting page {page_number}: {e}")
            return None

    def extract_pages_as_images(
        self, start_page: int, num_pages: int, dpi: int = 150
    ) -> List[str]:
        """Extract multiple pages as images and return list of file paths"""
        image_paths = []
        total_pages = self.get_total_pages()
        
        if total_pages == 0:
            logger.warning("Cannot extract pages: PDF has 0 pages or is invalid")
            return []

        for i in range(num_pages):
            page_number = start_page + i
            if page_number > total_pages:
                break

            image_path = self.extract_page_as_image(page_number, dpi)
            if image_path:
                image_paths.append(image_path)
            else:
                logger.warning(f"Could not extract page {page_number}")

        return image_paths

    def get_page_info(self, page_number: int) -> Optional[dict]:
        """Get information about a specific page"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            logger.error(f"PDF file not found: {self.pdf_path}")
            return None
            
        try:
            doc = pymupdf.open(self.pdf_path)

            if page_number < 1 or page_number > len(doc):
                doc.close()
                logger.warning(f"Page {page_number} is out of range (1-{len(doc)})")
                return None

            page = doc.load_page(page_number - 1)
            rect = page.rect

            info = {
                "page_number": page_number,
                "width": rect.width,
                "height": rect.height,
                "rotation": page.rotation,
            }

            doc.close()
            return info
        except Exception as e:
            logger.error(f"Error getting page info for page {page_number}: {e}")
            return None

    def cleanup_images(self, keep_latest: int = 10):
        """Clean up old image files, keeping only the latest ones"""
        if not os.path.exists(self.output_dir):
            return

        # Get all page image files
        image_files = []
        for filename in os.listdir(self.output_dir):
            if filename.startswith("page_") and filename.endswith(".png"):
                filepath = os.path.join(self.output_dir, filename)
                # Extract page number from filename
                try:
                    page_num = int(filename.replace("page_", "").replace(".png", ""))
                    image_files.append((page_num, filepath))
                except ValueError:
                    continue

        # Sort by page number and keep only the latest ones
        image_files.sort(key=lambda x: x[0], reverse=True)

        for i, (page_num, filepath) in enumerate(image_files):
            if i >= keep_latest:
                try:
                    os.remove(filepath)
                    logger.debug(f"Removed old image: {filepath}")
                except OSError as e:
                    logger.error(f"Error removing file {filepath}: {e}")
                    pass
                    
    def set_pdf_for_user(self, user_id: int, pdf_path: str) -> bool:
        """Set a new PDF file for a user and update the database"""
        try:
            # Verify the PDF file exists and is valid
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file does not exist: {pdf_path}")
                return False
                
            # Try to open the PDF to verify it's valid
            doc = pymupdf.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            
            if total_pages == 0:
                logger.error(f"PDF file has 0 pages: {pdf_path}")
                return False
            
            # Update the database with the new PDF path and total pages
            self.db.set_pdf_path(user_id, pdf_path)
            self.db.set_total_pages(user_id, total_pages)
            self.db.set_current_page(user_id, 1)  # Reset to page 1
            
            # Update instance variables if this reader is for the same user
            if self.user_id == user_id:
                self.pdf_path = pdf_path
                
            logger.info(f"Set PDF for user {user_id}: {pdf_path} ({total_pages} pages)")
            return True
        except Exception as e:
            logger.error(f"Error setting PDF for user {user_id}: {e}")
            return False
