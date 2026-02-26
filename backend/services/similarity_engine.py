import json
import os
from backend.services.phonetic_checker import check_phonetic
from backend.services.fuzzy_checker import check_fuzzy
from backend.services.rules_checker import check_rules

def load_existing_titles():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_titles.json')
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def verify_title(title: str) -> dict:
    existing_titles = load_existing_titles()
    
    phonetic_results = check_phonetic(title, existing_titles)
    fuzzy_results = check_fuzzy(title, existing_titles)
    
    reasons = check_rules(title)
    
    # Combine and de-duplicate highest similarity scores
    all_similarities = {}
    for res in phonetic_results + fuzzy_results:
        existing = res['existing_title']
        if existing not in all_similarities:
            all_similarities[existing] = res
        else:
            if res['match_percentage'] > all_similarities[existing]['match_percentage']:
                all_similarities[existing] = res
                
    similar_titles_list = list(all_similarities.values())
    
    # Sort descending by match percentage
    similar_titles_list.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    highest_similarity = 0
    if similar_titles_list:
        highest_similarity = similar_titles_list[0]['match_percentage']
        
    probability = max(0, 100 - highest_similarity)
    
    if highest_similarity > 80:
        reasons.append(f"Title is extremely similar ({highest_similarity}%) to an existing title.")
        
    return {
        "title": title,
        "similarity_score": round(highest_similarity, 2),
        "probability": round(probability, 2),
        "rejection_reasons": reasons,
        "similar_titles": similar_titles_list
    }