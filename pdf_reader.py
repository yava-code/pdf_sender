import os
from typing import List, Optional, Tuple

import pymupdf

from config import Config
from database_manager import DatabaseManager


class PDFReader:
    def __init__(self, pdf_path: Optional[str] = None, output_dir: Optional[str] = None):
        self.pdf_path = pdf_path or Config.PDF_PATH
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self.db = DatabaseManager()
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)

    def get_total_pages(self) -> int:
        """Get total number of pages in PDF"""
        try:
            doc = pymupdf.open(self.pdf_path)
            total_pages = len(doc)
            doc.close()

            # Update database with total pages
            self.db.set_total_pages(total_pages)
            return total_pages
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")

    def extract_page_as_image(self, page_number: int, dpi: int = 150) -> str:
        """Extract a single page as image and return file path"""
        try:
            doc = pymupdf.open(self.pdf_path)

            if page_number < 1 or page_number > len(doc):
                doc.close()
                raise ValueError(f"Page {page_number} is out of range (1-{len(doc)})")

            page = doc.load_page(page_number - 1)  # pymupdf uses 0-based indexing
            pix = page.get_pixmap(dpi=dpi)

            output_path = os.path.join(self.output_dir, f"page_{page_number}.png")
            pix.save(output_path)

            doc.close()
            return output_path
        except Exception as e:
            raise Exception(f"Error extracting page {page_number}: {e}")

    def extract_pages_as_images(
        self, start_page: int, num_pages: int, dpi: int = 150
    ) -> List[str]:
        """Extract multiple pages as images and return list of file paths"""
        image_paths = []
        total_pages = self.get_total_pages()

        for i in range(num_pages):
            page_number = start_page + i
            if page_number > total_pages:
                break

            try:
                image_path = self.extract_page_as_image(page_number, dpi)
                image_paths.append(image_path)
            except Exception as e:
                print(f"Warning: Could not extract page {page_number}: {e}")
                continue

        return image_paths

    def get_page_info(self, page_number: int) -> dict:
        """Get information about a specific page"""
        try:
            doc = pymupdf.open(self.pdf_path)

            if page_number < 1 or page_number > len(doc):
                doc.close()
                raise ValueError(f"Page {page_number} is out of range (1-{len(doc)})")

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
            raise Exception(f"Error getting page info for page {page_number}: {e}")

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
                    print(f"Removed old image: {filepath}")
                except OSError:
                    pass
