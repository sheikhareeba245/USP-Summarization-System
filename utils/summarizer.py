"""
LexRank extractive summarization utilities for USP Summarization System
Guarantees continuous fluid text output for 100% justified alignment
"""
import re
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

SENTENCE_COUNT = {
    'short': 4,
    'medium': 7,
    'detailed': 12
}

SECTION_KEYWORDS = {
    'Abstract': ['abstract', 'summary', 'overview', 'synopsis'],
    'Introduction': ['introduction', 'background', 'motivation', 'problem statement', 'objective', 'purpose'],
    'Methodology': ['methodology', 'method', 'methods', 'approach', 'procedure', 'implementation', 'design', 'proposed', 'algorithm', 'technique', 'system'],
    'Results': ['result', 'results', 'finding', 'findings', 'outcome', 'outcomes', 'experiment', 'evaluation', 'performance', 'analysis', 'discussion'],
    'Conclusion': ['conclusion', 'conclusions', 'summary', 'future work', 'future', 'recommendation', 'final', 'closing']
}

def clean_text(text):
    """Remove extra whitespace and special characters, preserving quotes and apostrophes."""
    try:
        if not text:
            return ""
        text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
        text = re.sub(r"[^\w\s\.\,\!\?\;\:\'\-\(\)\"\/]", ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    except Exception as e:
        print(f"Error in clean_text: {e}")
        return str(text)

def is_valid_summary_sentence(s):
    """Filter out headings, exam questions, document headers, and garbage text."""
    try:
        s_clean = s.strip()
        if not s_clean:
            return False

        if s_clean.endswith('?'):
            return False

        lower_s = s_clean.lower()
        heading_patterns = [
            r'^assignment\s*\d+',
            r'^chapter\s*\d+',
            r'^section\s*\d+',
            r'^page\s*\d+',
            r'^figure\s*\d+',
            r'^table\s*\d+',
            r'^question\s*\d+',
            r'^prepared by',
            r'^supervisor'
        ]
        for pattern in heading_patterns:
            if re.search(pattern, lower_s):
                return False

        if len(s_clean.split()) < 6:
            if not s_clean.endswith('.'):
                return False

        return True
    except Exception as e:
        print(f"Error in is_valid_summary_sentence: {e}")
        return True

def split_sentences(text):
    """Split text into individual sentences."""
    try:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [re.sub(r'\s+', ' ', s).strip() for s in sentences if len(s.strip()) > 20 and is_valid_summary_sentence(s)]
    except Exception as e:
        print(f"Error in split_sentences: {e}")
        return [text]

def _dedupe_sentences(sentences):
    """Remove duplicate sentences from list."""
    try:
        seen = set()
        unique = []
        for s in sentences:
            normalized = ' '.join(s.lower().split())
            if normalized not in seen:
                seen.add(normalized)
                unique.append(s)
        return unique
    except Exception as e:
        print(f"Error in _dedupe_sentences: {e}")
        return sentences

def lexrank_extract(text, num_sentences):
    """Extract top sentences using LexRank algorithm."""
    try:
        text = clean_text(text)
        if len(text.split()) < 30:
            sentences = split_sentences(text)
            filtered = [s for s in sentences if is_valid_summary_sentence(s)]
            return filtered[:num_sentences]

        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LexRankSummarizer()

        extra_count = max(num_sentences + 5, num_sentences * 2)
        result = summarizer(parser.document, extra_count)

        raw_sentences = [re.sub(r'\s+', ' ', str(s)).strip() for s in result]
        filtered_sentences = [s for s in raw_sentences if is_valid_summary_sentence(s)]

        return _dedupe_sentences(filtered_sentences)[:num_sentences]

    except Exception as e:
        print(f"LexRank error: {e}")
        sentences = split_sentences(text)
        filtered = [s for s in sentences if is_valid_summary_sentence(s)]
        return filtered[:num_sentences]

def _match_section(stripped, line_lower):
    """Return matched section name or None."""
    try:
        if len(stripped) >= 80:
            return None
        for sec_name, keywords in SECTION_KEYWORDS.items():
            for kw in keywords:
                pattern = rf'\b{re.escape(kw)}\b'
                if re.search(pattern, line_lower):
                    if stripped.isupper() or stripped.istitle() or len(stripped) < 50:
                        return sec_name
        return None
    except Exception as e:
        print(f"Error in _match_section: {e}")
        return None

def detect_sections(text):
    """Detect IMRaD sections in document text."""
    try:
        lines = text.split('\n')
        sections = {name: [] for name in SECTION_KEYWORDS}
        sections['General'] = []
        current = 'General'

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            line_lower = stripped.lower()
            matched = _match_section(stripped, line_lower)
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
    except Exception as e:
        print(f"Error in detect_sections: {e}")
        return {'General': text}

def chunk_text_equally(text, num_chunks):
    """Split text into equal chunks by sentence count."""
    try:
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
    except Exception as e:
        print(f"Error in chunk_text_equally: {e}")
        return [text]

def _remove_duplicate_sentences(sentences):
    """Remove semantically duplicate sentences by word overlap."""
    try:
        seen = set()
        unique = []
        for s in sentences:
            words = frozenset(s.lower().split())
            is_duplicate = any(
                len(words & ex) / max(len(words), 1) > 0.7
                for ex in seen
            )
            if not is_duplicate:
                seen.add(words)
                unique.append(s)
        return unique
    except Exception as e:
        print(f"Error in _remove_duplicate_sentences: {e}")
        return sentences

MAX_WORDS = 4000

def general_summary(text, length='medium', output_format='paragraph'):
    """Generate general extractive summary from text."""
    try:
        words = text.split()
        if len(words) > MAX_WORDS:
            text = ' '.join(words[:MAX_WORDS])

        num = SENTENCE_COUNT.get(length, 7)
        cleaned = clean_text(text)
        sentences = lexrank_extract(cleaned, num)
        unique = _remove_duplicate_sentences(sentences)

        if output_format in ['bullets', 'bullet', 'bullet_points']:
            return '\n'.join(['• ' + re.sub(r'\s+', ' ', s).strip() for s in unique])

        # Single fluid continuous paragraph for justified alignment
        return re.sub(r'\s+', ' ', ' '.join(unique)).strip()

    except Exception as e:
        print(f"Error in general_summary: {e}")
        return "Unable to generate summary due to processing error."


def _summarize_section(sec_text, fallback_text, num, output_format):
    """Summarize a single section with fallback."""
    try:
        if len(sec_text.split()) > 30:
            sentences = lexrank_extract(sec_text, num)
        else:
            sentences = lexrank_extract(fallback_text, num)

        if not sentences:
            sentences = lexrank_extract(fallback_text, num)

        if output_format in ['bullets', 'bullet', 'bullet_points']:
            return '\n'.join(['• ' + re.sub(r'\s+', ' ', s).strip() for s in sentences]) if sentences else '• Content not available.'

        # Clean string without linebreaks
        res = ' '.join([re.sub(r'\s+', ' ', s).strip() for s in sentences])
        return res if res else 'Content not available.'

    except Exception as e:
        print(f"Error in _summarize_section: {e}")
        return "Content processing error."


def academic_summary(text, length='medium', output_format='paragraph'):
    """Generate academic structured summary with IMRaD sections."""
    try:
        words = text.split()
        if len(words) > MAX_WORDS:
            text = ' '.join(words[:MAX_WORDS])

        num_per_section = max(2, SENTENCE_COUNT.get(length, 7) // 3)
        cleaned = clean_text(text)
        sections = detect_sections(cleaned)
        has_sections = any(k != 'General' for k in sections)

        result = {}

        if has_sections:
            for sec_name in SECTION_KEYWORDS:
                sec_text = sections.get(sec_name, '')
                fallback = sections.get('General', cleaned)
                result[sec_name] = _summarize_section(sec_text, fallback, num_per_section, output_format)
        else:
            chunks = chunk_text_equally(cleaned, len(SECTION_KEYWORDS))
            sec_names = list(SECTION_KEYWORDS.keys())
            for i, sec_name in enumerate(sec_names):
                chunk = chunks[i] if i < len(chunks) else cleaned
                result[sec_name] = _summarize_section(chunk, cleaned, num_per_section, output_format)

        return result
    except Exception as e:
        print(f"Error in academic_summary: {e}")
        return {
            'Abstract': 'Error processing document abstract.',
            'Introduction': 'Error processing document introduction.',
            'Methodology': 'Error processing document methodology.',
            'Results': 'Error processing document results.',
            'Conclusion': 'Error processing document conclusion.'
        }
