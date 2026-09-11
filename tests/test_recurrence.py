from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.recurrence_service import (
    create_recurring_series,
    delete_recurring_series,
    ensure_recurring_instances_through,
    generate_recurring_instances,
    get_recurring_template,
    get_series_instances,
    update_recurring_series,
)
from fateplanner.services.task_service import (
    delete_task,
    get_tasks,
    set_task_completed,
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

    template_id = create_recurring_series(
        title="Study",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        database_path=database,
    )

    template = get_recurring_template(
        template_id,
        database_path=database,
    )

    assert template is not None

    assert (
        template["is_recurring_template"]
        == 1
    )

    assert (
        template["recurrence_type"]
        == "daily"
    )


def test_templates_do_not_appear_as_tasks(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    create_recurring_series(
        title="Template",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        database_path=database,
    )

    assert (
        get_tasks(
            database_path=database
        )
        == []
    )


def test_daily_recurrence(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = create_recurring_series(
        title="Read",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        database_path=database,
    )

    created = generate_recurring_instances(
        template_id,
        "2026-09-15",
        database_path=database,
    )

    assert created == 5

    instances = get_series_instances(
        template_id,
        database_path=database,
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


def test_generation_has_no_duplicates(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = create_recurring_series(
        title="Read",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        database_path=database,
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

    assert len(
        get_series_instances(
            template_id,
            database_path=database,
        )
    ) == 5


def test_weekly_recurrence(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = create_recurring_series(
        title="Weekly study",
        recurrence_type="weekly",
        recurrence_start_date=(
            "2026-09-11"
        ),
        database_path=database,
    )

    generate_recurring_instances(
        template_id,
        "2026-09-30",
        database_path=database,
    )

    instances = get_series_instances(
        template_id,
        database_path=database,
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

    template_id = create_recurring_series(
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

    generate_recurring_instances(
        template_id,
        "2026-09-11",
        database_path=database,
    )

    instances = get_series_instances(
        template_id,
        database_path=database,
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

    template_id = create_recurring_series(
        title="Temporary",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        recurrence_end_date=(
            "2026-09-13"
        ),
        database_path=database,
    )

    generate_recurring_instances(
        template_id,
        "2026-09-20",
        database_path=database,
    )

    instances = get_series_instances(
        template_id,
        database_path=database,
    )

    assert [
        task["due_date"]
        for task in instances
    ] == [
        "2026-09-11",
        "2026-09-12",
        "2026-09-13",
    ]


def test_ensure_handles_ended_series(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = create_recurring_series(
        title="Short",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        recurrence_end_date=(
            "2026-09-13"
        ),
        database_path=database,
    )

    ensure_recurring_instances_through(
        "2026-09-20",
        database_path=database,
    )

    assert [
        task["due_date"]
        for task in get_series_instances(
            template_id,
            database_path=database,
        )
    ] == [
        "2026-09-11",
        "2026-09-12",
        "2026-09-13",
    ]


def test_delete_single_occurrence_keeps_series(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = create_recurring_series(
        title="Study",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
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

    delete_task(
        instances[1]["id"],
        database_path=database,
    )

    assert (
        get_recurring_template(
            template_id,
            database_path=database,
        )
        is not None
    )

    remaining = get_series_instances(
        template_id,
        database_path=database,
    )

    assert len(
        remaining
    ) == 2


def test_update_series_rebuilds_future(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = create_recurring_series(
        title="Old title",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        database_path=database,
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

    template = get_recurring_template(
        template_id,
        database_path=database,
    )

    assert (
        template["title"]
        == "New title"
    )

    assert (
        template["recurrence_type"]
        == "weekly"
    )

    assert [
        task["due_date"]
        for task in get_series_instances(
            template_id,
            database_path=database,
        )
    ] == [
        "2026-09-11",
        "2026-09-18",
        "2026-09-25",
    ]


def test_completed_occurrence_survives_series_update(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = create_recurring_series(
        title="Original",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        database_path=database,
    )

    generate_recurring_instances(
        template_id,
        "2026-09-15",
        database_path=database,
    )

    instances = get_series_instances(
        template_id,
        database_path=database,
    )

    completed_instance = (
        instances[2]
    )

    set_task_completed(
        completed_instance["id"],
        True,
        database_path=database,
    )

    update_recurring_series(
        template_id=template_id,
        title="Changed",
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

    instances = get_series_instances(
        template_id,
        database_path=database,
    )

    dates = [
        task["due_date"]
        for task in instances
    ]

    assert (
        "2026-09-13"
        in dates
    )

    preserved = [
        task
        for task in instances
        if (
            task["due_date"]
            == "2026-09-13"
        )
    ][0]

    assert (
        preserved["completed"]
        == 1
    )


def test_delete_series_removes_instances(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    template_id = create_recurring_series(
        title="Delete me",
        recurrence_type="daily",
        recurrence_start_date=(
            "2026-09-11"
        ),
        database_path=database,
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