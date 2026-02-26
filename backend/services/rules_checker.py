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

def check_periodicity_violation(new_title: str, existing_titles: list[str]) -> list[str]:
    reasons = []
    title_upper = new_title.strip().upper()
    title_words = title_upper.split()
    
    periodicity_words = ["DAILY", "WEEKLY", "MONTHLY", "ANNUAL", "YEARLY", "FORTNIGHTLY", "DAINIK", "SAPTAHIK", "MASIK"]
    
    for p_word in periodicity_words:
        if p_word in title_words:
            # Create a "core" title by stripping the periodicity word
            core_words = [w for w in title_words if w != p_word]
            core_title = " ".join(core_words)
            
            if core_title in [et.upper() for et in existing_titles]:
                reasons.append(f"Core title '{core_title}' already exists; periodicity word '{p_word}' added to an existing title is not allowed.")
                
    return reasons

def check_rules_detailed(title: str, existing_titles: list[str]) -> dict:
    violations = []
    prefix_suffix_found = []
    title_upper = title.strip().upper()
    title_words = title_upper.split()
    
    # 1. Check disallowed words
    disallowed = load_disallowed_words()
    for word in disallowed:
        if word in title_words:
            violations.append(f"Contains disallowed word: '{word}'")
            
    # 2. Check disallowed prefixes/suffixes
    restricted_terms = ["THE", "INDIA", "SAMACHAR", "NEWS", "DAILY", "WEEKLY", "MONTHLY", "TIMES", "PRESS", "JAN"]
    for term in restricted_terms:
        if title_upper.startswith(term + " ") or title_upper.endswith(" " + term) or title_upper == term:
            prefix_suffix_found.append(term)
            
    # 3. Periodicity Violation (Specific Core Title Check)
    p_reasons = check_periodicity_violation(title, existing_titles)
    violations.extend(p_reasons)
            
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
                        violations.append(f"Title appears to be a combination of existing titles: '{found_matches[i]}' and '{found_matches[j]}'")
                        break
                if len(violations) > 0 and "combination" in violations[-1]: break

    return {
        "violations": list(set(violations)),
        "prefix_suffix_found": list(set(prefix_suffix_found))
    }

# Keeping legacy check_rules for backward compatibility if needed, but similarity_engine should use check_rules_detailed
def check_rules(title: str, existing_titles: list[str]) -> list[str]:
    res = check_rules_detailed(title, existing_titles)
    return res["violations"] + [f"Restricted prefix/suffix used: '{t}'" for t in res["prefix_suffix_found"]]
