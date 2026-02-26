import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from backend.models.schemas import TitleRequest, TitleResponse, WordRequest
from backend.services.similarity_engine import verify_title, load_existing_titles
from backend.services.rules_checker import load_disallowed_words
from backend.database import init_db, add_disallowed_word, delete_disallowed_word, get_comprehensive_stats, search_db_full, get_disallowed_words

# Global in-memory list for last 10 submissions
RECENT_SUBMISSIONS = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="PRGI Title Validator", 
    description="Unified Editorial Title Verification System",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/verify-title", response_model=TitleResponse)
async def api_verify_title(request: TitleRequest):
    if not request.title or not request.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    result = verify_title(request.title.strip())
    
    # Store in recent submissions (limit 10)
    RECENT_SUBMISSIONS.insert(0, {
        "title": result["title"],
        "verdict": result["verdict"],
        "probability": result["approval_probability"]
    })
    if len(RECENT_SUBMISSIONS) > 10:
        RECENT_SUBMISSIONS.pop()
        
    return result

@app.get("/api/search")
async def api_search(request: Request):
    params = dict(request.query_params)
    return search_db_full(params)

@app.get("/api/stats")
async def api_stats():
    return get_comprehensive_stats()

@app.get("/api/recent")
async def api_recent():
    return RECENT_SUBMISSIONS

@app.get("/api/disallowed-words")
async def api_get_words():
    return get_disallowed_words()

@app.post("/api/disallowed-words")
async def api_add_word(request: WordRequest):
    word = request.word.strip()
    if not word:
        raise HTTPException(status_code=400, detail="Word cannot be empty")
    add_disallowed_word(word)
    return {"message": f"Word '{word}' added", "words": get_disallowed_words()}

@app.delete("/api/disallowed-words/{word}")
async def api_delete_word(word: str):
    delete_disallowed_word(word)
    return {"message": f"Word '{word}' removed", "words": get_disallowed_words()}
