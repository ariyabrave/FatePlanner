from fateplanner.database.connection import (
    get_connection,
    initialize_database,
)
from fateplanner.services.habit_service import (
    create_habit,
    delete_habit,
    get_habit,
    get_habit_month_stats,
    get_habit_progress_for_date,
    get_habit_stats,
    get_habits_for_date,
    is_habit_completed,
    set_habit_completed,
    update_habit,
)


def make_database(
    tmp_path,
):
    database = (
        tmp_path
        / "habits.db"
    )

    initialize_database(
        database
    )

    return database


def test_create_daily_habit(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Read",
        start_date="2026-09-11",
        database_path=database,
    )

    habit = get_habit(
        habit_id,
        database_path=database,
    )

    assert habit is not None
    assert habit["title"] == "Read"
    assert (
        habit["schedule_type"]
        == "daily"
    )


def test_selected_weekday_schedule(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    create_habit(
        title="Workout",
        schedule_type="weekdays",
        weekdays=[
            5,
            0,
            2,
        ],
        start_date="2026-09-12",
        database_path=database,
    )

    saturday = get_habits_for_date(
        "2026-09-12",
        database_path=database,
    )

    sunday = get_habits_for_date(
        "2026-09-13",
        database_path=database,
    )

    monday = get_habits_for_date(
        "2026-09-14",
        database_path=database,
    )

    assert len(saturday) == 1
    assert sunday == []
    assert len(monday) == 1


def test_complete_habit(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Study",
        start_date="2026-09-11",
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-09-11",
        True,
        database_path=database,
    )

    assert is_habit_completed(
        habit_id,
        "2026-09-11",
        database_path=database,
    )


def test_uncheck_habit(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Study",
        start_date="2026-09-11",
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-09-11",
        True,
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-09-11",
        False,
        database_path=database,
    )

    assert not is_habit_completed(
        habit_id,
        "2026-09-11",
        database_path=database,
    )


def test_daily_streak(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Read",
        start_date="2026-09-11",
        database_path=database,
    )

    for log_date in [
        "2026-09-11",
        "2026-09-12",
        "2026-09-13",
    ]:
        set_habit_completed(
            habit_id,
            log_date,
            True,
            database_path=database,
        )

    stats = get_habit_stats(
        habit_id,
        through_date="2026-09-13",
        database_path=database,
    )

    assert (
        stats["current_streak"]
        == 3
    )

    assert (
        stats["best_streak"]
        == 3
    )

    assert (
        stats["percentage"]
        == 100
    )


def test_best_streak_survives_gap(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Read",
        start_date="2026-09-10",
        database_path=database,
    )

    for log_date in [
        "2026-09-10",
        "2026-09-11",
        "2026-09-12",
    ]:
        set_habit_completed(
            habit_id,
            log_date,
            True,
            database_path=database,
        )

    set_habit_completed(
        habit_id,
        "2026-09-14",
        True,
        database_path=database,
    )

    stats = get_habit_stats(
        habit_id,
        through_date="2026-09-14",
        database_path=database,
    )

    assert (
        stats["best_streak"]
        == 3
    )

    assert (
        stats["current_streak"]
        == 1
    )


def test_weekday_streak_ignores_off_days(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Workout",
        schedule_type="weekdays",
        weekdays=[
            5,
            0,
            2,
        ],
        start_date="2026-09-12",
        database_path=database,
    )

    for log_date in [
        "2026-09-12",
        "2026-09-14",
        "2026-09-16",
    ]:
        set_habit_completed(
            habit_id,
            log_date,
            True,
            database_path=database,
        )

    stats = get_habit_stats(
        habit_id,
        through_date="2026-09-16",
        database_path=database,
    )

    assert (
        stats["current_streak"]
        == 3
    )

    assert (
        stats["best_streak"]
        == 3
    )


def test_daily_habit_progress(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    first = create_habit(
        title="Read",
        start_date="2026-09-12",
        database_path=database,
    )

    create_habit(
        title="Workout",
        schedule_type="weekdays",
        weekdays=[5],
        start_date="2026-09-12",
        database_path=database,
    )

    set_habit_completed(
        first,
        "2026-09-12",
        True,
        database_path=database,
    )

    (
        total,
        completed,
        percentage,
    ) = get_habit_progress_for_date(
        "2026-09-12",
        database_path=database,
    )

    assert total == 2
    assert completed == 1
    assert percentage == 50


def test_month_stats_daily_habit(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Read",
        start_date="2026-03-21",
        database_path=database,
    )

    for log_date in [
        "2026-03-21",
        "2026-03-22",
        "2026-03-24",
    ]:
        set_habit_completed(
            habit_id,
            log_date,
            True,
            database_path=database,
        )

    stats = get_habit_month_stats(
        habit_id,
        1405,
        1,
        through_date="2026-03-25",
        database_path=database,
    )

    assert (
        stats["scheduled"]
        == 5
    )

    assert (
        stats["completed"]
        == 3
    )

    assert (
        stats["missed"]
        == 2
    )

    assert (
        stats["percentage"]
        == 60
    )


def test_month_stats_ignore_future_days(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Read",
        start_date="2026-03-21",
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-03-21",
        True,
        database_path=database,
    )

    stats = get_habit_month_stats(
        habit_id,
        1405,
        1,
        through_date="2026-03-21",
        database_path=database,
    )

    assert (
        stats["scheduled"]
        == 1
    )

    assert (
        stats["completed"]
        == 1
    )

    assert (
        stats["missed"]
        == 0
    )

    assert (
        stats["percentage"]
        == 100
    )


def test_month_stats_selected_weekdays(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Saturday habit",
        schedule_type="weekdays",
        weekdays=[5],
        start_date="2026-03-21",
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-03-21",
        True,
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-04-04",
        True,
        database_path=database,
    )

    stats = get_habit_month_stats(
        habit_id,
        1405,
        1,
        through_date="2026-04-10",
        database_path=database,
    )

    assert (
        stats["scheduled"]
        == 3
    )

    assert (
        stats["completed"]
        == 2
    )

    assert (
        stats["missed"]
        == 1
    )

    assert (
        stats["percentage"]
        == 67
    )


def test_update_habit(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Old",
        start_date="2026-09-11",
        database_path=database,
    )

    update_habit(
        habit_id=habit_id,
        title="New",
        schedule_type="weekdays",
        weekdays=[5, 0],
        start_date="2026-09-12",
        database_path=database,
    )

    habit = get_habit(
        habit_id,
        database_path=database,
    )

    assert (
        habit["title"]
        == "New"
    )

    assert (
        habit["schedule_type"]
        == "weekdays"
    )

    assert (
        habit["weekdays"]
        == "0,5"
    )


def test_delete_habit_cascades_logs(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    habit_id = create_habit(
        title="Temporary",
        start_date="2026-09-11",
        database_path=database,
    )

    set_habit_completed(
        habit_id,
        "2026-09-11",
        True,
        database_path=database,
    )

    delete_habit(
        habit_id,
        database_path=database,
    )

    with get_connection(
        database
    ) as connection:

        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM habit_logs
            WHERE habit_id = ?
            """,
            (habit_id,),
        ).fetchone()

    assert (
        row["total"]
        == 0
    )