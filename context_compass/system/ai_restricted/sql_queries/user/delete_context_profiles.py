"""
SQLite query script to delete context_profiles payloads for a branch.

Purpose
- Delete context_profiles rows for a branch identifier.
- Report whether any context_profiles rows were removed.

Contract
- Requires payload.branch_name.
- Returns a deleted flag for the branch.
- Errors when the SQLite database is missing.
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
    ContextProfileItem,
    ContextProfileItemPath,
    ContextProfileItemStalenessReason,
    ContextProfilesCore,
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


def _delete_profiles(repo_root: Path, branch_name: str) -> bool:
    """
    Delete context_profiles rows for a branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.

    Returns:
        bool: True if the core row existed and was removed.
    """

    db_path = user_db_path(repo_root)
    with sqlite_session(db_path, must_exist=True) as session:
        session.query(ContextProfileItemPath).filter_by(branch_name=branch_name).delete()
        session.query(ContextProfileItemStalenessReason).filter_by(branch_name=branch_name).delete()
        session.query(ContextProfileItem).filter_by(branch_name=branch_name).delete()
        removed = session.query(ContextProfilesCore).filter_by(branch_name=branch_name).delete()
        return bool(removed)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete a context_profiles payload by branch_name.

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
        deleted = _delete_profiles(repo_root, branch_name)
        return ok_result(output={"branch_name": branch_name, "deleted": deleted})
    except Exception as exc:
        return exception_result(command_name, exc)
