"""
SQLite query script to persist dir_ctx payloads.

Purpose
- Persist dir_ctx payloads across core and child tables.
- Return the stored dir_ctx payload after the write.

Contract
- Requires payload.branch_name, payload.dir_ctx, and payload.exists.
- dir_ctx must be a JSON object with kind "dir_ctx".
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
from context_compass.system.ai_restricted.sql_queries.user._dir_ctx_payloads import (
    load_dir_ctx_snapshot,
    persist_dir_ctx_payload,
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


def _require_dir_ctx(raw_payload: dict, command_name: str) -> dict:
    """
    Require the dir_ctx payload object.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: dir_ctx payload.

    Raises:
        PayloadError: If dir_ctx is missing or invalid.
    """

    dir_ctx = raw_payload.get("dir_ctx")
    if not isinstance(dir_ctx, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "dir_ctx",
                "expected": "object",
                "payload_type": type(dir_ctx).__name__,
            },
        )
    return dir_ctx


def _extract_dir_path(dir_ctx: dict, command_name: str) -> str:
    """
    Extract dir_path from a dir_ctx payload.

    Args:
        dir_ctx (dict): dir_ctx payload.
        command_name (str): Command name for error context.

    Returns:
        str: dir_path string.

    Raises:
        PayloadError: If identity.dir_path is missing or invalid.
    """

    identity = dir_ctx.get("identity")
    if not isinstance(identity, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "dir_ctx.identity",
                "expected": "object",
                "payload_type": type(identity).__name__,
            },
        )
    dir_path = identity.get("dir_path")
    if not isinstance(dir_path, str) or not dir_path:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "dir_ctx.identity.dir_path",
                "expected": "non-empty string",
            },
        )
    return dir_path


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist a dir_ctx payload to SQLite.

    Args:
        payload (dict): Command payload containing payload.branch_name/dir_ctx.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the stored dir_ctx payload.

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
        dir_ctx = _require_dir_ctx(raw_payload, command_name)
        dir_path = _extract_dir_path(dir_ctx, command_name)
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
            persist_dir_ctx_payload(session, branch_name, dir_ctx, actor_id)
            record_payload, record_exists = load_dir_ctx_snapshot(
                session, branch_name, dir_path
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
            meaning="Invalid dir_ctx payload.",
            details={
                "command_name": command_name,
                "branch_name": branch_name,
                "error": str(exc),
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)
