import pytest

from fateplanner.database.connection import (
    get_connection,
    initialize_database,
)
from fateplanner.services.recurrence_service import (
    create_recurring_series,
    generate_recurring_instances,
    get_series_instances,
)
from fateplanner.services.task_service import (
    delete_task,
    get_tasks_for_date,
)


@pytest.fixture
def database(
    tmp_path,
):
    path = (
        tmp_path
        / "recurring-skip.db"
    )

    initialize_database(
        path
    )

    return path


def test_skipped_occurrence_is_not_regenerated(
    database,
):
    template_id = create_recurring_series(
        title="Study",
        recurrence_type="daily",
        recurrence_start_date="2026-09-11",
        database_path=database,
    )

    generate_recurring_instances(
        template_id,
        "2026-09-13",
        database_path=database,
    )

    instances = get_series_instances(
        template_id,
        database_path=database,
    )

    assert len(instances) == 3

    skipped_id = (
        instances[1]["id"]
    )

    skipped_date = (
        instances[1]["due_date"]
    )

    delete_task(
        skipped_id,
        database_path=database,
    )

    # Public APIs should hide it.
    remaining = get_series_instances(
        template_id,
        database_path=database,
    )

    assert len(remaining) == 2

    assert (
        get_tasks_for_date(
            skipped_date,
            database_path=database,
        )
        == []
    )

    # Run generation again.
    generate_recurring_instances(
        template_id,
        "2026-09-13",
        database_path=database,
    )

    # It must still stay hidden.
    remaining = get_series_instances(
        template_id,
        database_path=database,
    )

    assert len(remaining) == 2

    assert (
        get_tasks_for_date(
            skipped_date,
            database_path=database,
        )
        == []
    )

    # The underlying exception row still exists,
    # which blocks INSERT OR IGNORE from recreating it.
    with get_connection(
        database
    ) as connection:

        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                MAX(is_skipped)
                    AS is_skipped
            FROM tasks
            WHERE
                recurring_template_id = ?
                AND due_date = ?
            """,
            (
                template_id,
                skipped_date,
            ),
        ).fetchone()

    assert row["total"] == 1

    assert (
        row["is_skipped"]
        == 1
    )
