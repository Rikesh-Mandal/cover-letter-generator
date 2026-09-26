import pymupdf

def parse_pdf(path: str) -> str:
    if not path.lower().endswith(".pdf"):
        raise ValueError("Please upload a PDF file.")
    pages = []  
    with pymupdf.open(path) as doc:
        for page in doc:
            pages.append(page.get_text())
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("No text could be extracted from the PDF.")
    return text
