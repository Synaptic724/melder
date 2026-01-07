"""
SQLite query script to list file_ctx payloads for a branch.

Purpose
- Return all file_ctx payloads stored for a branch.
- Provide a stable list of file_ctx payloads for downstream filtering.

Contract
- Requires payload.branch_name.
- Returns records as a list of file_ctx payloads.
- Errors when the SQLite database is missing.
"""

from __future__ import annotations

from pathlib import Path

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
    sqlite_session,
    user_db_path,
)
from context_compass.system.ai_restricted.sql_queries.user._file_ctx_payloads import (
    list_file_ctx_payloads,
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

    Contract:
        - Always returns a dict when validation succeeds.
        - Does not mutate the input payload.
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
    List file_ctx payloads for a branch.

    Args:
        payload (dict): Command payload containing payload.branch_name.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing file_ctx payload records.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires actor_id in the outer payload for audit logging.
        - Requires payload.branch_name for branch scoping.
        - Returns records as a list in output.records.
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
            records = list_file_ctx_payloads(session, branch_name)
        return ok_result(
            output={
                "branch_name": branch_name,
                "records": records,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
