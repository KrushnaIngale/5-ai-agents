from __future__ import annotations

import streamlit as st

from multi_agent_chatbot.config import get_settings
from multi_agent_chatbot.pipeline import build_langgraph_app, run_pipeline


def _render_agent_card(agent) -> None:
    with st.container(border=True):
        left, right = st.columns([4, 1])
        with left:
            st.subheader(f"{agent.name}: {agent.role}")
        with right:
            st.caption(agent.provider.upper())
        st.write(agent.output)


def run_app() -> None:
    settings = get_settings()

    st.set_page_config(
        page_title="Multi-Agent AI Chatbot",
        page_icon="A",
        layout="wide",
    )

    st.title("Multi-Agent AI Chatbot")
    st.caption("5 AI agents -> pipeline -> single chatbot UI")

    info_col, status_col = st.columns([3, 2])
    with info_col:
        st.write(
            "This app sends the user prompt through five specialist agents: "
            "Analyzer, Research, Reasoning, Generator, and Formatter."
        )
    with status_col:
        st.metric("Mode", "Mock" if settings.mock_mode else "Live API")
        st.metric("Default Provider", settings.default_provider)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "latest_result" not in st.session_state:
        st.session_state.latest_result = None

    use_langgraph = st.toggle("Run through LangGraph pipeline", value=False)

    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.write(item["content"])

    user_prompt = st.chat_input("Ask something")

    if user_prompt and user_prompt.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.spinner("Running multi-agent pipeline..."):
            if use_langgraph:
                graph = build_langgraph_app(settings)
                state = graph.invoke({"text": user_prompt})
                ordered_agents = [
                    state["agent_1"],
                    state["agent_2"],
                    state["agent_3"],
                    state["agent_4"],
                    state["agent_5"],
                ]
                result = {
                    "final_answer": state["text"],
                    "agents": ordered_agents,
                    "mock_mode": settings.mock_mode,
                }
            else:
                result = run_pipeline(user_prompt, settings)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": result["final_answer"]}
        )
        st.session_state.latest_result = result

        with st.chat_message("assistant"):
            st.write(result["final_answer"])

        st.success("Pipeline completed.")

    if st.session_state.latest_result:
        st.markdown("## Agent Accountability")
        for agent in st.session_state.latest_result["agents"]:
            _render_agent_card(agent)
