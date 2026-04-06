"""Wrong answer statistics page."""

import json
import streamlit as st
import pandas as pd
from pathlib import Path

from models.stats import StatsManager

st.set_page_config(page_title="오답 통계 — RecallFlash", page_icon="📈", layout="centered")
st.title("📈 오답 통계")

stats = StatsManager()
data = stats.get_all()

if not data:
    st.info("아직 오답 기록이 없습니다. 퀴즈를 풀어보세요!")
    st.page_link("app.py", label="⚡ 퀴즈 풀러 가기")
    st.stop()

# Build list of questions with stable order for checkbox mapping
questions_list = list(data.keys())

df = pd.DataFrame(
    [
        {"카테고리": data[q]["category"], "문제": q, "정답": data[q].get("answer", ""), "오답 횟수": data[q]["count"]}
        for q in questions_list
    ]
)

sort_order = st.radio("정렬 기준", ["오답 많은 순", "오답 적은 순"], horizontal=True)
ascending = sort_order == "오답 적은 순"
df = df.sort_values("오답 횟수", ascending=ascending).reset_index(drop=True)
df.index = df.index + 1

# Add selection column
df.insert(0, "선택", False)
edited_df = st.data_editor(df, use_container_width=True, disabled=["카테고리", "문제", "정답", "오답 횟수"])

# Export selected questions as new quiz file
selected_rows = edited_df[edited_df["선택"] == True]
if len(selected_rows) > 0:
    st.divider()
    st.subheader(f"선택한 문제: {len(selected_rows)}개")

    file_name = st.text_input("새 퀴즈 파일 이름", placeholder="예: my_review")

    if st.button("퀴즈 파일 생성", type="primary"):
        if not file_name.strip():
            st.warning("파일 이름을 입력해주세요.")
        else:
            clean_name = file_name.strip().removesuffix(".json")
            quiz_dir = Path(__file__).resolve().parent.parent / "quiz_data"
            target = quiz_dir / f"{clean_name}.json"

            if target.exists():
                st.error(f"'{clean_name}.json' 파일이 이미 존재합니다. 다른 이름을 입력해주세요.")
            else:
                quiz_items = []
                for _, row in selected_rows.iterrows():
                    quiz_items.append({
                        "category": row["카테고리"],
                        "question": row["문제"],
                        "answer": row["정답"],
                    })
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(quiz_items, f, ensure_ascii=False, indent=2)
                st.success(f"'{clean_name}.json' 파일이 생성되었습니다!")

st.divider()
st.page_link("app.py", label="⚡ 퀴즈 풀러 가기")
