# PRGI Title Validator

**Press Registrar General of India — Title Uniqueness & Compliance Verification System**

Validates new publication title submissions against 58,582 registered titles using a 5-layer detection pipeline combining phonetic, fuzzy, and semantic similarity detection.

---

## How It Works

Every submitted title is run through 5 priority checks in order:

| Priority | Check | Method | Example |
|----------|-------|--------|---------|
| 1 | **Exact Match** | O(1) set lookup | "AAJ" → already registered |
| 2 | **Similar Titles** | Fuzzy + Phonetic > 80% | "Dainik Jagaran" → "Dainik Jagran" |
| 3 | **Same Words** | Combination detection | "Hindu Indian Express" → "Hindu" + "Indian Express" |
| 4 | **Semantic — Cross Language** | Translation + rapidfuzz | "Pratidin Sandhya" → "Daily Evening" |
| 5 | **Semantic — Conceptual Theme** | Keyword cluster matching | "Prabhat Times" → morning cluster |

**Approval Probability** = `100 − highest similarity score`
Any hard violation (disallowed word, periodicity, combination, exact match) = instant **0%**

---

## Tech Stack

**Backend**
- Python 3.8+
- FastAPI + Uvicorn
- SQLite — 58,582 titles, loaded into memory as a Python `set` on startup
- `rapidfuzz` — fuzzy string matching (Levenshtein)
- `jellyfish` — Soundex + NYSIIS phonetic algorithms
- `deep-translator` — cross-language semantic detection via Google Translate
- `pydantic` — request/response validation

**Frontend**
- Vanilla HTML + CSS + JS (zero build step, zero dependencies)
- Playfair Display + Source Sans 3 via Google Fonts
- Single page app with 4 tabs: Validator, Database Explorer, Statistics, Admin

**Data**
- 77,564 titles scraped from prgi.gov.in
- 12,324 official test titles from PRGI XLS dataset (excluded from DB intentionally)
- 58,582 unique non-test titles loaded into SQLite

> The 12,324 XLS test titles are deliberately excluded from the database so the system performs real similarity detection — not cheap exact matches — when evaluators test it.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/verify-title` | Validate a title — returns verdict, probability, priority_matches |
| `GET` | `/api/search` | Search database with filters (title, owner, state, language, etc.) |
| `GET` | `/api/stats` | Total titles, languages, states, disallowed words |
| `GET` | `/api/recent` | Last 10 verified submissions |
| `GET` | `/api/disallowed-words` | List all disallowed words |
| `POST` | `/api/disallowed-words` | Add a disallowed word |
| `DELETE` | `/api/disallowed-words/{word}` | Remove a disallowed word |
| `GET` | `/docs` | Auto-generated Swagger UI |

**Example response from `/api/verify-title`:**
```json
{
  "title": "Pratidin Sandhya",
  "verdict": "REJECTED",
  "approval_probability": 0.0,
  "rejection_reasons": ["..."],
  "priority_matches": [
    {
      "priority": 4,
      "label": "Semantic Match — Same Title in Different Language",
      "matches": [
        {
          "existing_title": "DAILY EVENING",
          "match_percentage": 91.67,
          "match_type": "semantic_cross_language"
        }
      ]
    }
  ],
  "checks": {
    "phonetic": { "score": 0 },
    "fuzzy": { "score": 0 },
    "semantic_cl": { "score": 91.67 },
    "rules": { "violation_count": 1, "warning_count": 0 }
  }
}
```

---

## Project Structure

```
prgi-title-validator/
├── backend/
│   ├── main.py                  # FastAPI app, all endpoints, CORS
│   ├── database.py              # SQLite connection, O(1) title cache (set)
│   ├── load_titles.py           # HTML-in-XLS regex parser for test data
│   ├── requirements.txt
│   ├── data/
│   │   ├── prgi_titles.db       # Main SQLite database (58,582 titles)
│   │   ├── disallowed_words.json
│   │   └── TestExcel*.xls       # Official PRGI test cases (6 files, 12,324 titles)
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   └── services/
│       ├── similarity_engine.py # Orchestrator — runs all 5 priority checks
│       ├── phonetic_checker.py  # Soundex + NYSIIS word-by-word comparison
│       ├── fuzzy_checker.py     # Levenshtein fuzzy matching via rapidfuzz
│       ├── rules_checker.py     # Disallowed words, periodicity, combination
│       └── semantic_checker.py  # Cross-language + conceptual theme detection
└── frontend/
    ├── index.html               # Single page app (HTML structure)
    └── assets/
        ├── style.css            # Dark Harvard-inspired theme
        └── app.js               # All JS — API calls, tab switching, rendering
```

---

## Setup

**Requirements:** Python 3.8+

```bash
# 1. Clone
git clone https://github.com/NandishSinha1403/prgi-title-validator
cd prgi-title-validator

# 2. Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install fastapi uvicorn rapidfuzz jellyfish deep-translator pydantic pandas httpx requests python-multipart

# 4. Start backend (from project root)
cd ..
uvicorn backend.main:app --reload
# API runs at http://127.0.0.1:8000
# Swagger docs at http://127.0.0.1:8000/docs

# 5. Start frontend (new terminal)
cd frontend
python3 -m http.server 8080
# Opens at http://localhost:8080
```

---

## Performance

- Average response time: 600–900ms
- Exact match lookup: O(1) via Python `set`
- 58,582 titles loaded into memory on startup
- Cross-language translation skipped for ASCII-only titles
- Target: under 2 seconds per verification (per problem statement)

---

## Contributing

1. Fork or clone the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Commit: `git commit -m "feat: description"`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request against `master` — requires 1 approval to merge

**Ownership:**
- `frontend/` — UI/UX
- `backend/services/` — similarity logic
- `backend/main.py` + admin tab — admin features

---
\
