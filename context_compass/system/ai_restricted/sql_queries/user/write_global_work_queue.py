"""
SQLite query script to write a global work queue payload.

Purpose
- Persist a global-scoped work queue payload in normalized work_queue tables.
- Return the stored queue payload after the write.

Contract
- Requires payload.bucket, payload.work_type, payload.queue_payload, and payload.exists.
- actor_id is required for audit logging.
- Returns queue payload and an exists flag.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
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
from context_compass.system.ai_restricted.sql_queries.user._global_work_queue_payloads import (
    load_global_queue_snapshot,
    persist_global_queue,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _require_payload(payload: dict, command_name: str) -> dict:
    """
    Require the nested payload object.

    Args:
        payload (dict): Command payload containing nested payload object.
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


def _parse_payload(raw_payload: dict, command_name: str) -> dict:
    """
    Parse and validate queue write fields.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict: Parsed payload values for bucket/work_type/queue_payload/exists.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    bucket = require_string(raw_payload, "bucket", command_name)
    work_type = require_string(raw_payload, "work_type", command_name)
    exists = require_bool(raw_payload, "exists", command_name)
    queue_payload = raw_payload.get("queue_payload")
    if not isinstance(queue_payload, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "queue_payload",
                "expected": "object",
                "payload_type": type(queue_payload).__name__,
            },
        )
    return {
        "bucket": bucket,
        "work_type": work_type,
        "exists": exists,
        "queue_payload": queue_payload,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist a global work queue payload to SQLite.

    Args:
        payload (dict): Command payload containing payload.bucket/work_type/queue_payload.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing queue payload and existence flag.

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
        parsed = _parse_payload(raw_payload, command_name)
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
            persist_global_queue(
                session,
                parsed["bucket"],
                parsed["work_type"],
                parsed["queue_payload"],
                actor_id,
            )
            record_payload, record_exists = load_global_queue_snapshot(
                session,
                parsed["bucket"],
                parsed["work_type"],
            )
        return ok_result(
            output={
                "bucket": parsed["bucket"],
                "work_type": parsed["work_type"],
                "record": record_payload,
                "exists": record_exists,
            }
        )
    except ValueError as exc:
        return error_result(
            code="payload_value_error",
            meaning="Invalid global work queue payload.",
            details={
                "command_name": command_name,
                "bucket": parsed["bucket"],
                "work_type": parsed["work_type"],
                "error": str(exc),
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)
