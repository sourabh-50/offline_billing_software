import sqlite3
import os

db_path = 'database.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT value FROM settings WHERE key='pdf_storage_path'")
        row = c.fetchone()
        print(f"PDF Storage Path: {row}")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
else:
    print("Database not found")
