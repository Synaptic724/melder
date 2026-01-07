"""
SQLite query script to read a global work queue payload.

Purpose
- Load a global-scoped work queue payload from normalized work_queue tables.
- Provide queue payloads for global work transfer flows without direct ORM access.

Contract
- Requires payload.bucket and payload.work_type.
- actor_id is required for audit logging.
- Returns queue payload and an exists flag.
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
from context_compass.system.ai_restricted.sql_queries.user._global_work_queue_payloads import (
    load_global_queue_snapshot,
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
    Parse and validate queue lookup fields.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict: Parsed payload values for bucket and work_type.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    bucket = require_string(raw_payload, "bucket", command_name)
    work_type = require_string(raw_payload, "work_type", command_name)
    return {
        "bucket": bucket,
        "work_type": work_type,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a global work queue payload.

    Args:
        payload (dict): Command payload containing payload.bucket/work_type.
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
        require_string(payload, "actor_id", command_name)
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
    except Exception as exc:
        return exception_result(command_name, exc)
