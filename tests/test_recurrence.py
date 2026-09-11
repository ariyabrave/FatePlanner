from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.recurrence_service import (
    create_recurring_series,
    delete_recurring_series,
    generate_recurring_instances,
    get_recurring_template,
    get_series_instances,
    update_recurring_series,
)


def make_database(
    tmp_path,
):
    database = (
        tmp_path
        / "recurrence.db"
    )

    initialize_database(
        database
    )

    return database


def test_create_recurring_template(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = (
        create_recurring_series(
            title="Study",
            recurrence_type="daily",
            recurrence_start_date=(
                "2026-09-11"
            ),
            database_path=database,
        )
    )

    template = (
        get_recurring_template(
            template_id,
            database_path=database,
        )
    )

    assert template is not None

    assert (
        template[
            "is_recurring_template"
        ]
        == 1
    )

    assert (
        template[
            "recurrence_type"
        ]
        == "daily"
    )


def test_daily_recurrence(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = (
        create_recurring_series(
            title="Read",
            recurrence_type="daily",
            recurrence_start_date=(
                "2026-09-11"
            ),
            database_path=database,
        )
    )

    created = (
        generate_recurring_instances(
            template_id,
            "2026-09-15",
            database_path=database,
        )
    )

    assert created == 5

    instances = (
        get_series_instances(
            template_id,
            database_path=database,
        )
    )

    assert [
        task["due_date"]
        for task in instances
    ] == [
        "2026-09-11",
        "2026-09-12",
        "2026-09-13",
        "2026-09-14",
        "2026-09-15",
    ]


def test_daily_generation_has_no_duplicates(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = (
        create_recurring_series(
            title="Read",
            recurrence_type="daily",
            recurrence_start_date=(
                "2026-09-11"
            ),
            database_path=database,
        )
    )

    generate_recurring_instances(
        template_id,
        "2026-09-15",
        database_path=database,
    )

    generate_recurring_instances(
        template_id,
        "2026-09-15",
        database_path=database,
    )

    instances = (
        get_series_instances(
            template_id,
            database_path=database,
        )
    )

    assert len(instances) == 5


def test_weekly_recurrence(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = (
        create_recurring_series(
            title="Weekly study",
            recurrence_type="weekly",
            recurrence_start_date=(
                "2026-09-11"
            ),
            database_path=database,
        )
    )

    generate_recurring_instances(
        template_id,
        "2026-09-30",
        database_path=database,
    )

    instances = (
        get_series_instances(
            template_id,
            database_path=database,
        )
    )

    assert [
        task["due_date"]
        for task in instances
    ] == [
        "2026-09-11",
        "2026-09-18",
        "2026-09-25",
    ]


def test_custom_weekdays(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = (
        create_recurring_series(
            title="Workout",
            recurrence_type="weekdays",
            recurrence_start_date=(
                "2026-09-05"
            ),
            recurrence_weekdays=[
                5,
                0,
                2,
            ],
            database_path=database,
        )
    )

    generate_recurring_instances(
        template_id,
        "2026-09-11",
        database_path=database,
    )

    instances = (
        get_series_instances(
            template_id,
            database_path=database,
        )
    )

    assert [
        task["due_date"]
        for task in instances
    ] == [
        "2026-09-05",
        "2026-09-07",
        "2026-09-09",
    ]


def test_recurrence_end_date(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = (
        create_recurring_series(
            title="Temporary habit",
            recurrence_type="daily",
            recurrence_start_date=(
                "2026-09-11"
            ),
            recurrence_end_date=(
                "2026-09-13"
            ),
            database_path=database,
        )
    )

    generate_recurring_instances(
        template_id,
        "2026-09-20",
        database_path=database,
    )

    instances = (
        get_series_instances(
            template_id,
            database_path=database,
        )
    )

    assert [
        task["due_date"]
        for task in instances
    ] == [
        "2026-09-11",
        "2026-09-12",
        "2026-09-13",
    ]


def test_update_recurring_series(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = (
        create_recurring_series(
            title="Old title",
            recurrence_type="daily",
            recurrence_start_date=(
                "2026-09-11"
            ),
            database_path=database,
        )
    )

    generate_recurring_instances(
        template_id,
        "2026-09-15",
        database_path=database,
    )

    update_recurring_series(
        template_id=template_id,
        title="New title",
        recurrence_type="weekly",
        recurrence_start_date=(
            "2026-09-11"
        ),
        replace_instances_from=(
            "2026-09-11"
        ),
        database_path=database,
    )

    generate_recurring_instances(
        template_id,
        "2026-09-30",
        database_path=database,
    )

    template = (
        get_recurring_template(
            template_id,
            database_path=database,
        )
    )

    assert (
        template["title"]
        == "New title"
    )

    assert (
        template[
            "recurrence_type"
        ]
        == "weekly"
    )

    instances = (
        get_series_instances(
            template_id,
            database_path=database,
        )
    )

    assert [
        task["due_date"]
        for task in instances
    ] == [
        "2026-09-11",
        "2026-09-18",
        "2026-09-25",
    ]


def test_delete_recurring_series(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = (
        create_recurring_series(
            title="Delete me",
            recurrence_type="daily",
            recurrence_start_date=(
                "2026-09-11"
            ),
            database_path=database,
        )
    )

    generate_recurring_instances(
        template_id,
        "2026-09-15",
        database_path=database,
    )

    delete_recurring_series(
        template_id,
        database_path=database,
    )

    assert (
        get_recurring_template(
            template_id,
            database_path=database,
        )
        is None
    )

    assert (
        get_series_instances(
            template_id,
            database_path=database,
        )
        == []
    )