"""
SQLite query script to delete architecture_context payloads.

Purpose
- Delete architecture_context or test_architecture_context rows by kind.
- Remove child rows tied to the architecture_context payload.

Contract
- Requires payload.branch_name and payload.kind.
- kind must be architecture_context or test_architecture_context.
- Returns deleted flag indicating whether a record was removed.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_choice,
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
    ArchitectureContext,
    ArchitectureContextAgentDirectory,
    ArchitectureContextAgentItem,
    ArchitectureContextAgentNotes,
    ArchitectureContextAgentSummary,
    ArchitectureContextMatrix,
    ArchitectureContextStalenessReason,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


ALLOWED_KINDS = ("architecture_context", "test_architecture_context")


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


def _delete_rows(repo_root: Path, branch_name: str, kind: str) -> bool:
    """
    Delete architecture_context rows within a single transaction.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        bool: True if rows were deleted, False if none existed.

    Raises:
        FileNotFoundError: If user.db is missing.

    Contract:
        - Deletes child rows before deleting the core record.
        - Returns False when no record exists for the branch/kind.
    """

    db_path = user_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(f"User database not found: {db_path}")

    with sqlite_session(db_path, must_exist=True) as session:
        row = session.get(ArchitectureContext, (branch_name, kind))
        if row is None:
            return False
        session.query(ArchitectureContextAgentItem).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextAgentDirectory).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextAgentSummary).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextAgentNotes).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextMatrix).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.query(ArchitectureContextStalenessReason).filter_by(
            branch_name=branch_name, kind=kind
        ).delete()
        session.delete(row)
        return True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete an architecture_context payload by kind.

    Args:
        payload (dict): Command payload containing payload.branch_name/kind.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing deleted flag.

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
        branch_name = require_string(raw_payload, "branch_name", command_name)
        kind = require_choice(raw_payload, "kind", command_name, ALLOWED_KINDS)
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
        deleted = _delete_rows(repo_root, branch_name, kind)
        return ok_result(
            output={"branch_name": branch_name, "kind": kind, "deleted": deleted}
        )
    except Exception as exc:
        return exception_result(command_name, exc)
