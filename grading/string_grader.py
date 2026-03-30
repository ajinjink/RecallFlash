"""String-based answer grader."""

import re
import unicodedata


def normalize(text: str) -> str:
    """Strip whitespace, punctuation, and symbols, then lowercase."""
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = re.sub(r"[^\w]", "", text)  # Keep only alphanumeric and underscores
    return text


def check(user_answer: str, correct_answer: str) -> bool:
    return normalize(user_answer) == normalize(correct_answer)
