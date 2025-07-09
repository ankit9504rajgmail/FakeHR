import sqlite3
from datetime import datetime
import bcrypt

DB_FILE = "fakehr.db"



def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # User table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )''')

    # Feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        rating INTEGER,
        comment TEXT
    )''')

     # Try to add 'created_at' column (only if it doesn't exist)
    try:
        c.execute("ALTER TABLE feedback ADD COLUMN created_at TEXT")
        c.execute("UPDATE feedback SET created_at = datetime('now') WHERE created_at IS NULL")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise  # only ignore if it's already added

    # Generation history table
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        data_type TEXT,
        details TEXT,
        timestamp TEXT
    )''')

    conn.commit()
    conn.close()


def register_user(username, password):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect(DB_FILE)  # Use fakehr.db instead of users.db
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
    conn.commit()
    conn.close()
    return True



def get_user(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def save_feedback(username, rating, comment):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO feedback (username, rating, comment, created_at) VALUES (?, ?, ?, datetime('now'))",
              (username, rating, comment))
    conn.commit()
    conn.close()


def get_all_feedback():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, rating, comment, created_at FROM feedback ORDER BY created_at DESC")
    feedback = c.fetchall()
    conn.close()
    return feedback


def save_generation_history(username, data_type, details):
    print(f"📌 SAVING HISTORY → username: {username}, type: {data_type}, details: {details}")  # Debug line
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO history (username, data_type, details, timestamp) VALUES (?, ?, ?, ?)",
              (username, data_type, details, timestamp))
    conn.commit()
    conn.close()

def get_user_history(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT data_type, details, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC", (username,))
    history = c.fetchall()
    conn.close()
    return history

