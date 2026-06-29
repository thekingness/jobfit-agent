from pathlib import Path
from pypdf import PdfReader
from docx import Document


def parse_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    texts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)

    return "\n".join(texts)


def parse_docx(file_path: str) -> str:
    doc = Document(file_path)
    texts = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            texts.append(paragraph.text.strip())

    return "\n".join(texts)


def parse_resume(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return parse_pdf(file_path)

    if suffix == ".docx":
        return parse_docx(file_path)

    if suffix == ".txt":
        return Path(file_path).read_text(encoding="utf-8")

    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")