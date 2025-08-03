# обработка PDF
import pymupdf
import os
from dotenv import load_dotenv
load_dotenv()
pages = int(os.getenv('AMOUNT'))

doc = pymupdf.open("book.pdf")

os.makedirs("output", exist_ok=True)

for page_number in range(pages):
    page = doc.load_page(page_number)
    pix = page.get_pixmap(dpi=150)
    pix.save(f"output/page_{page_number + 1}.png")
    print(f"Saved page {page_number + 1}")

doc.close()
