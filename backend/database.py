import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'prgi_titles.db')
ADMIN_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'admin', 'prgi_data.db')

TITLES_CACHE = []

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_titles_into_memory():
    global TITLES_CACHE
    titles1_raw = []
    titles2_raw = []
    
    # Load from prgi_titles.db
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT title FROM titles')
            titles1_raw = [row[0] for row in cursor.fetchall()]
            conn.close()
            print(f"Loaded {len(titles1_raw):,} titles from prgi_titles.db")
        except sqlite3.OperationalError:
            print("Loaded 0 titles from prgi_titles.db")
    
    # Load from admin/prgi_data.db
    if os.path.exists(ADMIN_DB_PATH):
        try:
            conn = sqlite3.connect(ADMIN_DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT title_name FROM registrations')
            titles2_raw = [row[0] for row in cursor.fetchall()]
            conn.close()
            print(f"Loaded {len(titles2_raw):,} titles from admin/prgi_data.db")
        except Exception as e:
            print(f"Warning: Could not load titles from admin/prgi_data.db: {e}")
    else:
        print(f"Warning: admin/prgi_data.db missing, skipping.")

    # Merge, filter NULL/empty, deduplicate, and store as UPPERCASE
    merged_set = set()
    for t in titles1_raw:
        if t and str(t).strip():
            merged_set.add(str(t).strip().upper())
            
    for t in titles2_raw:
        if t and str(t).strip():
            merged_set.add(str(t).strip().upper())
            
    TITLES_CACHE = list(merged_set)
    print(f"After deduplication: {len(TITLES_CACHE):,} unique titles ready")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS titles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        title TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS disallowed_words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON titles(title)')
    
    conn.commit()
    conn.close()
    
    # Load merged titles into memory on startup
    load_titles_into_memory()

def get_all_titles():
    # Return from memory cache if available, otherwise fallback to DB query
    if TITLES_CACHE:
        return TITLES_CACHE
        
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM titles')
        titles = [row[0] for row in cursor.fetchall()]
        conn.close()
        return titles
    except sqlite3.OperationalError:
        return []

def search_titles(query):
    # Search within the memory cache
    query_upper = query.upper()
    return [t for t in TITLES_CACHE if query_upper in t]

def add_disallowed_word(word):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO disallowed_words (word) VALUES (?)', (word.upper(),))
    conn.commit()
    conn.close()

def get_disallowed_words():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT word FROM disallowed_words')
        words = [row[0] for row in cursor.fetchall()]
        conn.close()
        return words
    except sqlite3.OperationalError:
        return []

def get_db_stats():
    return {
        "total_titles": len(TITLES_CACHE),
        "total_disallowed_words": len(get_disallowed_words()),
        "database": "SQLite (Merged Memory Cache)"
    }
