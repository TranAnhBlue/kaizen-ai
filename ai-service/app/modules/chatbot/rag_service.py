import io
import re
from pypdf import PdfReader
from docx import Document

def extract_text(data: bytes, kind: str) -> str:
    if kind == 'text/plain':
        return data.decode('utf-8-sig')
    if kind == 'application/pdf':
        reader = PdfReader(io.BytesIO(data))
        if len(reader.pages) > 80:
            raise ValueError('PDF has too many pages (max 80)')
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    if kind == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        doc = Document(io.BytesIO(data))
        return '\n'.join(p.text for p in doc.paragraphs)
    raise ValueError('Unsupported file type')

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks
