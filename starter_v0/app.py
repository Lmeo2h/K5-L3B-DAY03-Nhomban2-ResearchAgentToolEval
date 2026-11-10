"""Streamlit UI for the Research Agent.

Run from starter_v0/:  streamlit run app.py
Reuses chat.py's tool loop, so every UI turn is also saved to transcripts/*.transcript.json.
Tool calls and raw tool results (including errors) are shown in each reply — nothing is hidden.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import (ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, safe_slug, trim_history,
                  write_transcript)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

VERSION = os.getenv("AGENT_VERSION", "v5")
PROVIDER = os.getenv("AGENT_PROVIDER", "openai")
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4

SAMPLES = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Mọi người đang bàn gì về GPT-5 trên Twitter?",
    "Retrieval-augmented generation là gì? Tra Wikipedia giúp mình.",
    "Tóm tắt bài này giúp mình: https://openai.com/research/",
    "Tóm tắt 5 tweet mới nhất giúp mình",
    "Đăng câu 'Bản tin AI hôm nay đã sẵn sàng' lên Telegram",
]

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="centered")


@st.cache_resource
def load_agent():
    provider = make_provider(PROVIDER)
    tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))
    return provider, tools


def new_transcript() -> tuple[Path, dict]:
    av = build_artifact_version(VERSION, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    provider, _ = load_agent()
    ts = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    tid = "_".join([safe_slug(VERSION), safe_slug(PROVIDER), "ui", ts])
    path = ROOT / "transcripts" / f"{tid}.transcript.json"
    data = {
        "transcript_id": tid, **artifact_version_dict(av), "provider": PROVIDER,
        "model": getattr(provider, "default_model", None), "interface": "streamlit",
        "system_prompt": str(SYSTEM_PROMPT_PATH), "tools": str(TOOLS_PATH),
        "history_window": HISTORY_WINDOW, "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": now_iso(), "updated_at": now_iso(), "turns": [],
    }
    return path, data


if "messages" not in st.session_state:
    st.session_state.messages = []      # [{role, content, rounds?}]
    st.session_state.history = []       # model context (user/assistant text only)
    st.session_state.transcript_path, st.session_state.transcript = new_transcript()

with st.sidebar:
    st.header("🔎 Research Agent")
    st.caption(f"Version **{VERSION}** · provider **{PROVIDER}**")
    st.markdown(
        "**Tools:** `timeline` · `social_search` · `lookup` · `fetch` · `wiki` (mới) · `format` · "
        "`clarify` · `send` (cần xác nhận) · `policy` · `papers` · `paper_text`"
    )
    st.markdown("**Câu hỏi mẫu** (bấm để thử):")
    for q in SAMPLES:
        if st.button(q, use_container_width=True):
            st.session_state.pending = q
    if st.button("🗑️ Cuộc trò chuyện mới", use_container_width=True):
        for k in ("messages", "history", "transcript_path", "transcript"):
            st.session_state.pop(k, None)
        st.rerun()
    st.caption(f"Transcript: `{st.session_state.transcript_path.name}`")


def render_rounds(rounds: list[dict]) -> None:
    for rnd in rounds:
        for call, ev in zip(rnd.get("tool_calls", []), rnd.get("tool_results", []) or [None] * 99):
            result = (ev or {}).get("result", {}) if ev else {}
            failed = isinstance(result, dict) and result.get("error")
            label = f"{'⚠️' if failed else '🔧'} {call['name']}({json.dumps(call['args'], ensure_ascii=False)[:120]})"
            with st.expander(label, expanded=bool(failed)):
                st.json(result if ev else {"note": "no result"})


st.title("Research Agent")
st.caption("Tìm tin web/Twitter, đọc URL, tra Wikipedia, và gửi bản tin lên Telegram khi bạn xác nhận.")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m.get("rounds"):
            render_rounds(m["rounds"])
        st.markdown(m["content"])

user_text = st.chat_input("Hỏi agent...") or st.session_state.pop("pending", None)
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    provider, tools = load_agent()
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    messages = [{"role": "system", "content": system_prompt},
                *trim_history(st.session_state.history, HISTORY_WINDOW),
                {"role": "user", "content": user_text}]
    transcript = st.session_state.transcript
    turn = {"turn_index": len(transcript["turns"]) + 1, "started_at": now_iso(), "user": user_text,
            "status": "started", "assistant_text": None, "rounds": [], "tool_events": []}

    with st.chat_message("assistant"):
        with st.spinner("Agent đang làm việc..."):
            try:
                result = run_model_tool_loop(provider=provider, messages=messages, tools=tools,
                                             model=None, max_tool_rounds=MAX_TOOL_ROUNDS)
                turn.update(result)
                answer = result["assistant_text"] or "(không có nội dung)"
                if result["status"] == "waiting_for_user":
                    answer = f"❓ {answer}"
            except Exception as exc:
                turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
                result, answer = {"rounds": []}, f"⚠️ Lỗi provider: `{turn['error']}`"
        render_rounds(result.get("rounds", []))
        st.markdown(answer)

    if turn["status"] != "provider_error":
        st.session_state.history += [{"role": "user", "content": user_text},
                                     {"role": "assistant", "content": result["assistant_text"]}]
    st.session_state.messages.append({"role": "assistant", "content": answer, "rounds": result.get("rounds", [])})
    turn["ended_at"] = now_iso()
    transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, transcript)
