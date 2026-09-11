import os
import shutil
import sqlite3
import sys

from pathlib import Path


APP_NAME = "FatePlanner"
DATABASE_FILENAME = "fateplanner.db"

# FatePlanner used this location before the
# platform-native application-data migration.
LEGACY_APP_DATA_DIR = (
    Path.home()
    / ".fateplanner"
)


def _platform_name() -> str:
    return sys.platform


def get_app_data_directory() -> Path:
    """
    Return FatePlanner's writable application-data
    directory for the current operating system.

    An explicit FATEPLANNER_DATA_DIR environment
    variable always takes precedence.
    """

    custom_directory = os.getenv(
        "FATEPLANNER_DATA_DIR"
    )

    if custom_directory:
        return Path(
            custom_directory
        ).expanduser()

    platform_name = (
        _platform_name()
    )

    if platform_name.startswith(
        "win"
    ):
        appdata = (
            os.getenv("APPDATA")
            or os.getenv(
                "LOCALAPPDATA"
            )
        )

        if appdata:
            return (
                Path(appdata)
                / APP_NAME
            )

        return (
            Path.home()
            / "AppData"
            / "Roaming"
            / APP_NAME
        )

    if platform_name == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / APP_NAME
        )

    xdg_data_home = os.getenv(
        "XDG_DATA_HOME"
    )

    if xdg_data_home:
        return (
            Path(
                xdg_data_home
            ).expanduser()
            / APP_NAME
        )

    return (
        Path.home()
        / ".local"
        / "share"
        / APP_NAME
    )


# Kept for backwards compatibility with any code
# importing these constants directly.
APP_DATA_DIR = (
    get_app_data_directory()
)

DEFAULT_DATABASE_PATH = (
    APP_DATA_DIR
    / DATABASE_FILENAME
)


def get_database_path() -> Path:
    custom_path = os.getenv(
        "FATEPLANNER_DB_PATH"
    )

    if custom_path:
        return Path(
            custom_path
        ).expanduser()

    return (
        get_app_data_directory()
        / DATABASE_FILENAME
    )


def migrate_legacy_app_data() -> bool:
    """
    Copy data from FatePlanner's old ~/.fateplanner
    directory into the platform-native app-data
    directory.

    Existing destination data is never overwritten
    and the old directory is intentionally retained
    as an additional safety copy.
    """

    # Explicit development/test paths should never
    # trigger migration of a user's real data.
    if (
        os.getenv(
            "FATEPLANNER_DB_PATH"
        )
        or os.getenv(
            "FATEPLANNER_DATA_DIR"
        )
    ):
        return False

    source = (
        LEGACY_APP_DATA_DIR
    )

    destination = (
        get_app_data_directory()
    )

    if (
        source.resolve()
        == destination.resolve()
    ):
        return False

    if not source.exists():
        return False

    destination_database = (
        destination
        / DATABASE_FILENAME
    )

    # A database already exists at the new location,
    # so it wins. Never overwrite it automatically.
    if destination_database.exists():
        return False

    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    for item in source.iterdir():
        target = (
            destination
            / item.name
        )

        if target.exists():
            continue

        if item.is_dir():
            shutil.copytree(
                item,
                target,
            )

        else:
            shutil.copy2(
                item,
                target,
            )

    return True


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
    if database_path is None:
        migrate_legacy_app_data()

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
        # Study
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS study_subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                archived INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

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

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS
            study_timer_state (
                id INTEGER PRIMARY KEY
                    CHECK (id = 1),

                session_id INTEGER,

                phase TEXT NOT NULL
                    DEFAULT 'focus',

                focus_minutes INTEGER NOT NULL
                    DEFAULT 25,

                break_minutes INTEGER NOT NULL
                    DEFAULT 5,

                remaining_seconds INTEGER NOT NULL
                    DEFAULT 1500,

                pomodoro_count INTEGER NOT NULL
                    DEFAULT 0,

                is_running INTEGER NOT NULL
                    DEFAULT 0,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (session_id)
                    REFERENCES study_sessions(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ==================================
        # Finance categories
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS
            finance_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                transaction_type TEXT NOT NULL
                    CHECK (
                        transaction_type
                        IN ('income', 'expense')
                    ),

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_categories_type
            ON finance_categories(
                transaction_type
            )
            """
        )

        # ==================================
        # Finance transactions
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS
            finance_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                transaction_type TEXT NOT NULL
                    CHECK (
                        transaction_type
                        IN ('income', 'expense')
                    ),

                category_id INTEGER NOT NULL,

                amount INTEGER NOT NULL
                    CHECK (amount > 0),

                transaction_date TEXT NOT NULL,

                description TEXT,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (category_id)
                    REFERENCES finance_categories(id)
                    ON DELETE RESTRICT
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_transactions_date
            ON finance_transactions(
                transaction_date
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_transactions_type
            ON finance_transactions(
                transaction_type
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_transactions_category
            ON finance_transactions(
                category_id
            )
            """
        )
        # ==================================
        # Monthly finance budgets
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS
            finance_budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                category_id INTEGER NOT NULL,

                jalali_year INTEGER NOT NULL,

                jalali_month INTEGER NOT NULL
                    CHECK (
                        jalali_month >= 1
                        AND jalali_month <= 12
                    ),

                amount INTEGER NOT NULL
                    CHECK (amount > 0),

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (category_id)
                    REFERENCES finance_categories(id)
                    ON DELETE CASCADE,

                UNIQUE (
                    category_id,
                    jalali_year,
                    jalali_month
                )
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_budgets_period
            ON finance_budgets(
                jalali_year,
                jalali_month
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_budgets_category
            ON finance_budgets(
                category_id
            )
            """
        )
        # ==================================
        # Savings goals
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS
            savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title TEXT NOT NULL,

                description TEXT,

                target_amount INTEGER NOT NULL
                    CHECK (target_amount > 0),

                target_date TEXT,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # ==================================
        # Savings goal history
        # ==================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS
            savings_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                goal_id INTEGER NOT NULL,

                entry_type TEXT NOT NULL
                    CHECK (
                        entry_type
                        IN ('deposit', 'withdrawal')
                    ),

                amount INTEGER NOT NULL
                    CHECK (amount > 0),

                entry_date TEXT NOT NULL,

                note TEXT,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (goal_id)
                    REFERENCES savings_goals(id)
                    ON DELETE CASCADE
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_savings_entries_goal
            ON savings_entries(goal_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_savings_entries_date
            ON savings_entries(entry_date)
            """
        )

        # Recurring occurrence skip migration
        task_columns = {
            row["name"]
            for row in connection.execute(
                """
                PRAGMA table_info(tasks)
                """
            ).fetchall()
        }

        if "is_skipped" not in task_columns:
            connection.execute(
                """
                ALTER TABLE tasks
                ADD COLUMN is_skipped
                INTEGER NOT NULL
                DEFAULT 0
                """
            )

        connection.commit()