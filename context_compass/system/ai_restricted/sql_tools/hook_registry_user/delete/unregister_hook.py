"""
SQL tool script for deleting hook_registry_user records.

Purpose
- Remove hook registry records for user hooks.
- Prevent stale hooks from executing in the runner.

Contract
- Requires payload.record_id (hook_id) and actor_id.
- record_id must be "<hook_id>" and non-empty.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
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
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    HookRegistryUser,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _parse_record_id(record_id: str, command_name: str) -> str:
    """
    Parse the record_id into a hook id.

    Args:
        record_id (str): Record id string in "<hook_id>" form.
        command_name (str): Command name for error context.

    Returns:
        str: Parsed hook id.

    Raises:
        PayloadError: If record_id is invalid.
    """

    if not record_id.strip():
        raise PayloadError(
            code="record_id_invalid",
            details={
                "command_name": command_name,
                "record_id": record_id,
                "expected": "non-empty record_id",
            },
        )
    return record_id


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete a hook_registry_user record.

    Args:
        payload (dict): Command payload containing payload.record_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the deleted hook id.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = require_string(payload, "repo_root", command_name)
        repo_root = Path(repo_root_value).resolve()
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
        record_id = require_string(raw_payload, "record_id", command_name)
        actor_id = require_string(payload, "actor_id", command_name)
        hook_id_value = _parse_record_id(record_id, command_name)
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
            row = session.get(HookRegistryUser, hook_id_value)
            if row is None:
                return error_result(
                    code="record_missing",
                    meaning="Hook registry record does not exist.",
                    details={
                        "command_name": command_name,
                        "record_id": record_id,
                    },
                )
            session.delete(row)
            session.flush()
        return ok_result(
            output={
                "record_id": record_id,
                "hook_id": hook_id_value,
                "deleted_by": actor_id,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
