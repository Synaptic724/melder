"""
SQL tool script to update work_queue_items state fields.

Purpose
- Update core work item status fields in a queue.
- Touch updated_at/updated_by on the work item row.

Contract
- Requires payload.queue_id, payload.work_id, and actor_id.
- Optional payload.state/attempts/last_error_ref/priority update matching columns.
- Returns the updated work_queue_items record.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
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
from context_compass.system.ai_restricted.database_management.user_orm_models import WorkQueueItem
from context_compass.system.ai_restricted.system_management.command_runner import (
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


def _fetch_row(session: Session, queue_id: str, work_id: str) -> WorkQueueItem | None:
    """
    Load a work_queue_items row by queue_id/work_id.

    Args:
        session: SQLAlchemy session used for the query.
        queue_id (str): Queue identifier.
        work_id (str): Work item identifier.

    Returns:
        WorkQueueItem | None: ORM row if found, otherwise None.
    """

    stmt = select(WorkQueueItem).where(
        WorkQueueItem.queue_id == queue_id,
        WorkQueueItem.work_id == work_id,
    )
    return session.execute(stmt).scalar_one_or_none()


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Update a work_queue_items row with new state fields.

    Args:
        payload (dict): Command payload containing payload.queue_id/work_id and updates.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the updated work queue item record.

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
        queue_id = require_string(raw_payload, "queue_id", command_name)
        work_id = require_string(raw_payload, "work_id", command_name)
        state = optional_string(raw_payload, "state", command_name=command_name)
        attempts = optional_int(raw_payload, "attempts", command_name=command_name)
        last_error_ref = optional_string(
            raw_payload, "last_error_ref", command_name=command_name
        )
        priority = optional_int(raw_payload, "priority", command_name=command_name)
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

    now = utc_now_iso()
    try:
        with sqlite_session(db_path, must_exist=True) as session:
            row = _fetch_row(session, queue_id, work_id)
            if row is None:
                return error_result(
                    code="record_missing",
                    meaning="Work queue item not found.",
                    details={
                        "command_name": command_name,
                        "queue_id": queue_id,
                        "work_id": work_id,
                    },
                )
            if state is not None:
                row.state = state
            if attempts is not None:
                row.attempts = attempts
            if last_error_ref is not None:
                row.last_error_ref = last_error_ref
            if priority is not None:
                row.priority = priority
            row.updated_at = now
            row.updated_by = actor_id
            session.flush()
            return ok_result(output={"record": _row_to_dict(row)})
    except Exception as exc:
        return exception_result(command_name, exc)
