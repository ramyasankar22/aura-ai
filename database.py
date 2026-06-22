import sqlite3
import bcrypt
from datetime import datetime

DB_FILE = "aura.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            emotion TEXT NOT NULL,
            message TEXT,
            date TEXT,
            time TEXT,
            month TEXT
        )
    """)     
    c.execute("""
          CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
""")


    conn.commit()
    conn.close()

def register_user(username, password):
    try:
        conn = get_connection()
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username.lower(), hashed.decode())
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username=?",
        (username.lower(),)
    ).fetchone()
    conn.close()
    if not row:
        return False
    return bcrypt.checkpw(password.encode(), row["password_hash"].encode())

def save_message(username, role, content):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chats (username, role, content) VALUES (?, ?, ?)",
        (username.lower(), role, content)
    )
    conn.commit()
    conn.close()

def load_messages(username, limit=50):
    conn = get_connection()
    rows = conn.execute(
        """SELECT role, content FROM chats
           WHERE username=?
           ORDER BY timestamp DESC
           LIMIT ?""",
        (username.lower(), limit)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def save_emotion_db(username, emotion, message):
    now = datetime.now()
    conn = get_connection()
    conn.execute(
        """INSERT INTO emotions (username, emotion, message, date, time, month)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (username.lower(), emotion, message[:100],
         now.strftime("%Y-%m-%d"),
         now.strftime("%H:%M"),
         now.strftime("%B %Y"))
    )
    conn.commit()
    conn.close()

def load_emotions_db(username):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM emotions WHERE username=? ORDER BY date",
        (username.lower(),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_weekly_insights(username):
    conn = get_connection()
    rows = conn.execute(
        """SELECT emotion, date, time FROM emotions
           WHERE username=?
           AND date >= date('now', '-7 days')""",
        (username.lower(),)
    ).fetchall()
    conn.close()

    if not rows:
        return None

    from collections import Counter, defaultdict
    emotions = [r["emotion"] for r in rows]
    counts = Counter(emotions)
    total = len(emotions)

    day_happiness = defaultdict(int)
    for r in rows:
        if r["emotion"] == "happy":
            day_happiness[r["date"]] += 1
    happiest_day = max(day_happiness, key=day_happiness.get) if day_happiness else None

    stress_hours = []
    for r in rows:
        if r["emotion"] in ["anxious", "angry", "sad"]:
            hour = int(r["time"].split(":")[0])
            stress_hours.append(hour)
    avg_stress_hour = int(sum(stress_hours)/len(stress_hours)) if stress_hours else None

    return {
        "counts": counts,
        "total": total,
        "percentages": {k: round(v/total*100) for k, v in counts.items()},
        "happiest_day": happiest_day,
        "avg_stress_hour": avg_stress_hour,
        "mood_score": round((counts.get("happy", 0) / total) * 100)
    
    }
def save_journal(username, title, content):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO journals
        (username,title,content)
        VALUES (?,?,?)
        """,
        (username.lower(), title, content)
    )

    conn.commit()
    conn.close()


def load_journals(username):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM journals
        WHERE username=?
        ORDER BY created_at DESC
        """,
        (username.lower(),)
    ).fetchall()

    conn.close()

    return [dict(r) for r in rows]