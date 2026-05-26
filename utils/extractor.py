import os
import fitz
from docx import Document as DocxDocument

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_text(file_path, file_type):
    try:
        if file_type == 'pdf':
            return extract_pdf(file_path)
        elif file_type == 'docx':
            return extract_docx(file_path)
        elif file_type == 'txt':
            return extract_txt(file_path)
        else:
            return None
    except Exception as e:
        print(f"Extraction error: {e}")
        return None

def extract_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def extract_docx(file_path):
    doc = DocxDocument(file_path)
    text = ""
    for para in doc.paragraphs:
        if para.text.strip():
            text += para.text + "\n"
    return text.strip()

def extract_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read().strip()

def get_word_count(text):
    return len(text.split())

def get_file_size(file_path):
    size = os.path.getsize(file_path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size // 1024} KB"
    else:
        return f"{size // (1024 * 1024)} MB"