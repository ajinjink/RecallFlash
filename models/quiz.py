"""Quiz data models and loader."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QuizItem:
    category: str
    question: str
    answer: str

    def to_dict(self) -> dict:
        return {"category": self.category, "question": self.question, "answer": self.answer}


class QuizLoader:
    """Load quiz data from a JSON file."""

    @staticmethod
    def load(file_path: str | Path) -> list[QuizItem]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Quiz file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [QuizItem(**item) for item in data]
