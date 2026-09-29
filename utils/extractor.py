"""Text extraction utilities for PDF, DOCX, and TXT files."""
import os
import fitz
from docx import Document as DocxDocument
import re

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_text(file_path, file_type):
    """Extract text from file based on file type."""
    try:
        if file_type == 'pdf':
            return extract_pdf(file_path)
        if file_type == 'docx':
            return extract_docx(file_path)
        if file_type == 'txt':
            return extract_txt(file_path)
        return None
    except (OSError, ValueError) as e:
        print(f"Extraction error: {e}")
        return None

def extract_pdf(file_path):
    """Extract text from PDF file using PyMuPDF."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def extract_docx(file_path):
    """Extract text from DOCX file including tables."""
    try:
        doc = DocxDocument(file_path)
        text_parts = []

        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text.strip())

        full_text = '\n'.join(text_parts)

        if len(full_text.strip()) < 50:
            return None

        return full_text.strip()

    except (OSError,ValueError) as e:
        print(f"DOCX extraction error: {e}")
        return None

def extract_txt(file_path):
    """Extract text from TXT file trying multiple encodings."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read().strip()
                if text:
                    return text
        except (UnicodeDecodeError, OSError):
            continue
    return None

def get_word_count(text):
    """Return word count of given text."""
    return len(text.split())

def get_file_size(file_path):
    """Return human readable file size string."""
    size = os.path.getsize(file_path)
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size // 1024} KB"
    return f"{size // (1024 * 1024)} MB"

def clean_extracted_text(text):
    """Clean extracted text, fix broken hyphenated words, and remove junk lines."""
    if not text:
        return ""
    text = re.sub(r'(\b[a-zA-Z]{2,})-\s*\n?\s*([a-zA-Z]{2,}\b)', r'\1\2', text)
    text = re.sub(r'[ \t]+', ' ', text)
    """Clean extracted text remove junk lines."""
    lines = text.split('\n')
    clean_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue
        # Skip lines which is mostly numbers
        words = line.split()
        if not words:
            continue

        num_count = sum(
            1 for w in words
            if re.match(r'^[\d\.\-\+\%\/\(\)]+$', w)
        )
        if len(words) > 0 and num_count / len(words) > 0.6:
            continue

        if len(words) < 4:
            continue
        # Skip lines which has citations
        if re.match(r'^\(?\d{4}\)?', line) and len(words) < 10:
            continue

        # Skip lines which has mostly special characters
        alpha_count = sum(1 for c in line if c.isalpha())
        if len(line) > 0 and alpha_count / len(line) < 0.4:
            continue

        clean_lines.append(line)

    return '\n'.join(clean_lines)


def extract_pdf(file_path):
    """Extract text from PDF file using PyMuPDF."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    cleaned = clean_extracted_text(text)
    return cleaned.strip()
