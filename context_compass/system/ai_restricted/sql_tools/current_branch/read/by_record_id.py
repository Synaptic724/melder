"""
SQL tool script to read the current_branch record by record_id.

Purpose
- Fetch the active branch pointer stored in current_branch.
- Enforce that record_id is the stable "current" pointer.

Contract
- Requires payload.record_id and actor_id.
- record_id must be "current".
- Returns the current_branch record or a record_not_found error.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
from context_compass.system.ai_restricted.database_management.user_orm_models import CurrentBranch
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


CURRENT_RECORD_ID = "current"


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


def _parse_record_id(record_id: str, command_name: str) -> str:
    """
    Validate the record_id for current_branch reads.

    Args:
        record_id (str): Record identifier string.
        command_name (str): Command name for error context.

    Returns:
        str: Normalized record_id.

    Raises:
        PayloadError: If record_id is invalid.
    """

    if not record_id.strip():
        raise PayloadError(
            code="record_id_invalid",
            details={
                "command_name": command_name,
                "record_id": record_id,
                "expected": CURRENT_RECORD_ID,
            },
        )
    if record_id != CURRENT_RECORD_ID:
        raise PayloadError(
            code="record_id_invalid",
            details={
                "command_name": command_name,
                "record_id": record_id,
                "expected": CURRENT_RECORD_ID,
            },
        )
    return record_id


def _record_to_dict(row: CurrentBranch) -> dict[str, Any]:
    """
    Convert a CurrentBranch ORM row into a dictionary.

    Args:
        row (CurrentBranch): ORM row instance.

    Returns:
        dict[str, Any]: Serialized current_branch record.
    """

    return {
        "record_id": row.record_id,
        "schema_version": row.schema_version,
        "branch_name": row.branch_name,
        "notes": row.notes,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read the current_branch record by record_id.

    Args:
        payload (dict): Command payload containing payload.record_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the current_branch record.

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
        record_id = require_string(raw_payload, "record_id", command_name)
        normalized_id = _parse_record_id(record_id, command_name)
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
            row = session.get(CurrentBranch, normalized_id)
            if row is None:
                return error_result(
                    code="record_not_found",
                    meaning="Record not found.",
                    details={
                        "command_name": command_name,
                        "record_id": normalized_id,
                    },
                )
            return ok_result(output={"record": _record_to_dict(row)})
    except Exception as exc:
        return exception_result(command_name, exc)
