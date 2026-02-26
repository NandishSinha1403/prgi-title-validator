import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'prgi_titles.db')

TITLES_CACHE_LIST = []
TITLES_CACHE_SET = set()

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_titles_into_memory():
    global TITLES_CACHE_LIST, TITLES_CACHE_SET
    if not os.path.exists(DB_PATH):
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM titles')
        titles_raw = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        merged_set = {str(t).strip().upper() for t in titles_raw if t and str(t).strip()}
        TITLES_CACHE_SET = merged_set
        TITLES_CACHE_LIST = list(merged_set)
        print(f"Loaded {len(titles_raw):,} titles from prgi_titles.db")
        print(f"After deduplication: {len(TITLES_CACHE_SET):,} unique titles ready")
    except Exception as e:
        print(f"Error loading titles: {e}")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS titles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        registration_number TEXT,
        registration_date TEXT,
        language TEXT,
        periodicity TEXT,
        publisher TEXT,
        owner TEXT,
        pub_state TEXT,
        pub_district TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS disallowed_words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE NOT NULL
    )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON titles(title)')
    conn.commit()
    conn.close()
    load_titles_into_memory()

def get_all_titles():
    return TITLES_CACHE_LIST if TITLES_CACHE_LIST else []

def get_titles_set():
    return TITLES_CACHE_SET

def search_db_full(params):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM titles WHERE 1=1"
    args = []
    
    mapping = {
        "q": "title",
        "registration_number": "registration_number",
        "owner": "owner",
        "state": "pub_state",
        "district": "pub_district",
        "language": "language"
    }
    
    for key, col in mapping.items():
        val = params.get(key)
        if val:
            query += f" AND {col} LIKE ?"
            args.append(f"%{val}%")
            
    limit = params.get("limit", 100)
    query += f" LIMIT {limit}"
    
    cursor.execute(query, args)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_comprehensive_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    try:
        cursor.execute("SELECT COUNT(*) FROM titles")
        stats["total_titles"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT language) FROM titles WHERE language != ''")
        stats["total_languages"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT pub_state) FROM titles WHERE pub_state != ''")
        stats["total_states"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM disallowed_words")
        stats["total_disallowed_words"] = cursor.fetchone()[0]
    except:
        stats = {"total_titles": 0, "total_languages": 0, "total_states": 0, "total_disallowed_words": 0}
        
    conn.close()
    return stats

def add_disallowed_word(word):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO disallowed_words (word) VALUES (?)', (word.upper(),))
    conn.commit()
    conn.close()

def delete_disallowed_word(word):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM disallowed_words WHERE word = ?', (word.upper(),))
    conn.commit()
    conn.close()

def get_disallowed_words():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT word FROM disallowed_words')
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return words
