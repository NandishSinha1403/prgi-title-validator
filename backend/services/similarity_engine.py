import json
import os
from backend.services.phonetic_checker import check_phonetic
from backend.services.fuzzy_checker import check_fuzzy
from backend.services.rules_checker import check_rules_detailed
from backend.services.semantic_checker import check_cross_language_similarity, check_conceptual_theme
from backend.database import get_all_titles

def load_existing_titles():
    titles = get_all_titles()
    if titles:
        return titles
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    database_path = os.path.join(data_dir, 'titles_database.json')
    sample_path = os.path.join(data_dir, 'sample_titles.json')
    
    if os.path.exists(database_path):
        with open(database_path, 'r') as f:
            return json.load(f)
    elif os.path.exists(sample_path):
        with open(sample_path, 'r') as f:
            return json.load(f)
    return []

def verify_title(title: str) -> dict:
    existing_titles = load_existing_titles()
    
    # 1. Run similarity checks
    phonetic_results = check_phonetic(title, existing_titles)
    fuzzy_results = check_fuzzy(title, existing_titles)
    cross_lang_results = check_cross_language_similarity(title, existing_titles)
    
    # Get highest score among all checks
    scores = [0.0]
    if phonetic_results: scores.append(max(r['match_percentage'] for r in phonetic_results))
    if fuzzy_results: scores.append(max(r['match_percentage'] for r in fuzzy_results))
    if cross_lang_results: scores.append(max(r['match_percentage'] for r in cross_lang_results))
    
    highest_similarity = max(scores)
    
    # 2. Run detailed rules and conceptual theme checks
    rule_results = check_rules_detailed(title, existing_titles)
    hard_violations = rule_results["violations"]
    prefix_suffix_found = rule_results["prefix_suffix_found"]
    
    theme_match = check_conceptual_theme(title)
    if theme_match:
        hard_violations.append(f"Conceptual theme violation: Found '{theme_match['trigger']}' belonging to the '{theme_match['theme']}' cluster.")

    # 3. Process Prefix/Suffix logic (Violation if similarity > 70%, else Warning)
    rejection_reasons = list(hard_violations)
    warnings = []
    
    for term in prefix_suffix_found:
        if highest_similarity > 70:
            rejection_reasons.append(f"Restricted prefix/suffix '{term}' flagged due to high similarity ({highest_similarity}%).")
        else:
            warnings.append(f"Warning: Restricted prefix/suffix '{term}' found. Approval probability reduced.")

    # 4. Calculate Probability and Verdict
    if rejection_reasons:
        # Hard violations cause instant rejection with 0%
        approval_probability = 0
        verdict = "REJECTED"
    else:
        # No hard violations, calculate based on similarity and warnings
        base_prob = 100 - highest_similarity
        penalty = 10 if warnings else 0
        approval_probability = max(0, base_prob - penalty)
        verdict = "APPROVED" if approval_probability > 50 else "REJECTED"
    
    # Combine matches for UI
    all_matches = phonetic_results + fuzzy_results + cross_lang_results
    all_matches.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    # Display reasons and warnings combined for UI
    all_reasons = sorted(list(set(rejection_reasons + warnings)))
    
    return {
        "title": title,
        "approval_probability": round(approval_probability, 2),
        "verdict": verdict,
        "rejection_reasons": all_reasons,
        "top_similar_titles": all_matches[:5],
        "checks": {
            "phonetic": {"score": max([r['match_percentage'] for r in phonetic_results] or [0])},
            "fuzzy": {"score": max([r['match_percentage'] for r in fuzzy_results] or [0])},
            "cross_language": {"score": max([r['match_percentage'] for r in cross_lang_results] or [0])},
            "rules": {"violation_count": len(rejection_reasons), "warning_count": len(warnings)}
        }
    }
