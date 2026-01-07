"""
SQLite query script to move an agent_work_item into a work queue.

Purpose
- Move a work item from an agent queue into a branch/global queue in one transaction.
- Preserve item fields while updating queue_id/position and optional state.

Contract
- Requires payload.agent_id, payload.work_id, payload.dest_queue_id.
- Requires destination queue metadata when the destination queue is missing.
- Moves child rows in agent_work_item_reasons and agent_work_item_lease.
- Updates updated_at/updated_by on the agent queue and destination queue.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import func, select

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
    user_db_path,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    AgentWorkItem,
    AgentWorkItemLease,
    AgentWorkItemReason,
    AgentWorkQueue,
    WorkQueue,
    WorkQueueItem,
    WorkQueueItemLease,
    WorkQueueItemReason,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


SCOPES = ("branch", "global")


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


def _parse_move_payload(raw_payload: dict, command_name: str) -> dict[str, Any]:
    """
    Parse and validate the move request payload.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Parsed payload values.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    agent_id = require_string(raw_payload, "agent_id", command_name)
    work_id = require_string(raw_payload, "work_id", command_name)
    dest_queue_id = require_string(raw_payload, "dest_queue_id", command_name)
    dest_scope = require_choice(raw_payload, "dest_scope", command_name, SCOPES)
    dest_branch_name = optional_string(raw_payload, "dest_branch_name", command_name=command_name)
    dest_bucket = require_string(raw_payload, "dest_bucket", command_name)
    dest_work_kind = require_string(raw_payload, "dest_work_kind", command_name)
    dest_schema_version = require_int(raw_payload, "dest_schema_version", command_name)
    dest_repo_id = optional_string(raw_payload, "dest_repo_id", command_name=command_name)
    new_state = optional_string(raw_payload, "new_state", command_name=command_name)

    if dest_scope == "branch" and not dest_branch_name:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": "dest_branch_name",
                "expected": "branch_name for branch scope",
            },
        )
    if dest_scope == "global" and dest_branch_name is not None:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "dest_branch_name",
                "expected": "null for global scope",
                "actual": dest_branch_name,
            },
        )

    return {
        "agent_id": agent_id,
        "work_id": work_id,
        "dest_queue_id": dest_queue_id,
        "dest_scope": dest_scope,
        "dest_branch_name": dest_branch_name,
        "dest_bucket": dest_bucket,
        "dest_work_kind": dest_work_kind,
        "dest_schema_version": dest_schema_version,
        "dest_repo_id": dest_repo_id,
        "new_state": new_state,
    }


def _ensure_dest_queue(
    session,
    *,
    dest_queue_id: str,
    dest_scope: str,
    dest_branch_name: str | None,
    dest_bucket: str,
    dest_work_kind: str,
    dest_schema_version: int,
    dest_repo_id: str | None,
    actor_id: str,
    now: str,
) -> WorkQueue:
    """
    Ensure the destination queue exists or create it.

    Args:
        session (Session): Active SQLAlchemy session.
        dest_queue_id (str): Destination queue identifier.
        dest_scope (str): Destination queue scope.
        dest_branch_name (str | None): Destination branch name.
        dest_bucket (str): Destination bucket name.
        dest_work_kind (str): Destination work kind.
        dest_schema_version (int): Schema version for the queue.
        dest_repo_id (str | None): Optional repo identifier.
        actor_id (str): Actor identifier for audit fields.
        now (str): Timestamp for created/updated fields.

    Returns:
        WorkQueue: Destination queue row.

    Raises:
        ValueError: If an existing queue has conflicting metadata.
    """

    existing = session.get(WorkQueue, dest_queue_id)
    if existing is not None:
        mismatches = []
        if existing.scope != dest_scope:
            mismatches.append("scope")
        if existing.branch_name != dest_branch_name:
            mismatches.append("branch_name")
        if existing.bucket != dest_bucket:
            mismatches.append("bucket")
        if existing.work_kind != dest_work_kind:
            mismatches.append("work_kind")
        if mismatches:
            raise ValueError(
                f"Destination queue metadata mismatch: {', '.join(mismatches)}"
            )
        return existing

    row = WorkQueue(
        queue_id=dest_queue_id,
        scope=dest_scope,
        branch_name=dest_branch_name,
        bucket=dest_bucket,
        work_kind=dest_work_kind,
        schema_version=dest_schema_version,
        repo_id=dest_repo_id,
        created_at=now,
        created_by=actor_id,
        updated_at=now,
        updated_by=actor_id,
    )
    session.add(row)
    session.flush()
    return row


def _next_position(session, queue_id: str) -> int:
    """
    Compute the next position for a queue_id.

    Args:
        session (Session): Active SQLAlchemy session.
        queue_id (str): Queue identifier.

    Returns:
        int: Next queue position (0-based).
    """

    result = session.execute(
        select(func.max(WorkQueueItem.position)).where(WorkQueueItem.queue_id == queue_id)
    )
    max_pos = result.scalar_one_or_none()
    if max_pos is None:
        return 0
    return int(max_pos) + 1


def _move_reasons(
    session,
    *,
    agent_id: str,
    dest_queue_id: str,
    work_id: str,
    actor_id: str,
    now: str,
) -> None:
    """
    Move agent_work_item_reasons rows into work_queue_item_reasons.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        dest_queue_id (str): Destination queue identifier.
        work_id (str): Work identifier.
        actor_id (str): Actor identifier for updated_by.
        now (str): Timestamp for updated_at.
    """

    stmt = (
        select(AgentWorkItemReason)
        .where(
            (AgentWorkItemReason.agent_id == agent_id)
            & (AgentWorkItemReason.work_id == work_id)
        )
        .order_by(AgentWorkItemReason.position)
    )
    reasons = session.execute(stmt).scalars().all()
    if not reasons:
        return
    for row in reasons:
        session.delete(row)
    for row in reasons:
        session.add(
            WorkQueueItemReason(
                queue_id=dest_queue_id,
                work_id=work_id,
                position=row.position,
                reason=row.reason,
                created_at=row.created_at,
                created_by=row.created_by,
                updated_at=now,
                updated_by=actor_id,
            )
        )


def _move_lease(
    session,
    *,
    agent_id: str,
    dest_queue_id: str,
    work_id: str,
    actor_id: str,
    now: str,
) -> None:
    """
    Move agent_work_item_lease rows into work_queue_item_lease.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        dest_queue_id (str): Destination queue identifier.
        work_id (str): Work identifier.
        actor_id (str): Actor identifier for updated_by.
        now (str): Timestamp for updated_at.
    """

    lease = session.get(AgentWorkItemLease, {"agent_id": agent_id, "work_id": work_id})
    if lease is None:
        return
    session.delete(lease)
    session.add(
        WorkQueueItemLease(
            queue_id=dest_queue_id,
            work_id=work_id,
            schema_version=lease.schema_version,
            resource=lease.resource,
            owner_id=lease.owner_id,
            lease_work_id=lease.lease_work_id,
            created_at=lease.created_at,
            heartbeat_at=lease.heartbeat_at,
            expires_at=lease.expires_at,
            created_by=lease.created_by,
            updated_at=now,
            updated_by=actor_id,
        )
    )


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Move an agent work item into a branch/global work queue.

    Args:
        payload (dict): Command payload containing payload move fields.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result describing the move operation.

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
        move_payload = _parse_move_payload(raw_payload, command_name)
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
            agent_queue = session.get(AgentWorkQueue, move_payload["agent_id"])
            if agent_queue is None:
                return error_result(
                    code="record_missing",
                    meaning="Agent work queue not found.",
                    details={
                        "command_name": command_name,
                        "agent_id": move_payload["agent_id"],
                    },
                )

            item = session.get(
                AgentWorkItem,
                {
                    "agent_id": move_payload["agent_id"],
                    "work_id": move_payload["work_id"],
                },
            )
            if item is None:
                return error_result(
                    code="record_missing",
                    meaning="Agent work item not found.",
                    details={
                        "command_name": command_name,
                        "agent_id": move_payload["agent_id"],
                        "work_id": move_payload["work_id"],
                    },
                )

            dest_queue = _ensure_dest_queue(
                session,
                dest_queue_id=move_payload["dest_queue_id"],
                dest_scope=move_payload["dest_scope"],
                dest_branch_name=move_payload["dest_branch_name"],
                dest_bucket=move_payload["dest_bucket"],
                dest_work_kind=move_payload["dest_work_kind"],
                dest_schema_version=move_payload["dest_schema_version"],
                dest_repo_id=move_payload["dest_repo_id"],
                actor_id=actor_id,
                now=now,
            )

            existing_dest = session.get(
                WorkQueueItem,
                {
                    "queue_id": move_payload["dest_queue_id"],
                    "work_id": move_payload["work_id"],
                },
            )
            if existing_dest is not None:
                return error_result(
                    code="record_exists",
                    meaning="Destination queue already has this work item.",
                    details={
                        "command_name": command_name,
                        "queue_id": move_payload["dest_queue_id"],
                        "work_id": move_payload["work_id"],
                    },
                )

            new_state = move_payload["new_state"] or item.state
            position = _next_position(session, move_payload["dest_queue_id"])
            session.delete(item)
            session.add(
                WorkQueueItem(
                    queue_id=move_payload["dest_queue_id"],
                    work_id=item.work_id,
                    parent_work_id=item.parent_work_id,
                    root_work_id=item.root_work_id,
                    state=new_state,
                    kind=item.kind,
                    target_path=item.target_path,
                    ctx_path=item.ctx_path,
                    priority=item.priority,
                    attempts=item.attempts,
                    last_error_ref=item.last_error_ref,
                    position=position,
                    created_at=item.created_at,
                    created_by=item.created_by,
                    updated_at=now,
                    updated_by=actor_id,
                )
            )

            _move_reasons(
                session,
                agent_id=move_payload["agent_id"],
                dest_queue_id=move_payload["dest_queue_id"],
                work_id=item.work_id,
                actor_id=actor_id,
                now=now,
            )
            _move_lease(
                session,
                agent_id=move_payload["agent_id"],
                dest_queue_id=move_payload["dest_queue_id"],
                work_id=item.work_id,
                actor_id=actor_id,
                now=now,
            )

            agent_queue.updated_at = now
            agent_queue.updated_by = actor_id
            dest_queue.updated_at = now
            dest_queue.updated_by = actor_id

            session.flush()
            return ok_result(
                output={
                    "work_id": item.work_id,
                    "agent_id": move_payload["agent_id"],
                    "dest_queue_id": move_payload["dest_queue_id"],
                    "new_state": new_state,
                }
            )
    except Exception as exc:
        return exception_result(command_name, exc)
