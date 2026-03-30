"""OpenAI API-based semantic grader."""

from openai import OpenAI

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()  # Uses OPENAI_API_KEY env var
    return _client


def check(question: str, correct_answer: str, user_answer: str) -> bool:
    """Ask AI whether the user's answer is semantically equivalent to the correct answer."""
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict quiz grader. "
                    "Determine if the user's answer is correct for the given question. "
                    "The answer may use different wording or order, but must be factually equivalent. "
                    "Respond with ONLY 'correct' or 'incorrect'."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Expected answer: {correct_answer}\n"
                    f"User's answer: {user_answer}\n\n"
                    "Is the user's answer correct?"
                ),
            },
        ],
    )
    result = response.choices[0].message.content.strip().lower()
    return result == "correct"
