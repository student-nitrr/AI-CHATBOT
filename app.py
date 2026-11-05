from __future__ import annotations

import html
import os

import streamlit as st
from dotenv import load_dotenv

from agent import AgentResult, process_message
from database import (
    complete_task_by_id,
    delete_task_by_id,
    get_stats,
    init_db,
    list_tasks,
)
from styles import inject_css

load_dotenv()

# Load Streamlit Community Cloud secrets when the app is deployed.
# Local runs can continue using the .env file.
try:
    for key in ("AI_PROVIDER", "USE_OPENAI", "OPENAI_API_KEY", "OPENAI_MODEL", "GROQ_API_KEY", "GROQ_MODEL"):
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except Exception:
    # Streamlit secrets may not be configured during local development.
    pass

st.set_page_config(
    page_title="TaskBot AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css(st)
init_db()


def render_sidebar() -> str:
    openai_key = bool(os.getenv("OPENAI_API_KEY", "").strip())
    groq_key = bool(os.getenv("GROQ_API_KEY", "").strip())
    configured_provider = os.getenv("AI_PROVIDER", "").strip().lower()

    # Keep compatibility with the earlier OpenAI configuration.
    if not configured_provider and os.getenv("USE_OPENAI", "false").strip().lower() == "true":
        configured_provider = "openai"

    if configured_provider == "auto" and (groq_key or openai_key):
        default_mode = "Auto Mode"
    elif configured_provider == "groq" and groq_key:
        default_mode = "Groq Mode"
    else:
        default_mode = "Demo Mode"

    modes = ["Demo Mode", "Auto Mode", "Groq Mode"]

    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🤖 TaskBot AI</div>', unsafe_allow_html=True)
        selected_mode = st.selectbox(
            "Choose chatbot mode",
            modes,
            index=modes.index(default_mode),
            key="agent_mode",
        )

        if selected_mode == "Auto Mode":
            groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
            openai_model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
            mode_text = "Auto · Groq with OpenAI backup"
            if groq_key and openai_key:
                st.success("Auto Mode is ready · Groq primary, OpenAI backup")
            elif groq_key or openai_key:
                st.info("Auto Mode is ready with one configured provider.")
            else:
                st.warning("Add GROQ_API_KEY and/or OPENAI_API_KEY to Streamlit Secrets.")
        elif selected_mode == "Groq Mode":
            model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
            mode_text = f"Groq · {model}"
            if groq_key:
                st.success(f"Groq Mode is ready · {model}")
            else:
                st.warning("Add GROQ_API_KEY to your .env file or Streamlit Cloud Secrets.")
        else:
            mode_text = "Free local demo mode"
            st.caption("Demo Mode runs locally and does not use an API key.")

        st.markdown(f'<span class="mode-chip">{html.escape(mode_text)}</span>', unsafe_allow_html=True)

        st.markdown("### Try these commands")
        st.caption("Add project report for tomorrow")
        st.caption("Show my pending tasks")
        st.caption("Complete project report")
        st.caption("Delete project report")

        st.markdown(
            """
            <div class="sidebar-note">
                <strong>Why is this agentic?</strong><br>
                The chatbot detects an intention, selects a tool,
                executes a database action, and reports the result.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🧹 Clear chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Hello! I am **TaskBot AI**. I can add, show, "
                        "complete, and delete tasks."
                    ),
                    "activity": [],
                    "mode": mode_text,
                }
            ]
            st.rerun()

    return selected_mode

def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <span class="hero-badge">Final Year Agentic AI Project</span>
            <h1>Plan less.<br>Finish more.</h1>
            <p>
                A simple task-management chatbot that understands commands,
                chooses a tool, and performs real actions using SQLite.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats() -> None:
    stats = get_stats()
    columns = st.columns(3)
    cards = [
        ("Total tasks", stats["total"]),
        ("Pending", stats["pending"]),
        ("Completed", stats["completed"]),
    ]

    for column, (label, value) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-label">{html.escape(label)}</div>
                    <div class="stat-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_activity(activity: list[str], mode: str) -> None:
    if not activity:
        return

    steps = "<br>".join(
        f"✓ {html.escape(step)}" for step in activity
    )
    st.markdown(
        f"""
        <div class="activity-card">
            <strong>Agent activity · {html.escape(mode)}</strong><br>
            {steps}
        </div>
        """,
        unsafe_allow_html=True,
    )


def save_and_render_user_message(message: str) -> None:
    st.session_state.messages.append(
        {"role": "user", "content": message, "activity": [], "mode": ""}
    )
    with st.chat_message("user"):
        st.markdown(message)


def process_and_save_assistant_message(message: str) -> None:
    with st.chat_message("assistant"):
        with st.spinner("TaskBot is selecting a tool..."):
            result: AgentResult = process_message(
                message,
                st.session_state.get("agent_mode", "Demo Mode"),
            )
        st.markdown(result.reply)
        render_activity(result.activity, result.mode)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result.reply,
            "activity": result.activity,
            "mode": result.mode,
        }
    )


def render_chat_tab() -> None:
    st.markdown('<div class="section-title">Chat with your task agent</div>', unsafe_allow_html=True)
    st.caption("Use natural language. The agent will decide which task tool to run.")

    quick_columns = st.columns(4)
    quick_prompts = [
        ("➕ Add sample", "Add final presentation for tomorrow"),
        ("📋 Pending", "Show my pending tasks"),
        ("✅ Completed", "Show my completed tasks"),
        ("🧭 Help", "What can you do?"),
    ]

    selected_prompt = None
    for column, (label, prompt) in zip(quick_columns, quick_prompts):
        with column:
            if st.button(label, use_container_width=True):
                selected_prompt = prompt

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_activity(
                    message.get("activity", []),
                    message.get("mode", "Agent"),
                )

    typed_prompt = st.chat_input("Example: Add project report for Friday")
    prompt = typed_prompt or selected_prompt

    if prompt:
        save_and_render_user_message(prompt)
        process_and_save_assistant_message(prompt)
        st.rerun()


def render_task_card(task: dict) -> None:
    safe_title = html.escape(str(task["title"]))
    safe_deadline = html.escape(str(task["deadline"]))
    safe_priority = html.escape(str(task["priority"]))
    safe_status = html.escape(str(task["status"]))

    st.markdown(
        f"""
        <div class="task-card">
            <div class="task-title">#{task["id"]} · {safe_title}</div>
            <div class="task-meta">
                <span class="pill">{safe_status}</span>
                <span class="pill">{safe_priority} priority</span><br><br>
                Deadline: <strong>{safe_deadline}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tasks_tab() -> None:
    st.markdown('<div class="section-title">Task dashboard</div>', unsafe_allow_html=True)

    status_filter = st.segmented_control(
        "Filter tasks",
        options=["All", "Pending", "Completed"],
        default="All",
    )
    tasks = list_tasks(status_filter or "All")

    if not tasks:
        st.info("No tasks are available in this section.")
        return

    for task in tasks:
        left, complete_column, delete_column = st.columns([7, 1.25, 1.25])
        with left:
            render_task_card(task)

        with complete_column:
            st.write("")
            st.write("")
            if task["status"] == "Pending":
                if st.button(
                    "Complete",
                    key=f'complete_{task["id"]}',
                    use_container_width=True,
                ):
                    complete_task_by_id(task["id"])
                    st.toast("Task completed")
                    st.rerun()

        with delete_column:
            st.write("")
            st.write("")
            if st.button(
                "Delete",
                key=f'delete_{task["id"]}',
                use_container_width=True,
            ):
                delete_task_by_id(task["id"])
                st.toast("Task deleted")
                st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am **TaskBot AI**. I can add, show, "
                "complete, and delete your tasks."
            ),
            "activity": [
                "Application started",
                "Connected to the SQLite task database",
            ],
            "mode": "TaskBot",
        }
    ]

render_sidebar()
render_hero()
render_stats()

chat_tab, tasks_tab, about_tab = st.tabs(["💬 AI Chat", "📌 Tasks", "ℹ️ About"])

with chat_tab:
    render_chat_tab()

with tasks_tab:
    render_tasks_tab()

with about_tab:
    st.markdown("## How the agent works")
    st.markdown(
        """
        1. The user sends a natural-language request.
        2. TaskBot identifies the user's intention.
        3. It selects one tool: `add_task`, `list_tasks`,
           `complete_task`, or `delete_task`.
        4. The selected tool changes or reads the SQLite database.
        5. The chatbot explains the result and displays its activity steps.

        **Demo mode** uses a local intent detector and costs nothing.
        **OpenAI Mode** and **Groq Mode** use model function calling for better language understanding.
        """
    )
