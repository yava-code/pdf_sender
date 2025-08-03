# обработка PDF
import pymupdf
import os

doc = pymupdf.open("book.pdf")
max_pages = min(10, len(doc))

os.makedirs("output", exist_ok=True)

for page_number in range(max_pages):
    page = doc.load_page(page_number)
    pix = page.get_pixmap(dpi=150)
    pix.save(f"output/page_{page_number + 1}.png")
    print(f"Saved page {page_number + 1}")

doc.close()
