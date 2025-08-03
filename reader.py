# обработка PDF
import pymupdf

doc = pymupdf.open("book.pdf") # open a document

for page_number in range(len(doc)): # iterate over pdf pages
    page = doc.load_page(page_number)
    print(page)
