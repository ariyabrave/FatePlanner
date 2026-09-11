from datetime import (
    date,
    timedelta,
)
from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
)
from fateplanner.services.finance_service import (
    get_finance_budget_overview,
    get_finance_summary_between,
)
from fateplanner.services.savings_service import (
    get_savings_overview,
)
from fateplanner.services.study_analytics_service import (
    get_study_daily_totals_between,
    get_study_summary_between,
)
from fateplanner.utils.date_utils import (
    get_jalali_month_dates,
    get_persian_week,
    gregorian_to_jalali,
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
            "End date cannot be before start date."
        )

    return (
        start,
        end,
    )


# =====================================
# Tasks
# =====================================


def get_task_summary_between(
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
                is_recurring_template = 0
                AND is_skipped = 0
                AND parent_id IS NULL
                AND due_date IS NOT NULL
                AND due_date >= ?
                AND due_date <= ?
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchone()

    total = int(
        row["total"] or 0
    )

    completed = int(
        row["completed"] or 0
    )

    percentage = (
        round(
            completed
            / total
            * 100
        )
        if total
        else 0
    )

    return {
        "total": total,
        "completed": completed,
        "remaining": (
            total - completed
        ),
        "percentage": (
            percentage
        ),
    }


def get_overdue_task_count(
    as_of_date: str,
    database_path: str | Path | None = None,
) -> int:
    _parse_date(
        as_of_date
    )

    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM tasks

            WHERE
                is_recurring_template = 0
                AND is_skipped = 0
                AND parent_id IS NULL
                AND completed = 0
                AND due_date IS NOT NULL
                AND due_date < ?
            """,
            (
                as_of_date,
            ),
        ).fetchone()

    return int(
        row["total"] or 0
    )


def get_task_daily_totals_between(
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
                due_date,

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
                is_recurring_template = 0
                AND is_skipped = 0
                AND parent_id IS NULL
                AND due_date >= ?
                AND due_date <= ?

            GROUP BY due_date
            ORDER BY due_date ASC
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchall()

    indexed = {
        row["due_date"]: row
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

        result.append(
            {
                "date": iso_date,
                "total": (
                    int(
                        row["total"] or 0
                    )
                    if row
                    else 0
                ),
                "completed": (
                    int(
                        row["completed"] or 0
                    )
                    if row
                    else 0
                ),
            }
        )

        current += timedelta(
            days=1
        )

    return result


# =====================================
# Habits
# =====================================


def _deserialize_weekdays(
    value: str | None,
) -> set[int]:
    if not value:
        return set()

    return {
        int(item)
        for item in value.split(",")
        if item.strip()
    }


def _habit_is_scheduled(
    habit,
    target_date: date,
) -> bool:
    start_date = date.fromisoformat(
        habit["start_date"]
    )

    if target_date < start_date:
        return False

    if (
        habit["schedule_type"]
        == "daily"
    ):
        return True

    if (
        habit["schedule_type"]
        == "weekdays"
    ):
        weekdays = (
            _deserialize_weekdays(
                habit["weekdays"]
            )
        )

        return (
            target_date.weekday()
            in weekdays
        )

    return False


def get_habit_daily_totals_between(
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

        habits = connection.execute(
            """
            SELECT
                id,
                schedule_type,
                weekdays,
                start_date
            FROM habits
            WHERE archived = 0
            """
        ).fetchall()

        logs = connection.execute(
            """
            SELECT
                habit_id,
                log_date
            FROM habit_logs
            WHERE
                completed = 1
                AND log_date >= ?
                AND log_date <= ?
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchall()

    completed = {
        (
            row["habit_id"],
            row["log_date"],
        )
        for row in logs
    }

    result = []

    current = start

    while current <= end:
        scheduled_count = 0
        completed_count = 0

        for habit in habits:
            if not _habit_is_scheduled(
                habit,
                current,
            ):
                continue

            scheduled_count += 1

            if (
                habit["id"],
                current.isoformat(),
            ) in completed:
                completed_count += 1

        percentage = (
            round(
                completed_count
                / scheduled_count
                * 100
            )
            if scheduled_count
            else 0
        )

        result.append(
            {
                "date": (
                    current.isoformat()
                ),
                "scheduled": (
                    scheduled_count
                ),
                "completed": (
                    completed_count
                ),
                "percentage": (
                    percentage
                ),
            }
        )

        current += timedelta(
            days=1
        )

    return result


def get_habit_summary_between(
    start_date: str,
    end_date: str,
    database_path: str | Path | None = None,
) -> dict:
    daily = (
        get_habit_daily_totals_between(
            start_date,
            end_date,
            database_path=database_path,
        )
    )

    scheduled = sum(
        row["scheduled"]
        for row in daily
    )

    completed = sum(
        row["completed"]
        for row in daily
    )

    percentage = (
        round(
            completed
            / scheduled
            * 100
        )
        if scheduled
        else 0
    )

    return {
        "scheduled": scheduled,
        "completed": completed,
        "missed": (
            scheduled
            - completed
        ),
        "percentage": (
            percentage
        ),
    }


# =====================================
# Finance
# =====================================


def get_finance_category_spending_between(
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
                c.id AS category_id,
                c.name AS category_name,
                SUM(t.amount) AS total_amount,
                COUNT(t.id) AS transaction_count

            FROM finance_transactions AS t

            JOIN finance_categories AS c
                ON c.id = t.category_id

            WHERE
                t.transaction_type = 'expense'
                AND t.transaction_date >= ?
                AND t.transaction_date <= ?

            GROUP BY
                c.id,
                c.name

            ORDER BY
                total_amount DESC,
                c.name COLLATE NOCASE ASC
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchall()

    return [
        {
            "category_id": (
                row["category_id"]
            ),
            "category_name": (
                row["category_name"]
            ),
            "total_amount": int(
                row["total_amount"] or 0
            ),
            "transaction_count": int(
                row["transaction_count"] or 0
            ),
        }
        for row in rows
    ]


# =====================================
# Unified snapshots
# =====================================


def get_productivity_snapshot(
    anchor_date: date,
    database_path: str | Path | None = None,
) -> dict:
    week = get_persian_week(
        anchor_date
    )

    start = week[0]
    end = week[-1]

    start_iso = start.isoformat()
    end_iso = end.isoformat()

    return {
        "start_date": start,
        "end_date": end,

        "tasks": (
            get_task_summary_between(
                start_iso,
                end_iso,
                database_path=database_path,
            )
        ),

        "task_daily": (
            get_task_daily_totals_between(
                start_iso,
                end_iso,
                database_path=database_path,
            )
        ),

        "habits": (
            get_habit_summary_between(
                start_iso,
                end_iso,
                database_path=database_path,
            )
        ),

        "habit_daily": (
            get_habit_daily_totals_between(
                start_iso,
                end_iso,
                database_path=database_path,
            )
        ),

        "study": (
            get_study_summary_between(
                start_iso,
                end_iso,
                database_path=database_path,
            )
        ),

        "study_daily": (
            get_study_daily_totals_between(
                start_iso,
                end_iso,
                database_path=database_path,
            )
        ),

        "overdue_tasks": (
            get_overdue_task_count(
                anchor_date.isoformat(),
                database_path=database_path,
            )
        ),
    }


def get_finance_snapshot(
    anchor_date: date,
    database_path: str | Path | None = None,
) -> dict:
    jalali = gregorian_to_jalali(
        anchor_date
    )

    month_dates = (
        get_jalali_month_dates(
            jalali.year,
            jalali.month,
        )
    )

    start = month_dates[0]
    end = month_dates[-1]

    return {
        "jalali_year": (
            jalali.year
        ),
        "jalali_month": (
            jalali.month
        ),

        "start_date": start,
        "end_date": end,

        "finance": (
            get_finance_summary_between(
                start.isoformat(),
                end.isoformat(),
                database_path=database_path,
            )
        ),

        "budgets": (
            get_finance_budget_overview(
                jalali.year,
                jalali.month,
                database_path=database_path,
            )
        ),

        "category_spending": (
            get_finance_category_spending_between(
                start.isoformat(),
                end.isoformat(),
                database_path=database_path,
            )
        ),

        "savings": (
            get_savings_overview(
                database_path=database_path
            )
        ),
    }