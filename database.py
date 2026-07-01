from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "taskbot.db"


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection that returns rows like dictionaries."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the tasks table when the application starts for the first time."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                deadline TEXT NOT NULL DEFAULT 'No deadline',
                priority TEXT NOT NULL DEFAULT 'Medium',
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def add_task(
    title: str,
    deadline: str = "No deadline",
    priority: str = "Medium",
) -> dict[str, Any]:
    """Insert a new task and return the saved task."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Task title cannot be empty.")

    clean_deadline = deadline.strip() or "No deadline"
    clean_priority = priority.strip().title() or "Medium"
    if clean_priority not in {"Low", "Medium", "High"}:
        clean_priority = "Medium"

    created_at = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, deadline, priority, status, created_at)
            VALUES (?, ?, ?, 'Pending', ?)
            """,
            (clean_title, clean_deadline, clean_priority, created_at),
        )
        connection.commit()
        task_id = cursor.lastrowid

    return get_task_by_id(int(task_id))


def get_task_by_id(task_id: int) -> dict[str, Any]:
    """Return one task using its numeric ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Task #{task_id} was not found.")
    return dict(row)


def list_tasks(status: str = "All") -> list[dict[str, Any]]:
    """Return all, pending, or completed tasks."""
    normalized = status.strip().title()

    with get_connection() as connection:
        if normalized in {"Pending", "Completed"}:
            rows = connection.execute(
                """
                SELECT * FROM tasks
                WHERE status = ?
                ORDER BY
                    CASE priority
                        WHEN 'High' THEN 1
                        WHEN 'Medium' THEN 2
                        ELSE 3
                    END,
                    id DESC
                """,
                (normalized,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT * FROM tasks
                ORDER BY
                    CASE status WHEN 'Pending' THEN 1 ELSE 2 END,
                    id DESC
                """
            ).fetchall()

    return [dict(row) for row in rows]


def find_task(task_name: str, only_pending: bool = False) -> dict[str, Any] | None:
    """Find the newest task whose title contains the supplied text."""
    search_text = task_name.strip().lower()
    if not search_text:
        return None

    query = """
        SELECT * FROM tasks
        WHERE LOWER(title) LIKE ?
    """
    parameters: list[Any] = [f"%{search_text}%"]

    if only_pending:
        query += " AND status = 'Pending'"

    query += " ORDER BY id DESC LIMIT 1"

    with get_connection() as connection:
        row = connection.execute(query, parameters).fetchone()

    return dict(row) if row else None


def complete_task(task_name: str) -> dict[str, Any]:
    """Mark a matching pending task as completed."""
    task = find_task(task_name, only_pending=True)
    if task is None:
        raise ValueError(f'No pending task matching "{task_name}" was found.')

    with get_connection() as connection:
        connection.execute(
            "UPDATE tasks SET status = 'Completed' WHERE id = ?",
            (task["id"],),
        )
        connection.commit()

    return get_task_by_id(task["id"])


def delete_task(task_name: str) -> dict[str, Any]:
    """Delete a matching task and return the deleted task details."""
    task = find_task(task_name)
    if task is None:
        raise ValueError(f'No task matching "{task_name}" was found.')

    with get_connection() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task["id"],))
        connection.commit()

    return task


def complete_task_by_id(task_id: int) -> dict[str, Any]:
    """Complete a task from the dashboard button."""
    task = get_task_by_id(task_id)
    with get_connection() as connection:
        connection.execute(
            "UPDATE tasks SET status = 'Completed' WHERE id = ?",
            (task_id,),
        )
        connection.commit()
    return get_task_by_id(task_id)


def delete_task_by_id(task_id: int) -> dict[str, Any]:
    """Delete a task from the dashboard button."""
    task = get_task_by_id(task_id)
    with get_connection() as connection:
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()
    return task


def get_stats() -> dict[str, int]:
    """Return dashboard counters."""
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        pending = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'Pending'"
        ).fetchone()[0]
        completed = connection.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'Completed'"
        ).fetchone()[0]

    return {
        "total": int(total),
        "pending": int(pending),
        "completed": int(completed),
    }
