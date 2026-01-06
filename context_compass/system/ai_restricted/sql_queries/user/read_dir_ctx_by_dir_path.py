"""
SQLite query script to read dir_ctx payloads by dir_path.

Purpose
- Load dir_ctx payloads using directory path identifiers.
- Return a complete dir_ctx payload reconstructed from relational tables.

Contract
- Requires payload.branch_name and payload.dir_path.
- Returns record payload and exists flag.
- Errors when the SQLite database is missing.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    user_db_path,
)
from context_compass.system.ai_restricted.sql_queries.user._dir_ctx_payloads import (
    load_dir_ctx_snapshot,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a dir_ctx payload by dir_path.

    Args:
        payload (dict): Command payload containing payload.branch_name/dir_path.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing dir_ctx payload and existence flag.

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
        branch_name = require_string(raw_payload, "branch_name", command_name)
        dir_path = require_string(raw_payload, "dir_path", command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    db_path = user_db_path(repo_root)
    if not db_path.exists():
        return error_result(
            code="db_missing",
            meaning="User database does not exist.",
            details={
                "command_name": command_name,
                "db_path": str(db_path),
            },
        )

    try:
        with sqlite_session(db_path, must_exist=True) as session:
            record_payload, record_exists = load_dir_ctx_snapshot(
                session, branch_name, dir_path
            )
        return ok_result(
            output={
                "branch_name": branch_name,
                "dir_path": dir_path,
                "record": record_payload,
                "exists": record_exists,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
