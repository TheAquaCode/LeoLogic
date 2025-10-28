"""
File Text Extraction
"""

from pathlib import Path
from typing import List
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image


def extract_text_from_file(file_path: str) -> str:
    """Extract text content from various file types"""
    ext = Path(file_path).suffix.lower()
    try:
        if ext in ['.txt', '.md', '.csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ext == '.pdf':
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            return text
        elif ext == '.docx':
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img)
        else:
            return Path(file_path).stem
    except Exception as e:
        print(f"⚠️ Error extracting {file_path}: {e}")
        return Path(file_path).stem


def chunk_text(text: str, max_length=1000, overlap=100) -> List[str]:
    """Split text into overlapping chunks for processing"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        chunks.append(text[start:end])
        start += max_length - overlap
    return chunks
