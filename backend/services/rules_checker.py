import json
import os
from backend.database import get_disallowed_words

def load_disallowed_words():
    # Try getting from SQLite first
    words = get_disallowed_words()
    if words:
        return [word.upper() for word in words]
    
    # JSON Fallback
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'disallowed_words.json')
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return [word.upper() for word in json.load(f)]
    except Exception:
        pass
    return []

def check_rules(title: str, existing_titles: list[str]) -> list[str]:
    reasons = []
    title_upper = title.strip().upper()
    title_words = title_upper.split()
    
    # 1. Check disallowed words
    disallowed = load_disallowed_words()
    for word in disallowed:
        if word in title_words:
            reasons.append(f"Contains disallowed word: '{word}'")
            
    # 2. Check disallowed prefixes/suffixes
    restricted_terms = ["THE", "INDIA", "SAMACHAR", "NEWS", "DAILY", "WEEKLY", "MONTHLY", "TIMES", "PRESS", "JAN"]
    for term in restricted_terms:
        if title_upper.startswith(term + " ") or title_upper.endswith(" " + term) or title_upper == term:
            reasons.append(f"Restricted prefix/suffix used: '{term}'")
            
    # 3. Check periodicity words
    periodicity_words = ["DAILY", "WEEKLY", "MONTHLY", "FORTNIGHTLY", "QUARTERLY", "ANNUAL"]
    for word in periodicity_words:
        if word in title_words:
            reasons.append(f"Contains periodicity indicator: '{word}'")
            
    # 4. Check if title combines two existing titles as substrings
    if len(title_upper) > 10:
        found_matches = []
        for ex in existing_titles:
            ex_up = ex.upper()
            if len(ex_up) > 3 and ex_up in title_upper:
                found_matches.append(ex_up)
                
        if len(found_matches) >= 2:
            for i in range(len(found_matches)):
                for j in range(i + 1, len(found_matches)):
                    if found_matches[i] in title_upper and found_matches[j] in title_upper:
                        reasons.append(f"Title appears to be a combination of existing titles: '{found_matches[i]}' and '{found_matches[j]}'")
                        break
                if len(reasons) > 0 and "combination" in reasons[-1]: break

    return list(set(reasons))
