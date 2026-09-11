from datetime import (
    date,
    timedelta,
)
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
            "Invalid analytics date."
        ) from error


def _validate_range(
    start_date: str,
    end_date: str,
) -> tuple[date, date]:
    start = _parse_date(
        start_date
    )

    end = _parse_date(
        end_date
    )

    if end < start:
        raise ValueError(
            "End date cannot be before "
            "start date."
        )

    return (
        start,
        end,
    )


def get_study_sessions_between(
    start_date: str,
    end_date: str,
    database_path: str | Path | None = None,
):
    _validate_range(
        start_date,
        end_date,
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
            WHERE
                s.session_date >= ?
                AND s.session_date <= ?
            ORDER BY
                s.session_date ASC,
                s.id ASC
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchall()


def get_study_summary_between(
    start_date: str,
    end_date: str,
    database_path: str | Path | None = None,
) -> dict:
    _validate_range(
        start_date,
        end_date,
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
            WHERE
                session_date >= ?
                AND session_date <= ?
            """,
            (
                start_date,
                end_date,
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

    completion_percentage = (
        round(
            completed_sessions
            / total_sessions
            * 100
        )
        if total_sessions
        else 0
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
        "completion_percentage": (
            completion_percentage
        ),
        "time_percentage": (
            time_percentage
        ),
    }


def get_study_subject_totals_between(
    start_date: str,
    end_date: str,
    database_path: str | Path | None = None,
) -> list[dict]:
    _validate_range(
        start_date,
        end_date,
    )

    with get_connection(
        database_path
    ) as connection:

        rows = connection.execute(
            """
            SELECT
                sub.id AS subject_id,
                sub.name AS subject_name,

                COUNT(
                    s.id
                ) AS total_sessions,

                SUM(
                    CASE
                        WHEN s.completed = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS completed_sessions,

                SUM(
                    s.planned_minutes
                ) AS planned_minutes,

                SUM(
                    s.actual_seconds
                ) AS actual_seconds

            FROM study_sessions AS s
            JOIN study_subjects AS sub
                ON sub.id = s.subject_id

            WHERE
                s.session_date >= ?
                AND s.session_date <= ?

            GROUP BY
                sub.id,
                sub.name

            ORDER BY
                actual_seconds DESC,
                planned_minutes DESC,
                sub.name COLLATE NOCASE ASC
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchall()

    result = []

    for row in rows:
        total_sessions = int(
            row["total_sessions"] or 0
        )

        completed_sessions = int(
            row[
                "completed_sessions"
            ] or 0
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

        result.append(
            {
                "subject_id": (
                    row["subject_id"]
                ),
                "subject_name": (
                    row["subject_name"]
                ),
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
            }
        )

    return result


def get_study_daily_totals_between(
    start_date: str,
    end_date: str,
    database_path: str | Path | None = None,
) -> list[dict]:
    start, end = _validate_range(
        start_date,
        end_date,
    )

    with get_connection(
        database_path
    ) as connection:

        rows = connection.execute(
            """
            SELECT
                session_date,

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

            WHERE
                session_date >= ?
                AND session_date <= ?

            GROUP BY
                session_date

            ORDER BY
                session_date ASC
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchall()

    indexed = {
        row["session_date"]: row
        for row in rows
    }

    result = []

    current = start

    while current <= end:
        iso_date = (
            current.isoformat()
        )

        row = indexed.get(
            iso_date
        )

        if row is None:
            result.append(
                {
                    "session_date": (
                        iso_date
                    ),
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "planned_minutes": 0,
                    "actual_seconds": 0,
                }
            )

        else:
            result.append(
                {
                    "session_date": (
                        iso_date
                    ),
                    "total_sessions": int(
                        row[
                            "total_sessions"
                        ] or 0
                    ),
                    "completed_sessions": int(
                        row[
                            "completed_sessions"
                        ] or 0
                    ),
                    "planned_minutes": int(
                        row[
                            "planned_minutes"
                        ] or 0
                    ),
                    "actual_seconds": int(
                        row[
                            "actual_seconds"
                        ] or 0
                    ),
                }
            )

        current += timedelta(
            days=1
        )

    return result