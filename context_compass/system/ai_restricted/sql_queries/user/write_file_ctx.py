"""
SQLite query script to persist file_ctx payloads.

Purpose
- Persist file_ctx payloads across core and child tables.
- Return the stored file_ctx payload after the write.

Contract
- Requires payload.branch_name, payload.file_ctx, and payload.exists.
- file_ctx must be a JSON object with kind "file_ctx".
- Writes are performed within the SQLite transaction scope.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
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
from context_compass.system.ai_restricted.sql_queries.user._file_ctx_payloads import (
    load_file_ctx_snapshot,
    persist_file_ctx_payload,
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


def _require_file_ctx(raw_payload: dict, command_name: str) -> dict:
    """
    Require the file_ctx payload object.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: file_ctx payload.

    Raises:
        PayloadError: If file_ctx is missing or invalid.
    """

    file_ctx = raw_payload.get("file_ctx")
    if not isinstance(file_ctx, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "file_ctx",
                "expected": "object",
                "payload_type": type(file_ctx).__name__,
            },
        )
    return file_ctx


def _extract_file_path(file_ctx: dict, command_name: str) -> str:
    """
    Extract file_path from a file_ctx payload.

    Args:
        file_ctx (dict): file_ctx payload.
        command_name (str): Command name for error context.

    Returns:
        str: file_path string.

    Raises:
        PayloadError: If identity.path is missing or invalid.
    """

    identity = file_ctx.get("identity")
    if not isinstance(identity, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "file_ctx.identity",
                "expected": "object",
                "payload_type": type(identity).__name__,
            },
        )
    file_path = identity.get("path")
    if not isinstance(file_path, str) or not file_path:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "file_ctx.identity.path",
                "expected": "non-empty string",
            },
        )
    return file_path


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist a file_ctx payload to SQLite.

    Args:
        payload (dict): Command payload containing payload.branch_name/file_ctx.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the stored file_ctx payload.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        actor_id = require_string(payload, "actor_id", command_name)
        raw_payload = _require_payload(payload, command_name)
        branch_name = require_string(raw_payload, "branch_name", command_name)
        exists = require_bool(raw_payload, "exists", command_name)
        file_ctx = _require_file_ctx(raw_payload, command_name)
        file_path = _extract_file_path(file_ctx, command_name)
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
        _ = exists
        with sqlite_session(db_path, must_exist=True) as session:
            persist_file_ctx_payload(session, branch_name, file_ctx, actor_id)
            record_payload, record_exists = load_file_ctx_snapshot(
                session, branch_name, file_path
            )
        return ok_result(
            output={
                "branch_name": branch_name,
                "record": record_payload,
                "exists": record_exists,
            }
        )
    except ValueError as exc:
        return error_result(
            code="payload_value_error",
            meaning="Invalid file_ctx payload.",
            details={
                "command_name": command_name,
                "branch_name": branch_name,
                "error": str(exc),
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)
