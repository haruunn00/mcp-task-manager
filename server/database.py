import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "tasks.db"
TASK_STATUSES = ("todo", "in_progress", "done")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'todo'
                        CHECK (status IN ('todo', 'in_progress', 'done')),
                    user_id TEXT NOT NULL
                )
                """
            )


def run_query(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        with connection:
            rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def run_write(query: str, params: tuple[Any, ...] = ()) -> int:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            cursor = connection.execute(query, params)
            return cursor.rowcount


def list_tasks(status: str | None = None) -> list[dict[str, Any]]:
    if status is not None and status not in TASK_STATUSES:
        raise ValueError(f"Nepoznat status zadatka: {status}")
    query = "SELECT * FROM tasks WHERE status = ?" if status else "SELECT * FROM tasks"
    params = (status,) if status else ()
    return run_query(query, params)


def get_task(task_id: int) -> dict[str, Any] | None:
    tasks = run_query("SELECT * FROM tasks WHERE id = ?", (task_id,))
    return tasks[0] if tasks else None


def create_task(title: str, description: str, user_id: str) -> int:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        with connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, description, status, user_id) "
                "VALUES (?, ?, 'todo', ?)",
                (title, description, user_id),
            )
            return cursor.lastrowid


def update_task_status(task_id: int, status: str) -> bool:
    if status not in TASK_STATUSES:
        raise ValueError(f"Nepoznat status zadatka: {status}")
    return bool(
        run_write(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id),
        )
    )


def delete_task(task_id: int) -> bool:
    return bool(run_write("DELETE FROM tasks WHERE id = ?", (task_id,)))
