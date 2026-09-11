import pytest

from fateplanner.database.connection import (
    initialize_database,
)
from fateplanner.services.task_service import (
    create_subtask,
    create_task,
    delete_task,
    get_subtask_progress,
    get_subtasks,
    get_task,
    get_task_progress,
    get_task_progress_for_date,
    get_tasks,
    get_tasks_for_date,
    set_task_completed,
    update_task,
)


@pytest.fixture
def database(
    tmp_path,
):
    database_path = (
        tmp_path
        / "test_fateplanner.db"
    )

    initialize_database(
        database_path
    )

    return database_path


def test_create_task(
    database,
):
    task_id = create_task(
        title="Study English",
        description="Chapter 3",
        priority="high",
        database_path=database,
    )

    assert task_id > 0

    task = get_task(
        task_id,
        database_path=database,
    )

    assert task["title"] == (
        "Study English"
    )

    assert task["priority"] == (
        "high"
    )


def test_empty_title_is_rejected(
    database,
):
    with pytest.raises(
        ValueError
    ):
        create_task(
            title="   ",
            database_path=database,
        )


def test_update_task(
    database,
):
    task_id = create_task(
        title="Old title",
        database_path=database,
    )

    update_task(
        task_id=task_id,
        title="New title",
        description="Updated",
        priority="high",
        database_path=database,
    )

    task = get_task(
        task_id,
        database_path=database,
    )

    assert (
        task["title"]
        == "New title"
    )

    assert (
        task["description"]
        == "Updated"
    )

    assert (
        task["priority"]
        == "high"
    )


def test_create_subtask(
    database,
):
    parent_id = create_task(
        title="Main task",
        database_path=database,
    )

    subtask_id = create_subtask(
        parent_id=parent_id,
        title="Subtask 1",
        database_path=database,
    )

    assert subtask_id > 0

    subtasks = get_subtasks(
        parent_id,
        database_path=database,
    )

    assert len(subtasks) == 1

    assert (
        subtasks[0]["title"]
        == "Subtask 1"
    )


def test_subtasks_not_in_main_task_list(
    database,
):
    parent_id = create_task(
        title="Parent",
        database_path=database,
    )

    create_subtask(
        parent_id=parent_id,
        title="Child",
        database_path=database,
    )

    tasks = get_tasks(
        database_path=database
    )

    assert len(tasks) == 1

    assert (
        tasks[0]["title"]
        == "Parent"
    )


def test_parent_completion_cascades(
    database,
):
    parent_id = create_task(
        title="Parent",
        database_path=database,
    )

    create_subtask(
        parent_id=parent_id,
        title="Child 1",
        database_path=database,
    )

    create_subtask(
        parent_id=parent_id,
        title="Child 2",
        database_path=database,
    )

    set_task_completed(
        parent_id,
        True,
        database_path=database,
    )

    subtasks = get_subtasks(
        parent_id,
        database_path=database,
    )

    assert all(
        task["completed"] == 1
        for task in subtasks
    )


def test_subtasks_complete_parent(
    database,
):
    parent_id = create_task(
        title="Parent",
        database_path=database,
    )

    child_one = create_subtask(
        parent_id=parent_id,
        title="One",
        database_path=database,
    )

    child_two = create_subtask(
        parent_id=parent_id,
        title="Two",
        database_path=database,
    )

    set_task_completed(
        child_one,
        True,
        database_path=database,
    )

    parent = get_task(
        parent_id,
        database_path=database,
    )

    assert (
        parent["completed"]
        == 0
    )

    set_task_completed(
        child_two,
        True,
        database_path=database,
    )

    parent = get_task(
        parent_id,
        database_path=database,
    )

    assert (
        parent["completed"]
        == 1
    )


def test_unchecking_subtask_reopens_parent(
    database,
):
    parent_id = create_task(
        title="Parent",
        database_path=database,
    )

    child = create_subtask(
        parent_id=parent_id,
        title="Child",
        database_path=database,
    )

    set_task_completed(
        child,
        True,
        database_path=database,
    )

    assert (
        get_task(
            parent_id,
            database_path=database,
        )["completed"]
        == 1
    )

    set_task_completed(
        child,
        False,
        database_path=database,
    )

    assert (
        get_task(
            parent_id,
            database_path=database,
        )["completed"]
        == 0
    )


def test_subtask_progress(
    database,
):
    parent_id = create_task(
        title="Parent",
        database_path=database,
    )

    first = create_subtask(
        parent_id=parent_id,
        title="One",
        database_path=database,
    )

    create_subtask(
        parent_id=parent_id,
        title="Two",
        database_path=database,
    )

    set_task_completed(
        first,
        True,
        database_path=database,
    )

    (
        total,
        completed,
        percentage,
    ) = get_subtask_progress(
        parent_id,
        database_path=database,
    )

    assert total == 2
    assert completed == 1
    assert percentage == 50


def test_delete_parent_cascades_subtasks(
    database,
):
    parent_id = create_task(
        title="Parent",
        database_path=database,
    )

    create_subtask(
        parent_id=parent_id,
        title="Child",
        database_path=database,
    )

    delete_task(
        parent_id,
        database_path=database,
    )

    subtasks = get_subtasks(
        parent_id,
        database_path=database,
    )

    assert subtasks == []


def test_complete_task(
    database,
):
    task_id = create_task(
        title="Workout",
        database_path=database,
    )

    set_task_completed(
        task_id,
        True,
        database_path=database,
    )

    task = get_task(
        task_id,
        database_path=database,
    )

    assert (
        task["completed"]
        == 1
    )


def test_delete_task(
    database,
):
    task_id = create_task(
        title="Temporary task",
        database_path=database,
    )

    delete_task(
        task_id,
        database_path=database,
    )

    assert (
        get_task(
            task_id,
            database_path=database,
        )
        is None
    )


def test_progress_ignores_subtasks(
    database,
):
    first = create_task(
        title="Task 1",
        database_path=database,
    )

    second = create_task(
        title="Task 2",
        database_path=database,
    )

    create_subtask(
        parent_id=second,
        title="Subtask",
        database_path=database,
    )

    set_task_completed(
        first,
        True,
        database_path=database,
    )

    (
        total,
        completed,
        percentage,
    ) = get_task_progress(
        database_path=database
    )

    assert total == 2
    assert completed == 1
    assert percentage == 50


def test_get_tasks_for_date(
    database,
):
    create_task(
        title="Today task",
        due_date="2026-09-11",
        start_time="09:00",
        end_time="10:00",
        database_path=database,
    )

    create_task(
        title="Tomorrow task",
        due_date="2026-09-12",
        start_time="09:00",
        end_time="10:00",
        database_path=database,
    )

    tasks = get_tasks_for_date(
        "2026-09-11",
        database_path=database,
    )

    assert len(tasks) == 1

    assert (
        tasks[0]["title"]
        == "Today task"
    )


def test_daily_progress(
    database,
):
    first = create_task(
        title="Task 1",
        due_date="2026-09-11",
        database_path=database,
    )

    create_task(
        title="Task 2",
        due_date="2026-09-11",
        database_path=database,
    )

    set_task_completed(
        first,
        True,
        database_path=database,
    )

    (
        total,
        completed,
        percentage,
    ) = (
        get_task_progress_for_date(
            "2026-09-11",
            database_path=database,
        )
    )

    assert total == 2
    assert completed == 1
    assert percentage == 50


def test_invalid_time_range(
    database,
):
    with pytest.raises(
        ValueError
    ):
        create_task(
            title="Invalid",
            due_date="2026-09-11",
            start_time="15:00",
            end_time="14:00",
            database_path=database,
        )