from datetime import date
from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
)


def _parse_date(
    value: str,
) -> date:
    try:
        return date.fromisoformat(
            value
        )

    except ValueError as error:
        raise ValueError(
            "Invalid study session date."
        ) from error


def _validate_subject_name(
    name: str,
) -> str:
    name = name.strip()

    if not name:
        raise ValueError(
            "Subject name cannot be empty."
        )

    return name


def _validate_planned_minutes(
    planned_minutes: int,
) -> int:
    planned_minutes = int(
        planned_minutes
    )

    if planned_minutes < 1:
        raise ValueError(
            "Planned study time must "
            "be at least one minute."
        )

    if planned_minutes > 1440:
        raise ValueError(
            "Planned study time cannot "
            "exceed 1440 minutes."
        )

    return planned_minutes


# =====================================
# Subjects
# =====================================


def create_subject(
    *,
    name: str,
    description: str = "",
    database_path: str | Path | None = None,
) -> int:
    name = _validate_subject_name(
        name
    )

    description = (
        description.strip()
    )

    with get_connection(
        database_path
    ) as connection:

        cursor = connection.execute(
            """
            INSERT INTO study_subjects (
                name,
                description,
                archived
            )
            VALUES (?, ?, 0)
            """,
            (
                name,
                description,
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


def get_subject(
    subject_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                name,
                description,
                archived,
                created_at
            FROM study_subjects
            WHERE id = ?
            """,
            (
                subject_id,
            ),
        ).fetchone()


def get_subjects(
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                name,
                description,
                archived,
                created_at
            FROM study_subjects
            WHERE archived = 0
            ORDER BY
                name COLLATE NOCASE ASC,
                id ASC
            """
        ).fetchall()


def update_subject(
    *,
    subject_id: int,
    name: str,
    description: str = "",
    database_path: str | Path | None = None,
) -> None:
    name = _validate_subject_name(
        name
    )

    description = (
        description.strip()
    )

    with get_connection(
        database_path
    ) as connection:

        result = connection.execute(
            """
            UPDATE study_subjects
            SET
                name = ?,
                description = ?
            WHERE id = ?
            """,
            (
                name,
                description,
                subject_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Subject does not exist."
            )

        connection.commit()


def delete_subject(
    subject_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        connection.execute(
            """
            DELETE FROM study_subjects
            WHERE id = ?
            """,
            (
                subject_id,
            ),
        )

        connection.commit()


# =====================================
# Study sessions
# =====================================


def create_study_session(
    *,
    subject_id: int,
    session_date: str,
    planned_minutes: int,
    title: str = "",
    notes: str = "",
    completed: bool = False,
    database_path: str | Path | None = None,
) -> int:
    _parse_date(
        session_date
    )

    planned_minutes = (
        _validate_planned_minutes(
            planned_minutes
        )
    )

    title = title.strip()
    notes = notes.strip()

    with get_connection(
        database_path
    ) as connection:

        subject = connection.execute(
            """
            SELECT id
            FROM study_subjects
            WHERE
                id = ?
                AND archived = 0
            """,
            (
                subject_id,
            ),
        ).fetchone()

        if subject is None:
            raise ValueError(
                "Study subject does not exist."
            )

        cursor = connection.execute(
            """
            INSERT INTO study_sessions (
                subject_id,
                title,
                session_date,
                planned_minutes,
                actual_seconds,
                completed,
                notes
            )
            VALUES (?, ?, ?, ?, 0, ?, ?)
            """,
            (
                subject_id,
                title,
                session_date,
                planned_minutes,
                int(completed),
                notes,
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


def get_study_session(
    session_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                s.id,
                s.subject_id,
                s.title,
                s.session_date,
                s.planned_minutes,
                s.actual_seconds,
                s.completed,
                s.notes,
                s.created_at,
                sub.name AS subject_name
            FROM study_sessions AS s
            JOIN study_subjects AS sub
                ON sub.id = s.subject_id
            WHERE s.id = ?
            """,
            (
                session_id,
            ),
        ).fetchone()


def get_study_sessions_for_date(
    session_date: str,
    database_path: str | Path | None = None,
):
    _parse_date(
        session_date
    )

    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                s.id,
                s.subject_id,
                s.title,
                s.session_date,
                s.planned_minutes,
                s.actual_seconds,
                s.completed,
                s.notes,
                s.created_at,
                sub.name AS subject_name
            FROM study_sessions AS s
            JOIN study_subjects AS sub
                ON sub.id = s.subject_id
            WHERE s.session_date = ?
            ORDER BY
                s.completed ASC,
                s.id ASC
            """,
            (
                session_date,
            ),
        ).fetchall()


def get_recent_study_sessions(
    limit: int = 20,
    database_path: str | Path | None = None,
):
    limit = max(
        1,
        int(limit),
    )

    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                s.id,
                s.subject_id,
                s.title,
                s.session_date,
                s.planned_minutes,
                s.actual_seconds,
                s.completed,
                s.notes,
                s.created_at,
                sub.name AS subject_name
            FROM study_sessions AS s
            JOIN study_subjects AS sub
                ON sub.id = s.subject_id
            ORDER BY
                s.session_date DESC,
                s.id DESC
            LIMIT ?
            """,
            (
                limit,
            ),
        ).fetchall()


def update_study_session(
    *,
    session_id: int,
    subject_id: int,
    session_date: str,
    planned_minutes: int,
    title: str = "",
    notes: str = "",
    completed: bool = False,
    database_path: str | Path | None = None,
) -> None:
    _parse_date(
        session_date
    )

    planned_minutes = (
        _validate_planned_minutes(
            planned_minutes
        )
    )

    title = title.strip()
    notes = notes.strip()

    with get_connection(
        database_path
    ) as connection:

        subject = connection.execute(
            """
            SELECT id
            FROM study_subjects
            WHERE
                id = ?
                AND archived = 0
            """,
            (
                subject_id,
            ),
        ).fetchone()

        if subject is None:
            raise ValueError(
                "Study subject does not exist."
            )

        result = connection.execute(
            """
            UPDATE study_sessions
            SET
                subject_id = ?,
                title = ?,
                session_date = ?,
                planned_minutes = ?,
                completed = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                subject_id,
                title,
                session_date,
                planned_minutes,
                int(completed),
                notes,
                session_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Study session does not exist."
            )

        connection.commit()


def delete_study_session(
    session_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        connection.execute(
            """
            DELETE FROM study_sessions
            WHERE id = ?
            """,
            (
                session_id,
            ),
        )

        connection.commit()


def set_study_session_completed(
    session_id: int,
    completed: bool,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        connection.execute(
            """
            UPDATE study_sessions
            SET completed = ?
            WHERE id = ?
            """,
            (
                int(completed),
                session_id,
            ),
        )

        connection.commit()


def add_study_time(
    session_id: int,
    seconds: int,
    database_path: str | Path | None = None,
) -> None:
    seconds = int(
        seconds
    )

    if seconds <= 0:
        raise ValueError(
            "Study time must be positive."
        )

    with get_connection(
        database_path
    ) as connection:

        result = connection.execute(
            """
            UPDATE study_sessions
            SET
                actual_seconds =
                    actual_seconds + ?
            WHERE id = ?
            """,
            (
                seconds,
                session_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Study session does not exist."
            )

        connection.commit()


# =====================================
# Statistics
# =====================================


def get_study_stats_for_date(
    session_date: str,
    database_path: str | Path | None = None,
) -> dict:
    _parse_date(
        session_date
    )

    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_sessions,

                SUM(
                    CASE
                        WHEN completed = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS completed_sessions,

                SUM(
                    planned_minutes
                ) AS planned_minutes,

                SUM(
                    actual_seconds
                ) AS actual_seconds

            FROM study_sessions
            WHERE session_date = ?
            """,
            (
                session_date,
            ),
        ).fetchone()

    total_sessions = int(
        row["total_sessions"] or 0
    )

    completed_sessions = int(
        row["completed_sessions"] or 0
    )

    planned_minutes = int(
        row["planned_minutes"] or 0
    )

    actual_seconds = int(
        row["actual_seconds"] or 0
    )

    planned_seconds = (
        planned_minutes * 60
    )

    time_percentage = (
        round(
            actual_seconds
            / planned_seconds
            * 100
        )
        if planned_seconds
        else 0
    )

    session_percentage = (
        round(
            completed_sessions
            / total_sessions
            * 100
        )
        if total_sessions
        else 0
    )

    return {
        "total_sessions": (
            total_sessions
        ),
        "completed_sessions": (
            completed_sessions
        ),
        "planned_minutes": (
            planned_minutes
        ),
        "actual_seconds": (
            actual_seconds
        ),
        "time_percentage": (
            time_percentage
        ),
        "session_percentage": (
            session_percentage
        ),
    }


def format_study_duration(
    seconds: int,
) -> str:
    seconds = max(
        0,
        int(seconds),
    )

    hours = (
        seconds // 3600
    )

    minutes = (
        seconds % 3600
    ) // 60

    if hours:
        return (
            f"{hours} ساعت و "
            f"{minutes} دقیقه"
        )

    return (
        f"{minutes} دقیقه"
    )