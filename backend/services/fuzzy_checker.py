from rapidfuzz import fuzz, process

def check_fuzzy(title: str, existing_titles: list[str]) -> list[dict]:
    results = []
    extracted = process.extract(title, existing_titles, scorer=fuzz.ratio, limit=5)
    
    for match in extracted:
        match_str, score, _ = match
        if score >= 60.0: # Minimum threshold to report
            results.append({
                "existing_title": match_str,
                "match_percentage": round(score, 2),
                "match_type": "fuzzy"
            })
    return results