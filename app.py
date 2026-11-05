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

# Load provider settings from Streamlit Cloud Secrets or local environment.
try:
    for key in (
        "AI_PROVIDER", "GROQ_API_KEY", "GROQ_MODEL",
        "GEMINI_API_KEY", "GEMINI_MODEL",
    ):
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass

st.set_page_config(
    page_title="TaskBot AI · Workspace",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css(st)
init_db()

WELCOME = (
    "Hey! I'm **TaskBot AI** 👋\\n\\n"
    "I can add tasks, check your pending work, complete tasks, and keep your day organised. "
    "What would you like to do?"
)


def go_to_page(page_name: str) -> None:
    """Update navigation through a button callback before the next rerun."""
    st.session_state["active_page"] = page_name


def start_new_conversation() -> None:
    st.session_state["messages"] = [{
        "role": "assistant", "content": WELCOME,
        "activity": [], "mode": "TaskBot",
    }]
    st.session_state["active_page"] = "AI Assistant"


def initialize_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": WELCOME,
            "activity": ["Workspace ready", "Connected to SQLite task database"],
            "mode": "TaskBot",
        }]
    if "agent_mode" not in st.session_state:
        st.session_state.agent_mode = "Auto Mode"


def render_sidebar() -> str:
    groq_key = bool(os.getenv("GROQ_API_KEY", "").strip())
    gemini_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
    configured = os.getenv("AI_PROVIDER", "auto").strip().lower()

    if configured == "groq" and groq_key:
        default_mode = "Groq Mode"
    elif configured == "gemini" and gemini_key:
        default_mode = "Gemini Mode"
    elif configured == "auto" and (groq_key or gemini_key):
        default_mode = "Auto Mode"
    else:
        default_mode = "Demo Mode"

    modes = ["Auto Mode", "Groq Mode", "Gemini Mode", "Demo Mode"]
    with st.sidebar:
        st.markdown('<div class="brand-lockup"><div class="brand-mark">✦</div><div><div class="brand-name">TaskBot AI</div><div class="brand-caption">PERSONAL WORKSPACE</div></div></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="side-label">WORKSPACE</div>', unsafe_allow_html=True)
        page = st.radio(
            "Navigation",
            ["Overview", "AI Assistant", "My Tasks", "About"],
            label_visibility="collapsed",
            key="active_page",
        )
        st.markdown("---")
        st.markdown('<div class="side-label">AI PROVIDER</div>', unsafe_allow_html=True)
        selected_mode = st.selectbox(
            "Choose provider",
            modes,
            index=modes.index(st.session_state.get("agent_mode", default_mode))
            if st.session_state.get("agent_mode", default_mode) in modes
            else modes.index(default_mode),
            key="agent_mode",
        )
        if selected_mode == "Auto Mode":
            if groq_key and gemini_key:
                st.success("Auto mode · Groq + Gemini ready")
            elif groq_key or gemini_key:
                st.info("Auto mode · One provider configured")
            else:
                st.warning("Add a Groq or Gemini key in Secrets.")
        elif selected_mode == "Groq Mode":
            if groq_key:
                st.success("Groq key configured")
            else:
                st.warning("GROQ_API_KEY not found")
        elif selected_mode == "Gemini Mode":
            if gemini_key:
                st.success("Gemini key configured")
            else:
                st.warning("GEMINI_API_KEY not found")
        else:
            st.caption("Local demo · No API usage")

        st.markdown('<div class="sidebar-tip"><strong>Quick tip</strong><br>Try “Add assignment for Friday” or “Show my pending tasks”.</div>', unsafe_allow_html=True)
        st.button(
            "＋  New conversation",
            use_container_width=True,
            on_click=start_new_conversation,
        )
    return page


def render_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-heading"><div class="eyebrow">{html.escape(eyebrow)}</div>'
        f'<h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def render_stats() -> None:
    stats = get_stats()
    completion = round((stats["completed"] / stats["total"]) * 100) if stats["total"] else 0
    cards = [
        ("TOTAL TASKS", stats["total"], "▤", "All your tasks"),
        ("PENDING", stats["pending"], "◷", "Still to do"),
        ("COMPLETED", stats["completed"], "✓", "Successfully done"),
    ]
    cols = st.columns(3)
    for col, (label, value, symbol, hint) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-top"><span>{label}</span><span class="metric-icon">{symbol}</span></div>'
                f'<div class="metric-number">{value}</div><div class="metric-hint">{hint}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown(
        f'<div class="progress-panel"><div class="progress-copy"><span>Overall progress</span><strong>{completion}%</strong></div>'
        f'<div class="progress-track"><div class="progress-fill" style="width:{completion}%"></div></div></div>',
        unsafe_allow_html=True,
    )


def render_activity(activity: list[str], mode: str) -> None:
    if not activity:
        return
    steps = "".join(f"<li>{html.escape(step)}</li>" for step in activity)
    st.markdown(
        f'<div class="activity-panel"><div class="activity-heading">✦ Agent activity <span>{html.escape(mode)}</span></div><ul>{steps}</ul></div>',
        unsafe_allow_html=True,
    )


def process_and_save_assistant_message(message: str) -> None:
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("TaskBot is thinking..."):
            result: AgentResult = process_message(
                message, st.session_state.get("agent_mode", "Demo Mode")
            )
        st.markdown(result.reply)
        render_activity(result.activity, result.mode)
    st.session_state.messages.append({
        "role": "assistant", "content": result.reply,
        "activity": result.activity, "mode": result.mode,
    })


def render_chat_page() -> None:
    render_header("YOUR AI WORKSPACE", "AI Assistant", "Tell TaskBot what you need to get done. It can manage your tasks using natural language.")
    st.markdown('<div class="chat-intro"> <span class="online-dot"></span> TaskBot is ready to help</div>', unsafe_allow_html=True)
    suggestions = [
        ("＋  Add a task", "Add my project assignment for tomorrow"),
        ("▤  Pending tasks", "Show my pending tasks"),
        ("✓  Completed", "Show my completed tasks"),
        ("✦  Help me", "What can you do?"),
    ]
    cols = st.columns(4)
    chosen = None
    for col, (label, prompt) in zip(cols, suggestions):
        with col:
            if st.button(label, key=f"suggest_{label}", use_container_width=True):
                chosen = prompt

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "🙂"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_activity(message.get("activity", []), message.get("mode", "TaskBot"))

    typed = st.chat_input("Message TaskBot...  (e.g. Add project report for Friday)")
    prompt = typed or chosen
    if prompt:
        st.session_state.messages.append({
            "role": "user", "content": prompt, "activity": [], "mode": ""
        })
        process_and_save_assistant_message(prompt)
        st.rerun()


def render_task_card(task: dict) -> None:
    safe_title = html.escape(str(task["title"]))
    safe_deadline = html.escape(str(task["deadline"]))
    priority = str(task["priority"])
    status = str(task["status"])
    priority_class = priority.lower() if priority.lower() in {"low", "medium", "high"} else "medium"
    status_class = "completed" if status == "Completed" else "pending"
    st.markdown(
        f'<div class="task-row"><div class="task-main"><div class="task-name">{safe_title}</div>'
        f'<div class="task-sub">Task #{task["id"]} · Due {safe_deadline}</div></div>'
        f'<div class="task-tags"><span class="tag {priority_class}">{html.escape(priority)} priority</span>'
        f'<span class="tag {status_class}">{html.escape(status)}</span></div></div>',
        unsafe_allow_html=True,
    )


def render_tasks_page() -> None:
    render_header("STAY ON TRACK", "My Tasks", "A clear view of everything on your plate.")
    tasks = list_tasks("All")
    left, right = st.columns([2, 1])
    with left:
        search = st.text_input("Search tasks", placeholder="Search by task name...", label_visibility="collapsed")
    with right:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])
    priority_filter = st.selectbox("Priority", ["All priorities", "High", "Medium", "Low"], label_visibility="collapsed")
    filtered = [
        task for task in tasks
        if search.lower() in task["title"].lower()
        and (status_filter == "All" or task["status"] == status_filter)
        and (priority_filter == "All priorities" or task["priority"] == priority_filter)
    ]
    st.caption(f"Showing {len(filtered)} of {len(tasks)} tasks")
    if not filtered:
        st.info("No matching tasks. Try changing your search or filters.")
        return
    for task in filtered:
        a, b, c = st.columns([7, 1.2, 1.0], vertical_alignment="center")
        with a:
            render_task_card(task)
        with b:
            if task["status"] == "Pending" and st.button("Complete", key=f"done_{task['id']}", use_container_width=True):
                complete_task_by_id(task["id"])
                st.toast("Task completed")
                st.rerun()
        with c:
            if st.button("Delete", key=f"remove_{task['id']}", use_container_width=True):
                st.session_state[f"confirm_delete_{task['id']}"] = True
        if st.session_state.get(f"confirm_delete_{task['id']}", False):
            st.warning(f'Delete “{task["title"]}”? This cannot be undone.')
            yes, no = st.columns(2)
            with yes:
                if st.button("Yes, delete", key=f"yes_delete_{task['id']}"):
                    delete_task_by_id(task["id"])
                    st.session_state.pop(f"confirm_delete_{task['id']}", None)
                    st.toast("Task deleted")
                    st.rerun()
            with no:
                if st.button("Cancel", key=f"cancel_delete_{task['id']}"):
                    st.session_state.pop(f"confirm_delete_{task['id']}", None)
                    st.rerun()


def render_overview_page() -> None:
    render_header("YOUR PRODUCTIVITY, AT A GLANCE", "Good to see you 👋", "Plan your work, stay focused, and let TaskBot handle the task updates.")
    render_stats()
    st.markdown('<div class="section-heading">A little help to get started</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="feature-card"><div class="feature-icon">✦</div><h3>Talk to your assistant</h3><p>Add, complete, or find tasks with a simple message. No forms to fill in.</p></div>', unsafe_allow_html=True)
        st.button(
            "Open AI Assistant →",
            use_container_width=True,
            on_click=go_to_page,
            args=("AI Assistant",),
        )
    with col2:
        st.markdown('<div class="feature-card"><div class="feature-icon">▤</div><h3>Organise your tasks</h3><p>Search your task list, filter by status or priority, and mark work as complete.</p></div>', unsafe_allow_html=True)
        st.button(
            "View my tasks →",
            use_container_width=True,
            on_click=go_to_page,
            args=("My Tasks",),
        )
    recent = list_tasks("All")[:5]
    st.markdown('<div class="section-heading">Recent tasks</div>', unsafe_allow_html=True)
    if recent:
        for task in recent:
            render_task_card(task)
    else:
        st.info("Your task list is empty. Start by asking TaskBot to add your first task.")


def render_about_page() -> None:
    render_header("BEHIND THE ASSISTANT", "How TaskBot works", "A conversational task manager powered by AI function calling and a local SQLite database.")
    steps = [
        ("01", "Understand", "TaskBot reads your natural-language message and identifies what you want to do."),
        ("02", "Choose a tool", "The AI selects add_task, list_tasks, complete_task, or delete_task when needed."),
        ("03", "Take action", "Python executes the selected function and reads or updates your SQLite database."),
        ("04", "Respond", "TaskBot explains the result and shows the activity performed."),
    ]
    for number, title, description in steps:
        st.markdown(f'<div class="workflow-step"><span>{number}</span><div><strong>{title}</strong><p>{description}</p></div></div>', unsafe_allow_html=True)
    st.markdown("**Available providers:** Auto Mode (Groq with Gemini backup), Groq Mode, Gemini Mode, and Demo Mode.")


initialize_state()
page = render_sidebar()

if page == "Overview":
    render_overview_page()
elif page == "AI Assistant":
    render_chat_page()
elif page == "My Tasks":
    render_tasks_page()
else:
    render_about_page()

st.markdown('<div class="app-footer">TaskBot AI · Built to make everyday task management simpler</div>', unsafe_allow_html=True)
