"""Keyword extraction utilities using KeyBERT with Academic Stopwords & MMR Diversity."""
import re
import os
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

_KW_MODEL = None
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'models', 'keybert_model'
)

# Generic Academic & System Stopwords List
ACADEMIC_STOPWORDS = set([
    'summarization', 'summarize', 'summarizer', 'summarizers', 'summaries', 'summary',
    'paper', 'document', 'text', 'textual', 'method', 'methods', 'model', 'models',
    'result', 'results', 'figure', 'fig', 'table', 'show', 'shows', 'shown', 'using',
    'used', 'proposed', 'approach', 'section', 'author', 'authors', 'page', 'pages',
    'proceedings', 'association', 'computational', 'linguistics', 'volume', 'issue'
])


def get_kw_model():
    """Return singleton KeyBERT model instance."""
    global _KW_MODEL  # pylint: disable=global-statement
    if _KW_MODEL is None:
        if os.path.exists(MODEL_PATH):
            print("Loading Keybert from local cache.....")
            sentence_model = SentenceTransformer(MODEL_PATH)
            _KW_MODEL = KeyBERT(model=sentence_model)
        else:
            print("Downloading KeyBert model.....")
            _KW_MODEL = KeyBERT()
        print("KeyBert ready!")
    return _KW_MODEL


def clean_keyword(kw):
    """Clean and normalize keyword string."""
    return re.sub(r'\s+', ' ', kw.strip().lower())


def _deduplicate(all_kws, top_n):
    """Remove duplicate, substring, and root-stem matching keywords."""
    seen_exact = set()
    seen_stems = set()
    unique_kws = []

    for kw in all_kws:
        cleaned = clean_keyword(kw)

        # 1. Filter generic academic stopwords
        if cleaned in ACADEMIC_STOPWORDS:
            continue

        # 2. Extract 4-char root stem of first word (e.g. 'summ' for summarizers/summarization)
        first_word = cleaned.split()[0]
        root_stem = first_word[:4] if len(first_word) >= 4 else first_word

        # 3. Substring & Root-stem deduplication
        is_duplicate = (
            cleaned in seen_exact or
            root_stem in seen_stems or
            any(cleaned in s or s in cleaned for s in seen_exact)
        )

        if not is_duplicate:
            seen_exact.add(cleaned)
            seen_stems.add(root_stem)
            # Capitalize nicely for UI
            unique_kws.append(kw.title() if len(kw) <= 20 else kw)

    return unique_kws[:top_n]


def _fallback_keywords(text, top_n):
    """Extract simple, clean keywords as fallback if model fails."""
    basic_stopwords = {'the', 'and', 'that', 'have', 'for', 'not', 'with', 'you', 'this', 'but', 'from', 'they', 'more', 'been', 'into', 'were', 'about', 'their', 'which', 'would', 'there'}
    ignore_all = basic_stopwords.union(ACADEMIC_STOPWORDS)

    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    seen_stems = set()
    unique = []

    for word in words:
        if word not in ignore_all:
            stem = word[:4]
            if stem not in seen_stems:
                seen_stems.add(stem)
                unique.append(word.title())
        if len(unique) >= top_n:
            break

    return unique[:top_n]


def extract_keywords(text, top_n=8):
    """Extract top dynamic keyphrases from text using KeyBERT with MMR."""

    words = text.split()
    if len(words) > 1500:
        text = ' '.join(words[:1500])

    try:
        model = get_kw_model()

        # Combine English Stopwords with Academic Stopwords
        custom_stopwords = list(ENGLISH_STOP_WORDS.union(ACADEMIC_STOPWORDS))

        # KeyBERT with MMR (Maximal Marginal Relevance) for diverse, non-repeating keyphrases!
        keywords = model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),  # Extract 1-word and 2-word keyphrases
            stop_words=custom_stopwords,
            use_mmr=True,                   # Prevents repeating terms
            diversity=0.65,                 # High diversity for keyphrases
            top_n=top_n * 2
        )

        all_kws = [kw[0] for kw in keywords]
        cleaned = _deduplicate(all_kws, top_n)

        final = []
        for kw in cleaned:
            kw = ' '.join(kw.split()).strip()
            if kw:
                final.append(kw)

        return final if final else _fallback_keywords(text, top_n)

    except Exception as e:
        print(f"Keyword extraction error: {e}")
        return _fallback_keywords(text, top_n)
