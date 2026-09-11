from fateplanner.database.connection import (
    get_connection,
    initialize_database,
)
from fateplanner.services.analytics_service import (
    get_finance_category_spending_between,
    get_habit_daily_totals_between,
    get_habit_summary_between,
    get_overdue_task_count,
    get_task_daily_totals_between,
    get_task_summary_between,
)
from fateplanner.services.finance_service import (
    create_finance_category,
    create_finance_transaction,
)
from fateplanner.services.habit_service import (
    create_habit,
    set_habit_completed,
)


def make_database(
    tmp_path,
):
    database = (
        tmp_path
        / "analytics.db"
    )

    initialize_database(
        database
    )

    return database


def test_task_summary(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    with get_connection(
        database
    ) as connection:

        connection.execute(
            """
            INSERT INTO tasks (
                title,
                due_date,
                completed,
                is_recurring_template
            )
            VALUES
                ('A', '2026-09-12', 1, 0),
                ('B', '2026-09-13', 0, 0),
                ('Template', NULL, 0, 1)
            """
        )

        connection.commit()

    summary = get_task_summary_between(
        "2026-09-12",
        "2026-09-18",
        database_path=database,
    )

    assert summary["total"] == 2

    assert (
        summary["completed"]
        == 1
    )

    assert (
        summary["percentage"]
        == 50
    )


def test_task_daily_totals(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    with get_connection(
        database
    ) as connection:

        connection.execute(
            """
            INSERT INTO tasks (
                title,
                due_date,
                completed,
                is_recurring_template
            )
            VALUES
                ('A', '2026-09-12', 1, 0),
                ('B', '2026-09-12', 0, 0)
            """
        )

        connection.commit()

    rows = get_task_daily_totals_between(
        "2026-09-12",
        "2026-09-18",
        database_path=database,
    )

    assert len(rows) == 7

    assert rows[0]["total"] == 2

    assert (
        rows[0]["completed"]
        == 1
    )


def test_overdue_tasks(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    with get_connection(
        database
    ) as connection:

        connection.execute(
            """
            INSERT INTO tasks (
                title,
                due_date,
                completed,
                is_recurring_template
            )
            VALUES
                ('Late', '2026-09-10', 0, 0),
                ('Done', '2026-09-10', 1, 0)
            """
        )

        connection.commit()

    assert (
        get_overdue_task_count(
            "2026-09-12",
            database_path=database,
        )
        == 1
    )


def test_habit_summary(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Read",
        schedule_type="daily",
        start_date="2026-09-12",
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-09-12",
        True,
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-09-13",
        True,
        database_path=database,
    )

    summary = get_habit_summary_between(
        "2026-09-12",
        "2026-09-14",
        database_path=database,
    )

    assert (
        summary["scheduled"]
        == 3
    )

    assert (
        summary["completed"]
        == 2
    )

    assert (
        summary["percentage"]
        == 67
    )


def test_habit_daily_totals(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Read",
        schedule_type="daily",
        start_date="2026-09-12",
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-09-12",
        True,
        database_path=database,
    )

    rows = get_habit_daily_totals_between(
        "2026-09-12",
        "2026-09-13",
        database_path=database,
    )

    assert len(rows) == 2

    assert (
        rows[0]["percentage"]
        == 100
    )

    assert (
        rows[1]["percentage"]
        == 0
    )


def test_finance_category_spending(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    food = create_finance_category(
        name="Food",
        transaction_type="expense",
        database_path=database,
    )

    transport = (
        create_finance_category(
            name="Transport",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=food,
        amount=500_000,
        transaction_date="2026-09-12",
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=food,
        amount=250_000,
        transaction_date="2026-09-13",
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=transport,
        amount=100_000,
        transaction_date="2026-09-13",
        database_path=database,
    )

    rows = (
        get_finance_category_spending_between(
            "2026-09-01",
            "2026-09-30",
            database_path=database,
        )
    )

    assert len(rows) == 2

    assert (
        rows[0]["category_name"]
        == "Food"
    )

    assert (
        rows[0]["total_amount"]
        == 750_000
    )