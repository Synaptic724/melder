"""
Load ctx artifact output configuration from user-scoped SQLite.

Purpose
- Provide a runtime configuration toggle for emitting ctx JSON artifacts.
- Keep the default behavior as SQLite-only unless explicitly enabled.

Contract
- Configuration lives in user.db under config_ctx_artifact_output_core.
- config_id=1 must exist when the config is seeded.
- Missing databases or tables raise explicit errors.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management.orm_session import user_db_path


def default_ctx_artifact_output() -> dict:
    """
    Return default ctx artifact output settings.

    Returns:
        dict: Default configuration payload.
    """

    return {
        "schema_version": 1,
        "emit_to_repo": False,
        "emit_file_ctx": False,
        "emit_dir_ctx": False,
        "emit_architecture_context": False,
        "emit_component_contexts": False,
        "notes": None,
    }


CONFIG_TABLE = "config_ctx_artifact_output_core"
CONFIG_ACTION = "by_config_id"
CONFIG_ID = 1
CONFIG_ACTOR_ID = "system:ctx_artifact_output"


def _raise_crud_error(exc: sqlite_crud.SqliteCrudError, db_path: Path) -> None:
    """
    Raise a consistent error for CRUD lookup failures.

    Args:
        exc (sqlite_crud.SqliteCrudError): CRUD error to map.
        db_path (Path): User database path for error context.

    Raises:
        FileNotFoundError: If user.db is missing.
        RuntimeError: If required tables or records are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    if exc.code == "db_missing":
        raise FileNotFoundError(f"User database not found: {db_path}") from exc
    if exc.code in {"table_missing", "table_not_registered", "action_not_registered", "registry_missing"}:
        raise RuntimeError("Missing configuration tables in user.db.") from exc
    if exc.code == "record_not_found":
        raise RuntimeError("Missing config_ctx_artifact_output_core row for config_id=1.") from exc
    raise exc


def load_ctx_artifact_output(repo_root: Path) -> dict:
    """
    Load ctx artifact output configuration from SQLite with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Configuration payload.

    Raises:
        FileNotFoundError: If the user database is missing.
        RuntimeError: If required tables or config rows are missing.
        ValueError: If configuration values are invalid.
    """

    db_path = user_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=CONFIG_TABLE,
                action=CONFIG_ACTION,
                payload={"config_id": CONFIG_ID},
                actor_id=CONFIG_ACTOR_ID,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(exc, db_path)

    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_ctx_artifact_output_core read returned an invalid record payload.")

    config = default_ctx_artifact_output()
    config["schema_version"] = record.get("schema_version")
    config["emit_to_repo"] = bool(record.get("emit_to_repo"))
    config["emit_file_ctx"] = bool(record.get("emit_file_ctx"))
    config["emit_dir_ctx"] = bool(record.get("emit_dir_ctx"))
    config["emit_architecture_context"] = bool(record.get("emit_architecture_context"))
    config["emit_component_contexts"] = bool(record.get("emit_component_contexts"))
    config["notes"] = record.get("notes")

    if not isinstance(config["schema_version"], int):
        raise ValueError("config_ctx_artifact_output_core.schema_version must be an integer.")
    if config["notes"] is not None and not isinstance(config["notes"], str):
        raise ValueError("config_ctx_artifact_output_core.notes must be a string or null.")
    return config
