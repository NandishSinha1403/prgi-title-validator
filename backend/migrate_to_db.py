import json
import os
import sqlite3
from backend.database import get_connection, init_db

def migrate():
    # Ensure database and tables exist
    init_db()
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    titles_json = os.path.join(data_dir, 'titles_database.json')
    disallowed_json = os.path.join(data_dir, 'disallowed_words.json')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Migrate Titles
    if os.path.exists(titles_json):
        print(f"Loading titles from {titles_json}...")
        with open(titles_json, 'r') as f:
            titles = json.load(f)
        
        print(f"Inserting {len(titles)} titles into SQLite...")
        # Prepare data for executemany (list of tuples)
        titles_data = [(t.upper(),) for t in titles]
        cursor.executemany('INSERT OR IGNORE INTO titles (title) VALUES (?)', titles_data)
        conn.commit()
        print(f"Titles migration complete.")
    else:
        print("titles_database.json not found, skipping titles migration.")

    # Migrate Disallowed Words
    if os.path.exists(disallowed_json):
        print(f"Loading disallowed words from {disallowed_json}...")
        with open(disallowed_json, 'r') as f:
            words = json.load(f)
            
        print(f"Inserting {len(words)} disallowed words into SQLite...")
        words_data = [(w.upper(),) for w in words]
        cursor.executemany('INSERT OR IGNORE INTO disallowed_words (word) VALUES (?)', words_data)
        conn.commit()
        print(f"Disallowed words migration complete.")
    else:
        print("disallowed_words.json not found, skipping words migration.")

    # Get final counts
    cursor.execute('SELECT COUNT(*) FROM titles')
    final_titles_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM disallowed_words')
    final_words_count = cursor.fetchone()[0]
    
    print("\n--- Migration Summary ---")
    print(f"Total Titles in DB: {final_titles_count}")
    print(f"Total Disallowed Words in DB: {final_words_count}")
    
    conn.close()

if __name__ == "__main__":
    migrate()
