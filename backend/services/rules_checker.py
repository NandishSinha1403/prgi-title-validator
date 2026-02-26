import json
import os
from backend.database import get_disallowed_words, get_titles_set

def load_disallowed_words():
    words = get_disallowed_words()
    if words:
        return [word.upper() for word in words]
    return []

def check_periodicity_violation(new_title: str, existing_titles: list[str]) -> list[str]:
    reasons = []
    title_upper = new_title.strip().upper()
    title_words = title_upper.split()
    
    periodicity_words = ["DAILY", "WEEKLY", "MONTHLY", "ANNUAL", "YEARLY", "FORTNIGHTLY", "DAINIK", "SAPTAHIK", "MASIK"]
    
    # Use O(1) set for exact lookups
    titles_set = get_titles_set()
    
    for p_word in periodicity_words:
        if p_word in title_words:
            core_words = [w for w in title_words if w != p_word]
            core_title = " ".join(core_words)
            # FAST O(1) lookup
            if core_title and core_title in titles_set:
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
            
    # 2. Check restricted prefixes/suffixes
    restricted_terms = ["THE", "INDIA", "SAMACHAR", "NEWS", "DAILY", "WEEKLY", "MONTHLY", "TIMES", "PRESS", "JAN"]
    for term in restricted_terms:
        if title_upper.startswith(term + " ") or title_upper.endswith(" " + term) or title_upper == term:
            prefix_suffix_found.append(term)
            
    # 3. Periodicity Violation
    violations.extend(check_periodicity_violation(title, existing_titles))
            
    # 4. Refined Combination Detection
    if len(title_words) >= 3:
        stop_words = {"THE", "AND", "OF", "FOR", "IN", "TO", "A", "AN"}
        found_existing_titles = []
        
        for ex in existing_titles:
            if len(ex) < 4 or ex in stop_words:
                continue
            
            if f" {ex} " in f" {title_upper} " or title_upper.startswith(f"{ex} ") or title_upper.endswith(f" {ex}"):
                found_existing_titles.append(ex)
        
        unique_matches = []
        found_existing_titles.sort(key=len, reverse=True)
        for match in found_existing_titles:
            if not any(match in other for other in unique_matches if match != other):
                unique_matches.append(match)
        
        if len(unique_matches) >= 2:
            violations.append(f"Title appears to be a combination of existing titles: '{unique_matches[0]}' and '{unique_matches[1]}'")

    return {
        "violations": list(set(violations)),
        "prefix_suffix_found": list(set(prefix_suffix_found))
    }

def check_rules(title: str, existing_titles: list[str]) -> list[str]:
    res = check_rules_detailed(title, existing_titles)
    return res["violations"] + [f"Restricted prefix/suffix used: '{t}'" for t in res["prefix_suffix_found"]]
