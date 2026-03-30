"""Wrong answer statistics page."""

import streamlit as st
import pandas as pd

from models.stats import StatsManager

st.set_page_config(page_title="오답 통계 — RecallFlash", page_icon="📈", layout="centered")
st.title("📈 오답 통계")

stats = StatsManager()
data = stats.get_all()

if not data:
    st.info("아직 오답 기록이 없습니다. 퀴즈를 풀어보세요!")
    st.page_link("app.py", label="⚡ 퀴즈 풀러 가기")
    st.stop()

df = pd.DataFrame(
    [
        {"카테고리": entry["category"], "문제": q, "오답 횟수": entry["count"]}
        for q, entry in data.items()
    ]
)

sort_order = st.radio("정렬 기준", ["오답 많은 순", "오답 적은 순"], horizontal=True)
ascending = sort_order == "오답 적은 순"
df = df.sort_values("오답 횟수", ascending=ascending).reset_index(drop=True)
df.index = df.index + 1

st.dataframe(df, use_container_width=True)

st.divider()
st.page_link("app.py", label="⚡ 퀴즈 풀러 가기")
