"""Wrong answer statistics manager."""

import json
from pathlib import Path

STATS_FILE = Path(__file__).resolve().parent.parent / "quiz_data" / "stats.json"


class StatsManager:
    """Track wrong answer counts and categories per question."""

    def __init__(self, path: Path = STATS_FILE):
        self.path = path
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict[str, dict]:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Migrate legacy {question: int} format
            migrated = {}
            for k, v in raw.items():
                if isinstance(v, int):
                    migrated[k] = {"category": "", "count": v}
                else:
                    migrated[k] = v
            return migrated
        return {}

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def record_wrong(self, question: str, category: str) -> None:
        if question in self._data:
            self._data[question]["count"] += 1
            self._data[question]["category"] = category
        else:
            self._data[question] = {"category": category, "count": 1}
        self._save()

    def undo_wrong(self, question: str) -> None:
        """Decrement wrong count; remove entry if it reaches zero."""
        if question not in self._data:
            return
        self._data[question]["count"] -= 1
        if self._data[question]["count"] <= 0:
            del self._data[question]
        self._save()

    def get_all(self) -> dict[str, dict]:
        return dict(self._data)

    def get_count(self, question: str) -> int:
        entry = self._data.get(question)
        return entry["count"] if entry else 0
