"""
SQLite query script to describe system table columns.

Purpose
- Return column metadata for a named table in system.db.
- Support registry validation and schema discovery workflows.

Contract
- Requires payload.table_name.
- actor_id is required for audit logging.
- Returns columns in SQLite table order when the table exists.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.sql_command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted.database_management.orm_session import (
    build_sqlite_engine,
    system_db_path,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _require_payload(payload: dict, command_name: str) -> dict:
    """
    Require and validate the nested payload object.

    Args:
        payload (dict): Command payload containing a nested payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: Nested payload dictionary.

    Raises:
        PayloadError: If the payload is missing or invalid.
    """

    raw_payload = payload.get("payload")
    if not isinstance(raw_payload, dict):
        raise PayloadError(
            code="payload_invalid",
            details={
                "command_name": command_name,
                "field": "payload",
                "expected": "object",
                "payload_type": type(raw_payload).__name__,
            },
        )
    return raw_payload


def _describe_table(db_path: Path, table_name: str) -> tuple[bool, list[str]]:
    """
    Describe table columns for a SQLite database.

    Args:
        db_path (Path): SQLite database path.
        table_name (str): Table name to inspect.

    Returns:
        tuple[bool, list[str]]: Existence flag and column name list.

    Contract:
        - Columns are returned in SQLite table order.
        - Returns (False, []) when the table does not exist.

    Raises:
        Exception: Propagates database inspection errors.
    """

    engine = build_sqlite_engine(db_path, must_exist=True)
    try:
        inspector = inspect(engine)
        if not inspector.has_table(table_name):
            return False, []
        columns = [column["name"] for column in inspector.get_columns(table_name)]
        return True, columns
    finally:
        engine.dispose()


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Describe a system table and return its column list.

    Args:
        payload (dict): Command payload containing payload.table_name.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing table existence and columns.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        require_string(payload, "actor_id", command_name)
        raw_payload = _require_payload(payload, command_name)
        table_name = require_string(raw_payload, "table_name", command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    db_path = system_db_path(repo_root)
    if not db_path.exists():
        return error_result(
            code="db_missing",
            meaning="System database does not exist.",
            details={
                "command_name": command_name,
                "db_path": str(db_path),
            },
        )

    try:
        exists, columns = _describe_table(db_path, table_name)
        return ok_result(
            output={
                "table_name": table_name,
                "exists": exists,
                "columns": columns,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
