from pydantic import BaseModel
from typing import List, Optional

class TitleRequest(BaseModel):
    title: str

class SimilarityResult(BaseModel):
    existing_title: str
    match_percentage: float
    match_type: str

class TitleResponse(BaseModel):
    title: str
    similarity_score: float
    probability: float
    rejection_reasons: List[str]
    similar_titles: List[SimilarityResult]

class WordRequest(BaseModel):
    word: str