import sqlite3
from pathlib import Path
from utils import thai_now, generate_prefix

DB_PATH = Path("dn.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS running_numbers (
            prefix TEXT PRIMARY KEY,
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
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_no TEXT,
            downloaded_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_next_job_no(file_prefix="EG"):
    init_db()

    prefix = generate_prefix(file_prefix)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("BEGIN IMMEDIATE")

        cur.execute(
            "SELECT last_number FROM running_numbers WHERE prefix = ?",
            (prefix,)
        )
        row = cur.fetchone()

        if row is None:
            next_number = 1
            cur.execute(
                "INSERT INTO running_numbers (prefix, last_number) VALUES (?, ?)",
                (prefix, next_number)
            )
        else:
            next_number = row[0] + 1
            cur.execute(
                "UPDATE running_numbers SET last_number = ? WHERE prefix = ?",
                (next_number, prefix)
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return f"{prefix}{next_number:03d}"


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
        thai_now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def record_download(job_no):
    init_db()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO downloads (job_no, downloaded_at)
        VALUES (?, ?)
    """, (
        job_no,
        thai_now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
