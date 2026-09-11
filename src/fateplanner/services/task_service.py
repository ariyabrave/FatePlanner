from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
)


VALID_PRIORITIES = {
    "low",
    "normal",
    "high",
}


def _validate_task_data(
    title: str,
    priority: str,
    start_time: str | None,
    end_time: str | None,
) -> None:
    if not title.strip():
        raise ValueError(
            "Task title cannot be empty."
        )

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            "Invalid task priority."
        )

    if (
        start_time
        and end_time
        and end_time <= start_time
    ):
        raise ValueError(
            "End time must be later "
            "than start time."
        )


def create_task(
    title: str,
    description: str = "",
    due_date: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    all_day: bool = False,
    priority: str = "normal",
    parent_id: int | None = None,
    database_path: str | Path | None = None,
) -> int:
    title = title.strip()
    description = description.strip()

    _validate_task_data(
        title,
        priority,
        start_time,
        end_time,
    )

    if all_day:
        start_time = None
        end_time = None

    with get_connection(
        database_path
    ) as connection:

        if parent_id is not None:
            parent = connection.execute(
                """
                SELECT
                    id,
                    parent_id
                FROM tasks
                WHERE id = ?
                """,
                (parent_id,),
            ).fetchone()

            if parent is None:
                raise ValueError(
                    "Parent task does not exist."
                )

            if parent["parent_id"] is not None:
                raise ValueError(
                    "Nested subtasks are not supported."
                )

        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title,
                description,
                due_date,
                start_time,
                end_time,
                all_day,
                priority,
                parent_id,
                is_recurring_template,
                recurrence_type
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, 0, 'none'
            )
            """,
            (
                title,
                description,
                due_date,
                start_time,
                end_time,
                int(all_day),
                priority,
                parent_id,
            ),
        )

        connection.commit()

        task_id = int(
            cursor.lastrowid
        )

    if parent_id is not None:
        _sync_parent_completion(
            parent_id,
            database_path,
        )

    return task_id


def create_subtask(
    parent_id: int,
    title: str,
    description: str = "",
    database_path: str | Path | None = None,
) -> int:
    return create_task(
        title=title,
        description=description,
        parent_id=parent_id,
        database_path=database_path,
    )


def get_task(
    task_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                title,
                description,
                due_date,
                start_time,
                end_time,
                all_day,
                priority,
                completed,
                parent_id,
                is_recurring_template,
                recurrence_type,
                recurrence_weekdays,
                recurrence_start_date,
                recurrence_end_date,
                recurring_template_id,
                created_at
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()


def get_tasks(
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                title,
                description,
                due_date,
                start_time,
                end_time,
                all_day,
                priority,
                completed,
                parent_id,
                is_recurring_template,
                recurrence_type,
                recurrence_weekdays,
                recurrence_start_date,
                recurrence_end_date,
                recurring_template_id,
                created_at
            FROM tasks
            WHERE
                parent_id IS NULL
                AND is_recurring_template = 0
                AND is_skipped = 0
            ORDER BY
                completed ASC,
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'normal' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END ASC,
                due_date ASC,
                id DESC
            """
        ).fetchall()


def get_tasks_for_date(
    date: str,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                title,
                description,
                due_date,
                start_time,
                end_time,
                all_day,
                priority,
                completed,
                parent_id,
                is_recurring_template,
                recurrence_type,
                recurrence_weekdays,
                recurrence_start_date,
                recurrence_end_date,
                recurring_template_id,
                created_at
            FROM tasks
            WHERE
                due_date = ?
                AND parent_id IS NULL
                AND is_recurring_template = 0
                AND is_skipped = 0
            ORDER BY
                completed ASC,
                all_day DESC,
                start_time ASC,
                id ASC
            """,
            (date,),
        ).fetchall()


def get_subtasks(
    parent_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                title,
                description,
                completed,
                parent_id,
                created_at
            FROM tasks
            WHERE parent_id = ?
            ORDER BY
                completed ASC,
                id ASC
            """,
            (parent_id,),
        ).fetchall()


def update_task(
    task_id: int,
    title: str,
    description: str = "",
    due_date: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    all_day: bool = False,
    priority: str = "normal",
    database_path: str | Path | None = None,
) -> None:
    title = title.strip()
    description = description.strip()

    _validate_task_data(
        title,
        priority,
        start_time,
        end_time,
    )

    if all_day:
        start_time = None
        end_time = None

    with get_connection(
        database_path
    ) as connection:

        result = connection.execute(
            """
            UPDATE tasks
            SET
                title = ?,
                description = ?,
                due_date = ?,
                start_time = ?,
                end_time = ?,
                all_day = ?,
                priority = ?
            WHERE
                id = ?
                AND is_recurring_template = 0
                AND is_skipped = 0
            """,
            (
                title,
                description,
                due_date,
                start_time,
                end_time,
                int(all_day),
                priority,
                task_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Task does not exist."
            )

        connection.commit()


def set_task_completed(
    task_id: int,
    completed: bool,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        task = connection.execute(
            """
            SELECT
                id,
                parent_id,
                is_recurring_template
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        if task is None:
            return

        if task["is_recurring_template"]:
            return

        connection.execute(
            """
            UPDATE tasks
            SET completed = ?
            WHERE id = ?
            """,
            (
                int(completed),
                task_id,
            ),
        )

        if task["parent_id"] is None:
            connection.execute(
                """
                UPDATE tasks
                SET completed = ?
                WHERE parent_id = ?
                """,
                (
                    int(completed),
                    task_id,
                ),
            )

        connection.commit()

        parent_id = task["parent_id"]

    if parent_id is not None:
        _sync_parent_completion(
            parent_id,
            database_path,
        )


def _sync_parent_completion(
    parent_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS completed
            FROM tasks
            WHERE parent_id = ?
            """,
            (parent_id,),
        ).fetchone()

        total = int(
            row["total"]
        )

        completed = int(
            row["completed"] or 0
        )

        if total == 0:
            return

        parent_completed = (
            completed == total
        )

        connection.execute(
            """
            UPDATE tasks
            SET completed = ?
            WHERE id = ?
            """,
            (
                int(parent_completed),
                parent_id,
            ),
        )

        connection.commit()


def delete_task(
    task_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(database_path) as connection:
        task = connection.execute(
            """
            SELECT
                id,
                is_recurring_template,
                recurring_template_id
            FROM tasks
            WHERE id = ?
            """,
            (
                task_id,
            ),
        ).fetchone()

        if task is None:
            return

        is_occurrence = (
            not bool(
                task[
                    "is_recurring_template"
                ]
            )
            and task[
                "recurring_template_id"
            ]
            is not None
        )

        if is_occurrence:
            connection.execute(
                """
                UPDATE tasks
                SET is_skipped = 1
                WHERE id = ?
                """,
                (
                    task_id,
                ),
            )

        else:
            connection.execute(
                """
                DELETE FROM tasks
                WHERE id = ?
                """,
                (
                    task_id,
                ),
            )

        connection.commit()


def get_subtask_progress(
    parent_id: int,
    database_path: str | Path | None = None,
) -> tuple[int, int, int]:
    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS completed
            FROM tasks
            WHERE parent_id = ?
            """,
            (parent_id,),
        ).fetchone()

    total = int(
        row["total"]
    )

    completed = int(
        row["completed"] or 0
    )

    percentage = (
        round(
            completed / total * 100
        )
        if total
        else 0
    )

    return (
        total,
        completed,
        percentage,
    )


def get_task_progress(
    database_path: str | Path | None = None,
) -> tuple[int, int, int]:
    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS completed
            FROM tasks
            WHERE
                parent_id IS NULL
                AND is_recurring_template = 0
                AND is_skipped = 0
            """
        ).fetchone()

    total = int(
        row["total"]
    )

    completed = int(
        row["completed"] or 0
    )

    percentage = (
        round(
            completed / total * 100
        )
        if total
        else 0
    )

    return (
        total,
        completed,
        percentage,
    )


def get_task_progress_for_date(
    date: str,
    database_path: str | Path | None = None,
) -> tuple[int, int, int]:
    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS completed
            FROM tasks
            WHERE
                due_date = ?
                AND parent_id IS NULL
                AND is_recurring_template = 0
                AND is_skipped = 0
            """,
            (date,),
        ).fetchone()

    total = int(
        row["total"]
    )

    completed = int(
        row["completed"] or 0
    )

    percentage = (
        round(
            completed / total * 100
        )
        if total
        else 0
    )

    return (
        total,
        completed,
        percentage,
    )