import pytest

from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.finance_service import (
    create_finance_budget,
    create_finance_category,
    create_finance_transaction,
    delete_finance_budget,
    get_finance_budget,
    get_finance_budget_overview,
    get_finance_budget_statuses,
    get_finance_budgets_for_month,
    update_finance_budget,
)


@pytest.fixture
def database(
    tmp_path,
):
    path = (
        tmp_path
        / "budgets.db"
    )

    initialize_database(
        path
    )

    return path


def test_create_budget(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    budget_id = (
        create_finance_budget(
            category_id=category,
            jalali_year=1405,
            jalali_month=6,
            amount=5_000_000,
            database_path=database,
        )
    )

    budget = get_finance_budget(
        budget_id,
        database_path=database,
    )

    assert budget is not None

    assert (
        budget["amount"]
        == 5_000_000
    )


def test_income_category_cannot_have_budget(
    database,
):
    category = (
        create_finance_category(
            name="Salary",
            transaction_type="income",
            database_path=database,
        )
    )

    with pytest.raises(
        ValueError
    ):
        create_finance_budget(
            category_id=category,
            jalali_year=1405,
            jalali_month=6,
            amount=5_000_000,
            database_path=database,
        )


def test_duplicate_month_budget_rejected(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_budget(
        category_id=category,
        jalali_year=1405,
        jalali_month=6,
        amount=5_000_000,
        database_path=database,
    )

    with pytest.raises(
        ValueError
    ):
        create_finance_budget(
            category_id=category,
            jalali_year=1405,
            jalali_month=6,
            amount=6_000_000,
            database_path=database,
        )


def test_same_category_different_month_allowed(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_budget(
        category_id=category,
        jalali_year=1405,
        jalali_month=6,
        amount=5_000_000,
        database_path=database,
    )

    create_finance_budget(
        category_id=category,
        jalali_year=1405,
        jalali_month=7,
        amount=6_000_000,
        database_path=database,
    )

    month_six = (
        get_finance_budgets_for_month(
            1405,
            6,
            database_path=database,
        )
    )

    month_seven = (
        get_finance_budgets_for_month(
            1405,
            7,
            database_path=database,
        )
    )

    assert len(month_six) == 1
    assert len(month_seven) == 1


def test_budget_status_uses_real_expenses(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_budget(
        category_id=category,
        jalali_year=1405,
        jalali_month=6,
        amount=1_000_000,
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=category,
        amount=400_000,
        transaction_date="2026-09-01",
        database_path=database,
    )

    statuses = (
        get_finance_budget_statuses(
            1405,
            6,
            database_path=database,
        )
    )

    assert len(statuses) == 1

    assert (
        statuses[0]["spent"]
        == 400_000
    )

    assert (
        statuses[0]["remaining"]
        == 600_000
    )

    assert (
        statuses[0]["percentage"]
        == 40
    )

    assert (
        statuses[0]["overspent"]
        is False
    )


def test_overspent_budget(
    database,
):
    category = (
        create_finance_category(
            name="Shopping",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_budget(
        category_id=category,
        jalali_year=1405,
        jalali_month=6,
        amount=1_000_000,
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=category,
        amount=1_250_000,
        transaction_date="2026-09-01",
        database_path=database,
    )

    status = (
        get_finance_budget_statuses(
            1405,
            6,
            database_path=database,
        )[0]
    )

    assert (
        status["remaining"]
        == -250_000
    )

    assert (
        status["percentage"]
        == 125
    )

    assert (
        status["overspent"]
        is True
    )


def test_budget_overview(
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

    entertainment = (
        create_finance_category(
            name="Entertainment",
            transaction_type="expense",
            database_path=database,
        )
    )

    create_finance_budget(
        category_id=food,
        jalali_year=1405,
        jalali_month=6,
        amount=2_000_000,
        database_path=database,
    )

    create_finance_budget(
        category_id=transport,
        jalali_year=1405,
        jalali_month=6,
        amount=1_000_000,
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=food,
        amount=500_000,
        transaction_date="2026-09-01",
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=transport,
        amount=250_000,
        transaction_date="2026-09-01",
        database_path=database,
    )

    create_finance_transaction(
        transaction_type="expense",
        category_id=entertainment,
        amount=300_000,
        transaction_date="2026-09-01",
        database_path=database,
    )

    overview = (
        get_finance_budget_overview(
            1405,
            6,
            database_path=database,
        )
    )

    assert (
        overview["total_budget"]
        == 3_000_000
    )

    assert (
        overview[
            "budgeted_spending"
        ]
        == 750_000
    )

    assert (
        overview["remaining"]
        == 2_250_000
    )

    assert (
        overview[
            "unbudgeted_expense"
        ]
        == 300_000
    )


def test_update_budget(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    budget_id = (
        create_finance_budget(
            category_id=category,
            jalali_year=1405,
            jalali_month=6,
            amount=1_000_000,
            database_path=database,
        )
    )

    update_finance_budget(
        budget_id=budget_id,
        category_id=category,
        jalali_year=1405,
        jalali_month=6,
        amount=2_000_000,
        database_path=database,
    )

    budget = get_finance_budget(
        budget_id,
        database_path=database,
    )

    assert (
        budget["amount"]
        == 2_000_000
    )


def test_delete_budget(
    database,
):
    category = (
        create_finance_category(
            name="Food",
            transaction_type="expense",
            database_path=database,
        )
    )

    budget_id = (
        create_finance_budget(
            category_id=category,
            jalali_year=1405,
            jalali_month=6,
            amount=1_000_000,
            database_path=database,
        )
    )

    delete_finance_budget(
        budget_id,
        database_path=database,
    )

    assert (
        get_finance_budget(
            budget_id,
            database_path=database,
        )
        is None
    )