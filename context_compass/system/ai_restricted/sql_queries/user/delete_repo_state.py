"""
SQLite query script to delete repo_state payloads for a branch.

Purpose
- Delete repo_state rows for a branch identifier.
- Remove tooling disabled feature rows associated with the repo_state.

Contract
- Requires payload.branch_name.
- Returns a deleted flag for the branch.
- Errors when the SQLite user database is missing.
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
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    RepoState,
    RepoStateToolingDisabledFeature,
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


def _delete_repo_state_rows(repo_root: Path, branch_name: str) -> bool:
    """
    Delete repo_state rows directly from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        bool: True if the repo_state row existed and was deleted.

    Raises:
        FileNotFoundError: If user.db is missing.
    """

    db_path = user_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(f"User database not found: {db_path}")

    with sqlite_session(db_path, must_exist=True) as session:
        session.query(RepoStateToolingDisabledFeature).filter_by(branch_name=branch_name).delete()
        removed = session.query(RepoState).filter_by(branch_name=branch_name).delete()
        return bool(removed)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete a repo_state payload by branch_name.

    Args:
        payload (dict): Command payload containing payload.branch_name.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the deleted flag for the branch.

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
        deleted = _delete_repo_state_rows(repo_root, branch_name)
        return ok_result(output={"branch_name": branch_name, "deleted": deleted})
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
