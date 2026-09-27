from openai import OpenAI
from cover_letter_generator import (
    cv_parser,
    job_parser,
    cover_letter
    )
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile
)
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from cover_letter_generator.llm import generate

from html import escape
import pymupdf
from pydantic import BaseModel


load_dotenv()

app = FastAPI()

""" CORS """
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["*"],
)


""" Request models """
class CoverLetterPDFRequest(BaseModel):
    cover_letter: str


""" PDF creation """
def create_cover_letter_pdf(cover_letter: str,) -> bytes:

    if not cover_letter.strip():
        raise ValueError("Cover letter cannot be empty.")

    # Escape special HTML characters because PyMuPDF Story
    # interprets its input as HTML.
    safe_text = escape(cover_letter.strip())

    # Split the cover letter into paragraphs.
    paragraphs = safe_text.split("\n\n")

    html_parts = []

    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        # Preserve any single line breaks inside a paragraph.
        paragraph = paragraph.replace("\n","<br>")
        html_parts.append(f"<p>{paragraph}</p>")

    html_content = "\n".join(html_parts)

    # Basic professional PDF styling.
    css = """
        body {
            font-family: sans-serif;
            font-size: 11pt;
            line-height: 1.45;
            color: #111111;
        }

        p {
            margin-top: 0;
            margin-bottom: 10pt;
        }
    """

    # Standard A4 page.
    page_rect = pymupdf.paper_rect("a4")

    # Leave 54 PDF points around the page.
    # 72 points = 1 inch.
    content_rect = page_rect + (
        54,
        54,
        -54,
        -54
    )

    story = pymupdf.Story(html=html_content, user_css=css)

    # PyMuPDF calls this function whenever it needs
    # another page/rectangle for the Story.
    def rect_function(rect_number,filled,):
        return (
            page_rect,
            content_rect,
            None
        )

    pdf_document = story.write_with_links(rect_function)

    try:
        pdf_bytes = (pdf_document.tobytes())
    finally:
        pdf_document.close()
    return pdf_bytes


""" generate cover letter """
@app.post("/generate")
def generate_cover_letter(cv: Annotated[UploadFile, File()], job_url: Annotated[str, Form()]):
    # Validate uploaded cv
    if (not cv.filename or not cv.filename.lower().endswith(".pdf")):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )
    if cv.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a pdf file."
        )
    
    # Read PDF
    pdf_bytes = cv.file.read()
    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )
    
    # Extract CV text
    try:
        cv_text = cv_parser.parse_pdf_bytes(pdf_bytes)
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the uploaded PDF."
        ) from error

    # Fetch job posting
    try:
        job_description = job_parser.fetch_website_contents(job_url)
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the job posting."
        ) from error

    #Build LLM Prompt
    messages = cover_letter.build_messages(
        cv_text,
        job_description
    )

    return StreamingResponse(generate(messages), media_type="text/plain")

# Download cover letter as PDF
@app.post("/download-pdf")
def download_pdf(request: CoverLetterPDFRequest):

    if not request.cover_letter.strip():
        raise HTTPException(
            status_code=400,
            detail=("Cover letter cannot be empty")
        )

    try:
        pdf_bytes = (create_cover_letter_pdf(request.cover_letter))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=("Unable to create the PDF.")
        ) from error

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            'attachment; filename="cover-letter.pdf"'
        }
    )