from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

DB_FILE = "kurdsmart.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kurdish TEXT NOT NULL,
    persian TEXT NOT NULL,
    english TEXT NOT NULL,
    domain TEXT NOT NULL,
    dialect TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS saved_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vocabulary_id INTEGER NOT NULL,
    note TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
);

CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    answer TEXT NOT NULL,
    level TEXT NOT NULL,
    dialect TEXT NOT NULL
);
"""

SEED_VOCABULARY: Iterable[tuple[str, str, str, str, str]] = [
    ("سڵاو", "سلام", "Hello", "general", "Sorani"),
    ("سپاس", "متشکرم", "Thank you", "general", "Sorani"),
    ("پزیشک", "پزشک", "Doctor", "medical", "Sorani"),
    ("فشاری خوێن", "فشار خون", "Blood pressure", "medical", "Sorani"),
    ("سیستەم", "سیستم", "System", "technical", "Sorani"),
    ("ڕاژە", "سرور", "Server", "technical", "Sorani"),
    ("Silav", "سلام", "Hello", "general", "Kurmanji"),
    ("Spas", "متشکرم", "Thank you", "general", "Kurmanji"),
    ("Bijîşk", "پزشک", "Doctor", "medical", "Kurmanji"),
    ("Pergal", "سیستم", "System", "technical", "Kurmanji"),
]

SEED_EXERCISES: Iterable[tuple[str, str, str, str]] = [
    ("Translate to Kurdish (Sorani): Hello", "سڵاو", "easy", "Sorani"),
    ("Translate to Kurdish (Kurmanji): Thank you", "Spas", "easy", "Kurmanji"),
    ("Complete the phrase: ____ bo te heye (I have ... for you)", "سپاس", "medium", "Sorani"),
]


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_dir: Path) -> Path:
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / DB_FILE

    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)

        count = conn.execute("SELECT COUNT(*) AS c FROM vocabulary").fetchone()["c"]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO vocabulary (kurdish, persian, english, domain, dialect)
                VALUES (?, ?, ?, ?, ?)
                """,
                SEED_VOCABULARY,
            )

        ex_count = conn.execute("SELECT COUNT(*) AS c FROM exercises").fetchone()["c"]
        if ex_count == 0:
            conn.executemany(
                """
                INSERT INTO exercises (prompt, answer, level, dialect)
                VALUES (?, ?, ?, ?)
                """,
                SEED_EXERCISES,
            )

        conn.commit()

    return db_path
