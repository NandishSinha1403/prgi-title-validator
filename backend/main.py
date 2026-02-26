import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import TitleRequest, TitleResponse, WordRequest
from backend.services.similarity_engine import verify_title, load_existing_titles
from backend.services.rules_checker import load_disallowed_words

app = FastAPI(title="PRGI Title Validator", description="API for Title Validation")

# Setup CORS to allow the frontend to interact with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_disallowed_words_path():
    return os.path.join(os.path.dirname(__file__), 'data', 'disallowed_words.json')

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
def add_disallowed_word(request: WordRequest):
    words = load_disallowed_words()
    word = request.word.strip()
    if word not in words:
        words.append(word)
        # Assuming we can write to this file locally during dev/hackathon
        with open(get_disallowed_words_path(), 'w') as f:
            json.dump(words, f, indent=2)
    return {"message": "Word added successfully", "words": words}