"""
SQL tool script to read work_queue_items by queue_id.

Purpose
- Provide ordered work item reads for a specific queue.
- Support bulk move selection without JSON payloads.

Contract
- Requires payload.queue_id and actor_id.
- Returns items ordered by position.
- Optional payload.limit limits returned rows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
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
from context_compass.system.ai_restricted.database_management.user_orm_models import WorkQueueItem
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


def _row_to_dict(row: WorkQueueItem) -> dict[str, Any]:
    """
    Convert a WorkQueueItem row to a dictionary.

    Args:
        row (WorkQueueItem): ORM row instance.

    Returns:
        dict[str, Any]: Serialized work item row.
    """

    return {
        "queue_id": row.queue_id,
        "work_id": row.work_id,
        "parent_work_id": row.parent_work_id,
        "root_work_id": row.root_work_id,
        "state": row.state,
        "kind": row.kind,
        "target_path": row.target_path,
        "ctx_path": row.ctx_path,
        "priority": row.priority,
        "attempts": row.attempts,
        "last_error_ref": row.last_error_ref,
        "position": row.position,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read work_queue_items ordered by position for a queue_id.

    Args:
        payload (dict): Command payload containing payload.queue_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing ordered work queue items.

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
        queue_id = require_string(raw_payload, "queue_id", command_name)
        limit = optional_int(raw_payload, "limit", command_name=command_name)
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
            stmt = select(WorkQueueItem).where(WorkQueueItem.queue_id == queue_id).order_by(
                WorkQueueItem.position
            )
            if limit is not None:
                stmt = stmt.limit(limit)
            rows = session.execute(stmt).scalars().all()
            items = [_row_to_dict(row) for row in rows]
            return ok_result(output={"queue_id": queue_id, "items": items})
    except Exception as exc:
        return exception_result(command_name, exc)
