"""
SQL tool script for creating branch_registry records.

Purpose
- Create a new branch registry entry in system.db.
- Persist branch lifecycle metadata for branch tracking.

Contract
- Requires payload.record_id (branch_name), payload, and actor_id.
- record_id must be "<branch_name>" and non-empty.
- payload must include: schema_version, status.
- Optional payload fields: branch_name, notes.
- created_at/created_by/updated_at/updated_by are set by the script.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_choice,
    require_int,
    require_string,
)
from context_compass.system.ai_restricted._shared.sql_command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    BranchRegistry,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


STATUSES = ("active", "archived", "disabled")


def _parse_record_id(record_id: str, command_name: str) -> str:
    """
    Parse the record_id into a branch name.

    Args:
        record_id (str): Record id string in "<branch_name>" form.
        command_name (str): Command name for error context.

    Returns:
        str: Parsed branch name.

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


def _record_id(branch_name: str) -> str:
    """
    Build a canonical record_id for a branch registry entry.

    Args:
        branch_name (str): Branch name primary key.

    Returns:
        str: Canonical record_id string.
    """

    return branch_name


def _record_to_dict(row: BranchRegistry) -> dict:
    """
    Convert a branch registry ORM row into a dictionary.

    Args:
        row (BranchRegistry): ORM row instance.

    Returns:
        dict: Serialized branch registry payload.
    """

    record_id = _record_id(row.branch_name)
    return {
        "record_id": record_id,
        "branch_name": row.branch_name,
        "schema_version": row.schema_version,
        "status": row.status,
        "notes": row.notes,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def _require_payload_branch_name(
    raw_payload: dict,
    branch_name_value: str,
    command_name: str,
) -> None:
    """
    Ensure payload.branch_name matches the record_id, if supplied.

    Args:
        raw_payload (dict): Parsed payload object.
        branch_name_value (str): Parsed branch_name from record_id.
        command_name (str): Command name for error context.

    Raises:
        PayloadError: If payload.branch_name conflicts with record_id.
    """

    payload_branch = raw_payload.get("branch_name")
    if payload_branch is None:
        return
    if not isinstance(payload_branch, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "branch_name",
                "expected": "string",
                "payload_type": type(payload_branch).__name__,
            },
        )
    if payload_branch != branch_name_value:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "branch_name",
                "expected": branch_name_value,
                "actual": payload_branch,
            },
        )


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Create a branch_registry record.

    Args:
        payload (dict): Command payload containing payload.record_id and branch data.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the created record.

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
        actor_id = require_string(payload, "actor_id", command_name)
        branch_name_value = _parse_record_id(record_id, command_name)
        _require_payload_branch_name(raw_payload, branch_name_value, command_name)
        schema_version = require_int(raw_payload, "schema_version", command_name)
        status = require_choice(raw_payload, "status", command_name, STATUSES)
        notes = optional_string(raw_payload, "notes", command_name=command_name)
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

    now = utc_now_iso()
    try:
        with sqlite_session(db_path, must_exist=True) as session:
            existing = session.get(BranchRegistry, branch_name_value)
            if existing is not None:
                return error_result(
                    code="record_exists",
                    meaning="Branch registry record already exists.",
                    details={
                        "command_name": command_name,
                        "record_id": record_id,
                    },
                )
            row = BranchRegistry(
                branch_name=branch_name_value,
                schema_version=schema_version,
                status=status,
                notes=notes,
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
            session.add(row)
            session.flush()
            record = _record_to_dict(row)
        return ok_result(output={"record": record})
    except Exception as exc:
        return exception_result(command_name, exc)
