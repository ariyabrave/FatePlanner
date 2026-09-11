import pytest

from fateplanner.database.connection import (
    get_connection,
    initialize_database,
)
from fateplanner.services.savings_service import (
    add_savings_entry,
    create_savings_goal,
    delete_savings_entry,
    delete_savings_goal,
    get_savings_entries,
    get_savings_goal,
    get_savings_goals,
    get_savings_overview,
    update_savings_goal,
)


@pytest.fixture
def database(
    tmp_path,
):
    path = (
        tmp_path
        / "savings.db"
    )

    initialize_database(
        path
    )

    return path


def test_create_savings_goal(
    database,
):
    goal_id = create_savings_goal(
        title="Laptop",
        target_amount=50_000_000,
        target_date="2027-01-01",
        database_path=database,
    )

    goal = get_savings_goal(
        goal_id,
        database_path=database,
    )

    assert goal is not None

    assert (
        goal["target_amount"]
        == 50_000_000
    )

    assert (
        goal["current_amount"]
        == 0
    )

    assert goal["completed"] is False


def test_deposit_updates_goal(
    database,
):
    goal_id = create_savings_goal(
        title="Trip",
        target_amount=10_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=2_000_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    goal = get_savings_goal(
        goal_id,
        database_path=database,
    )

    assert (
        goal["current_amount"]
        == 2_000_000
    )

    assert (
        goal["remaining_amount"]
        == 8_000_000
    )

    assert goal["percentage"] == 20


def test_withdrawal_reduces_saved_amount(
    database,
):
    goal_id = create_savings_goal(
        title="Emergency",
        target_amount=10_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=5_000_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="withdrawal",
        amount=1_500_000,
        entry_date="2026-09-12",
        database_path=database,
    )

    goal = get_savings_goal(
        goal_id,
        database_path=database,
    )

    assert (
        goal["current_amount"]
        == 3_500_000
    )


def test_cannot_withdraw_more_than_saved(
    database,
):
    goal_id = create_savings_goal(
        title="Trip",
        target_amount=10_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=2_000_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    with pytest.raises(
        ValueError
    ):
        add_savings_entry(
            goal_id=goal_id,
            entry_type="withdrawal",
            amount=3_000_000,
            entry_date="2026-09-12",
            database_path=database,
        )


def test_backdated_withdrawal_rejected(
    database,
):
    goal_id = create_savings_goal(
        title="Laptop",
        target_amount=10_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=5_000_000,
        entry_date="2026-09-15",
        database_path=database,
    )

    with pytest.raises(
        ValueError
    ):
        add_savings_entry(
            goal_id=goal_id,
            entry_type="withdrawal",
            amount=1_000_000,
            entry_date="2026-09-10",
            database_path=database,
        )


def test_goal_completion(
    database,
):
    goal_id = create_savings_goal(
        title="Phone",
        target_amount=5_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=5_500_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    goal = get_savings_goal(
        goal_id,
        database_path=database,
    )

    assert goal["completed"] is True

    assert (
        goal["remaining_amount"]
        == 0
    )

    assert goal["percentage"] == 110


def test_update_goal_preserves_history(
    database,
):
    goal_id = create_savings_goal(
        title="Old",
        target_amount=10_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=2_000_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    update_savings_goal(
        goal_id=goal_id,
        title="New",
        target_amount=20_000_000,
        description="Changed",
        database_path=database,
    )

    goal = get_savings_goal(
        goal_id,
        database_path=database,
    )

    assert goal["title"] == "New"

    assert (
        goal["current_amount"]
        == 2_000_000
    )

    assert goal["percentage"] == 10


def test_savings_overview(
    database,
):
    first = create_savings_goal(
        title="Laptop",
        target_amount=10_000_000,
        database_path=database,
    )

    second = create_savings_goal(
        title="Trip",
        target_amount=5_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=first,
        entry_type="deposit",
        amount=10_000_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    add_savings_entry(
        goal_id=second,
        entry_type="deposit",
        amount=2_000_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    overview = get_savings_overview(
        database_path=database
    )

    assert overview["goal_count"] == 2

    assert (
        overview["completed_goals"]
        == 1
    )

    assert (
        overview["total_target"]
        == 15_000_000
    )

    assert (
        overview["total_saved"]
        == 12_000_000
    )

    assert (
        overview["total_remaining"]
        == 3_000_000
    )


def test_entry_history(
    database,
):
    goal_id = create_savings_goal(
        title="Laptop",
        target_amount=10_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=1_000_000,
        entry_date="2026-09-11",
        note="First",
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=2_000_000,
        entry_date="2026-09-12",
        note="Second",
        database_path=database,
    )

    entries = get_savings_entries(
        goal_id,
        database_path=database,
    )

    assert len(entries) == 2

    assert (
        entries[0]["note"]
        == "Second"
    )


def test_delete_entry_updates_goal(
    database,
):
    goal_id = create_savings_goal(
        title="Trip",
        target_amount=10_000_000,
        database_path=database,
    )

    entry_id = add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=2_000_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    delete_savings_entry(
        entry_id,
        database_path=database,
    )

    goal = get_savings_goal(
        goal_id,
        database_path=database,
    )

    assert (
        goal["current_amount"]
        == 0
    )


def test_cannot_delete_required_deposit(
    database,
):
    goal_id = create_savings_goal(
        title="Emergency",
        target_amount=10_000_000,
        database_path=database,
    )

    deposit_id = add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=5_000_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="withdrawal",
        amount=4_000_000,
        entry_date="2026-09-12",
        database_path=database,
    )

    with pytest.raises(
        ValueError
    ):
        delete_savings_entry(
            deposit_id,
            database_path=database,
        )


def test_delete_goal_cascades_entries(
    database,
):
    goal_id = create_savings_goal(
        title="Temporary",
        target_amount=1_000_000,
        database_path=database,
    )

    add_savings_entry(
        goal_id=goal_id,
        entry_type="deposit",
        amount=500_000,
        entry_date="2026-09-11",
        database_path=database,
    )

    delete_savings_goal(
        goal_id,
        database_path=database,
    )

    assert (
        get_savings_goal(
            goal_id,
            database_path=database,
        )
        is None
    )

    with get_connection(
        database
    ) as connection:

        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM savings_entries
            """
        ).fetchone()

    assert row["total"] == 0


def test_get_all_goals(
    database,
):
    create_savings_goal(
        title="Laptop",
        target_amount=10_000_000,
        database_path=database,
    )

    create_savings_goal(
        title="Trip",
        target_amount=20_000_000,
        database_path=database,
    )

    assert len(
        get_savings_goals(
            database_path=database
        )
    ) == 2