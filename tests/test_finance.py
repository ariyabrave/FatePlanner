import pytest

from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.finance_service import (
    create_finance_category,
    create_finance_transaction,
    delete_finance_category,
    delete_finance_transaction,
    get_finance_categories,
    get_finance_summary_between,
    get_finance_transaction,
    get_finance_transactions_between,
    update_finance_category,
    update_finance_transaction,
)


@pytest.fixture
def database(
    tmp_path,
):
    path = (
        tmp_path
        / "finance.db"
    )

    initialize_database(
        path
    )

    return path


def test_create_finance_category(
    database,
):
    category_id = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    categories = (
        get_finance_categories(
            "expense",
            database_path=database,
        )
    )

    assert len(categories) == 1

    assert (
        categories[0]["id"]
        == category_id
    )

    assert (
        categories[0]["name"]
        == "Food"
    )


def test_create_income_transaction(
    database,
):
    category_id = (
        create_finance_category(
            name="Salary",
            transaction_type="income",
            database_path=database,
        )
    )

    transaction_id = (
        create_finance_transaction(
            transaction_type="income",
            category_id=category_id,
            amount=10_000_000,
            transaction_date=(
                "2026-09-11"
            ),
            description="September",
            database_path=database,
        )
    )

    transaction = (
        get_finance_transaction(
            transaction_id,
            database_path=database,
        )
    )

    assert (
        transaction["amount"]
        == 10_000_000
    )

    assert (
        transaction[
            "category_name"
        ]
        == "Salary"
    )


def test_category_type_must_match(
    database,
):
    category_id = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    with pytest.raises(
        ValueError
    ):
        create_finance_transaction(
            transaction_type="income",
            category_id=category_id,
            amount=1000,
            transaction_date=(
                "2026-09-11"
            ),
            database_path=database,
        )


def test_finance_summary(
    database,
):
    salary = (
        create_finance_category(
            name="Salary",
            transaction_type="income",
            database_path=database,
        )
    )

    food = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_transaction(
        transaction_type="income",
        category_id=salary,
        amount=10_000_000,
        transaction_date="2026-09-11",
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=food,
        amount=2_000_000,
        transaction_date="2026-09-12",
        database_path=database,
    )

    summary = (
        get_finance_summary_between(
            "2026-09-01",
            "2026-09-30",
            database_path=database,
        )
    )

    assert (
        summary["income"]
        == 10_000_000
    )

    assert (
        summary["expense"]
        == 2_000_000
    )

    assert (
        summary["balance"]
        == 8_000_000
    )

    assert (
        summary[
            "total_transactions"
        ]
        == 2
    )


def test_transactions_filter_by_date(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=category,
        amount=100,
        transaction_date="2026-09-01",
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=category,
        amount=200,
        transaction_date="2026-10-01",
        database_path=database,
    )

    rows = (
        get_finance_transactions_between(
            "2026-09-01",
            "2026-09-30",
            database_path=database,
        )
    )

    assert len(rows) == 1

    assert (
        rows[0]["amount"]
        == 100
    )


def test_update_transaction(
    database,
):
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

    transaction_id = (
        create_finance_transaction(
            transaction_type="expense",
            category_id=food,
            amount=100,
            transaction_date="2026-09-11",
            database_path=database,
        )
    )

    update_finance_transaction(
        transaction_id=transaction_id,
        transaction_type="expense",
        category_id=transport,
        amount=250,
        transaction_date="2026-09-12",
        description="Taxi",
        database_path=database,
    )

    transaction = (
        get_finance_transaction(
            transaction_id,
            database_path=database,
        )
    )

    assert (
        transaction["amount"]
        == 250
    )

    assert (
        transaction[
            "category_name"
        ]
        == "Transport"
    )

    assert (
        transaction["description"]
        == "Taxi"
    )


def test_delete_transaction(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    transaction_id = (
        create_finance_transaction(
            transaction_type="expense",
            category_id=category,
            amount=100,
            transaction_date="2026-09-11",
            database_path=database,
        )
    )

    delete_finance_transaction(
        transaction_id,
        database_path=database,
    )

    assert (
        get_finance_transaction(
            transaction_id,
            database_path=database,
        )
        is None
    )


def test_used_category_cannot_be_deleted(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=category,
        amount=100,
        transaction_date="2026-09-11",
        database_path=database,
    )

    with pytest.raises(
        ValueError
    ):
        delete_finance_category(
            category,
            database_path=database,
        )


def test_unused_category_can_be_deleted(
    database,
):
    category = (
        create_finance_category(
            name="Temporary",
            transaction_type="expense",
            database_path=database,
        )
    )

    delete_finance_category(
        category,
        database_path=database,
    )

    assert (
        get_finance_categories(
            database_path=database
        )
        == []
    )


def test_used_category_cannot_change_type(
    database,
):
    category = (
        create_finance_category(
            name="Salary",
            transaction_type="income",
            database_path=database,
        )
    )

    create_finance_transaction(
        transaction_type="income",
        category_id=category,
        amount=1000,
        transaction_date="2026-09-11",
        database_path=database,
    )

    with pytest.raises(
        ValueError
    ):
        update_finance_category(
            category_id=category,
            name="Salary",
            transaction_type="expense",
            database_path=database,
        )