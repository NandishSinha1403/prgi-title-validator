import json
import os

def load_disallowed_words():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'disallowed_words.json')
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def check_rules(title: str) -> list[str]:
    reasons = []
    
    # Check disallowed words
    disallowed = load_disallowed_words()
    title_words = title.lower().split()
    
    for word in disallowed:
        if word.lower() in title_words:
            reasons.append(f"Contains disallowed word: '{word}'")
            
    # Check prefixes/suffixes and typical components
    common_terms = ["the", "india", "samachar", "news", "daily", "weekly", "monthly"]
    for term in common_terms:
        if title.lower().startswith(term + " ") or title.lower().endswith(" " + term):
            reasons.append(f"Uses common prefix/suffix which might not be unique: '{term}'")
            
    return list(set(reasons))