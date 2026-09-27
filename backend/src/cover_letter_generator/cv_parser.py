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


def parse_pdf_bytes(pdf_bytes: bytes) -> str:
    pages = []
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            pages.append(page.get_text())
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("No text could be extracted from the pdf.")
    return text