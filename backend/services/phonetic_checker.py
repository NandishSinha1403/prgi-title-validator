import jellyfish

def check_phonetic(title: str, existing_titles: list[str]) -> list[dict]:
    results = []
    title_soundex = jellyfish.soundex(title)
    title_nysiis = jellyfish.nysiis(title)
    
    for existing in existing_titles:
        ex_soundex = jellyfish.soundex(existing)
        ex_nysiis = jellyfish.nysiis(existing)
        
        score = 0
        if title_soundex == ex_soundex:
            score += 50
        if title_nysiis == ex_nysiis:
            score += 50
            
        if score > 0:
            results.append({
                "existing_title": existing,
                "match_percentage": score,
                "match_type": "phonetic"
            })
    return results