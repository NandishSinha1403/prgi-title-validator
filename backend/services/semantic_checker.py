from deep_translator import GoogleTranslator
from rapidfuzz import fuzz

THEMES = {
    "morning": ["morning", "sunrise", "dawn", "pratah", "subah", "bhor", "prabhat"],
    "evening": ["evening", "sandhya", "sham", "dusk", "sunset", "sayam"],
    "nation": ["rashtra", "desh", "bharat"],
    "daily": ["daily", "dainik", "pratidin", "roz"]
}

def check_cross_language_similarity(new_title: str, existing_titles: list[str]) -> list[dict]:
    """
    Translates title to English and performs token-based fuzzy matching.
    Lightweight alternative to sentence-transformers.
    """
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(new_title)
    except Exception:
        translated = new_title

    results = []
    # Use token_sort_ratio to be order-agnostic
    for existing in existing_titles:
        score = fuzz.token_sort_ratio(translated.upper(), existing.upper())
        if score > 75:
            results.append({
                "existing_title": existing,
                "match_percentage": round(score, 2),
                "match_type": "cross-language"
            })
    
    results.sort(key=lambda x: x['match_percentage'], reverse=True)
    return results

def check_conceptual_theme(new_title: str) -> dict:
    """
    Checks if words in title fall into sensitive or common conceptual theme clusters.
    """
    words = new_title.lower().split()
    for theme, keywords in THEMES.items():
        for word in words:
            if word in keywords:
                return {"theme": theme, "trigger": word}
    return None
