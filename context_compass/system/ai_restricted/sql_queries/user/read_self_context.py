"""
SQLite query script to read self_context payloads.

Purpose
- Load self_context payloads by agent_id.
- Return a complete payload reconstructed from normalized tables.

Contract
- Requires payload.agent_id.
- actor_id is required for audit logging.
- Returns record payload and exists flag.
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
from context_compass.system.ai_restricted.sql_queries.user._self_context_payloads import (
    load_self_context_snapshot,
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
    Read a self_context payload by agent_id.

    Args:
        payload (dict): Command payload containing payload.agent_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing self_context payload and existence flag.

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
        agent_id = require_string(raw_payload, "agent_id", command_name)
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
            record_payload, record_exists = load_self_context_snapshot(session, agent_id)
        if not isinstance(record_payload, dict):
            return error_result(
                code="payload_invalid",
                meaning="self_context record returned invalid payload.",
                details={
                    "command_name": command_name,
                    "agent_id": agent_id,
                    "payload_type": type(record_payload).__name__,
                },
            )
        return ok_result(
            output={
                "agent_id": agent_id,
                "record": record_payload,
                "exists": record_exists,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
