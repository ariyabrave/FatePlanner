from datetime import date
from pathlib import Path

from fateplanner.database.connection import (
    get_connection,
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
                    "A category already used by "
                    "transactions cannot change type."
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
# Summary
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
            row["total_transactions"] or 0
        ),
    }


def format_money(
    amount: int,
) -> str:
    return f"{int(amount):,}"