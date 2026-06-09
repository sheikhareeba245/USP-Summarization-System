"""Keyword extraction utilities using KeyBERT."""
import re
import os
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

_KW_MODEL = None
MODEL_PATH=os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'models','keybert_model'
)

def get_kw_model():
    """Return singleton KeyBERT model instance."""
    global _KW_MODEL  # pylint: disable=global-statement
    if _KW_MODEL is None:
        if os.path.exists(MODEL_PATH):
            print("Loading Keybert from local cache.....")
            sentence_model=SentenceTransformer(MODEL_PATH)
            _KW_MODEL=KeyBERT(model=sentence_model)
        else:
            print("Downloading KeyBert model.....")
            _KW_MODEL = KeyBERT()
        print("KeyBert ready!")
    return _KW_MODEL


def clean_keyword(kw):
    """Clean and normalize keyword string."""
    return re.sub(r'\s+', ' ', kw.strip().lower())


def _deduplicate(all_kws, top_n):
    """Remove duplicate and substring keywords."""
    seen = set()
    unique_kws = []
    for kw in all_kws:
        cleaned = clean_keyword(kw)
        is_duplicate = any(
            cleaned in seen_kw or seen_kw in cleaned
            for seen_kw in seen
        )
        if not is_duplicate and cleaned not in seen:
            seen.add(cleaned)
            unique_kws.append(kw)
    return unique_kws[:top_n]


def _fallback_keywords(text, top_n):
    """Extract simple keywords as fallback."""
    words = text.split()
    seen = set()
    unique = []
    for word in words:
        w_lower = word.lower().strip('.,;:')
        if len(w_lower) > 5 and w_lower not in seen:
            seen.add(w_lower)
            unique.append(w_lower)
    return unique[:top_n]


def extract_keywords(text, top_n=8):
    """Extract top keywords from text using KeyBERT."""

    words=text.split()
    if len(words)>1500:
        text=' '.join(words[:1500])
    try:
        model = get_kw_model()

        keywords_1 = model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 1),
            stop_words='english',
            top_n=top_n // 2
        )
        keywords_2 = model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=top_n // 2
        )

        all_kws = [kw[0] for kw in keywords_1 + keywords_2]
        cleaned=_deduplicate(all_kws,top_n)

        final=[]
        for kw in cleaned:
            kw=' '.join(kw.split())
            kw=kw.strip()
            if kw:
                final.append(kw)
        return final

    except (RuntimeError, ValueError) as e:
        print(f"Keyword error: {e}")
        return _fallback_keywords(text, top_n)
