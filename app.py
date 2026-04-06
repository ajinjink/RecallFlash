"""RecallFlash - Main quiz app."""

import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from models.quiz import QuizLoader, QuizItem
from models.stats import StatsManager
from grading import string_grader, ai_grader

load_dotenv()

st.set_page_config(page_title="RecallFlash", page_icon="⚡", layout="centered")

# ── State initialization ─────────────────────────────────────
if "quiz_items" not in st.session_state:
    st.session_state.quiz_items = []
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0
if "wrong_items" not in st.session_state:
    st.session_state.wrong_items = []
if "phase" not in st.session_state:
    st.session_state.phase = "select"  # select | quiz | result | round_end
if "last_correct" not in st.session_state:
    st.session_state.last_correct = None
if "round_number" not in st.session_state:
    st.session_state.round_number = 1
if "correct_answer_display" not in st.session_state:
    st.session_state.correct_answer_display = ""
if "input_key_counter" not in st.session_state:
    st.session_state.input_key_counter = 0
if "user_answer_display" not in st.session_state:
    st.session_state.user_answer_display = ""

stats = StatsManager()

def autofocus_html():
    """Inject JS to auto-focus the text input."""
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
        const tryFocus = (attempts) => {
            if (attempts <= 0) return;
            const doc = window.parent.document;
            const inputs = doc.querySelectorAll('input[type="text"]:not([disabled])');
            if (inputs.length > 0) {
                const target = inputs[inputs.length - 1];
                target.focus();
            } else {
                setTimeout(() => tryFocus(attempts - 1), 100);
            }
        };
        // Attempt focus after render completes
        setTimeout(() => tryFocus(20), 200);
        </script>
        """,
        height=0,
    )


# ── Utilities ────────────────────────────────────────────────
def start_quiz(items: list[QuizItem]) -> None:
    st.session_state.quiz_items = items
    st.session_state.current_idx = 0
    st.session_state.wrong_items = []
    st.session_state.phase = "quiz"
    st.session_state.last_correct = None
    st.session_state.input_key_counter += 1


def next_question() -> None:
    st.session_state.current_idx += 1
    st.session_state.last_correct = None
    st.session_state.input_key_counter += 1
    if st.session_state.current_idx >= len(st.session_state.quiz_items):
        st.session_state.phase = "round_end"


def grade(user_answer: str, item: QuizItem, use_ai: bool) -> bool:
    if string_grader.check(user_answer, item.answer):
        return True
    if use_ai:
        try:
            return ai_grader.check(item.question, item.answer, user_answer)
        except Exception as e:
            st.warning(f"AI 채점 오류: {e}. 문자열 채점 결과를 사용합니다.")
    return False


# ── File selection screen ─────────────────────────────────────
def render_select() -> None:
    st.title("⚡ RecallFlash")
    st.write("퀴즈 JSON 파일을 선택하세요.")

    quiz_dir = Path(__file__).parent / "quiz_data"
    json_files = sorted(quiz_dir.glob("*.json"))
    json_files = [f for f in json_files if f.name != "stats.json"]

    if not json_files:
        st.error("quiz_data/ 폴더에 JSON 파일이 없습니다.")
        return

    file_names = [f.name for f in json_files]
    selected = st.selectbox("파일 선택", file_names)

    if st.button("시작", type="primary"):
        items = QuizLoader.load(quiz_dir / selected)
        st.session_state.round_number = 1
        start_quiz(items)
        st.rerun()


# ── Quiz screen ──────────────────────────────────────────────
def render_quiz(use_ai: bool) -> None:
    items = st.session_state.quiz_items
    idx = st.session_state.current_idx
    item = items[idx]
    total = len(items)

    st.progress((idx) / total, text=f"Round {st.session_state.round_number} — {idx + 1} / {total}")
    st.caption(item.category)
    st.subheader(item.question)

    # Not yet graded
    if st.session_state.last_correct is None:
        with st.form("answer_form", clear_on_submit=True):
            user_answer = st.text_input(
                "답변을 입력하세요",
                key=f"answer_input_{st.session_state.input_key_counter}",
                label_visibility="collapsed",
                placeholder="답변을 입력하세요...",
            )
            submitted = st.form_submit_button("제출", type="primary")
        autofocus_html()

        if submitted and user_answer.strip():
            is_correct = grade(user_answer.strip(), item, use_ai)
            st.session_state.last_correct = is_correct
            if not is_correct:
                st.session_state.wrong_items.append(item)
                stats.record_wrong(item.question, item.category, item.answer)
            st.session_state.correct_answer_display = item.answer
            st.session_state.user_answer_display = user_answer.strip()
            st.rerun()
        elif submitted:
            st.warning("답변을 입력해주세요.")

    # Show grading result
    else:
        st.text_input(
            "Your answer",
            value=st.session_state.user_answer_display,
            disabled=True,
            label_visibility="collapsed",
        )
        if st.session_state.last_correct:
            st.success("🎉 정답입니다!")
        else:
            st.error("❌ 오답입니다.")
            st.info(f"정답: {st.session_state.correct_answer_display}")
            if st.button("✅ 정답으로 처리", key="override_correct"):
                # Remove from wrong list
                if item in st.session_state.wrong_items:
                    st.session_state.wrong_items.remove(item)
                # Undo stats recording
                stats.undo_wrong(item.question)
                st.session_state.last_correct = True
                st.rerun()

        with st.form("next_form", clear_on_submit=True):
            st.text_input(
                "엔터를 눌러 다음 문제로",
                key=f"next_input_{st.session_state.input_key_counter}",
                label_visibility="collapsed",
                placeholder="엔터를 눌러 다음 문제로...",
            )
            st.form_submit_button("다음", type="primary", on_click=next_question)
        autofocus_html()


# ── Round end screen ─────────────────────────────────────────
def render_round_end() -> None:
    total = len(st.session_state.quiz_items)
    wrong_count = len(st.session_state.wrong_items)
    correct_count = total - wrong_count

    st.title("📊 라운드 결과")
    st.write(f"**Round {st.session_state.round_number}** 완료!")

    col1, col2 = st.columns(2)
    col1.metric("맞은 문제", f"{correct_count}/{total}")
    col2.metric("틀린 문제", f"{wrong_count}/{total}")

    if wrong_count > 0:
        st.write("틀린 문제들을 다시 풀어보시겠습니까?")
        col_a, col_b = st.columns(2)
        if col_a.button("틀린 문제 다시 풀기", type="primary"):
            wrong = list(st.session_state.wrong_items)
            st.session_state.round_number += 1
            start_quiz(wrong)
            st.rerun()
        if col_b.button("종료"):
            st.session_state.phase = "select"
            st.rerun()
    else:
        st.balloons()
        st.success("모든 문제를 맞혔습니다! 🎉")
        if st.button("처음으로"):
            st.session_state.phase = "select"
            st.rerun()


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("설정")
    use_ai = st.toggle("AI 채점 모드", value=False, help="OpenAI API를 사용하여 의미 기반 채점을 합니다.")
    if use_ai:
        st.caption("🤖 AI 채점 활성화 — 문자열 비교 후 틀리면 AI가 재판별합니다.")

    st.divider()
    if st.session_state.phase != "select":
        if st.button("처음으로 돌아가기"):
            st.session_state.phase = "select"
            st.rerun()

    st.divider()
    st.page_link("pages/stats_page.py", label="📈 오답 통계 보기")

# ── Main routing ─────────────────────────────────────────────
if st.session_state.phase == "select":
    render_select()
elif st.session_state.phase == "quiz":
    render_quiz(use_ai)
elif st.session_state.phase == "round_end":
    render_round_end()
