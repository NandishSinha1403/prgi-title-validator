from deep_translator import GoogleTranslator
from rapidfuzz import fuzz, process

# Final restricted clusters (No English dictionary words)
THEMES = {
    "morning": ["pratah", "prabhat", "bhor", "ushakal", "subah"],
    "evening": ["sayam", "sham"],
    "nation":  ["rashtra", "desh"]
}

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def check_cross_language_similarity(new_title: str, existing_titles: list[str]) -> list[dict]:
    """
    Translates title only if non-ASCII characters are present, then performs high-performance fuzzy matching.
    """
    # OPTIMIZATION: If title is pure ASCII (English), skip translation to save 600ms+ network time
    if is_ascii(new_title):
        translated_upper = new_title.upper()
    else:
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(new_title)
            translated_upper = translated.upper()
        except Exception:
            translated_upper = new_title.upper()
    
    # Use C++ optimized process.extract
    matches = process.extract(
        translated_upper, 
        existing_titles, 
        scorer=fuzz.token_sort_ratio, 
        limit=5, 
        score_cutoff=76
    )

    results = []
    for match in matches:
        match_str, score, _ = match
        results.append({
            "existing_title": match_str,
            "match_percentage": round(score, 2),
            "match_type": "cross-language"
        })
    
    return results

def check_conceptual_theme(new_title: str) -> dict:
    """
    Checks if words in title fall into conceptual theme clusters.
    """
    words = new_title.lower().split()
    for theme, keywords in THEMES.items():
        for word in words:
            if word in keywords:
                return {"theme": theme, "trigger": word}
    return None
