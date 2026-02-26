import json
import os
from backend.services.phonetic_checker import check_phonetic
from backend.services.fuzzy_checker import check_fuzzy
from backend.services.rules_checker import check_rules
from backend.database import get_all_titles

def load_existing_titles():
    # Try getting from database first
    titles = get_all_titles()
    if titles:
        return titles
    
    # Fallback to JSON if database not found or empty
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
    
    phonetic_results = check_phonetic(title, existing_titles)
    fuzzy_results = check_fuzzy(title, existing_titles)
    
    reasons = check_rules(title, existing_titles)
    
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
    
    # Final check: if very high similarity, add to rejection reasons
    if highest_similarity > 80:
        reasons.append(f"Title is extremely similar ({highest_similarity}%) to an existing title.")
        
    return {
        "title": title,
        "similarity_score": round(highest_similarity, 2),
        "probability": round(probability, 2),
        "rejection_reasons": sorted(list(set(reasons))),
        "similar_titles": similar_titles_list
    }
