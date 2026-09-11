import json

import pytest

from fateplanner.database.connection import (
    get_connection,
    initialize_database,
)
from fateplanner.services.backup_service import (
    create_automatic_backup,
    create_backup,
    export_csv_bundle,
    export_json,
    restore_database,
    validate_database,
)


@pytest.fixture
def database(
    tmp_path,
):
    path = (
        tmp_path
        / "fateplanner.db"
    )

    initialize_database(
        path
    )

    return path


def add_task(
    database,
    title,
):
    with get_connection(
        database
    ) as connection:

        connection.execute(
            """
            INSERT INTO tasks (
                title,
                due_date,
                completed,
                is_recurring_template
            )
            VALUES (?, '2026-09-11', 0, 0)
            """,
            (
                title,
            ),
        )

        connection.commit()


def get_task_titles(
    database,
):
    with get_connection(
        database
    ) as connection:

        rows = connection.execute(
            """
            SELECT title
            FROM tasks
            ORDER BY id
            """
        ).fetchall()

    return [
        row["title"]
        for row in rows
    ]


def test_validate_database(
    database,
):
    result = validate_database(
        database
    )

    assert (
        result["valid"]
        is True
    )

    assert (
        result["integrity"]
        == "ok"
    )


def test_create_backup_preserves_data(
    database,
):
    add_task(
        database,
        "Important task",
    )

    backup = create_backup(
        database_path=database
    )

    assert backup.exists()

    assert (
        validate_database(
            backup
        )["valid"]
        is True
    )

    assert get_task_titles(
        backup
    ) == [
        "Important task"
    ]


def test_automatic_backup_once_per_day(
    database,
):
    first = (
        create_automatic_backup(
            database_path=database
        )
    )

    second = (
        create_automatic_backup(
            database_path=database
        )
    )

    assert first == second

    assert first.exists()


def test_invalid_database_rejected(
    tmp_path,
):
    invalid = (
        tmp_path
        / "broken.db"
    )

    invalid.write_text(
        "not sqlite",
        encoding="utf-8",
    )

    result = validate_database(
        invalid
    )

    assert (
        result["valid"]
        is False
    )


def test_restore_database(
    database,
):
    add_task(
        database,
        "Before backup",
    )

    backup = create_backup(
        database_path=database
    )

    with get_connection(
        database
    ) as connection:

        connection.execute(
            """
            DELETE FROM tasks
            """
        )

        connection.execute(
            """
            INSERT INTO tasks (
                title,
                due_date,
                completed,
                is_recurring_template
            )
            VALUES (
                'After backup',
                '2026-09-11',
                0,
                0
            )
            """
        )

        connection.commit()

    assert get_task_titles(
        database
    ) == [
        "After backup"
    ]

    safety_backup = (
        restore_database(
            backup,
            database_path=database,
        )
    )

    assert (
        safety_backup is not None
    )

    assert (
        safety_backup.exists()
    )

    assert get_task_titles(
        database
    ) == [
        "Before backup"
    ]


def test_json_export(
    database,
    tmp_path,
):
    add_task(
        database,
        "Export me",
    )

    output = export_json(
        tmp_path
        / "export.json",
        database_path=database,
    )

    assert output.exists()

    data = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "tasks"
        in data["tables"]
    )

    titles = [
        row["title"]
        for row in (
            data["tables"][
                "tasks"
            ]
        )
    ]

    assert (
        "Export me"
        in titles
    )


def test_csv_export(
    database,
    tmp_path,
):
    add_task(
        database,
        "CSV task",
    )

    output = (
        export_csv_bundle(
            tmp_path,
            database_path=database,
        )
    )

    assert output.exists()

    tasks_csv = (
        output
        / "tasks.csv"
    )

    assert tasks_csv.exists()

    content = (
        tasks_csv.read_text(
            encoding="utf-8-sig"
        )
    )

    assert (
        "CSV task"
        in content
    )

    assert (
        output
        .joinpath(
            "manifest.json"
        )
        .exists()
    )


def test_restore_rejects_invalid_database(
    database,
    tmp_path,
):
    invalid = (
        tmp_path
        / "invalid.db"
    )

    invalid.write_text(
        "bad database",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError
    ):
        restore_database(
            invalid,
            database_path=database,
        )