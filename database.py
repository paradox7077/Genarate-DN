import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("dn.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS running_number (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            last_number INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_no TEXT NOT NULL UNIQUE,
            original_file_name TEXT,
            upload_path TEXT,
            output_path TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO running_number (id, last_number)
        VALUES (1, 0)
    """)

    conn.commit()
    conn.close()


def get_next_job_no():
    init_db()

    now = datetime.now()
    prefix = now.strftime("EG%y%m%d%H%M")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT last_number FROM running_number WHERE id = 1")
    last_number = cur.fetchone()[0]

    next_number = last_number + 1

    cur.execute(
        "UPDATE running_number SET last_number = ? WHERE id = 1",
        (next_number,)
    )

    conn.commit()
    conn.close()

    running = f"{next_number:03d}"
    return f"{prefix}{running}"


def create_job(job_no, original_file_name, upload_path, output_path, status="Success"):
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO jobs (
            job_no,
            original_file_name,
            upload_path,
            output_path,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        job_no,
        original_file_name,
        upload_path,
        output_path,
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
