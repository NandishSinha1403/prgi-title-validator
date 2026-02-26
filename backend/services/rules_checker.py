import json
import os

def load_disallowed_words():
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
    
    # 1. Check disallowed words from data file
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
    # Optimization: Only check if title is long enough to potentially contain two existing titles
    if len(title_upper) > 10:
        found_matches = []
        for ex in existing_titles:
            ex_up = ex.upper()
            if len(ex_up) > 3 and ex_up in title_upper:
                found_matches.append(ex_up)
                
        # If title contains more than one existing title as a component
        if len(found_matches) >= 2:
            # Check for actual combinations
            for i in range(len(found_matches)):
                for j in range(i + 1, len(found_matches)):
                    comb1 = found_matches[i] + found_matches[j]
                    comb2 = found_matches[j] + found_matches[i]
                    # Check if the title is exactly or contains the combination of these two
                    if found_matches[i] in title_upper and found_matches[j] in title_upper:
                        reasons.append(f"Title appears to be a combination of existing titles: '{found_matches[i]}' and '{found_matches[j]}'")
                        break
                if len(reasons) > 0 and "combination" in reasons[-1]: break

    return list(set(reasons))