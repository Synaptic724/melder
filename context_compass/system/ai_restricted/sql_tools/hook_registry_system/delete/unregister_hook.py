"""
SQL tool script for deleting hook_registry_system records.

Purpose
- Remove a system hook registration from system.db.
- Return a deterministic deleted flag for auditing.

Contract
- Requires payload.record_id and actor_id.
- record_id must be "<hook_id>" and non-empty.
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
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    HookRegistrySystem,
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
    Delete a hook_registry_system record.

    Args:
        payload (dict): Command payload containing payload.record_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the delete status.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
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
        require_string(payload, "actor_id", command_name)
        hook_id_value = _parse_record_id(record_id, command_name)
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
        with sqlite_session(db_path, must_exist=True) as session:
            row = session.get(HookRegistrySystem, (hook_id_value))
            if row is None:
                return error_result(
                    code="record_not_found",
                    meaning="Record not found.",
                    details={
                        "command_name": command_name,
                        "record_id": record_id,
                    },
                )
            session.delete(row)
            session.flush()
        return ok_result(output={"deleted": True})
    except Exception as exc:
        return exception_result(command_name, exc)
