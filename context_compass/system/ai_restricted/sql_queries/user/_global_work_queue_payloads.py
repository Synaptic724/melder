"""
Global work queue payload helpers for SQLite query scripts.

Purpose
- Provide shared load/write helpers for global work queue query scripts.
- Centralize payload validation and hydration logic for global queues.

Contract
- All functions accept an active SQLAlchemy session; they do not open sessions.
- Validation raises ValueError with tasks-prefixed messages.
- Payloads emitted by load_global_queue_snapshot follow tasks.schema.json.
"""

from __future__ import annotations

from typing import Any

from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    WorkQueue,
    WorkQueueItem,
    WorkQueueItemLease,
    WorkQueueItemReason,
)


QUEUE_SCOPE = "global"


def queue_id(bucket: str, work_type: str) -> str:
    """
    Build the queue_id for a global work queue.

    Args:
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        str: Stable queue identifier.
    """

    return f"{QUEUE_SCOPE}:global:{bucket}:{work_type}"


def default_queue(now: str) -> dict[str, Any]:
    """
    Build a default global work queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict[str, Any]: Default queue payload with empty entries.
    """

    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _require_string(payload: dict[str, Any], key: str) -> str:
    """
    Require a non-empty string payload field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str: Field value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"tasks.{key} must be a non-empty string.")
    return value


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    """
    Return an optional string field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str | None: Field value if present.

    Raises:
        ValueError: If the field is not a string or null.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"tasks.{key} must be a string or null.")
    return value


def _require_int(payload: dict[str, Any], key: str) -> int:
    """
    Require an integer payload field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        int: Field value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"tasks.{key} must be an integer.")
    return value


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    """
    Require a list payload field.

    Args:
        payload (dict[str, Any]): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        list[Any]: Field value.

    Raises:
        ValueError: If the field is missing or invalid.
    """

    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"tasks.{key} must be a list.")
    return value


def load_global_queue_snapshot(
    session: Any,
    bucket: str,
    work_type: str,
) -> tuple[dict[str, Any], bool]:
    """
    Load a global work queue payload from SQLite.

    Args:
        session (Any): Active SQLAlchemy session.
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        tuple[dict[str, Any], bool]: Payload and exists flag.

    Contract:
        - Returns a default payload with exists False when no row is found.
    """

    now = utc_now_iso()
    queue_key = queue_id(bucket, work_type)
    core = session.get(WorkQueue, queue_key)
    if core is None:
        return default_queue(now), False

    items = (
        session.query(WorkQueueItem)
        .filter_by(queue_id=queue_key)
        .order_by(WorkQueueItem.position)
        .all()
    )
    reasons = (
        session.query(WorkQueueItemReason)
        .filter_by(queue_id=queue_key)
        .order_by(WorkQueueItemReason.work_id, WorkQueueItemReason.position)
        .all()
    )
    leases = session.query(WorkQueueItemLease).filter_by(queue_id=queue_key).all()

    reasons_by_work: dict[str, list[str]] = {}
    for row in reasons:
        reasons_by_work.setdefault(row.work_id, []).append(row.reason)
    lease_by_work: dict[str, dict[str, Any]] = {}
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

    queue: list[dict[str, Any]] = []
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

    payload = {
        "schema_version": core.schema_version,
        "repo_id": core.repo_id,
        "updated_at": core.updated_at or now,
        "queue": queue,
    }
    return payload, True


def persist_global_queue(
    session: Any,
    bucket: str,
    work_type: str,
    payload: dict[str, Any],
    actor_id: str,
) -> None:
    """
    Persist a global work queue payload to SQLite.

    Args:
        session (Any): Active SQLAlchemy session.
        bucket (str): Work bucket name.
        work_type (str): Work type name.
        payload (dict[str, Any]): Queue payload to persist.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        ValueError: If payload validation fails.

    Contract:
        - updated_at is refreshed at write time when absent.
        - Replaces child rows with the provided payload state.
        - Populates audit fields using existing queue metadata and actor_id.
    """

    if not isinstance(payload, dict):
        raise ValueError("Queue payload must be a JSON object.")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("tasks.schema_version must be an integer >= 1.")
    queue = payload.get("queue")
    if not isinstance(queue, list):
        raise ValueError("tasks.queue must be a list.")

    repo_id = payload.get("repo_id")
    if repo_id is not None and not isinstance(repo_id, str):
        raise ValueError("tasks.repo_id must be a string or null.")

    now = utc_now_iso()
    updated_at = payload.get("updated_at") or now
    if not isinstance(updated_at, str):
        raise ValueError("tasks.updated_at must be a string or null.")

    queue_key = queue_id(bucket, work_type)
    existing = session.get(WorkQueue, queue_key)
    record_created_at = existing.created_at if existing else now
    record_created_by = existing.created_by if existing else actor_id

    core = WorkQueue(
        queue_id=queue_key,
        scope=QUEUE_SCOPE,
        branch_name=None,
        bucket=bucket,
        work_kind=work_type,
        schema_version=schema_version,
        repo_id=repo_id,
        updated_at=updated_at,
        created_at=record_created_at,
        created_by=record_created_by,
        updated_by=actor_id,
    )
    session.merge(core)

    session.query(WorkQueueItemReason).filter_by(queue_id=queue_key).delete()
    session.query(WorkQueueItemLease).filter_by(queue_id=queue_key).delete()
    session.query(WorkQueueItem).filter_by(queue_id=queue_key).delete()

    for position, item in enumerate(queue, start=1):
        if not isinstance(item, dict):
            raise ValueError("tasks.queue entries must be objects.")
        work_id = _require_string(item, "work_id")
        parent_work_id = _optional_string(item, "parent_work_id")
        root_work_id = _require_string(item, "root_work_id")
        state = _require_string(item, "state")
        kind = _require_string(item, "kind")
        target_path = _require_string(item, "target_path")
        ctx_path = _require_string(item, "ctx_path")
        priority = _require_int(item, "priority")
        attempts = _require_int(item, "attempts")
        last_error_ref = _optional_string(item, "last_error_ref")
        reason_list = _require_list(item, "reason")
        created_at = item.get("created_at") or now
        updated_item_at = item.get("updated_at") or now
        if not isinstance(created_at, str):
            raise ValueError("tasks.queue.created_at must be a string or null.")
        if not isinstance(updated_item_at, str):
            raise ValueError("tasks.queue.updated_at must be a string or null.")

        session.add(
            WorkQueueItem(
                queue_id=queue_key,
                work_id=work_id,
                parent_work_id=parent_work_id,
                root_work_id=root_work_id,
                state=state,
                kind=kind,
                target_path=target_path,
                ctx_path=ctx_path,
                priority=priority,
                attempts=attempts,
                last_error_ref=last_error_ref,
                position=position,
                created_at=created_at,
                created_by=record_created_by,
                updated_at=updated_item_at,
                updated_by=actor_id,
            )
        )

        for reason_pos, reason in enumerate(reason_list, start=1):
            if not isinstance(reason, str):
                raise ValueError("tasks.queue.reason entries must be strings.")
            session.add(
                WorkQueueItemReason(
                    queue_id=queue_key,
                    work_id=work_id,
                    position=reason_pos,
                    reason=reason,
                    created_at=created_at,
                    created_by=record_created_by,
                    updated_at=updated_item_at,
                    updated_by=actor_id,
                )
            )

        lease = item.get("lease")
        if lease is None:
            continue
        if not isinstance(lease, dict):
            raise ValueError("tasks.queue.lease must be an object or null.")
        lease_schema_version = lease.get("schema_version")
        if not isinstance(lease_schema_version, int):
            raise ValueError("tasks.queue.lease.schema_version must be an integer.")
        lease_resource = _require_string(lease, "resource")
        lease_owner_id = _require_string(lease, "owner_id")
        lease_created_at = _require_string(lease, "created_at")
        lease_heartbeat_at = _optional_string(lease, "heartbeat_at")
        lease_expires_at = _optional_string(lease, "expires_at")
        lease_work_id = _require_string(lease, "work_id")
        session.add(
            WorkQueueItemLease(
                queue_id=queue_key,
                work_id=work_id,
                schema_version=lease_schema_version,
                resource=lease_resource,
                owner_id=lease_owner_id,
                created_at=lease_created_at,
                heartbeat_at=lease_heartbeat_at,
                expires_at=lease_expires_at,
                lease_work_id=lease_work_id,
                created_by=record_created_by,
                updated_at=updated_item_at,
                updated_by=actor_id,
            )
        )
