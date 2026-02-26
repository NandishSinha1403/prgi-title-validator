import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.models.schemas import TitleRequest, TitleResponse, WordRequest
from backend.services.similarity_engine import verify_title, load_existing_titles
from backend.services.rules_checker import load_disallowed_words
from backend.database import init_db, add_disallowed_word, get_db_stats

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    init_db()
    yield

app = FastAPI(
    title="PRGI Title Validator", 
    description="API for Title Validation with Semantic & SQLite backend",
    lifespan=lifespan
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/verify-title", response_model=TitleResponse)
def api_verify_title(request: TitleRequest):
    if not request.title or not request.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return verify_title(request.title.strip())

@app.get("/api/titles")
def get_titles():
    return load_existing_titles()

@app.get("/api/disallowed-words")
def get_disallowed_words():
    return load_disallowed_words()

@app.post("/api/admin/add-disallowed-word")
def api_add_disallowed_word(request: WordRequest):
    word = request.word.strip()
    if not word:
        raise HTTPException(status_code=400, detail="Word cannot be empty")
    
    # Save to SQLite
    add_disallowed_word(word)
    
    # Return message and refreshed list
    return {"message": f"Word '{word}' added successfully", "words": load_disallowed_words()}

@app.get("/api/stats")
def get_api_stats():
    return get_db_stats()
