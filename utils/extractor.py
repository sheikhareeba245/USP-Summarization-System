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
        
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return None


def extract_txt(file_path):
    encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read().strip()
                if text:
                    return text
        except:
            continue
    return None

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