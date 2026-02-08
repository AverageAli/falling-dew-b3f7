from __future__ import annotations

from pathlib import Path

from ..database import get_connection


class PracticeService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def list_exercises(self, dialect: str) -> list[dict]:
        query = "SELECT id, prompt, answer, level, dialect FROM exercises WHERE dialect = ? ORDER BY id"
        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, (dialect,)).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def check_answer(user_answer: str, expected: str) -> bool:
        return user_answer.strip().casefold() == expected.strip().casefold()
