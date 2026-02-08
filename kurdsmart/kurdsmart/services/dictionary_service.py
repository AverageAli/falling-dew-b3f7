from __future__ import annotations

from pathlib import Path

from ..database import get_connection


class DictionaryService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def search(self, term: str, dialect: str, domain: str) -> list[dict]:
        query = """
        SELECT id, kurdish, persian, english, domain, dialect
        FROM vocabulary
        WHERE dialect = ?
          AND (? = 'all' OR domain = ?)
          AND (
            kurdish LIKE ?
            OR persian LIKE ?
            OR english LIKE ?
          )
        ORDER BY kurdish ASC
        LIMIT 100
        """
        like = f"%{term.strip()}%"
        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, (dialect, domain, domain, like, like, like)).fetchall()
        return [dict(row) for row in rows]

    def save_word(self, vocabulary_id: int, note: str = "") -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                "INSERT INTO saved_words (vocabulary_id, note) VALUES (?, ?)",
                (vocabulary_id, note),
            )
            conn.commit()

    def get_saved_words(self) -> list[dict]:
        query = """
        SELECT s.id, v.kurdish, v.persian, v.english, v.domain, v.dialect, s.note, s.created_at
        FROM saved_words s
        JOIN vocabulary v ON v.id = s.vocabulary_id
        ORDER BY s.created_at DESC
        """
        with get_connection(self.db_path) as conn:
            rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
