import pytest

from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.task_service import (
    create_task,
    delete_task,
    get_task_progress,
    get_tasks,
    set_task_completed,
)


@pytest.fixture
def database(tmp_path):
    database_path = (
        tmp_path / "test_fateplanner.db"
    )

    initialize_database(database_path)

    return database_path


def test_create_task(database):
    task_id = create_task(
        title="Study English",
        description="Chapter 3",
        priority="high",
        database_path=database,
    )

    assert task_id > 0

    tasks = get_tasks(
        database_path=database
    )

    assert len(tasks) == 1

    assert (
        tasks[0]["title"]
        == "Study English"
    )

    assert (
        tasks[0]["priority"]
        == "high"
    )


def test_empty_title_is_rejected(
    database,
):
    with pytest.raises(ValueError):
        create_task(
            title="   ",
            database_path=database,
        )


def test_complete_task(database):
    task_id = create_task(
        title="Workout",
        database_path=database,
    )

    set_task_completed(
        task_id,
        True,
        database_path=database,
    )

    tasks = get_tasks(
        database_path=database
    )

    assert (
        tasks[0]["completed"]
        == 1
    )


def test_delete_task(database):
    task_id = create_task(
        title="Temporary task",
        database_path=database,
    )

    delete_task(
        task_id,
        database_path=database,
    )

    tasks = get_tasks(
        database_path=database
    )

    assert tasks == []


def test_progress(database):
    task_one = create_task(
        title="Task 1",
        database_path=database,
    )

    create_task(
        title="Task 2",
        database_path=database,
    )

    create_task(
        title="Task 3",
        database_path=database,
    )

    create_task(
        title="Task 4",
        database_path=database,
    )

    set_task_completed(
        task_one,
        True,
        database_path=database,
    )

    total, completed, percentage = (
        get_task_progress(
            database_path=database
        )
    )

    assert total == 4
    assert completed == 1
    assert percentage == 25