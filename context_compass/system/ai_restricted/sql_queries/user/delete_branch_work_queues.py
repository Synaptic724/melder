"""
SQLite query script to delete branch work queues.

Purpose
- Delete branch-scoped work queue rows from shared work_queue tables.
- Return queue_ids removed for the branch.

Contract
- Requires payload.branch_name.
- Returns queue_ids list (may be empty).
- Errors when the SQLite user database is missing.
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
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    WorkQueue,
    WorkQueueItem,
    WorkQueueItemLease,
    WorkQueueItemReason,
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


def _queue_ids_for_branch(session: Any, branch_name: str) -> list[str]:
    """
    Collect queue_ids for a branch scope.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.

    Returns:
        list[str]: Queue identifiers for the branch.
    """

    rows = (
        session.query(WorkQueue.queue_id)
        .filter_by(scope="branch", branch_name=branch_name)
        .all()
    )
    return [row.queue_id for row in rows]


def _delete_queue_rows(session: Any, queue_ids: list[str]) -> None:
    """
    Delete work queue rows for the provided queue_ids.

    Args:
        session (Any): SQLAlchemy session.
        queue_ids (list[str]): Queue identifiers to delete.

    Returns:
        None: Rows are deleted in-place.
    """

    if not queue_ids:
        return
    session.query(WorkQueueItemReason).filter(
        WorkQueueItemReason.queue_id.in_(queue_ids)
    ).delete(synchronize_session=False)
    session.query(WorkQueueItemLease).filter(
        WorkQueueItemLease.queue_id.in_(queue_ids)
    ).delete(synchronize_session=False)
    session.query(WorkQueueItem).filter(
        WorkQueueItem.queue_id.in_(queue_ids)
    ).delete(synchronize_session=False)
    session.query(WorkQueue).filter(
        WorkQueue.queue_id.in_(queue_ids)
    ).delete(synchronize_session=False)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete branch work queue rows by branch_name.

    Args:
        payload (dict): Command payload containing payload.branch_name.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the queue_ids removed for the branch.

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
        with sqlite_session(db_path, must_exist=True) as session:
            queue_ids = _queue_ids_for_branch(session, branch_name)
            _delete_queue_rows(session, queue_ids)
        return ok_result(output={"branch_name": branch_name, "queue_ids": queue_ids})
    except Exception as exc:
        return exception_result(command_name, exc)
