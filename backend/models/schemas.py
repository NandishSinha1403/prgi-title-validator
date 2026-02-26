from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TitleRequest(BaseModel):
    title: str

class SimilarityResult(BaseModel):
    existing_title: str
    match_percentage: float
    match_type: str

class TitleResponse(BaseModel):
    title: str
    approval_probability: float
    verdict: str
    rejection_reasons: List[str]
    top_similar_titles: List[SimilarityResult]
    checks: Dict[str, Any]

class WordRequest(BaseModel):
    word: str
