"""
SQL tool script for updating current_branch records.

Purpose
- Persist the active branch pointer in user.db.
- Upsert the current_branch row when it does not exist.

Contract
- Requires payload.record_id and payload.branch_name.
- record_id must be "current" (stable pointer identifier).
- actor_id is required for audit logging.
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
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    user_db_path,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import CurrentBranch
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


CURRENT_RECORD_ID = "current"


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


def _parse_record_id(record_id: str, command_name: str) -> str:
    """
    Validate the record_id for current_branch operations.

    Args:
        record_id (str): Record id string.
        command_name (str): Command name for error context.

    Returns:
        str: Normalized record id.

    Raises:
        PayloadError: If record_id is invalid or not supported.
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


def _record_to_dict(row: CurrentBranch) -> dict:
    """
    Convert a CurrentBranch ORM row into a dictionary.

    Args:
        row (CurrentBranch): ORM row instance.

    Returns:
        dict: Serialized current_branch payload.
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


def _upsert_current_branch(
    repo_root: Path,
    *,
    record_id: str,
    branch_name: str,
    notes: str | None,
    actor_id: str,
) -> dict:
    """
    Upsert the current_branch record.

    Args:
        repo_root (Path): Repository root.
        record_id (str): Record identifier for the current branch row.
        branch_name (str): Active branch name to persist.
        notes (str | None): Optional notes to store.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Serialized current_branch record.
    """

    now = utc_now_iso()
    db_path = user_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(f"User database not found: {db_path}")

    with sqlite_session(db_path, must_exist=True) as session:
        row = session.get(CurrentBranch, record_id)
        if row is None:
            row = CurrentBranch(
                record_id=record_id,
                schema_version=1,
                branch_name=branch_name,
                notes=notes,
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
            session.add(row)
        else:
            row.schema_version = 1
            row.branch_name = branch_name
            row.notes = notes
            row.updated_at = now
            row.updated_by = actor_id
        session.flush()
        record = _record_to_dict(row)
    return record


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Set the active branch in the current_branch table.

    Args:
        payload (dict): Command payload containing payload record fields.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the updated current_branch record.

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
        record_id_value = require_string(raw_payload, "record_id", command_name)
        branch_name = require_string(raw_payload, "branch_name", command_name)
        notes = optional_string(raw_payload, "notes", command_name=command_name)
        record_id = _parse_record_id(record_id_value, command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        record = _upsert_current_branch(
            repo_root,
            record_id=record_id,
            branch_name=branch_name,
            notes=notes,
            actor_id=actor_id,
        )
        return ok_result(output={"record": record})
    except FileNotFoundError as exc:
        return error_result(
            code="db_missing",
            meaning=str(exc),
            details={
                "command_name": command_name,
                "db_path": str(user_db_path(repo_root)),
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)
