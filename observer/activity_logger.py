import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'gruntkill.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            data TEXT NOT NULL,
            cwd TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✓ Database initialized at", DB_PATH)

def log_event(event_type: str, data: str, cwd: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activity (timestamp, event_type, data, cwd)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), event_type, data, cwd))
    conn.commit()
    conn.close()

def get_recent_activity(days: int = 7):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, event_type, data, cwd
        FROM activity
        WHERE timestamp >= datetime('now', ?)
        ORDER BY timestamp DESC
    ''', (f'-{days} days',))
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    log_event("test", "logger is working", os.getcwd())
    print("✓ Test event logged")
    rows = get_recent_activity()
    print(f"✓ {len(rows)} events in DB")