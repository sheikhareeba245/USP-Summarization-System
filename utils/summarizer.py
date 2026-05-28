from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import re

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

SENTENCE_COUNT = {
    'short': 4,
    'medium': 7,
    'detailed': 12
}

SECTION_KEYWORDS = {
    'Abstract': [
        'abstract', 'summary', 'overview', 'synopsis'
    ],
    'Introduction': [
        'introduction', 'background', 'motivation',
        'problem statement', 'objective', 'purpose'
    ],
    'Methodology': [
        'methodology', 'method', 'methods', 'approach',
        'procedure', 'implementation', 'design',
        'proposed', 'algorithm', 'technique', 'system'
    ],
    'Results': [
        'result', 'results', 'finding', 'findings',
        'outcome', 'outcomes', 'experiment', 'evaluation',
        'performance', 'analysis', 'discussion'
    ],
    'Conclusion': [
        'conclusion', 'conclusions', 'summary',
        'future work', 'future', 'recommendation',
        'final', 'closing'
    ]
}

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
    return text.strip()

def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]

def lexrank_extract(text, num_sentences):
    try:
        text = clean_text(text)
        if len(text.split()) < 30:
            return split_sentences(text)[:num_sentences]
        
        parser = PlaintextParser.from_string(
            text, Tokenizer("english")
        )
        summarizer = LexRankSummarizer()
        result = summarizer(parser.document, num_sentences)
        sentences = [str(s) for s in result]
        
        seen = set()
        unique = []
        for s in sentences:
            normalized = ' '.join(s.lower().split())
            if normalized not in seen:
                seen.add(normalized)
                unique.append(s)
        return unique
        
    except Exception as e:
        print(f"LexRank error: {e}")
        return split_sentences(text)[:num_sentences]

def detect_sections(text):
    lines = text.split('\n')
    sections = {name: [] for name in SECTION_KEYWORDS.keys()}
    sections['General'] = []
    
    current = 'General'
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        line_lower = stripped.lower()
        matched = None
        
        if len(stripped) < 80:
            for sec_name, keywords in SECTION_KEYWORDS.items():
                for kw in keywords:
                    pattern = rf'\b{re.escape(kw)}\b'
                    if re.search(pattern, line_lower):
                        if stripped.isupper() or stripped.istitle() or len(stripped) < 50:
                            matched = sec_name
                            break
                if matched:
                    break
        
        if matched:
            current = matched
        else:
            sections[current].append(stripped)
    
    result = {}
    for name, lines_list in sections.items():
        content = ' '.join(lines_list).strip()
        if len(content.split()) > 20:
            result[name] = content
    
    return result

def chunk_text_equally(text, num_chunks):
    sentences = split_sentences(text)
    if not sentences:
        return [text]
    
    chunk_size = max(1, len(sentences) // num_chunks)
    chunks = []
    for i in range(0, len(sentences), chunk_size):
        chunk = ' '.join(sentences[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks[:num_chunks]

def general_summary(text, length='medium', output_format='paragraph'):
    num = SENTENCE_COUNT.get(length, 7)
    text = clean_text(text)
    sentences = lexrank_extract(text, num)
    
    seen = set()
    unique = []
    for s in sentences:
        words = frozenset(s.lower().split())
        is_duplicate = False
        for existing_words in seen:
            overlap = len(words & existing_words) / max(len(words), 1)
            if overlap > 0.7:
                is_duplicate = True
                break
        if not is_duplicate:
            seen.add(words)
            unique.append(s)
    
    if output_format == 'bullets':
        return '\n'.join(['• ' + s for s in unique])
    return ' '.join(unique)

def academic_summary(text, length='medium', output_format='paragraph'):
    num_per_section = max(2, SENTENCE_COUNT.get(length, 7) // 3)
    text = clean_text(text)
    sections = detect_sections(text)
    
    has_sections = len([k for k in sections if k != 'General']) > 0
    
    result = {}
    
    if has_sections:
        for sec_name in SECTION_KEYWORDS.keys():
            sec_text = sections.get(sec_name, '')
            
            if len(sec_text.split()) > 30:
                sentences = lexrank_extract(sec_text, num_per_section)
            else:
                general_text = sections.get('General', text)
                sentences = lexrank_extract(general_text, num_per_section)
            
            if not sentences:
                sentences = lexrank_extract(text, num_per_section)
            
            if output_format == 'bullets':
                result[sec_name] = '\n'.join(['• ' + s for s in sentences])
            else:
                result[sec_name] = ' '.join(sentences)
    else:
        chunks = chunk_text_equally(text, len(SECTION_KEYWORDS))
        sec_names = list(SECTION_KEYWORDS.keys())
        
        for i, sec_name in enumerate(sec_names):
            chunk = chunks[i] if i < len(chunks) else text
            sentences = lexrank_extract(chunk, num_per_section)
            
            if output_format == 'bullets':
                result[sec_name] = '\n'.join(['• ' + s for s in sentences]) if sentences else '• Content not available.'
            else:
                result[sec_name] = ' '.join(sentences) if sentences else 'Content not available.'
    
    return result