from keybert import KeyBERT
import re

kw_model = None

def get_kw_model():
    global kw_model
    if kw_model is None:
        kw_model = KeyBERT()
    return kw_model

def clean_keyword(kw):
    return re.sub(r'\s+', ' ', kw.strip().lower())

def extract_keywords(text, top_n=8):
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
        
        seen = set()
        unique_kws = []
        for kw in all_kws:
            cleaned = clean_keyword(kw)
            
            is_duplicate = False
            for seen_kw in seen:
                if cleaned in seen_kw or seen_kw in cleaned:
                    is_duplicate = True
                    break
            
            if not is_duplicate and cleaned not in seen:
                seen.add(cleaned)
                unique_kws.append(kw)
        
        return unique_kws[:top_n]
        
    except Exception as e:
        print(f"Keyword error: {e}")
        words = text.split()
        seen = set()
        unique = []
        for w in words:
            w_lower = w.lower().strip('.,;:')
            if len(w_lower) > 5 and w_lower not in seen:
                seen.add(w_lower)
                unique.append(w_lower)
        return unique[:top_n]