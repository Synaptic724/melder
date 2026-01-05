"""
Load source root configuration for prod and test directories.

Contract
- Loads source roots from SQLite system.db.
- Fails fast if system.db or required tables are missing.
"""

from pathlib import Path
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management.orm_session import system_db_path


CONFIG_SOURCE_ROOTS_CORE_TABLE = "config_source_roots_core"
CONFIG_SOURCE_ROOTS_ENTRIES_TABLE = "config_source_roots_entries"
CONFIG_SOURCE_ROOTS_ACTION = "by_config_id"
CONFIG_SOURCE_ROOTS_ID = 1
CONFIG_ACTOR_ID = "system:source_roots"


def default_source_roots() -> dict:
    """
    Return default source root configuration.

    Returns:
        dict: Default source root payload.

    Contract:
        - Returns a new dict on each call (no shared mutation).
    """
    return {"schema_version": 1, "prod_roots": [], "test_roots": [], "notes": None}


def _load_root_entries(
    entries: list[dict],
    root_type: str,
) -> list[str]:
    """
    Extract ordered root paths for a given root type.

    Args:
        entries (list[dict]): Source root records.
        root_type (str): Root type to filter ("prod" or "test").

    Returns:
        list[str]: Ordered list of root paths.
    """

    filtered = [entry for entry in entries if entry.get("root_type") == root_type]
    filtered.sort(
        key=lambda entry: (
            entry.get("position") is None,
            entry.get("position") if entry.get("position") is not None else 0,
            entry.get("root_path") or "",
        )
    )
    return [entry.get("root_path") for entry in filtered if entry.get("root_path")]


def _raise_crud_error(exc: sqlite_crud.SqliteCrudError, db_path: Path, message: str) -> None:
    """
    Raise a consistent error for CRUD lookup failures.

    Args:
        exc (sqlite_crud.SqliteCrudError): CRUD error to map.
        db_path (Path): System database path for error context.
        message (str): Message to use for missing record cases.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or records are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    if exc.code == "db_missing":
        raise FileNotFoundError(f"System database not found: {db_path}") from exc
    if exc.code in {"table_missing", "table_not_registered", "action_not_registered", "registry_missing"}:
        raise RuntimeError("Missing source root configuration tables in system.db.") from exc
    if exc.code == "record_not_found":
        raise RuntimeError(message) from exc
    raise exc


def _read_core_record(repo_root: Path, actor_id: str) -> dict:
    """
    Read the source root core record from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Source root core record.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or the core record are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=CONFIG_SOURCE_ROOTS_CORE_TABLE,
                action=CONFIG_SOURCE_ROOTS_ACTION,
                payload={"config_id": CONFIG_SOURCE_ROOTS_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing config_source_roots_core row for config_id=1.",
        )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_source_roots_core read returned an invalid record payload.")
    return record


def _read_entry_records(repo_root: Path, actor_id: str) -> list[dict]:
    """
    Read source root entry records from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Source root entry records.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=CONFIG_SOURCE_ROOTS_ENTRIES_TABLE,
                action=CONFIG_SOURCE_ROOTS_ACTION,
                payload={"config_id": CONFIG_SOURCE_ROOTS_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing config_source_roots_entries rows for config_id=1.",
        )
    records = response.output.get("result", {}).get("records")
    if not isinstance(records, list):
        raise ValueError("config_source_roots_entries read returned an invalid record payload.")
    return [record for record in records if isinstance(record, dict)]


def load_source_roots(repo_root: Path) -> dict:
    """
    Load source root configuration with defaults applied.

    Contract:
    - SQLite is the source of truth for source roots.
    - system.db and required tables must exist for SQLite loads.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Source roots payload.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or core rows are missing.
    """

    actor_id = CONFIG_ACTOR_ID
    core = _read_core_record(repo_root, actor_id)
    entries = _read_entry_records(repo_root, actor_id)

    schema_version = core.get("schema_version")
    notes = core.get("notes")
    if not isinstance(schema_version, int):
        raise ValueError("config_source_roots_core.schema_version must be an integer.")
    if notes is not None and not isinstance(notes, str):
        raise ValueError("config_source_roots_core.notes must be a string or null.")

    return {
        "schema_version": schema_version,
        "prod_roots": _load_root_entries(entries, "prod"),
        "test_roots": _load_root_entries(entries, "test"),
        "notes": notes,
    }
