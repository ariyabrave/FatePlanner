import os
import sqlite3
from pathlib import Path


APP_DATA_DIR = Path.home() / ".fateplanner"
DEFAULT_DATABASE_PATH = APP_DATA_DIR / "fateplanner.db"


def get_database_path() -> Path:
    custom_path = os.getenv("FATEPLANNER_DB_PATH")

    if custom_path:
        return Path(custom_path)

    return DEFAULT_DATABASE_PATH


def get_connection(
    database_path: str | Path | None = None,
) -> sqlite3.Connection:
    path = Path(database_path) if database_path else get_database_path()

    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database(
    database_path: str | Path | None = None,
) -> None:
    with get_connection(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT NOT NULL DEFAULT 'normal',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()