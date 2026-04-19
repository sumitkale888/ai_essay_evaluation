from __future__ import annotations

import tempfile
from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


class FileExtractionError(Exception):
    pass


def extract_text_from_upload(filename: str, payload: bytes) -> str:
    suffix = Path(filename or "").suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(payload)
    if suffix == ".docx":
        return _extract_docx(payload)
    if suffix == ".doc":
        return _extract_doc(payload)

    raise FileExtractionError("Unsupported format. Upload PDF, DOCX, or DOC.")


def _extract_pdf(payload: bytes) -> str:
    reader = PdfReader(BytesIO(payload))
    text_chunks = []
    for page in reader.pages:
        text_chunks.append(page.extract_text() or "")
    text = "\n".join(text_chunks).strip()
    if not text:
        raise FileExtractionError("Could not extract text from PDF.")
    return text


def _extract_docx(payload: bytes) -> str:
    document = Document(BytesIO(payload))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
    if not text:
        raise FileExtractionError("Could not extract text from DOCX.")
    return text


def _extract_doc(payload: bytes) -> str:
    try:
        import textract  # type: ignore
    except Exception as exc:
        raise FileExtractionError(
            "DOC extraction requires textract (and antiword/catdoc installed on system)."
        ) from exc

    with tempfile.NamedTemporaryFile(delete=False, suffix=".doc") as temp:
        temp.write(payload)
        temp_path = temp.name

    try:
        extracted = textract.process(temp_path)
        text = extracted.decode("utf-8", errors="ignore").strip()
        if not text:
            raise FileExtractionError("Could not extract text from DOC.")
        return text
    finally:
        Path(temp_path).unlink(missing_ok=True)
