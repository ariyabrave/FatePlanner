from pathlib import Path

from fateplanner.database import (
    connection,
)


def clear_path_environment(
    monkeypatch,
):
    for name in (
        "FATEPLANNER_DATA_DIR",
        "FATEPLANNER_DB_PATH",
        "APPDATA",
        "LOCALAPPDATA",
        "XDG_DATA_HOME",
    ):
        monkeypatch.delenv(
            name,
            raising=False,
        )


def test_windows_uses_appdata(
    tmp_path,
    monkeypatch,
):
    clear_path_environment(
        monkeypatch
    )

    roaming = (
        tmp_path
        / "Roaming"
    )

    monkeypatch.setenv(
        "APPDATA",
        str(roaming),
    )

    monkeypatch.setattr(
        connection,
        "_platform_name",
        lambda: "win32",
    )

    assert (
        connection.get_app_data_directory()
        == roaming / "FatePlanner"
    )

    assert (
        connection.get_database_path()
        == (
            roaming
            / "FatePlanner"
            / "fateplanner.db"
        )
    )


def test_linux_uses_xdg_data_home(
    tmp_path,
    monkeypatch,
):
    clear_path_environment(
        monkeypatch
    )

    data_home = (
        tmp_path
        / "share"
    )

    monkeypatch.setenv(
        "XDG_DATA_HOME",
        str(data_home),
    )

    monkeypatch.setattr(
        connection,
        "_platform_name",
        lambda: "linux",
    )

    assert (
        connection.get_app_data_directory()
        == (
            data_home
            / "FatePlanner"
        )
    )


def test_custom_data_directory_wins(
    tmp_path,
    monkeypatch,
):
    clear_path_environment(
        monkeypatch
    )

    custom = (
        tmp_path
        / "custom-data"
    )

    monkeypatch.setenv(
        "FATEPLANNER_DATA_DIR",
        str(custom),
    )

    assert (
        connection.get_app_data_directory()
        == custom
    )

    assert (
        connection.get_database_path()
        == (
            custom
            / "fateplanner.db"
        )
    )


def test_database_override_wins(
    tmp_path,
    monkeypatch,
):
    clear_path_environment(
        monkeypatch
    )

    database = (
        tmp_path
        / "custom.db"
    )

    monkeypatch.setenv(
        "FATEPLANNER_DB_PATH",
        str(database),
    )

    assert (
        connection.get_database_path()
        == database
    )


def test_legacy_data_is_copied_safely(
    tmp_path,
    monkeypatch,
):
    clear_path_environment(
        monkeypatch
    )

    legacy = (
        tmp_path
        / "legacy"
    )

    destination = (
        tmp_path
        / "new-data"
    )

    legacy.mkdir()

    old_database = (
        legacy
        / "fateplanner.db"
    )

    old_database.write_bytes(
        b"legacy-database"
    )

    old_backups = (
        legacy
        / "backups"
    )

    old_backups.mkdir()

    (
        old_backups
        / "old-backup.db"
    ).write_bytes(
        b"legacy-backup"
    )

    monkeypatch.setattr(
        connection,
        "LEGACY_APP_DATA_DIR",
        legacy,
    )

    monkeypatch.setattr(
        connection,
        "get_app_data_directory",
        lambda: destination,
    )

    migrated = (
        connection.migrate_legacy_app_data()
    )

    assert migrated is True

    assert (
        destination
        / "fateplanner.db"
    ).read_bytes() == (
        b"legacy-database"
    )

    assert (
        destination
        / "backups"
        / "old-backup.db"
    ).read_bytes() == (
        b"legacy-backup"
    )

    # Migration is copy-only. The legacy data
    # remains untouched as a safety fallback.
    assert old_database.exists()

    # Once the destination DB exists, another
    # migration must not overwrite anything.
    assert (
        connection.migrate_legacy_app_data()
        is False
    )
