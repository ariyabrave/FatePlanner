import os
import sqlite3
from pathlib import Path


APP_DATA_DIR = Path.home() / ".fateplanner"
DEFAULT_DATABASE_PATH = APP_DATA_DIR / "fateplanner.db"


def get_database_path() -> Path:
    custom_path = os.getenv(
        "FATEPLANNER_DB_PATH"
    )

    if custom_path:
        return Path(custom_path)

    return DEFAULT_DATABASE_PATH


def get_connection(
    database_path: str | Path | None = None,
) -> sqlite3.Connection:
    path = (
        Path(database_path)
        if database_path
        else get_database_path()
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        path
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def initialize_database(
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        # ==================================
        # Tasks
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                start_time TEXT,
                end_time TEXT,
                all_day INTEGER NOT NULL DEFAULT 0,
                priority TEXT NOT NULL DEFAULT 'normal',
                completed INTEGER NOT NULL DEFAULT 0,

                parent_id INTEGER,

                is_recurring_template
                    INTEGER NOT NULL DEFAULT 0,

                recurrence_type
                    TEXT NOT NULL DEFAULT 'none',

                recurrence_weekdays TEXT,

                recurrence_start_date TEXT,

                recurrence_end_date TEXT,

                recurring_template_id INTEGER,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (parent_id)
                    REFERENCES tasks(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (recurring_template_id)
                    REFERENCES tasks(id)
                    ON DELETE CASCADE
            )
            """
        )

        task_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(tasks)"
            ).fetchall()
        }

        task_migrations = {
            "start_time":
                """
                ALTER TABLE tasks
                ADD COLUMN start_time TEXT
                """,

            "end_time":
                """
                ALTER TABLE tasks
                ADD COLUMN end_time TEXT
                """,

            "all_day":
                """
                ALTER TABLE tasks
                ADD COLUMN all_day
                INTEGER NOT NULL DEFAULT 0
                """,

            "parent_id":
                """
                ALTER TABLE tasks
                ADD COLUMN parent_id INTEGER
                REFERENCES tasks(id)
                ON DELETE CASCADE
                """,

            "is_recurring_template":
                """
                ALTER TABLE tasks
                ADD COLUMN is_recurring_template
                INTEGER NOT NULL DEFAULT 0
                """,

            "recurrence_type":
                """
                ALTER TABLE tasks
                ADD COLUMN recurrence_type
                TEXT NOT NULL DEFAULT 'none'
                """,

            "recurrence_weekdays":
                """
                ALTER TABLE tasks
                ADD COLUMN recurrence_weekdays TEXT
                """,

            "recurrence_start_date":
                """
                ALTER TABLE tasks
                ADD COLUMN recurrence_start_date TEXT
                """,

            "recurrence_end_date":
                """
                ALTER TABLE tasks
                ADD COLUMN recurrence_end_date TEXT
                """,

            "recurring_template_id":
                """
                ALTER TABLE tasks
                ADD COLUMN recurring_template_id INTEGER
                REFERENCES tasks(id)
                ON DELETE CASCADE
                """,
        }

        for column, sql in (
            task_migrations.items()
        ):
            if column not in task_columns:
                connection.execute(sql)

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_tasks_parent_id
            ON tasks(parent_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_tasks_due_date
            ON tasks(due_date)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_tasks_recurring_template_id
            ON tasks(recurring_template_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_tasks_recurring_templates
            ON tasks(is_recurring_template)
            """
        )

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_unique_recurring_occurrence
            ON tasks(
                recurring_template_id,
                due_date
            )
            WHERE recurring_template_id
                IS NOT NULL
            """
        )

        # ==================================
        # Habits
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,

                schedule_type TEXT NOT NULL
                    DEFAULT 'daily',

                weekdays TEXT,

                start_date TEXT NOT NULL,

                archived INTEGER NOT NULL
                    DEFAULT 0,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                habit_id INTEGER NOT NULL,

                log_date TEXT NOT NULL,

                completed INTEGER NOT NULL
                    DEFAULT 1,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (habit_id)
                    REFERENCES habits(id)
                    ON DELETE CASCADE,

                UNIQUE(
                    habit_id,
                    log_date
                )
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_habit_logs_habit_id
            ON habit_logs(habit_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_habit_logs_date
            ON habit_logs(log_date)
            """
        )

        # ==================================
        # Study subjects
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS study_subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                description TEXT,

                archived INTEGER NOT NULL
                    DEFAULT 0,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ==================================
        # Study sessions
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                subject_id INTEGER NOT NULL,

                title TEXT,

                session_date TEXT NOT NULL,

                planned_minutes INTEGER NOT NULL
                    DEFAULT 25,

                actual_seconds INTEGER NOT NULL
                    DEFAULT 0,

                completed INTEGER NOT NULL
                    DEFAULT 0,

                notes TEXT,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (subject_id)
                    REFERENCES study_subjects(id)
                    ON DELETE CASCADE
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_study_sessions_subject
            ON study_sessions(subject_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_study_sessions_date
            ON study_sessions(session_date)
            """
        )

        connection.commit()