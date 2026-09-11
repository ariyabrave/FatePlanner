from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.study_analytics_service import (
    get_study_daily_totals_between,
    get_study_sessions_between,
    get_study_subject_totals_between,
    get_study_summary_between,
)
from fateplanner.services.study_service import (
    add_study_time,
    create_study_session,
    create_subject,
    set_study_session_completed,
)


def make_database(
    tmp_path,
):
    database = (
        tmp_path
        / "study_analytics.db"
    )

    initialize_database(
        database
    )

    return database


def test_study_summary_between(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    subject_id = create_subject(
        name="English",
        database_path=database,
    )

    first = create_study_session(
        subject_id=subject_id,
        session_date="2026-09-12",
        planned_minutes=30,
        database_path=database,
    )

    create_study_session(
        subject_id=subject_id,
        session_date="2026-09-13",
        planned_minutes=60,
        database_path=database,
    )

    set_study_session_completed(
        first,
        True,
        database_path=database,
    )

    add_study_time(
        first,
        1800,
        database_path=database,
    )

    summary = (
        get_study_summary_between(
            "2026-09-12",
            "2026-09-18",
            database_path=database,
        )
    )

    assert (
        summary["total_sessions"]
        == 2
    )

    assert (
        summary["completed_sessions"]
        == 1
    )

    assert (
        summary["planned_minutes"]
        == 90
    )

    assert (
        summary["actual_seconds"]
        == 1800
    )

    assert (
        summary[
            "completion_percentage"
        ]
        == 50
    )

    assert (
        summary["time_percentage"]
        == 33
    )


def test_sessions_between_filters_dates(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    subject_id = create_subject(
        name="Math",
        database_path=database,
    )

    create_study_session(
        subject_id=subject_id,
        session_date="2026-09-10",
        planned_minutes=30,
        database_path=database,
    )

    create_study_session(
        subject_id=subject_id,
        session_date="2026-09-12",
        planned_minutes=30,
        database_path=database,
    )

    create_study_session(
        subject_id=subject_id,
        session_date="2026-09-20",
        planned_minutes=30,
        database_path=database,
    )

    sessions = (
        get_study_sessions_between(
            "2026-09-12",
            "2026-09-18",
            database_path=database,
        )
    )

    assert len(sessions) == 1

    assert (
        sessions[0]["session_date"]
        == "2026-09-12"
    )


def test_subject_totals(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    english = create_subject(
        name="English",
        database_path=database,
    )

    security = create_subject(
        name="Security",
        database_path=database,
    )

    english_session = (
        create_study_session(
            subject_id=english,
            session_date="2026-09-12",
            planned_minutes=30,
            database_path=database,
        )
    )

    security_session = (
        create_study_session(
            subject_id=security,
            session_date="2026-09-12",
            planned_minutes=60,
            database_path=database,
        )
    )

    add_study_time(
        english_session,
        1800,
        database_path=database,
    )

    add_study_time(
        security_session,
        3600,
        database_path=database,
    )

    totals = (
        get_study_subject_totals_between(
            "2026-09-12",
            "2026-09-18",
            database_path=database,
        )
    )

    assert len(totals) == 2

    names = {
        row["subject_name"]
        for row in totals
    }

    assert names == {
        "English",
        "Security",
    }


def test_daily_totals_include_empty_days(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    subject_id = create_subject(
        name="English",
        database_path=database,
    )

    session_id = (
        create_study_session(
            subject_id=subject_id,
            session_date="2026-09-12",
            planned_minutes=30,
            database_path=database,
        )
    )

    add_study_time(
        session_id,
        900,
        database_path=database,
    )

    totals = (
        get_study_daily_totals_between(
            "2026-09-12",
            "2026-09-18",
            database_path=database,
        )
    )

    assert len(totals) == 7

    assert (
        totals[0]["session_date"]
        == "2026-09-12"
    )

    assert (
        totals[0]["planned_minutes"]
        == 30
    )

    assert (
        totals[0]["actual_seconds"]
        == 900
    )

    assert (
        totals[1]["planned_minutes"]
        == 0
    )

    assert (
        totals[1]["actual_seconds"]
        == 0
    )


def test_subject_time_percentage_can_exceed_100(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    subject_id = create_subject(
        name="Security",
        database_path=database,
    )

    session_id = (
        create_study_session(
            subject_id=subject_id,
            session_date="2026-09-12",
            planned_minutes=30,
            database_path=database,
        )
    )

    add_study_time(
        session_id,
        3600,
        database_path=database,
    )

    totals = (
        get_study_subject_totals_between(
            "2026-09-12",
            "2026-09-18",
            database_path=database,
        )
    )

    assert (
        totals[0]["time_percentage"]
        == 200
    )