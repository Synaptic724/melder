"""
SQLite query script to read a branch work queue payload.

Purpose
- Load a branch-scoped work queue payload from normalized work_queue tables.
- Provide queue payloads for branch work copy/delete flows without direct ORM access.

Contract
- Requires payload.branch_name, payload.bucket, and payload.work_type.
- actor_id is required for audit logging.
- Returns queue payload and an exists flag.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    WorkQueue,
    WorkQueueItem,
    WorkQueueItemLease,
    WorkQueueItemReason,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


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


def _parse_payload(raw_payload: dict, command_name: str) -> dict:
    """
    Parse and validate queue lookup fields.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict: Parsed payload values for branch_name, bucket, and work_type.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    branch_name = require_string(raw_payload, "branch_name", command_name)
    bucket = require_string(raw_payload, "bucket", command_name)
    work_type = require_string(raw_payload, "work_type", command_name)
    return {
        "branch_name": branch_name,
        "bucket": bucket,
        "work_type": work_type,
    }


def _queue_id(branch_name: str, bucket: str, work_type: str) -> str:
    """
    Build the queue_id for a branch work queue.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        str: Stable queue identifier.
    """

    return f"branch:{branch_name}:{bucket}:{work_type}"


def _default_queue(now: str) -> dict:
    """
    Build a default branch work queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Default queue payload with empty entries.
    """

    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _build_reasons_map(reasons: list[WorkQueueItemReason]) -> dict[str, list[str]]:
    """
    Build a map of work_id to reason list.

    Args:
        reasons (list[WorkQueueItemReason]): Reason rows for a queue.

    Returns:
        dict[str, list[str]]: Mapping of work_id to ordered reasons.
    """

    reasons_by_work: dict[str, list[str]] = {}
    for row in reasons:
        reasons_by_work.setdefault(row.work_id, []).append(row.reason)
    return reasons_by_work


def _build_lease_map(leases: list[WorkQueueItemLease]) -> dict[str, dict]:
    """
    Build a map of work_id to lease payloads.

    Args:
        leases (list[WorkQueueItemLease]): Lease rows for a queue.

    Returns:
        dict[str, dict]: Mapping of work_id to lease payloads.
    """

    lease_by_work: dict[str, dict] = {}
    for row in leases:
        lease_by_work[row.work_id] = {
            "schema_version": row.schema_version,
            "resource": row.resource,
            "owner_id": row.owner_id,
            "created_at": row.created_at,
            "heartbeat_at": row.heartbeat_at,
            "expires_at": row.expires_at,
            "work_id": row.lease_work_id,
        }
    return lease_by_work


def _build_queue_entries(
    items: list[WorkQueueItem],
    reasons_by_work: dict[str, list[str]],
    lease_by_work: dict[str, dict],
) -> list[dict]:
    """
    Build queue entry payloads from ORM rows.

    Args:
        items (list[WorkQueueItem]): Work queue item rows.
        reasons_by_work (dict[str, list[str]]): Reason mapping by work_id.
        lease_by_work (dict[str, dict]): Lease payload mapping by work_id.

    Returns:
        list[dict]: Queue entry payloads.
    """

    queue: list[dict] = []
    for item in items:
        queue.append(
            {
                "work_id": item.work_id,
                "parent_work_id": item.parent_work_id,
                "root_work_id": item.root_work_id,
                "state": item.state,
                "kind": item.kind,
                "target_path": item.target_path,
                "ctx_path": item.ctx_path,
                "reason": reasons_by_work.get(item.work_id, []),
                "priority": item.priority,
                "lease": lease_by_work.get(item.work_id),
                "attempts": item.attempts,
                "last_error_ref": item.last_error_ref,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
        )
    return queue


def _load_queue_snapshot(
    session: Any,
    branch_name: str,
    bucket: str,
    work_type: str,
    now: str,
) -> dict:
    """
    Load a branch work queue snapshot from ORM rows.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.
        now (str): Current timestamp for defaults.

    Returns:
        dict: Snapshot payload containing queue and exists fields.
    """

    queue_id = _queue_id(branch_name, bucket, work_type)
    core = session.get(WorkQueue, queue_id)
    if core is None:
        return {"queue": _default_queue(now), "exists": False}

    items = (
        session.query(WorkQueueItem)
        .filter_by(queue_id=queue_id)
        .order_by(WorkQueueItem.position)
        .all()
    )
    reasons = (
        session.query(WorkQueueItemReason)
        .filter_by(queue_id=queue_id)
        .order_by(WorkQueueItemReason.work_id, WorkQueueItemReason.position)
        .all()
    )
    leases = session.query(WorkQueueItemLease).filter_by(queue_id=queue_id).all()
    reasons_by_work = _build_reasons_map(reasons)
    lease_by_work = _build_lease_map(leases)
    queue = _build_queue_entries(items, reasons_by_work, lease_by_work)
    return {
        "queue": {
            "schema_version": core.schema_version,
            "repo_id": core.repo_id,
            "updated_at": core.updated_at or now,
            "queue": queue,
        },
        "exists": True,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a branch work queue payload for the given branch/bucket/work_type.

    Args:
        payload (dict): Command payload containing payload branch metadata.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing queue payload and exists flag.

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
        parsed = _parse_payload(raw_payload, command_name)
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
        now = utc_now_iso()
        db_path = user_db_path(repo_root)
        with sqlite_session(db_path, must_exist=True) as session:
            snapshot = _load_queue_snapshot(
                session,
                parsed["branch_name"],
                parsed["bucket"],
                parsed["work_type"],
                now,
            )
        return ok_result(
            output={
                "branch_name": parsed["branch_name"],
                "bucket": parsed["bucket"],
                "work_type": parsed["work_type"],
                "queue": snapshot["queue"],
                "exists": snapshot["exists"],
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
