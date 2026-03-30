# RecallFlash

A local quiz app built with Python and Streamlit. Load questions from a JSON file, test yourself in a web-based GUI, and get instant feedback with two grading modes.

## Features

- **JSON-based quiz data** — Each item has a category, question, and answer
- **Two grading modes** (toggle in the sidebar):
  - **String mode** — Strips whitespace and punctuation, then compares text exactly
  - **AI mode** — Falls back to OpenAI API for semantic comparison when string matching fails
- **Keyboard-driven flow** — Type your answer and press Enter to submit; press Enter again to advance to the next question
- **Wrong answer retry** — After completing a round, retry only the questions you got wrong, repeating until you get them all right (or choose to stop)
- **Wrong answer stats** — Tracks how many times each question was answered incorrectly (with category), viewable on a separate stats page with sorting

## Project Structure

```
RecallFlash/
├── app.py                    # Main Streamlit app (quiz flow)
├── pages/
│   └── stats_page.py         # Wrong answer statistics page
├── models/
│   ├── quiz.py               # QuizItem dataclass + JSON loader
│   └── stats.py              # StatsManager — tracks wrong answer counts
├── grading/
│   ├── string_grader.py      # Normalize & compare text
│   └── ai_grader.py          # OpenAI API semantic grading
├── quiz_data/
│   ├── sample.json           # Sample quiz file
│   └── stats.json            # Auto-generated wrong answer stats
├── requirements.txt
├── .env.example
└── .venv/
```

## Getting Started

### 1. Clone and set up the environment

```bash
git clone https://github.com/ajinjink/RecallFlash.git
cd RecallFlash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. (Optional) Configure OpenAI API key for AI grading

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run the app

```bash
streamlit run app.py
```

## Quiz Data Format

Place JSON files in the `quiz_data/` directory. Each file should be an array of objects:

```json
[
  {
    "category": "Python Basics",
    "question": "What index accesses the last element of a list in Python?",
    "answer": "-1"
  },
  {
    "category": "Data Structures",
    "question": "What is the operating principle of a stack?",
    "answer": "LIFO (Last In First Out)"
  }
]
```

## Grading Modes

### String Mode (default)

Strips all whitespace, punctuation, and symbols from both the user's answer and the expected answer, converts to lowercase, then compares. For example, `"LIFO Last In First Out"` matches `"LIFO (Last In First Out)"`.

### AI Mode

First attempts string comparison. If that fails, sends the question, expected answer, and user's answer to OpenAI (`gpt-4o-mini`) to determine semantic equivalence. Useful when the correct answer can be expressed in different ways or in a different order.

Enable AI mode via the toggle in the sidebar. Requires a valid `OPENAI_API_KEY` in your `.env` file.

## Stats Page

Navigate to the stats page from the sidebar. It displays every question you've gotten wrong along with its category and the number of times you got it wrong. Sort by most or fewest mistakes to identify weak areas.
