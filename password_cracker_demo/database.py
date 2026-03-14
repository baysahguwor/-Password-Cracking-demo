import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "attack_logs.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attack_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            password_length INTEGER NOT NULL,
            attack_type TEXT NOT NULL,
            attempts INTEGER NOT NULL,
            time_taken REAL NOT NULL,
            result TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_log(timestamp, password_length, attack_type, attempts, time_taken, result):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attack_logs (timestamp, password_length, attack_type, attempts, time_taken, result)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, password_length, attack_type, attempts, time_taken, result))
    conn.commit()
    conn.close()


def fetch_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, password_length, attack_type, attempts, time_taken, result
        FROM attack_logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attack_logs")
    conn.commit()
    conn.close()
