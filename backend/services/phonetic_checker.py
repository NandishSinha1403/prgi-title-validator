import jellyfish

def get_phonetic_codes(title: str):
    words = title.upper().split()
    soundex_codes = {jellyfish.soundex(word) for word in words if word}
    nysiis_codes = {jellyfish.nysiis(word) for word in words if word}
    return soundex_codes, nysiis_codes

def check_phonetic(title: str, existing_titles: list[str]) -> list[dict]:
    results = []
    t_soundex, t_nysiis = get_phonetic_codes(title)
    
    if not t_soundex and not t_nysiis:
        return []

    for existing in existing_titles:
        e_soundex, e_nysiis = get_phonetic_codes(existing)
        
        # Calculate overlap for Soundex
        s_overlap = t_soundex.intersection(e_soundex)
        s_score = (len(s_overlap) / max(len(t_soundex), len(e_soundex))) * 100 if max(len(t_soundex), len(e_soundex)) > 0 else 0
        
        # Calculate overlap for NYSIIS
        n_overlap = t_nysiis.intersection(e_nysiis)
        n_score = (len(n_overlap) / max(len(t_nysiis), len(e_nysiis))) * 100 if max(len(t_nysiis), len(e_nysiis)) > 0 else 0
        
        # Take the best score
        final_score = max(s_score, n_score)
        
        if final_score > 30: # Reporting threshold
            results.append({
                "existing_title": existing,
                "match_percentage": round(final_score, 2),
                "match_type": "phonetic"
            })
            
    return results