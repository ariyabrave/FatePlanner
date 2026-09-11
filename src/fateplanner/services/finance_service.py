import sqlite3

from datetime import date
from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
)
from fateplanner.utils.date_utils import (
    get_jalali_month_dates,
)


VALID_TRANSACTION_TYPES = {
    "income",
    "expense",
}


def _validate_type(
    transaction_type: str,
) -> str:
    if (
        transaction_type
        not in VALID_TRANSACTION_TYPES
    ):
        raise ValueError(
            "Invalid transaction type."
        )

    return transaction_type


def _parse_date(
    value: str,
) -> date:
    try:
        return date.fromisoformat(
            value
        )

    except ValueError as error:
        raise ValueError(
            "Invalid transaction date."
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


def _validate_jalali_period(
    jalali_year: int,
    jalali_month: int,
) -> tuple[int, int]:
    jalali_year = int(
        jalali_year
    )

    jalali_month = int(
        jalali_month
    )

    if jalali_year < 1:
        raise ValueError(
            "Invalid Jalali year."
        )

    if not (
        1 <= jalali_month <= 12
    ):
        raise ValueError(
            "Invalid Jalali month."
        )

    return (
        jalali_year,
        jalali_month,
    )


# =====================================
# Categories
# =====================================


def create_finance_category(
    *,
    name: str,
    transaction_type: str,
    database_path: str | Path | None = None,
) -> int:
    name = name.strip()

    if not name:
        raise ValueError(
            "Category name cannot be empty."
        )

    _validate_type(
        transaction_type
    )

    with get_connection(
        database_path
    ) as connection:

        cursor = connection.execute(
            """
            INSERT INTO finance_categories (
                name,
                transaction_type
            )
            VALUES (?, ?)
            """,
            (
                name,
                transaction_type,
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


def get_finance_category(
    category_id: int,
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
                transaction_type,
                created_at
            FROM finance_categories
            WHERE id = ?
            """,
            (
                category_id,
            ),
        ).fetchone()


def get_finance_categories(
    transaction_type: str | None = None,
    database_path: str | Path | None = None,
):
    parameters = []

    sql = """
        SELECT
            id,
            name,
            transaction_type,
            created_at
        FROM finance_categories
    """

    if transaction_type is not None:
        _validate_type(
            transaction_type
        )

        sql += """
            WHERE transaction_type = ?
        """

        parameters.append(
            transaction_type
        )

    sql += """
        ORDER BY
            transaction_type ASC,
            name COLLATE NOCASE ASC,
            id ASC
    """

    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            sql,
            parameters,
        ).fetchall()


def update_finance_category(
    *,
    category_id: int,
    name: str,
    transaction_type: str,
    database_path: str | Path | None = None,
) -> None:
    name = name.strip()

    if not name:
        raise ValueError(
            "Category name cannot be empty."
        )

    _validate_type(
        transaction_type
    )

    with get_connection(
        database_path
    ) as connection:

        existing = connection.execute(
            """
            SELECT
                transaction_type
            FROM finance_categories
            WHERE id = ?
            """,
            (
                category_id,
            ),
        ).fetchone()

        if existing is None:
            raise ValueError(
                "Category does not exist."
            )

        if (
            existing["transaction_type"]
            != transaction_type
        ):
            transaction_usage = (
                connection.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM finance_transactions
                    WHERE category_id = ?
                    """,
                    (
                        category_id,
                    ),
                ).fetchone()
            )

            budget_usage = (
                connection.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM finance_budgets
                    WHERE category_id = ?
                    """,
                    (
                        category_id,
                    ),
                ).fetchone()
            )

            if (
                int(
                    transaction_usage[
                        "total"
                    ]
                )
                or int(
                    budget_usage[
                        "total"
                    ]
                )
            ):
                raise ValueError(
                    "A category already used "
                    "by transactions or budgets "
                    "cannot change type."
                )

        connection.execute(
            """
            UPDATE finance_categories
            SET
                name = ?,
                transaction_type = ?
            WHERE id = ?
            """,
            (
                name,
                transaction_type,
                category_id,
            ),
        )

        connection.commit()


def delete_finance_category(
    category_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        usage = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM finance_transactions
            WHERE category_id = ?
            """,
            (
                category_id,
            ),
        ).fetchone()

        if int(
            usage["total"]
        ):
            raise ValueError(
                "This category is already used "
                "by one or more transactions."
            )

        connection.execute(
            """
            DELETE FROM finance_categories
            WHERE id = ?
            """,
            (
                category_id,
            ),
        )

        connection.commit()


# =====================================
# Transactions
# =====================================


def _validate_category_for_transaction(
    connection,
    category_id: int,
    transaction_type: str,
) -> None:
    category = connection.execute(
        """
        SELECT
            id,
            transaction_type
        FROM finance_categories
        WHERE id = ?
        """,
        (
            category_id,
        ),
    ).fetchone()

    if category is None:
        raise ValueError(
            "Finance category does not exist."
        )

    if (
        category["transaction_type"]
        != transaction_type
    ):
        raise ValueError(
            "Category type does not match "
            "transaction type."
        )


def create_finance_transaction(
    *,
    transaction_type: str,
    category_id: int,
    amount: int,
    transaction_date: str,
    description: str = "",
    database_path: str | Path | None = None,
) -> int:
    _validate_type(
        transaction_type
    )

    amount = _validate_amount(
        amount
    )

    _parse_date(
        transaction_date
    )

    description = (
        description.strip()
    )

    with get_connection(
        database_path
    ) as connection:

        _validate_category_for_transaction(
            connection,
            category_id,
            transaction_type,
        )

        cursor = connection.execute(
            """
            INSERT INTO finance_transactions (
                transaction_type,
                category_id,
                amount,
                transaction_date,
                description
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                transaction_type,
                category_id,
                amount,
                transaction_date,
                description,
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


def get_finance_transaction(
    transaction_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                t.id,
                t.transaction_type,
                t.category_id,
                t.amount,
                t.transaction_date,
                t.description,
                t.created_at,
                c.name AS category_name
            FROM finance_transactions AS t
            JOIN finance_categories AS c
                ON c.id = t.category_id
            WHERE t.id = ?
            """,
            (
                transaction_id,
            ),
        ).fetchone()


def get_finance_transactions_between(
    start_date: str,
    end_date: str,
    transaction_type: str | None = None,
    database_path: str | Path | None = None,
):
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

    parameters = [
        start_date,
        end_date,
    ]

    sql = """
        SELECT
            t.id,
            t.transaction_type,
            t.category_id,
            t.amount,
            t.transaction_date,
            t.description,
            t.created_at,
            c.name AS category_name
        FROM finance_transactions AS t
        JOIN finance_categories AS c
            ON c.id = t.category_id
        WHERE
            t.transaction_date >= ?
            AND t.transaction_date <= ?
    """

    if transaction_type is not None:
        _validate_type(
            transaction_type
        )

        sql += """
            AND t.transaction_type = ?
        """

        parameters.append(
            transaction_type
        )

    sql += """
        ORDER BY
            t.transaction_date DESC,
            t.id DESC
    """

    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            sql,
            parameters,
        ).fetchall()


def update_finance_transaction(
    *,
    transaction_id: int,
    transaction_type: str,
    category_id: int,
    amount: int,
    transaction_date: str,
    description: str = "",
    database_path: str | Path | None = None,
) -> None:
    _validate_type(
        transaction_type
    )

    amount = _validate_amount(
        amount
    )

    _parse_date(
        transaction_date
    )

    description = (
        description.strip()
    )

    with get_connection(
        database_path
    ) as connection:

        _validate_category_for_transaction(
            connection,
            category_id,
            transaction_type,
        )

        result = connection.execute(
            """
            UPDATE finance_transactions
            SET
                transaction_type = ?,
                category_id = ?,
                amount = ?,
                transaction_date = ?,
                description = ?
            WHERE id = ?
            """,
            (
                transaction_type,
                category_id,
                amount,
                transaction_date,
                description,
                transaction_id,
            ),
        )

        if result.rowcount == 0:
            raise ValueError(
                "Finance transaction "
                "does not exist."
            )

        connection.commit()


def delete_finance_transaction(
    transaction_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        connection.execute(
            """
            DELETE FROM finance_transactions
            WHERE id = ?
            """,
            (
                transaction_id,
            ),
        )

        connection.commit()


# =====================================
# Finance summary
# =====================================


def get_finance_summary_between(
    start_date: str,
    end_date: str,
    database_path: str | Path | None = None,
) -> dict:
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

    with get_connection(
        database_path
    ) as connection:

        row = connection.execute(
            """
            SELECT
                SUM(
                    CASE
                        WHEN transaction_type = 'income'
                        THEN amount
                        ELSE 0
                    END
                ) AS income,

                SUM(
                    CASE
                        WHEN transaction_type = 'expense'
                        THEN amount
                        ELSE 0
                    END
                ) AS expense,

                COUNT(*) AS total_transactions

            FROM finance_transactions

            WHERE
                transaction_date >= ?
                AND transaction_date <= ?
            """,
            (
                start_date,
                end_date,
            ),
        ).fetchone()

    income = int(
        row["income"] or 0
    )

    expense = int(
        row["expense"] or 0
    )

    return {
        "income": income,
        "expense": expense,
        "balance": (
            income - expense
        ),
        "total_transactions": int(
            row["total_transactions"]
            or 0
        ),
    }


# =====================================
# Budgets
# =====================================


def _validate_expense_category(
    connection,
    category_id: int,
) -> None:
    category = connection.execute(
        """
        SELECT
            id,
            transaction_type
        FROM finance_categories
        WHERE id = ?
        """,
        (
            category_id,
        ),
    ).fetchone()

    if category is None:
        raise ValueError(
            "Finance category does not exist."
        )

    if (
        category[
            "transaction_type"
        ]
        != "expense"
    ):
        raise ValueError(
            "Budgets can only be created "
            "for expense categories."
        )


def create_finance_budget(
    *,
    category_id: int,
    jalali_year: int,
    jalali_month: int,
    amount: int,
    database_path: str | Path | None = None,
) -> int:
    (
        jalali_year,
        jalali_month,
    ) = _validate_jalali_period(
        jalali_year,
        jalali_month,
    )

    amount = _validate_amount(
        amount
    )

    with get_connection(
        database_path
    ) as connection:

        _validate_expense_category(
            connection,
            category_id,
        )

        try:
            cursor = connection.execute(
                """
                INSERT INTO finance_budgets (
                    category_id,
                    jalali_year,
                    jalali_month,
                    amount
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    category_id,
                    jalali_year,
                    jalali_month,
                    amount,
                ),
            )

        except sqlite3.IntegrityError as error:
            raise ValueError(
                "A budget already exists "
                "for this category and month."
            ) from error

        connection.commit()

        return int(
            cursor.lastrowid
        )


def get_finance_budget(
    budget_id: int,
    database_path: str | Path | None = None,
):
    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                b.id,
                b.category_id,
                b.jalali_year,
                b.jalali_month,
                b.amount,
                b.created_at,
                c.name AS category_name
            FROM finance_budgets AS b
            JOIN finance_categories AS c
                ON c.id = b.category_id
            WHERE b.id = ?
            """,
            (
                budget_id,
            ),
        ).fetchone()


def get_finance_budgets_for_month(
    jalali_year: int,
    jalali_month: int,
    database_path: str | Path | None = None,
):
    (
        jalali_year,
        jalali_month,
    ) = _validate_jalali_period(
        jalali_year,
        jalali_month,
    )

    with get_connection(
        database_path
    ) as connection:

        return connection.execute(
            """
            SELECT
                b.id,
                b.category_id,
                b.jalali_year,
                b.jalali_month,
                b.amount,
                b.created_at,
                c.name AS category_name
            FROM finance_budgets AS b
            JOIN finance_categories AS c
                ON c.id = b.category_id
            WHERE
                b.jalali_year = ?
                AND b.jalali_month = ?
            ORDER BY
                c.name COLLATE NOCASE ASC
            """,
            (
                jalali_year,
                jalali_month,
            ),
        ).fetchall()


def update_finance_budget(
    *,
    budget_id: int,
    category_id: int,
    jalali_year: int,
    jalali_month: int,
    amount: int,
    database_path: str | Path | None = None,
) -> None:
    (
        jalali_year,
        jalali_month,
    ) = _validate_jalali_period(
        jalali_year,
        jalali_month,
    )

    amount = _validate_amount(
        amount
    )

    with get_connection(
        database_path
    ) as connection:

        _validate_expense_category(
            connection,
            category_id,
        )

        try:
            result = connection.execute(
                """
                UPDATE finance_budgets
                SET
                    category_id = ?,
                    jalali_year = ?,
                    jalali_month = ?,
                    amount = ?
                WHERE id = ?
                """,
                (
                    category_id,
                    jalali_year,
                    jalali_month,
                    amount,
                    budget_id,
                ),
            )

        except sqlite3.IntegrityError as error:
            raise ValueError(
                "A budget already exists "
                "for this category and month."
            ) from error

        if result.rowcount == 0:
            raise ValueError(
                "Budget does not exist."
            )

        connection.commit()


def delete_finance_budget(
    budget_id: int,
    database_path: str | Path | None = None,
) -> None:
    with get_connection(
        database_path
    ) as connection:

        connection.execute(
            """
            DELETE FROM finance_budgets
            WHERE id = ?
            """,
            (
                budget_id,
            ),
        )

        connection.commit()


def get_finance_budget_statuses(
    jalali_year: int,
    jalali_month: int,
    database_path: str | Path | None = None,
) -> list[dict]:
    (
        jalali_year,
        jalali_month,
    ) = _validate_jalali_period(
        jalali_year,
        jalali_month,
    )

    month_dates = (
        get_jalali_month_dates(
            jalali_year,
            jalali_month,
        )
    )

    start_date = (
        month_dates[0].isoformat()
    )

    end_date = (
        month_dates[-1].isoformat()
    )

    budgets = (
        get_finance_budgets_for_month(
            jalali_year,
            jalali_month,
            database_path=database_path,
        )
    )

    result = []

    with get_connection(
        database_path
    ) as connection:

        for budget in budgets:
            row = connection.execute(
                """
                SELECT
                    SUM(amount) AS spent
                FROM finance_transactions
                WHERE
                    transaction_type = 'expense'
                    AND category_id = ?
                    AND transaction_date >= ?
                    AND transaction_date <= ?
                """,
                (
                    budget[
                        "category_id"
                    ],
                    start_date,
                    end_date,
                ),
            ).fetchone()

            spent = int(
                row["spent"] or 0
            )

            amount = int(
                budget["amount"]
            )

            remaining = (
                amount - spent
            )

            percentage = (
                round(
                    spent
                    / amount
                    * 100
                )
                if amount
                else 0
            )

            result.append(
                {
                    "id": (
                        budget["id"]
                    ),
                    "category_id": (
                        budget[
                            "category_id"
                        ]
                    ),
                    "category_name": (
                        budget[
                            "category_name"
                        ]
                    ),
                    "amount": amount,
                    "spent": spent,
                    "remaining": (
                        remaining
                    ),
                    "percentage": (
                        percentage
                    ),
                    "overspent": (
                        spent > amount
                    ),
                }
            )

    return result


def get_finance_budget_overview(
    jalali_year: int,
    jalali_month: int,
    database_path: str | Path | None = None,
) -> dict:
    statuses = (
        get_finance_budget_statuses(
            jalali_year,
            jalali_month,
            database_path=database_path,
        )
    )

    month_dates = (
        get_jalali_month_dates(
            jalali_year,
            jalali_month,
        )
    )

    summary = (
        get_finance_summary_between(
            month_dates[
                0
            ].isoformat(),
            month_dates[
                -1
            ].isoformat(),
            database_path=database_path,
        )
    )

    total_budget = sum(
        row["amount"]
        for row in statuses
    )

    budgeted_spending = sum(
        row["spent"]
        for row in statuses
    )

    overspent_count = sum(
        1
        for row in statuses
        if row["overspent"]
    )

    all_expense = (
        summary["expense"]
    )

    unbudgeted_expense = max(
        0,
        all_expense
        - budgeted_spending,
    )

    return {
        "total_budget": (
            total_budget
        ),
        "budgeted_spending": (
            budgeted_spending
        ),
        "remaining": (
            total_budget
            - budgeted_spending
        ),
        "overspent_count": (
            overspent_count
        ),
        "all_expense": (
            all_expense
        ),
        "unbudgeted_expense": (
            unbudgeted_expense
        ),
    }


# =====================================
# Money formatting
# =====================================


def format_money(
    amount: int,
) -> str:
    return f"{int(amount):,}"