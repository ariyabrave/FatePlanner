import pytest

from fateplanner.database.connection import (
    get_connection,
    initialize_database,
)
from fateplanner.services.study_service import (
    add_study_time,
    create_study_session,
    create_subject,
    delete_study_session,
    delete_subject,
    get_study_session,
    get_study_sessions_for_date,
    get_study_stats_for_date,
    get_subject,
    get_subjects,
    set_study_session_completed,
    update_study_session,
    update_subject,
)


@pytest.fixture
def database(
    tmp_path,
):
    path = (
        tmp_path
        / "study.db"
    )

    initialize_database(
        path
    )

    return path


def test_create_subject(
    database,
):
    subject_id = create_subject(
        name="English",
        description="Vocabulary",
        database_path=database,
    )

    subject = get_subject(
        subject_id,
        database_path=database,
    )

    assert subject is not None
    assert subject["name"] == "English"
    assert (
        subject["description"]
        == "Vocabulary"
    )


def test_update_subject(
    database,
):
    subject_id = create_subject(
        name="Old",
        database_path=database,
    )

    update_subject(
        subject_id=subject_id,
        name="New",
        description="Updated",
        database_path=database,
    )

    subject = get_subject(
        subject_id,
        database_path=database,
    )

    assert subject["name"] == "New"

    assert (
        subject["description"]
        == "Updated"
    )


def test_create_study_session(
    database,
):
    subject_id = create_subject(
        name="Math",
        database_path=database,
    )

    session_id = create_study_session(
        subject_id=subject_id,
        title="Chapter 3",
        session_date="2026-09-11",
        planned_minutes=50,
        database_path=database,
    )

    session = get_study_session(
        session_id,
        database_path=database,
    )

    assert session is not None

    assert (
        session["subject_name"]
        == "Math"
    )

    assert (
        session["title"]
        == "Chapter 3"
    )

    assert (
        session["planned_minutes"]
        == 50
    )


def test_filter_sessions_by_date(
    database,
):
    subject_id = create_subject(
        name="English",
        database_path=database,
    )

    create_study_session(
        subject_id=subject_id,
        session_date="2026-09-11",
        planned_minutes=30,
        database_path=database,
    )

    create_study_session(
        subject_id=subject_id,
        session_date="2026-09-12",
        planned_minutes=30,
        database_path=database,
    )

    sessions = (
        get_study_sessions_for_date(
            "2026-09-11",
            database_path=database,
        )
    )

    assert len(sessions) == 1

    assert (
        sessions[0]["session_date"]
        == "2026-09-11"
    )


def test_invalid_planned_time(
    database,
):
    subject_id = create_subject(
        name="Math",
        database_path=database,
    )

    with pytest.raises(
        ValueError
    ):
        create_study_session(
            subject_id=subject_id,
            session_date="2026-09-11",
            planned_minutes=0,
            database_path=database,
        )


def test_complete_study_session(
    database,
):
    subject_id = create_subject(
        name="Math",
        database_path=database,
    )

    session_id = create_study_session(
        subject_id=subject_id,
        session_date="2026-09-11",
        planned_minutes=25,
        database_path=database,
    )

    set_study_session_completed(
        session_id,
        True,
        database_path=database,
    )

    session = get_study_session(
        session_id,
        database_path=database,
    )

    assert (
        session["completed"]
        == 1
    )


def test_add_study_time(
    database,
):
    subject_id = create_subject(
        name="Security",
        database_path=database,
    )

    session_id = create_study_session(
        subject_id=subject_id,
        session_date="2026-09-11",
        planned_minutes=50,
        database_path=database,
    )

    add_study_time(
        session_id,
        600,
        database_path=database,
    )

    add_study_time(
        session_id,
        300,
        database_path=database,
    )

    session = get_study_session(
        session_id,
        database_path=database,
    )

    assert (
        session["actual_seconds"]
        == 900
    )


def test_update_session_preserves_actual_time(
    database,
):
    subject_id = create_subject(
        name="Security",
        database_path=database,
    )

    session_id = create_study_session(
        subject_id=subject_id,
        title="Old",
        session_date="2026-09-11",
        planned_minutes=50,
        database_path=database,
    )

    add_study_time(
        session_id,
        1200,
        database_path=database,
    )

    update_study_session(
        session_id=session_id,
        subject_id=subject_id,
        title="New",
        session_date="2026-09-11",
        planned_minutes=60,
        database_path=database,
    )

    session = get_study_session(
        session_id,
        database_path=database,
    )

    assert session["title"] == "New"

    assert (
        session["planned_minutes"]
        == 60
    )

    assert (
        session["actual_seconds"]
        == 1200
    )


def test_daily_study_stats(
    database,
):
    subject_id = create_subject(
        name="English",
        database_path=database,
    )

    first = create_study_session(
        subject_id=subject_id,
        session_date="2026-09-11",
        planned_minutes=30,
        database_path=database,
    )

    create_study_session(
        subject_id=subject_id,
        session_date="2026-09-11",
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

    stats = get_study_stats_for_date(
        "2026-09-11",
        database_path=database,
    )

    assert (
        stats["total_sessions"]
        == 2
    )

    assert (
        stats["completed_sessions"]
        == 1
    )

    assert (
        stats["planned_minutes"]
        == 90
    )

    assert (
        stats["actual_seconds"]
        == 1800
    )

    assert (
        stats["session_percentage"]
        == 50
    )

    assert (
        stats["time_percentage"]
        == 33
    )


def test_delete_session(
    database,
):
    subject_id = create_subject(
        name="Math",
        database_path=database,
    )

    session_id = create_study_session(
        subject_id=subject_id,
        session_date="2026-09-11",
        planned_minutes=30,
        database_path=database,
    )

    delete_study_session(
        session_id,
        database_path=database,
    )

    assert (
        get_study_session(
            session_id,
            database_path=database,
        )
        is None
    )


def test_delete_subject_cascades_sessions(
    database,
):
    subject_id = create_subject(
        name="Temporary",
        database_path=database,
    )

    create_study_session(
        subject_id=subject_id,
        session_date="2026-09-11",
        planned_minutes=30,
        database_path=database,
    )

    delete_subject(
        subject_id,
        database_path=database,
    )

    assert (
        get_subjects(
            database_path=database
        )
        == []
    )

    with get_connection(
        database
    ) as connection:

        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM study_sessions
            """
        ).fetchone()

    assert row["total"] == 0