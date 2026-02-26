# PRGI Title Similarity & Compliance Validation System

A hackathon project for verifying newspaper and publication titles against existing PRGI records. 
This tool utilizes AI-driven phonetic and fuzzy string matching, as well as strict compliance checks, to evaluate new title submissions.

## Features
- **Phonetic Matching:** Uses `jellyfish` (Soundex, NYSIIS) to catch similar sounding titles.
- **Fuzzy String Matching:** Uses `rapidfuzz` to detect typographical variations and minor differences.
- **Rule-based Compliance:** Checks against disallowed words (e.g., Police, Corruption) and common prefixes/suffixes.
- **Approval Probability Engine:** Computes an approval probability score based on the highest matched similarity and active infractions.

## Setup Instructions

### Backend (FastAPI)
1. Navigate to the project root directory.
2. Install python dependencies:
```bash
pip install -r backend/requirements.txt
```
3. Run the FastAPI server:
```bash
uvicorn backend.main:app --reload
```
The API will be hosted at `http://127.0.0.1:8000`. You can test endpoints via `http://127.0.0.1:8000/docs`.

### Frontend (Vanilla JS + HTML/CSS)
1. Navigate to the `frontend` directory.
2. Serve the frontend using a static python server:
```bash
cd frontend
python -m http.server 8000
```
*(Note: If port 8000 is used by FastAPI, run the frontend on a different port like `python -m http.server 8080`)*

3. Open the browser and navigate to the frontend port (e.g., `http://localhost:8080`).