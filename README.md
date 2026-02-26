# PRGI Title Validator
**Press Registrar General of India — Title Uniqueness & Compliance Verification System**

Built for the PRGI Hackathon. Validates new publication title submissions against 58,582 registered titles using a 5-layer detection pipeline combining phonetic, fuzzy, and semantic similarity.

---

## What It Does

When a publisher submits a new title, the system runs it through 5 priority checks:

| Priority | Check | Method | Example Caught |
|----------|-------|--------|----------------|
| 1 | Exact Match | Direct string lookup (O(1) set) | "AAJ" → already exists |
| 2 | Similar Titles | Fuzzy + Phonetic matching | "Dainik Jagaran" → "Dainik Jagran" |
| 3 | Same Words | Combination detection | "Hindu Indian Express" → "Hindu" + "Indian Express" |
| 4 | Semantic — Cross Language | Translation + fuzzy match | "Pratidin Sandhya" → "Daily Evening" |
| 5 | Semantic — Conceptual Theme | Keyword cluster matching | "Prabhat Times" → morning cluster |

**Approval Probability** = `100 - highest similarity score`
Any hard violation (disallowed word, periodicity, combination) = instant 0%

---

## Tech Stack

**Backend**
- Python 3.13
- FastAPI + Uvicorn
- SQLite (58,582 titles, indexed)
- rapidfuzz — fuzzy string matching
- jellyfish — Soundex + NYSIIS phonetic algorithms
- deep-translator — cross-language semantic detection
- pydantic — request/response validation

**Frontend**
- Vanilla HTML/CSS/JS (zero build step)
- Playfair Display + Source Sans 3 (Google Fonts)
- index.html, assets/style.css, assets/app.js

**Data**
- 77,564 titles scraped from prgi.gov.in
- 12,324 official test titles from PRGI XLS dataset
- 58,582 unique non-test titles loaded into SQLite
- Test titles deliberately excluded from DB so evaluators 
  get real similarity detection, not cheap exact matches

---

## Project Structure
prgi-title-validator/
├── backend/
│   ├── main.py                  # FastAPI app, all endpoints
│   ├── database.py              # SQLite connection, title cache (set for O(1))
│   ├── load_titles.py           # HTML-in-XLS parser for test data
│   ├── requirements.txt
│   ├── data/
│   │   ├── prgi_titles.db       # Main SQLite database (58,582 titles)
│   │   ├── disallowed_words.json
│   │   └── TestExcel*.xls       # Official PRGI test cases (6 files)
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   └── services/
│       ├── similarity_engine.py # Orchestrator — runs all 5 priority checks
│       ├── phonetic_checker.py  # Soundex + NYSIIS word-by-word comparison
│       ├── fuzzy_checker.py     # Levenshtein-based rapidfuzz matching
│       ├── rules_checker.py     # Disallowed words, periodicity, combination
│       └── semantic_checker.py  # Cross-language + conceptual theme detection
└── frontend/
    ├── index.html               # Main single-page app (HTML structure only)
    └── assets/
        ├── style.css            # All styles, dark Harvard-inspired theme
        └── app.js               # All JavaScript, API calls, tab switching

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/verify-title | Validate a title, returns priority_matches |
| GET | /api/search | Search database with filters |
| GET | /api/stats | Total titles, languages, states |
| GET | /api/recent | Last 10 submissions |
| GET | /api/disallowed-words | List disallowed words |
| POST | /api/disallowed-words | Add disallowed word |
| DELETE | /api/disallowed-words/{word} | Remove disallowed word |
| GET | /docs | Auto-generated Swagger UI |

---

## Setup

**Requirements:** Python 3.8+
```bash
# 1. Clone
git clone https://github.com/NandishSinha1403/prgi-title-validator
cd prgi-title-validator

# 2. Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn rapidfuzz jellyfish deep-translator pydantic pandas httpx requests python-multipart

# 3. Start backend (from project root)
cd ..
uvicorn backend.main:app --reload
# Runs at http://127.0.0.1:8000
# API docs at http://127.0.0.1:8000/docs

# 4. Start frontend (new terminal)
cd frontend
python3 -m http.server 8080
# Opens at http://localhost:8080
```

---

## Contributing

1. Fork → `https://github.com/NandishSinha1403/prgi-title-validator`
2. Clone your fork
3. Create a branch: `git checkout -b feature/your-feature`
4. Make changes + commit: `git commit -m "feat: description"`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request against `master`

---

## Performance

- Title verification: ~600–900ms average
- Database: 58,582 titles loaded into memory as a Python set on startup
- Exact match lookup: O(1)
- Cross-language check skips translation for ASCII-only titles

---
