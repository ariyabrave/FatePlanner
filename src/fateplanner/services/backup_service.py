import csv
import json
import sqlite3

from datetime import datetime
from pathlib import Path

from fateplanner.database.connection import (
    get_database_path,
    get_connection,
)


REQUIRED_TABLES = {
    "tasks",
    "habits",
    "habit_logs",
    "study_subjects",
    "study_sessions",
    "study_timer_state",
    "finance_categories",
    "finance_transactions",
    "finance_budgets",
    "savings_goals",
    "savings_entries",
}


EXPORT_TABLES = [
    "tasks",
    "habits",
    "habit_logs",
    "study_subjects",
    "study_sessions",
    "study_timer_state",
    "finance_categories",
    "finance_transactions",
    "finance_budgets",
    "savings_goals",
    "savings_entries",
]


def _resolve_database_path(
    database_path: str | Path | None = None,
) -> Path:
    if database_path is not None:
        return Path(
            database_path
        )

    return Path(
        get_database_path()
    )


def get_backup_directory(
    database_path: str | Path | None = None,
) -> Path:
    database = _resolve_database_path(
        database_path
    )

    backup_directory = (
        database.parent
        / "backups"
    )

    backup_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return backup_directory


def _unique_path(
    path: Path,
) -> Path:
    if not path.exists():
        return path

    counter = 1

    while True:
        candidate = (
            path.with_name(
                f"{path.stem}-{counter}"
                f"{path.suffix}"
            )
        )

        if not candidate.exists():
            return candidate

        counter += 1


def validate_database(
    database_path: str | Path,
) -> dict:
    path = Path(
        database_path
    )

    if not path.exists():
        return {
            "valid": False,
            "integrity": (
                "File does not exist."
            ),
            "missing_tables": sorted(
                REQUIRED_TABLES
            ),
            "tables": [],
        }

    try:
        connection = sqlite3.connect(
            path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        integrity_row = (
            connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()
        )

        integrity = (
            integrity_row[0]
            if integrity_row
            else "unknown"
        )

        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """
        ).fetchall()

        tables = {
            row["name"]
            for row in rows
        }

        connection.close()

    except sqlite3.DatabaseError as error:
        return {
            "valid": False,
            "integrity": str(
                error
            ),
            "missing_tables": sorted(
                REQUIRED_TABLES
            ),
            "tables": [],
        }

    missing = (
        REQUIRED_TABLES
        - tables
    )

    return {
        "valid": (
            integrity == "ok"
            and not missing
        ),
        "integrity": integrity,
        "missing_tables": sorted(
            missing
        ),
        "tables": sorted(
            tables
        ),
    }


def _assert_valid_database(
    database_path: str | Path,
) -> None:
    result = validate_database(
        database_path
    )

    if not result["valid"]:
        missing = ", ".join(
            result[
                "missing_tables"
            ]
        )

        message = (
            "Database validation failed."
        )

        if (
            result["integrity"]
            != "ok"
        ):
            message += (
                " Integrity check: "
                f"{result['integrity']}."
            )

        if missing:
            message += (
                " Missing tables: "
                f"{missing}."
            )

        raise ValueError(
            message
        )


def create_backup(
    destination_path: str | Path | None = None,
    *,
    database_path: str | Path | None = None,
    prefix: str = "fateplanner",
) -> Path:
    source_path = (
        _resolve_database_path(
            database_path
        )
    )

    if not source_path.exists():
        raise ValueError(
            "FatePlanner database "
            "does not exist."
        )

    if destination_path is None:
        timestamp = (
            datetime.now()
            .strftime(
                "%Y%m%d-%H%M%S"
            )
        )

        destination = (
            get_backup_directory(
                database_path
            )
            / (
                f"{prefix}-"
                f"{timestamp}.db"
            )
        )

    else:
        destination = Path(
            destination_path
        )

        if (
            destination.suffix.lower()
            != ".db"
        ):
            destination = (
                destination.with_suffix(
                    ".db"
                )
            )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = _unique_path(
        destination
    )

    if (
        source_path.resolve()
        == destination.resolve()
    ):
        raise ValueError(
            "Backup destination cannot "
            "be the live database."
        )

    with get_connection(
        database_path
    ) as source:

        destination_connection = (
            sqlite3.connect(
                destination
            )
        )

        try:
            source.backup(
                destination_connection
            )

            destination_connection.commit()

        finally:
            destination_connection.close()

    try:
        _assert_valid_database(
            destination
        )

    except Exception:
        destination.unlink(
            missing_ok=True
        )

        raise

    return destination


def get_backup_files(
    database_path: str | Path | None = None,
) -> list[Path]:
    directory = (
        get_backup_directory(
            database_path
        )
    )

    backups = [
        path
        for path in directory.glob(
            "*.db"
        )
        if path.is_file()
    ]

    return sorted(
        backups,
        key=lambda path:
            path.stat().st_mtime,
        reverse=True,
    )


def create_automatic_backup(
    *,
    database_path: str | Path | None = None,
    keep: int = 10,
) -> Path:
    keep = max(
        1,
        int(
            keep
        ),
    )

    directory = (
        get_backup_directory(
            database_path
        )
    )

    today = (
        datetime.now()
        .strftime(
            "%Y%m%d"
        )
    )

    existing = sorted(
        directory.glob(
            f"auto-{today}-*.db"
        )
    )

    if existing:
        return existing[-1]

    backup = create_backup(
        database_path=database_path,
        prefix="auto",
    )

    automatic_backups = sorted(
        directory.glob(
            "auto-*.db"
        ),
        key=lambda path:
            path.stat().st_mtime,
        reverse=True,
    )

    for old_backup in (
        automatic_backups[
            keep:
        ]
    ):
        old_backup.unlink(
            missing_ok=True
        )

    return backup


def _restore_from_source(
    source_path: Path,
    destination_path: Path,
) -> None:
    source_connection = (
        sqlite3.connect(
            source_path
        )
    )

    destination_connection = (
        sqlite3.connect(
            destination_path
        )
    )

    try:
        source_connection.backup(
            destination_connection
        )

        destination_connection.commit()

    finally:
        source_connection.close()
        destination_connection.close()


def restore_database(
    backup_path: str | Path,
    *,
    database_path: str | Path | None = None,
    create_safety_backup: bool = True,
) -> Path | None:
    source = Path(
        backup_path
    )

    target = _resolve_database_path(
        database_path
    )

    if not source.exists():
        raise ValueError(
            "Backup file does not exist."
        )

    if (
        source.resolve()
        == target.resolve()
    ):
        raise ValueError(
            "Cannot restore the live "
            "database from itself."
        )

    _assert_valid_database(
        source
    )

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    safety_backup = None

    if (
        create_safety_backup
        and target.exists()
    ):
        safety_backup = create_backup(
            database_path=database_path,
            prefix="pre-restore",
        )

    try:
        _restore_from_source(
            source,
            target,
        )

        _assert_valid_database(
            target
        )

    except Exception:
        if (
            safety_backup is not None
            and safety_backup.exists()
        ):
            _restore_from_source(
                safety_backup,
                target,
            )

        raise

    return safety_backup


def _existing_export_tables(
    connection,
) -> list[str]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()

    existing = {
        row["name"]
        for row in rows
    }

    return [
        table
        for table in EXPORT_TABLES
        if table in existing
    ]


def export_json(
    destination_path: str | Path,
    *,
    database_path: str | Path | None = None,
) -> Path:
    destination = Path(
        destination_path
    )

    if (
        destination.suffix.lower()
        != ".json"
    ):
        destination = (
            destination.with_suffix(
                ".json"
            )
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with get_connection(
        database_path
    ) as connection:

        tables = (
            _existing_export_tables(
                connection
            )
        )

        data = {
            "format": (
                "FatePlanner JSON Export"
            ),
            "exported_at": (
                datetime.now()
                .isoformat(
                    timespec="seconds"
                )
            ),
            "tables": {},
        }

        for table in tables:
            rows = connection.execute(
                f"""
                SELECT *
                FROM "{table}"
                ORDER BY rowid ASC
                """
            ).fetchall()

            data["tables"][
                table
            ] = [
                dict(
                    row
                )
                for row in rows
            ]

    with destination.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return destination


def export_csv_bundle(
    destination_directory: str | Path,
    *,
    database_path: str | Path | None = None,
) -> Path:
    parent = Path(
        destination_directory
    )

    parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d-%H%M%S"
        )
    )

    export_directory = (
        parent
        / (
            "FatePlanner-CSV-"
            f"{timestamp}"
        )
    )

    export_directory = (
        _unique_path(
            export_directory
        )
    )

    export_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    with get_connection(
        database_path
    ) as connection:

        tables = (
            _existing_export_tables(
                connection
            )
        )

        for table in tables:
            rows = connection.execute(
                f"""
                SELECT *
                FROM "{table}"
                ORDER BY rowid ASC
                """
            ).fetchall()

            columns = [
                row["name"]
                for row in (
                    connection.execute(
                        f"""
                        PRAGMA table_info(
                            "{table}"
                        )
                        """
                    ).fetchall()
                )
            ]

            csv_path = (
                export_directory
                / f"{table}.csv"
            )

            with csv_path.open(
                "w",
                encoding="utf-8-sig",
                newline="",
            ) as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=columns,
                )

                writer.writeheader()

                for row in rows:
                    writer.writerow(
                        dict(
                            row
                        )
                    )

    manifest = (
        export_directory
        / "manifest.json"
    )

    with manifest.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "format": (
                    "FatePlanner CSV Export"
                ),
                "exported_at": (
                    datetime.now()
                    .isoformat(
                        timespec="seconds"
                    )
                ),
                "tables": tables,
            },
            file,
            ensure_ascii=False,
            indent=2,
        )

    return export_directory