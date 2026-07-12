"""LexRank extractive summarization utilities for USP Summarization System."""
import re
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

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
    """Remove extra whitespace and special characters, preserving quotes and apostrophes."""
    # Normalize curly quotes and apostrophes to standard ones (prevents "it s" bug)
    text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')

    # Allow alphanumeric, standard punctuation, single/double quotes, hyphens, and parenthesis
    text = re.sub(r"[^\w\s\.\,\!\?\;\:\'\-\(\)\"\/]", ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_valid_summary_sentence(s):
    """Filter out headings, exam questions, document headers, and garbage text from summary."""
    s_clean = s.strip()
    if not s_clean:
        return False

    # 1. Skip questions (Summary contains statements/answers, not questions)
    if s_clean.endswith('?'):
        return False

    # 2. Skip assignment, chapter, page, or figure headings
    lower_s = s_clean.lower()
    heading_patterns = [
        r'^assignment\s*\d+',
        r'^chapter\s*\d+',
        r'^section\s*\d+',
        r'^page\s*\d+',
        r'^figure\s*\d+',
        r'^table\s*\d+',
        r'^question\s*\d+'
    ]
    for pattern in heading_patterns:
        if re.search(pattern, lower_s):
            return False

    # 3. Skip short titles/lines that don't end with a period (usually subheadings)
    if len(s_clean.split()) < 6:
        if not s_clean.endswith('.'):
            return False

    return True


def split_sentences(text):
    """Split text into individual sentences and filter out headers/questions."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20 and is_valid_summary_sentence(s)]


def _dedupe_sentences(sentences):
    """Remove duplicate sentences from list."""
    seen = set()
    unique = []
    for s in sentences:
        normalized = ' '.join(s.lower().split())
        if normalized not in seen:
            seen.add(normalized)
            unique.append(s)
    return unique


# def lexrank_extract(text, num_sentences):
#     """Extract top sentences using LexRank algorithm."""
#     try:
#         text = clean_text(text)
#         if len(text.split()) < 30:
#             return split_sentences(text)[:num_sentences]

#         parser = PlaintextParser.from_string(
#             text, Tokenizer("english")
#         )
#         summarizer = LexRankSummarizer()
#         result = summarizer(parser.document, num_sentences)
#         sentences = [str(s) for s in result]
#         return _dedupe_sentences(sentences)

#     except (ValueError, RuntimeError) as e:
#         print(f"LexRank error: {e}")
#         return split_sentences(text)[:num_sentences]
def lexrank_extract(text, num_sentences):
    """Extract top sentences using LexRank algorithm and filter them."""
    try:
        text = clean_text(text)
        if len(text.split()) < 30:
            sentences = split_sentences(text)
            filtered = [s for s in sentences if is_valid_summary_sentence(s)]
            return filtered[:num_sentences]

        parser = PlaintextParser.from_string(
            text, Tokenizer("english")
        )
        summarizer = LexRankSummarizer()

        extra_count = max(num_sentences + 5, num_sentences * 2)
        result = summarizer(parser.document, extra_count)

        raw_sentences = [str(s).strip() for s in result]

        filtered_sentences = [s for s in raw_sentences if is_valid_summary_sentence(s)]

        return _dedupe_sentences(filtered_sentences)[:num_sentences]

    except (ValueError, RuntimeError) as e:
        print(f"LexRank error: {e}")
        sentences = split_sentences(text)
        filtered = [s for s in sentences if is_valid_summary_sentence(s)]
        return filtered[:num_sentences]

def _match_section(stripped, line_lower):
    """Return matched section name or None."""
    if len(stripped) >= 80:
        return None
    for sec_name, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            pattern = rf'\b{re.escape(kw)}\b'
            if re.search(pattern, line_lower):
                if (stripped.isupper()
                        or stripped.istitle()
                        or len(stripped) < 50):
                    return sec_name
    return None


def detect_sections(text):
    """Detect IMRaD sections in document text."""
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


def chunk_text_equally(text, num_chunks):
    """Split text into equal chunks by sentence count."""
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


def _remove_duplicate_sentences(sentences):
    """Remove semantically duplicate sentences by word overlap."""
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


MAX_WORDS=4000
def general_summary(text, length='medium', output_format='paragraph'):
    """Generate general extractive summary from text."""
    # Truncate Text
    words=text.split()
    if len(words)>MAX_WORDS:
        text=' '.join(words[:MAX_WORDS])

    num = SENTENCE_COUNT.get(length, 7)
    text = clean_text(text)
    sentences = lexrank_extract(text, num)
    unique = _remove_duplicate_sentences(sentences)

    if output_format == 'bullets':
        return '\n'.join(['• ' + s for s in unique])
    return ' '.join(unique)


def _summarize_section(sec_text, fallback_text, num, output_format):
    """Summarize a single section with fallback."""
    if len(sec_text.split()) > 30:
        sentences = lexrank_extract(sec_text, num)
    else:
        sentences = lexrank_extract(fallback_text, num)

    if not sentences:
        sentences = lexrank_extract(fallback_text, num)

    if output_format == 'bullets':
        return '\n'.join(['• ' + s for s in sentences]) if sentences \
            else '• Content not available.'
    return ' '.join(sentences) if sentences else 'Content not available.'


def academic_summary(text, length='medium', output_format='paragraph'):
    """Generate academic structured summary with IMRaD sections."""
    #Truncate Text
    words=text.split()
    if len(words)>MAX_WORDS:
        text =' '.join(words[:MAX_WORDS])
    num_per_section = max(2, SENTENCE_COUNT.get(length, 7) // 3)
    text = clean_text(text)
    sections = detect_sections(text)
    has_sections = any(k != 'General' for k in sections)

    result = {}

    if has_sections:
        for sec_name in SECTION_KEYWORDS:
            sec_text = sections.get(sec_name, '')
            fallback = sections.get('General', text)
            result[sec_name] = _summarize_section(
                sec_text, fallback, num_per_section, output_format
            )
    else:
        chunks = chunk_text_equally(text, len(SECTION_KEYWORDS))
        sec_names = list(SECTION_KEYWORDS.keys())
        for i, sec_name in enumerate(sec_names):
            chunk = chunks[i] if i < len(chunks) else text
            result[sec_name] = _summarize_section(
                chunk, text, num_per_section, output_format
            )

    return result
