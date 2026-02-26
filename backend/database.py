import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'prgi_titles.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

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

def get_all_titles():
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT title FROM titles WHERE title LIKE ?', (f'%{query}%',))
    titles = [row[0] for row in cursor.fetchall()]
    conn.close()
    return titles

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
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM titles')
        total_titles = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM disallowed_words')
        total_words = cursor.fetchone()[0]
        conn.close()
        return {
            "total_titles": total_titles,
            "total_disallowed_words": total_words,
            "database": "SQLite"
        }
    except sqlite3.OperationalError:
        return {"error": "Database not initialized"}
