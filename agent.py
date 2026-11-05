from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from dateparser.search import search_dates
from dotenv import load_dotenv

from database import add_task, complete_task, delete_task, list_tasks

load_dotenv()


@dataclass
class AgentResult:
    """The data returned to the Streamlit interface."""

    reply: str
    activity: list[str] = field(default_factory=list)
    mode: str = "Demo Agent"


TOOLS = [
    {
        "type": "function",
        "name": "add_task",
        "description": "Add a new task to the task database.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "A short and clear task title.",
                },
                "deadline": {
                    "type": "string",
                    "description": (
                        "Deadline in a readable format such as 2026-07-05, "
                        "Tomorrow, Friday, or No deadline."
                    ),
                },
                "priority": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High"],
                    "description": "Task priority.",
                },
            },
            "required": ["title", "deadline", "priority"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_tasks",
        "description": "Show all tasks, pending tasks, or completed tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["All", "Pending", "Completed"],
                    "description": "Which tasks should be returned.",
                }
            },
            "required": ["status"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "complete_task",
        "description": "Mark a task as completed by matching its title.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_name": {
                    "type": "string",
                    "description": "Full or partial title of the task.",
                }
            },
            "required": ["task_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "delete_task",
        "description": "Delete a task by matching its title.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_name": {
                    "type": "string",
                    "description": "Full or partial title of the task.",
                }
            },
            "required": ["task_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def _format_task(task: dict[str, Any]) -> str:
    icon = "✅" if task["status"] == "Completed" else "🟣"
    return (
        f'{icon} **#{task["id"]} — {task["title"]}**  \n'
        f'Deadline: {task["deadline"]} · '
        f'Priority: {task["priority"]} · Status: {task["status"]}'
    )


def _format_task_list(tasks: list[dict[str, Any]], heading: str) -> str:
    if not tasks:
        return f"### {heading}\nNo tasks found."

    task_lines = "\n\n".join(_format_task(task) for task in tasks)
    return f"### {heading}\n{task_lines}"


def _execute_tool(name: str, arguments: dict[str, Any]) -> tuple[str, str]:
    """Run a database function and return JSON plus an activity message."""
    if name == "add_task":
        task = add_task(
            title=arguments["title"],
            deadline=arguments["deadline"],
            priority=arguments["priority"],
        )
        result = {"success": True, "task": task}
        activity = f'Added task: {task["title"]}'

    elif name == "list_tasks":
        tasks = list_tasks(arguments["status"])
        result = {
            "success": True,
            "status": arguments["status"],
            "tasks": tasks,
        }
        activity = f'Loaded {arguments["status"].lower()} tasks'

    elif name == "complete_task":
        task = complete_task(arguments["task_name"])
        result = {"success": True, "task": task}
        activity = f'Completed task: {task["title"]}'

    elif name == "delete_task":
        task = delete_task(arguments["task_name"])
        result = {"success": True, "task": task}
        activity = f'Deleted task: {task["title"]}'

    else:
        raise ValueError(f"Unknown tool: {name}")

    return json.dumps(result, ensure_ascii=False), activity


class ProviderUnavailableError(Exception):
    """Raised only when a provider's first API request fails, before task actions run."""


def _openai_agent(message: str) -> AgentResult:
    """Use OpenAI Responses API function calling when an API key is configured."""
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    today = datetime.now().strftime("%A, %d %B %Y")

    instructions = f"""
You are TaskBot AI, a concise and friendly task-management agent.
Today is {today}.

You can add, list, complete, and delete tasks by calling tools.
Always use a tool when the user requests a task-management action.
For an add request:
- create a short title,
- use "No deadline" when no deadline is provided,
- use Medium priority when no priority is provided.
Never claim an action succeeded unless the tool result says it succeeded.
Keep the final answer brief and use readable Markdown.
"""

    running_input: list[Any] = [{"role": "user", "content": message}]
    try:
        response = client.responses.create(
            model=model,
            instructions=instructions,
            tools=TOOLS,
            input=running_input,
            parallel_tool_calls=False,
        )
    except Exception as error:
        raise ProviderUnavailableError(str(error)) from error

    running_input += response.output
    activity = ["Understood your request", "Selected the appropriate tool"]
    tool_was_called = False

    for item in response.output:
        if item.type != "function_call":
            continue

        tool_was_called = True
        arguments = json.loads(item.arguments)

        try:
            tool_output, step = _execute_tool(item.name, arguments)
            activity.append(step)
        except Exception as error:
            tool_output = json.dumps(
                {"success": False, "error": str(error)},
                ensure_ascii=False,
            )
            activity.append(f"Tool reported: {error}")

        running_input.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": tool_output,
            }
        )

    if tool_was_called:
        response = client.responses.create(
            model=model,
            instructions=instructions,
            tools=TOOLS,
            input=running_input,
            parallel_tool_calls=False,
        )
        activity.append("Prepared the final response")

    reply = response.output_text.strip()
    if not reply:
        reply = "I processed your request."

    return AgentResult(
        reply=reply,
        activity=activity,
        mode=f"OpenAI · {model}",
    )



def _groq_agent(message: str) -> AgentResult:
    """Use Groq Chat Completions with function calling for task actions."""
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    today = datetime.now().strftime("%A, %d %B %Y")

    instructions = f"""
You are TaskBot AI, a concise and friendly task-management agent.
Today is {today}.

You can add, list, complete, and delete tasks by calling tools.
Always use a tool when the user requests a task-management action.
For an add request:
- create a short title,
- use "No deadline" when no deadline is provided,
- use Medium priority when no priority is provided.
Never claim an action succeeded unless the tool result says it succeeded.
Keep the final answer brief and use readable Markdown.
"""

    # Groq uses the Chat Completions function-tool format.
    groq_tools = [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            },
        }
        for tool in TOOLS
    ]

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": message},
    ]
    activity = ["Understood your request", "Selected the appropriate tool"]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
            parallel_tool_calls=False,
        )
    except Exception as error:
        raise ProviderUnavailableError(str(error)) from error

    assistant_message = response.choices[0].message
    tool_calls = assistant_message.tool_calls or []

    if tool_calls:
        messages.append(assistant_message.model_dump(exclude_none=True))

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")

            try:
                tool_output, step = _execute_tool(tool_name, arguments)
                activity.append(step)
            except Exception as error:
                tool_output = json.dumps(
                    {"success": False, "error": str(error)},
                    ensure_ascii=False,
                )
                activity.append(f"Tool reported: {error}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_output,
                }
            )

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
            parallel_tool_calls=False,
        )
        activity.append("Prepared the final response")

    reply = response.choices[0].message.content or "I processed your request."
    return AgentResult(
        reply=reply.strip(),
        activity=activity,
        mode=f"Groq · {model}",
    )



def _gemini_agent(message: str) -> AgentResult:
    """Use Gemini through Google's OpenAI-compatible Chat Completions endpoint."""
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    today = datetime.now().strftime("%A, %d %B %Y")
    instructions = f"""You are TaskBot AI, a concise task-management agent.
Today is {today}. You can add, list, complete, and delete tasks using tools.
Always use a tool for task actions. For adds, use No deadline if absent and Medium priority if absent.
Never claim an action succeeded unless the tool result confirms it. Keep replies brief."""

    gemini_tools = [
        {"type": "function", "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"],
        }}
        for tool in TOOLS
    ]
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": message},
    ]
    activity = ["Understood your request", "Selected the appropriate tool"]
    try:
        response = client.chat.completions.create(
            model=model, messages=messages, tools=gemini_tools, tool_choice="auto"
        )
    except Exception as error:
        raise ProviderUnavailableError(str(error)) from error

    assistant_message = response.choices[0].message
    tool_calls = assistant_message.tool_calls or []
    if tool_calls:
        messages.append(assistant_message.model_dump(exclude_none=True))
        for tool_call in tool_calls:
            try:
                output, step = _execute_tool(
                    tool_call.function.name,
                    json.loads(tool_call.function.arguments or "{}"),
                )
                activity.append(step)
            except Exception as error:
                output = json.dumps({"success": False, "error": str(error)}, ensure_ascii=False)
                activity.append(f"Tool reported: {error}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": output,
            })
        response = client.chat.completions.create(
            model=model, messages=messages, tools=gemini_tools, tool_choice="auto"
        )
        activity.append("Prepared the final response")

    reply = response.choices[0].message.content or "I processed your request."
    return AgentResult(reply=reply.strip(), activity=activity, mode=f"Gemini · {model}")


def _extract_deadline(message: str) -> tuple[str, str]:
    """
    Find a date phrase and return:
    (readable deadline, message with that date phrase removed).
    """
    found = search_dates(
        message,
        languages=["en"],
        settings={
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": datetime.now(),
        },
    )

    if not found:
        return "No deadline", message

    phrase, parsed_date = found[-1]
    deadline = parsed_date.strftime("%d %b %Y")
    cleaned = re.sub(re.escape(phrase), "", message, flags=re.IGNORECASE)
    return deadline, cleaned


def _clean_task_title(text: str) -> str:
    """Remove command words and leftover date connectors."""
    cleaned = text.strip(" .,!?:;-")
    cleaned = re.sub(
        r"^(please\s+)?(add|create|make|remember)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"^(please\s+)?remind\s+me\s+to\s+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"^(a\s+)?task\s+(to\s+)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\b(for|on|by|before|due)\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,!?:;-")
    return cleaned


def _extract_target(message: str, verbs: str) -> str:
    pattern = rf"\b(?:{verbs})\b\s+(?:the\s+task\s+)?(?:task\s+)?(.+)"
    match = re.search(pattern, message, flags=re.IGNORECASE)
    if not match:
        return ""
    target = match.group(1)
    target = re.sub(r"\b(as\s+)?(complete|completed|done)\b", "", target, flags=re.I)
    return target.strip(" .,!?:;-'\"")


def _detect_priority(message: str) -> str:
    lower = message.lower()
    if "high priority" in lower or "urgent" in lower:
        return "High"
    if "low priority" in lower:
        return "Low"
    return "Medium"


def _demo_agent(message: str, fallback_reason: str | None = None) -> AgentResult:
    """
    A zero-cost local agent.

    It detects the user's intent and selects one of four database tools.
    This makes the project runnable before an API key is added.
    """
    lower = message.lower().strip()
    activity = ["Read the message", "Detected the user's intent"]

    if fallback_reason:
        activity.insert(0, "OpenAI unavailable — switched to local demo mode")

    try:
        # LIST TASKS
        if any(word in lower for word in ("show", "list", "view", "display", "what")) and (
            "task" in lower or "todo" in lower or "to-do" in lower
        ):
            if "completed" in lower or "finished" in lower or "done" in lower:
                status = "Completed"
            elif "pending" in lower or "remaining" in lower:
                status = "Pending"
            else:
                status = "All"

            tasks = list_tasks(status)
            activity.extend(
                [
                    f"Selected list_tasks({status})",
                    f"Loaded {len(tasks)} task(s) from SQLite",
                ]
            )
            return AgentResult(
                reply=_format_task_list(tasks, f"{status} Tasks"),
                activity=activity,
            )

        # COMPLETE TASK
        if any(word in lower for word in ("complete", "completed", "finish", "finished", "done")):
            target = _extract_target(
                message,
                "complete|completed|finish|finished|mark",
            )
            if not target:
                return AgentResult(
                    reply='Please include the task name, for example: **Complete project report**.',
                    activity=activity + ["Needed a task name"],
                )

            task = complete_task(target)
            activity.extend(
                [
                    f'Selected complete_task("{target}")',
                    "Updated the task in SQLite",
                ]
            )
            return AgentResult(
                reply=f'✅ **{task["title"]}** has been marked as completed.',
                activity=activity,
            )

        # DELETE TASK
        if any(word in lower for word in ("delete", "remove")):
            target = _extract_target(message, "delete|remove")
            if not target:
                return AgentResult(
                    reply='Please include the task name, for example: **Delete project report**.',
                    activity=activity + ["Needed a task name"],
                )

            task = delete_task(target)
            activity.extend(
                [
                    f'Selected delete_task("{target}")',
                    "Removed the task from SQLite",
                ]
            )
            return AgentResult(
                reply=f'🗑️ **{task["title"]}** has been deleted.',
                activity=activity,
            )

        # ADD TASK
        if (
            any(word in lower for word in ("add", "create", "remember", "remind"))
            or lower.startswith("task ")
        ):
            deadline, text_without_date = _extract_deadline(message)
            title = _clean_task_title(text_without_date)
            priority = _detect_priority(message)

            # Remove priority wording from the task title.
            title = re.sub(
                r"\b(high|medium|low)\s+priority\b",
                "",
                title,
                flags=re.IGNORECASE,
            ).strip(" .,!?:;-")
            title = re.sub(
                r"\b(for|on|by|before|due)\s+(with\s*)?$",
                "",
                title,
                flags=re.IGNORECASE,
            ).strip(" .,!?:;-")
            title = re.sub(r"\s+", " ", title)

            if not title:
                return AgentResult(
                    reply='Please include a task title, for example: **Add project report for tomorrow**.',
                    activity=activity + ["Needed a task title"],
                )

            task = add_task(title, deadline, priority)
            activity.extend(
                [
                    f'Selected add_task("{title}")',
                    "Saved the task in SQLite",
                ]
            )
            return AgentResult(
                reply=(
                    "✅ **Task added successfully**\n\n"
                    f'- **Task:** {task["title"]}\n'
                    f'- **Deadline:** {task["deadline"]}\n'
                    f'- **Priority:** {task["priority"]}'
                ),
                activity=activity,
            )

        # HELP / GENERAL MESSAGE
        activity.append("Returned usage help")
        return AgentResult(
            reply=(
                "I can manage your tasks. Try one of these:\n\n"
                "- **Add project report for tomorrow**\n"
                "- **Show my pending tasks**\n"
                "- **Complete project report**\n"
                "- **Delete project report**"
            ),
            activity=activity,
        )

    except ValueError as error:
        activity.append(f"Database tool reported: {error}")
        return AgentResult(
            reply=f"⚠️ {error}",
            activity=activity,
        )


def process_message(message: str, mode: str = "Demo Mode") -> AgentResult:
    """Use Groq first and Gemini as the backup provider."""
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if mode == "Auto Mode":
        groq_error = ""
        if groq_key:
            try:
                result = _groq_agent(message)
                result.activity.insert(0, "Auto Mode · Groq handled the request")
                result.mode = f"Auto · {result.mode}"
                return result
            except ProviderUnavailableError as error:
                groq_error = str(error)
            except Exception as error:
                return AgentResult(
                    reply=f"⚠️ Groq failed after processing started. No retry was made to avoid repeating a task action. Error: {error}",
                    activity=["Auto Mode selected", "Groq failed after initial response"],
                    mode="Auto · Groq error",
                )
        if gemini_key:
            try:
                result = _gemini_agent(message)
                result.activity.insert(0, "Auto Mode · Gemini handled the request")
                if groq_error:
                    result.activity.insert(1, "Groq was unavailable; switched to Gemini")
                result.mode = f"Auto · {result.mode}"
                return result
            except ProviderUnavailableError as error:
                return AgentResult(
                    reply=f"⚠️ Groq and Gemini are unavailable. Groq: {groq_error or 'not configured'}. Gemini: {error}",
                    activity=["Auto Mode selected", "Both provider requests failed"],
                    mode="Auto · Error",
                )
            except Exception as error:
                return AgentResult(
                    reply=f"⚠️ Gemini failed after processing started. No retry was made to avoid repeating a task action. Error: {error}",
                    activity=["Auto Mode selected", "Gemini failed after initial response"],
                    mode="Auto · Gemini error",
                )
        return AgentResult(
            reply="⚠️ Add GROQ_API_KEY and/or GEMINI_API_KEY to Streamlit Secrets to use Auto Mode.",
            activity=["Auto Mode selected", "No API keys found"],
            mode="Auto · Not configured",
        )

    if mode == "Gemini Mode":
        if not gemini_key:
            return AgentResult(
                reply="⚠️ Add GEMINI_API_KEY to Streamlit Secrets or your .env file.",
                activity=["Gemini Mode selected", "API key not found"],
                mode="Gemini · Not configured",
            )
        try:
            return _gemini_agent(message)
        except ProviderUnavailableError as error:
            return AgentResult(
                reply=f"⚠️ Could not connect to Gemini. Check your API key, model, and quota. Error: {error}",
                activity=["Gemini Mode selected", "Gemini request failed"],
                mode="Gemini · Error",
            )
        except Exception as error:
            return AgentResult(
                reply=f"⚠️ Gemini failed after processing started. No retry was made to avoid duplicate task actions. Error: {error}",
                activity=["Gemini Mode selected", "Gemini request failed after initial response"],
                mode="Gemini · Error",
            )

    if mode == "Groq Mode":
        if not groq_key:
            return AgentResult(
                reply="⚠️ Add GROQ_API_KEY to Streamlit Secrets or your .env file.",
                activity=["Groq Mode selected", "API key not found"],
                mode="Groq · Not configured",
            )
        try:
            return _groq_agent(message)
        except ProviderUnavailableError as error:
            if gemini_key:
                try:
                    result = _gemini_agent(message)
                    result.activity.insert(0, "Groq was unavailable; Gemini handled the request")
                    result.mode = f"Fallback · {result.mode}"
                    return result
                except Exception as backup_error:
                    return AgentResult(
                        reply=f"⚠️ Groq and Gemini are unavailable. Groq: {error}. Gemini: {backup_error}",
                        activity=["Groq failed", "Gemini backup failed"],
                        mode="Both providers · Error",
                    )
            return AgentResult(
                reply=f"⚠️ Groq failed and no Gemini backup key is configured. Error: {error}",
                activity=["Groq Mode selected", "No Gemini backup key"],
                mode="Groq · Error",
            )
        except Exception as error:
            return AgentResult(
                reply=f"⚠️ Groq failed after processing started. No retry was made to avoid duplicate task actions. Error: {error}",
                activity=["Groq failed after initial response"],
                mode="Groq · Error",
            )

    return _demo_agent(message)
