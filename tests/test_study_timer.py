from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.study_service import (
    add_study_time,
    clear_study_timer_state,
    create_study_session,
    create_subject,
    delete_study_session,
    get_study_session,
    get_study_timer_state,
    save_study_timer_state,
    sync_study_session_completion_from_time,
)


def make_database(
    tmp_path,
):
    database = (
        tmp_path
        / "study_timer.db"
    )

    initialize_database(
        database
    )

    return database


def make_session(
    database,
    planned_minutes=25,
):
    subject_id = create_subject(
        name="Security",
        database_path=database,
    )

    return create_study_session(
        subject_id=subject_id,
        title="Study",
        session_date="2026-09-11",
        planned_minutes=planned_minutes,
        database_path=database,
    )


def test_save_timer_state(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    session_id = make_session(
        database
    )

    save_study_timer_state(
        session_id=session_id,
        phase="focus",
        focus_minutes=25,
        break_minutes=5,
        remaining_seconds=1200,
        pomodoro_count=2,
        is_running=True,
        database_path=database,
    )

    state = get_study_timer_state(
        database_path=database
    )

    assert state is not None

    assert (
        state["session_id"]
        == session_id
    )

    assert (
        state["phase"]
        == "focus"
    )

    assert (
        state["remaining_seconds"]
        == 1200
    )

    assert (
        state["pomodoro_count"]
        == 2
    )

    assert (
        state["is_running"]
        == 1
    )


def test_update_timer_state(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    session_id = make_session(
        database
    )

    save_study_timer_state(
        session_id=session_id,
        phase="focus",
        focus_minutes=25,
        break_minutes=5,
        remaining_seconds=1500,
        pomodoro_count=0,
        is_running=False,
        database_path=database,
    )

    save_study_timer_state(
        session_id=session_id,
        phase="break",
        focus_minutes=50,
        break_minutes=10,
        remaining_seconds=600,
        pomodoro_count=1,
        is_running=False,
        database_path=database,
    )

    state = get_study_timer_state(
        database_path=database
    )

    assert (
        state["phase"]
        == "break"
    )

    assert (
        state["focus_minutes"]
        == 50
    )

    assert (
        state["break_minutes"]
        == 10
    )

    assert (
        state["pomodoro_count"]
        == 1
    )


def test_clear_timer_state(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    session_id = make_session(
        database
    )

    save_study_timer_state(
        session_id=session_id,
        phase="focus",
        focus_minutes=25,
        break_minutes=5,
        remaining_seconds=1500,
        pomodoro_count=0,
        is_running=False,
        database_path=database,
    )

    clear_study_timer_state(
        database_path=database
    )

    assert (
        get_study_timer_state(
            database_path=database
        )
        is None
    )


def test_deleted_session_detaches_timer_state(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    session_id = make_session(
        database
    )

    save_study_timer_state(
        session_id=session_id,
        phase="focus",
        focus_minutes=25,
        break_minutes=5,
        remaining_seconds=1000,
        pomodoro_count=0,
        is_running=False,
        database_path=database,
    )

    delete_study_session(
        session_id,
        database_path=database,
    )

    state = get_study_timer_state(
        database_path=database
    )

    assert state is not None

    assert (
        state["session_id"]
        is None
    )


def test_timer_time_completes_session(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    session_id = make_session(
        database,
        planned_minutes=25,
    )

    add_study_time(
        session_id,
        1500,
        database_path=database,
    )

    completed = (
        sync_study_session_completion_from_time(
            session_id,
            database_path=database,
        )
    )

    assert completed is True

    session = get_study_session(
        session_id,
        database_path=database,
    )

    assert (
        session["completed"]
        == 1
    )


def test_insufficient_time_does_not_complete_session(
    tmp_path,
):
    database = make_database(
        tmp_path
    )

    session_id = make_session(
        database,
        planned_minutes=25,
    )

    add_study_time(
        session_id,
        600,
        database_path=database,
    )

    completed = (
        sync_study_session_completion_from_time(
            session_id,
            database_path=database,
        )
    )

    assert completed is False

    session = get_study_session(
        session_id,
        database_path=database,
    )

    assert (
        session["completed"]
        == 0
    )