import json
import os
from backend.services.phonetic_checker import check_phonetic
from backend.services.fuzzy_checker import check_fuzzy
from backend.services.rules_checker import check_rules_detailed
from backend.services.semantic_checker import check_cross_language_similarity, check_conceptual_theme
from backend.database import get_all_titles

def load_existing_titles():
    titles = get_all_titles()
    return titles if titles else []

def verify_title(title: str) -> dict:
    existing_titles = load_existing_titles()
    title_upper = title.strip().upper()
    
    # 1. Run similarity checks
    phonetic_results = check_phonetic(title, existing_titles)
    fuzzy_results = check_fuzzy(title, existing_titles)
    semantic_cl_results = check_cross_language_similarity(title, existing_titles)
    theme_match = check_conceptual_theme(title)
    
    # 2. Categorize into 5 Priorities
    priority_matches = []
    
    # PRIORITY 1 — EXACT MATCH
    if title_upper in existing_titles:
        priority_matches.append({
            "priority": 1,
            "label": "Exact Match: Title already exists verbatim",
            "matches": [{"existing_title": title_upper, "match_percentage": 100.0, "match_type": "exact"}]
        })

    # PRIORITY 2 — SIMILAR TITLES (fuzzy/phonetic > 80%)
    p2_matches = []
    for res in fuzzy_results + phonetic_results:
        if res['match_percentage'] > 80:
            p2_matches.append(res)
    
    if p2_matches:
        # Deduplicate and sort
        unique_p2 = {}
        for m in p2_matches:
            if m['existing_title'] not in unique_p2 or m['match_percentage'] > unique_p2[m['existing_title']]['match_percentage']:
                unique_p2[m['existing_title']] = m
        sorted_p2 = sorted(list(unique_p2.values()), key=lambda x: x['match_percentage'], reverse=True)
        priority_matches.append({
            "priority": 2,
            "label": "Similar Titles: High typographical or phonetic similarity",
            "matches": sorted_p2[:5]
        })

    # PRIORITY 3 — SAME WORDS (combination/partial word matches)
    rule_results = check_rules_detailed(title, existing_titles)
    combination_violations = [v for v in rule_results["violations"] if "combination" in v.lower()]
    if combination_violations:
        priority_matches.append({
            "priority": 3,
            "label": "Same Words: Title combines existing registered titles",
            "matches": [{"existing_title": v.split(": '")[1].split("'")[0] if ": '" in v else "Multiple Titles", "match_percentage": 100.0, "match_type": "combination"} for v in combination_violations]
        })

    # PRIORITY 4 — SEMANTIC SIMILARITY (CROSS-LANGUAGE)
    if semantic_cl_results:
        # Map match_type to explicit semantic string
        for m in semantic_cl_results:
            m['match_type'] = "semantic_cross_language"
        priority_matches.append({
            "priority": 4,
            "label": "Semantic Match — Same Title in Different Language",
            "matches": semantic_cl_results[:5]
        })

    # PRIORITY 5 — SEMANTIC SIMILARITY (CONCEPTUAL THEME)
    if theme_match:
        priority_matches.append({
            "priority": 5,
            "label": "Semantic Match — Same Conceptual Theme",
            "matches": [{
                "existing_title": f"Theme: {theme_match['theme'].capitalize()}", 
                "match_percentage": 100.0, 
                "match_type": "semantic_conceptual",
                "trigger": theme_match['trigger']
            }]
        })

    # 3. Probability Calculation
    scores = [0.0]
    if phonetic_results: scores.append(max(r['match_percentage'] for r in phonetic_results))
    if fuzzy_results: scores.append(max(r['match_percentage'] for r in fuzzy_results))
    if semantic_cl_results: scores.append(max(r['match_percentage'] for r in semantic_cl_results))
    
    highest_similarity = max(scores)
    
    # 4. Rules and Rejection Logic
    hard_violations = rule_results["violations"]
    if theme_match:
        hard_violations.append(f"Conceptual theme violation: Found '{theme_match['trigger']}' belonging to the '{theme_match['theme']}' cluster.")
    if title_upper in existing_titles:
        hard_violations.append(f"Title '{title_upper}' already exists in the registry.")

    rejection_reasons = list(hard_violations)
    warnings = []
    for term in rule_results["prefix_suffix_found"]:
        if highest_similarity > 70:
            rejection_reasons.append(f"Restricted prefix/suffix '{term}' flagged due to high similarity.")
        else:
            warnings.append(f"Warning: Restricted prefix/suffix '{term}' found.")

    if rejection_reasons:
        approval_probability = 0
        verdict = "REJECTED"
    else:
        base_prob = 100 - highest_similarity
        penalty = 10 if warnings else 0
        approval_probability = max(0, base_prob - penalty)
        verdict = "APPROVED" if approval_probability >= 50 else "REJECTED"
    
    return {
        "title": title,
        "approval_probability": round(approval_probability, 2),
        "verdict": verdict,
        "rejection_reasons": sorted(list(set(rejection_reasons + warnings))),
        "priority_matches": priority_matches,
        "checks": {
            "phonetic": {"score": max([r['match_percentage'] for r in phonetic_results] or [0])},
            "fuzzy": {"score": max([r['match_percentage'] for r in fuzzy_results] or [0])},
            "semantic_cl": {"score": max([r['match_percentage'] for r in semantic_cl_results] or [0])},
            "rules": {"violation_count": len(rejection_reasons), "warning_count": len(warnings)}
        }
    }
