from __future__ import annotations


class SentenceService:
    _templates = {
        "Sorani": [
            "{subject} {verb} {object}.",
            "ئەمڕۆ {subject} لەگەڵ {object} {verb}.",
            "تکایە {object} {verb}.",
        ],
        "Kurmanji": [
            "{subject} {verb} {object}.",
            "Îro {subject} bi {object} re {verb}.",
            "Ji kerema xwe {object} {verb}.",
        ],
    }

    def generate(self, subject: str, verb: str, object_: str, dialect: str) -> list[str]:
        templates = self._templates.get(dialect, self._templates["Sorani"])
        return [
            template.format(subject=subject.strip(), verb=verb.strip(), object=object_.strip())
            for template in templates
        ]

    def analyze(self, sentence: str) -> dict:
        clean = sentence.strip()
        words = [token for token in clean.replace(".", "").split(" ") if token]
        return {
            "word_count": len(words),
            "characters": len(clean),
            "tokens": words,
            "hint": "Try changing one verb tense and compare meaning.",
        }
