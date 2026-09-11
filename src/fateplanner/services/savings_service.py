from datetime import date
from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
)


VALID_ENTRY_TYPES = {
    "deposit",
    "withdrawal",
}


def _parse_date(
    value: str,
) -> date:
    try:
        return date.fromisoformat(
            value
        )

    except ValueError as error:
        raise ValueError(
            "Invalid savings date."
        ) from error


def _validate_amount(
    amount: int,
) -> int:
    amount = int(
        amount
    )

    if amount <= 0:
        raise ValueError(
            "Amount must be positive."
        )

    return amount


def _validate_entry_type(
    entry_type: str,
) -> str:
    if (
        entry_type
        not in VALID_ENTRY_TYPES
    ):
        raise ValueError(
            "Invalid savings entry type."
        )

    return entry_type


def _current_amount_from_connection(
    connection,
    goal_id: int,
) -> int:
    row = connection.execute(
        """
        SELECT
            SUM(
                CASE
                    WHEN entry_type = 'deposit'
                    THEN amount
                    ELSE -amount
                END
            ) AS current_amount
        FROM savings_entries
        WHERE goal_id = ?
        """,
        (
            goal_id,
        ),
    ).fetchone()

    return int(
        row["current_amount"] or 0
    )


def _history_has_valid_balances(
    connection,
    goal_id: int,
    exclude_entry_id: int | None = None,
) -> bool:
    parameters = [
        goal_id,
    ]

    sql = """
        SELECT
            entry_date,

            SUM(
                CASE
                    WHEN entry_type = 'deposit'
                    THEN amount
                    ELSE -amount
                END
            ) AS daily_change

        FROM savings_entries

        WHERE goal_id = ?
    """

    if exclude_entry_id is not None:
        sql += """
            AND id != ?
        """

        parameters.append(
            exclude_entry_id
        )

    sql += """
        GROUP BY entry_date
        ORDER BY entry_date ASC
    """

    rows = connection.execute(
        sql,
        parameters,
    ).fetchall()

    balance = 0

    for row in rows:
        balance += int(
            row["daily_change"] or 0
        )

        if balance < 0:
            return False

    return True


# =====================================
# Goals
# =====================================


def create_savings_goal(
    *,
    title: str,
    target_amount: int,
    description: str = "",
    target_date: str | None = None,
    database_path: str | Path | None = None,
) -> int:
    title = title.strip()

    if not title:
        raise ValueError(
            "Savings goal title "
            "cannot be empty."
        )

    target_amount = (
        _validate_amount(
            target_amount
        )
    )

    description = (
        description.strip()
    )

    if target_date:
        _parse_date(
            target_date
        )

    with get_connection(
        database_path
    ) as connection:

        cursor = connection.execute(
            """
            INSERT INTO savings_goals (
                title,
                description,
                target_amount,
                target_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                description,
                target_amount,
                target_date,
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


def get_savings_goal(
    goal_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT
                id,
                title,
                description,
                target_amount,
                target_date,
                created_at
            FROM savings_goals
            WHERE id = ?
            """,
            (
                goal_id,
            ),
        ).fetchone()

        if row is None:
            return None

        current_amount = (
            _current_amount_from_connection(
                connection,
                goal_id,
            )
        )

    target_amount = int(
        row["target_amount"]
    )

    percentage = round(
        current_amount
        / target_amount
        * 100
    )

    return {
        "id": row["id"],
        "title": row["title"],
        "description": (
            row["description"]
        ),
        "target_amount": (
            target_amount
        ),
        "target_date": (
            row["target_date"]
        ),
        "created_at": (
            row["created_at"]
        ),
        "current_amount": (
            current_amount
        ),
        "remaining_amount": max(
            0,
            target_amount
            - current_amount,
        ),
        "percentage": (
            percentage
        ),
        "completed": (
            current_amount
            >= target_amount
        ),
    }


def get_savings_goals(
    database_path: str | Path | None = None,
) -> list[dict]:
    with get_connection(
        database_path
    ) as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                title,
                description,
                target_amount,
                target_date,
                created_at
            FROM savings_goals
            ORDER BY
                created_at DESC,
                id DESC
            """
        ).fetchall()

        result = []

        for row in rows:
            current_amount = (
                _current_amount_from_connection(
                    connection,
                    row["id"],
                )
            )

            target_amount = int(
                row["target_amount"]
            )

            percentage = round(
                current_amount
                / target_amount
                * 100
            )

            result.append(
                {
                    "id": row["id"],
                    "title": (
                        row["title"]
                    ),
                    "description": (
                        row["description"]
                    ),
                    "target_amount": (
                        target_amount
                    ),
                    "target_date": (
                        row["target_date"]
                    ),
                    "created_at": (
                        row["created_at"]
                    ),
                    "current_amount": (
                        current_amount
                    ),
                    "remaining_amount": max(
                        0,
                        target_amount
                        - current_amount,
                    ),
                    "percentage": (
                        percentage
                    ),
                    "completed": (
                        current_amount
                        >= target_amount
                    ),
                }
            )

    return result


def update_savings_goal(
    *,
    goal_id: int,
    title: str,
    target_amount: int,
    description: str = "",
    target_date: str | None = None,
    database_path: str | Path | None = None,
) -> None:
    title = title.strip()

    if not title:
        raise ValueError(
            "Savings goal title "
            "cannot be empty."
        )

    target_amount = (
        _validate_amount(
            target_amount
        )
    )

    description = (
        description.strip()
    )

    if target_date:
        _parse_date(
            target_date
        )

    with get_connection(
        database_path
    ) as connection:

        result = connection.execute(
            """
            UPDATE savings_goals
            SET
                title = ?,
                description = ?,
                target_amount = ?,
                target_date = ?
            WHERE id = ?
            """,
            (
                title,
                description,
                target_amount,
                target_date,
                goal_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Savings goal does not exist."
            )

        connection.commit()


def delete_savings_goal(
    goal_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        connection.execute(
            """
            DELETE FROM savings_goals
            WHERE id = ?
            """,
            (
                goal_id,
            ),
        )

        connection.commit()


# =====================================
# Entries
# =====================================


def add_savings_entry(
    *,
    goal_id: int,
    entry_type: str,
    amount: int,
    entry_date: str,
    note: str = "",
    database_path: str | Path | None = None,
) -> int:
    entry_type = (
        _validate_entry_type(
            entry_type
        )
    )

    amount = _validate_amount(
        amount
    )

    _parse_date(
        entry_date
    )

    note = note.strip()

    with get_connection(
        database_path
    ) as connection:

        goal = connection.execute(
            """
            SELECT id
            FROM savings_goals
            WHERE id = ?
            """,
            (
                goal_id,
            ),
        ).fetchone()

        if goal is None:
            raise ValueError(
                "Savings goal does not exist."
            )

        cursor = connection.execute(
            """
            INSERT INTO savings_entries (
                goal_id,
                entry_type,
                amount,
                entry_date,
                note
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                goal_id,
                entry_type,
                amount,
                entry_date,
                note,
            ),
        )

        entry_id = int(
            cursor.lastrowid
        )

        if not _history_has_valid_balances(
            connection,
            goal_id,
        ):
            connection.execute(
                """
                DELETE FROM savings_entries
                WHERE id = ?
                """,
                (
                    entry_id,
                ),
            )

            raise ValueError(
                "Withdrawal cannot exceed "
                "the amount saved up to "
                "that date."
            )

        connection.commit()

        return entry_id


def get_savings_entries(
    goal_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                id,
                goal_id,
                entry_type,
                amount,
                entry_date,
                note,
                created_at
            FROM savings_entries
            WHERE goal_id = ?
            ORDER BY
                entry_date DESC,
                id DESC
            """,
            (
                goal_id,
            ),
        ).fetchall()


def delete_savings_entry(
    entry_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        entry = connection.execute(
            """
            SELECT
                id,
                goal_id
            FROM savings_entries
            WHERE id = ?
            """,
            (
                entry_id,
            ),
        ).fetchone()

        if entry is None:
            return

        if not _history_has_valid_balances(
            connection,
            entry["goal_id"],
            exclude_entry_id=entry_id,
        ):
            raise ValueError(
                "This history entry cannot "
                "be deleted because it would "
                "make the savings balance "
                "negative at a later date."
            )

        connection.execute(
            """
            DELETE FROM savings_entries
            WHERE id = ?
            """,
            (
                entry_id,
            ),
        )

        connection.commit()


# =====================================
# Overview
# =====================================


def get_savings_overview(
    database_path: str | Path | None = None,
) -> dict:
    goals = get_savings_goals(
        database_path=database_path
    )

    total_target = sum(
        goal["target_amount"]
        for goal in goals
    )

    total_saved = sum(
        goal["current_amount"]
        for goal in goals
    )

    total_remaining = sum(
        goal["remaining_amount"]
        for goal in goals
    )

    completed_goals = sum(
        1
        for goal in goals
        if goal["completed"]
    )

    return {
        "goal_count": len(
            goals
        ),
        "completed_goals": (
            completed_goals
        ),
        "total_target": (
            total_target
        ),
        "total_saved": (
            total_saved
        ),
        "total_remaining": (
            total_remaining
        ),
    }