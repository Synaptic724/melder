"""
SQLite query script to upsert work queue tasks for scan workflows.

Purpose
- Upsert task rows into branch-scoped work queues in one transaction.
- Insert/update work_queue_items and related reason/lease rows atomically.

Contract
- Requires payload.branch_name, payload.bucket, payload.work_type, payload.tasks.
- Ensures a branch work queue row exists for the queue_id.
- Skips updates for tasks currently leased or in_progress.
- Returns counts for inserted, updated, and skipped tasks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import func, select

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
    optional_list,
    optional_string,
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
    WorkQueue,
    WorkQueueItem,
    WorkQueueItemLease,
    WorkQueueItemReason,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


ALLOWED_STATES = ("queued", "leased", "in_progress", "done", "failed", "cancelled")
QUEUE_SCOPE = "branch"
SKIP_STATES = ("leased", "in_progress")


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

    return f"{QUEUE_SCOPE}:{branch_name}:{bucket}:{work_type}"


def _require_tasks(raw_payload: dict, command_name: str) -> list[dict]:
    """
    Require the tasks list from the request payload.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name (str): Command name for error context.

    Returns:
        list[dict]: List of task payloads.

    Raises:
        PayloadError: If tasks are missing or invalid.
    """

    tasks = optional_list(raw_payload, "tasks", command_name=command_name)
    if tasks is None:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": "tasks",
                "expected": "list",
            },
        )
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"tasks[{index}]",
                    "expected": "object",
                    "payload_type": type(task).__name__,
                },
            )
    return tasks


def _require_task_string(task: dict, field: str, index: int, command_name: str) -> str:
    """
    Require a non-empty string field in a task payload.

    Args:
        task (dict): Task payload dictionary.
        field (str): Field name to extract.
        index (int): Task index for error context.
        command_name (str): Command name for error context.

    Returns:
        str: Field value.

    Raises:
        PayloadError: If the field is missing or invalid.
    """

    value = task.get(field)
    if not isinstance(value, str) or not value:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": f"tasks[{index}].{field}",
                "expected": "non-empty string",
                "actual": value,
            },
        )
    return value


def _optional_task_string(task: dict, field: str, index: int, command_name: str) -> str | None:
    """
    Read an optional string field from a task payload.

    Args:
        task (dict): Task payload dictionary.
        field (str): Field name to extract.
        index (int): Task index for error context.
        command_name (str): Command name for error context.

    Returns:
        str | None: Field value or None if missing.

    Raises:
        PayloadError: If the field is not a string when provided.
    """

    if field not in task:
        return None
    value = task.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"tasks[{index}].{field}",
                "expected": "string or null",
                "payload_type": type(value).__name__,
            },
        )
    return value


def _require_task_int(task: dict, field: str, index: int, command_name: str) -> int:
    """
    Require an integer field in a task payload.

    Args:
        task (dict): Task payload dictionary.
        field (str): Field name to extract.
        index (int): Task index for error context.
        command_name (str): Command name for error context.

    Returns:
        int: Field value.

    Raises:
        PayloadError: If the field is missing or invalid.
    """

    value = task.get(field)
    if not isinstance(value, int):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"tasks[{index}].{field}",
                "expected": "integer",
                "payload_type": type(value).__name__,
            },
        )
    return value


def _require_task_reasons(task: dict, index: int, command_name: str) -> list[str]:
    """
    Require and validate task reasons.

    Args:
        task (dict): Task payload dictionary.
        index (int): Task index for error context.
        command_name (str): Command name for error context.

    Returns:
        list[str]: List of reason strings.

    Raises:
        PayloadError: If reasons are missing or invalid.
    """

    reasons = task.get("reason")
    if not isinstance(reasons, list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"tasks[{index}].reason",
                "expected": "list",
                "payload_type": type(reasons).__name__,
            },
        )
    normalized: list[str] = []
    for reason in reasons:
        if not isinstance(reason, str) or not reason.strip():
            raise PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": f"tasks[{index}].reason",
                    "expected": "non-empty string entries",
                    "actual": reason,
                },
            )
        normalized.append(reason)
    return normalized


def _parse_task_lease(
    lease_payload: dict,
    index: int,
    command_name: str,
) -> dict[str, Any]:
    """
    Parse a lease payload for a task.

    Args:
        lease_payload (dict): Lease payload mapping.
        index (int): Task index for error context.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Parsed lease fields.

    Raises:
        PayloadError: If lease fields are missing or invalid.
    """

    schema_version = lease_payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": f"tasks[{index}].lease.schema_version",
                "expected": "integer >= 1",
                "actual": schema_version,
            },
        )
    resource = _require_task_string(lease_payload, "resource", index, command_name)
    owner_id = _require_task_string(lease_payload, "owner_id", index, command_name)
    created_at = _require_task_string(lease_payload, "created_at", index, command_name)
    heartbeat_at = _require_task_string(lease_payload, "heartbeat_at", index, command_name)
    expires_at = _require_task_string(lease_payload, "expires_at", index, command_name)
    work_id = _optional_task_string(lease_payload, "work_id", index, command_name)
    return {
        "schema_version": schema_version,
        "resource": resource,
        "owner_id": owner_id,
        "created_at": created_at,
        "heartbeat_at": heartbeat_at,
        "expires_at": expires_at,
        "work_id": work_id,
    }


def _normalize_task(
    task: dict,
    index: int,
    command_name: str,
    now: str,
) -> dict[str, Any]:
    """
    Normalize a task payload into validated fields.

    Args:
        task (dict): Task payload dictionary.
        index (int): Task index for error context.
        command_name (str): Command name for error context.
        now (str): Timestamp to use for defaults.

    Returns:
        dict[str, Any]: Normalized task fields.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    state = _require_task_string(task, "state", index, command_name)
    if state not in ALLOWED_STATES:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": f"tasks[{index}].state",
                "expected": f"one of {list(ALLOWED_STATES)}",
                "actual": state,
            },
        )
    created_at = _optional_task_string(task, "created_at", index, command_name) or now
    updated_at = _optional_task_string(task, "updated_at", index, command_name) or now
    lease_payload = task.get("lease")
    lease = None
    if lease_payload is not None:
        if not isinstance(lease_payload, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"tasks[{index}].lease",
                    "expected": "object or null",
                    "payload_type": type(lease_payload).__name__,
                },
            )
        lease = _parse_task_lease(lease_payload, index, command_name)

    return {
        "work_id": _require_task_string(task, "work_id", index, command_name),
        "parent_work_id": _optional_task_string(task, "parent_work_id", index, command_name),
        "root_work_id": _require_task_string(task, "root_work_id", index, command_name),
        "state": state,
        "kind": _require_task_string(task, "kind", index, command_name),
        "target_path": _require_task_string(task, "target_path", index, command_name),
        "ctx_path": _require_task_string(task, "ctx_path", index, command_name),
        "priority": _require_task_int(task, "priority", index, command_name),
        "attempts": _require_task_int(task, "attempts", index, command_name),
        "last_error_ref": _optional_task_string(task, "last_error_ref", index, command_name),
        "reason": _require_task_reasons(task, index, command_name),
        "created_at": created_at,
        "updated_at": updated_at,
        "lease": lease,
    }


def _next_position(session, queue_id: str) -> int:
    """
    Compute the next queue position for new items.

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


def _upsert_task_row(
    session,
    queue_id: str,
    task: dict[str, Any],
    actor_id: str,
    now: str,
) -> str:
    """
    Insert or update a task row and its child entries.

    Args:
        session (Session): Active SQLAlchemy session.
        queue_id (str): Queue identifier.
        task (dict[str, Any]): Normalized task payload.
        actor_id (str): Actor identifier.
        now (str): Timestamp for updates.

    Returns:
        str: One of "inserted", "updated", or "skipped".
    """

    existing = session.get(WorkQueueItem, (queue_id, task["work_id"]))
    if existing is not None and existing.state in SKIP_STATES:
        return "skipped"

    if existing is None:
        position = _next_position(session, queue_id)
        session.add(
            WorkQueueItem(
                queue_id=queue_id,
                work_id=task["work_id"],
                parent_work_id=task["parent_work_id"],
                root_work_id=task["root_work_id"],
                state=task["state"],
                kind=task["kind"],
                target_path=task["target_path"],
                ctx_path=task["ctx_path"],
                priority=task["priority"],
                attempts=task["attempts"],
                last_error_ref=task["last_error_ref"],
                position=position,
                created_at=task["created_at"],
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
        )
        _replace_reasons(session, queue_id, task["work_id"], task["reason"], actor_id, now)
        _replace_lease(session, queue_id, task["work_id"], task["lease"], actor_id, now)
        return "inserted"

    existing.state = task["state"]
    existing.parent_work_id = task["parent_work_id"]
    existing.root_work_id = task["root_work_id"]
    existing.kind = task["kind"]
    existing.target_path = task["target_path"]
    existing.ctx_path = task["ctx_path"]
    existing.priority = task["priority"]
    existing.attempts = task["attempts"]
    existing.last_error_ref = task["last_error_ref"]
    existing.updated_at = now
    existing.updated_by = actor_id
    _replace_reasons(session, queue_id, task["work_id"], task["reason"], actor_id, now)
    _replace_lease(session, queue_id, task["work_id"], task["lease"], actor_id, now)
    return "updated"


def _replace_reasons(
    session,
    queue_id: str,
    work_id: str,
    reasons: list[str],
    actor_id: str,
    now: str,
) -> None:
    """
    Replace reason rows for a work item.

    Args:
        session (Session): Active SQLAlchemy session.
        queue_id (str): Queue identifier.
        work_id (str): Work item identifier.
        reasons (list[str]): Ordered reason values.
        actor_id (str): Actor identifier.
        now (str): Timestamp for updates.

    Returns:
        None: This function mutates the database session.
    """

    session.query(WorkQueueItemReason).filter_by(
        queue_id=queue_id,
        work_id=work_id,
    ).delete()
    for position, reason in enumerate(reasons, start=1):
        session.add(
            WorkQueueItemReason(
                queue_id=queue_id,
                work_id=work_id,
                position=position,
                reason=reason,
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
        )


def _replace_lease(
    session,
    queue_id: str,
    work_id: str,
    lease: dict[str, Any] | None,
    actor_id: str,
    now: str,
) -> None:
    """
    Replace lease metadata for a work item.

    Args:
        session (Session): Active SQLAlchemy session.
        queue_id (str): Queue identifier.
        work_id (str): Work item identifier.
        lease (dict[str, Any] | None): Lease payload or None.
        actor_id (str): Actor identifier.
        now (str): Timestamp for updates.

    Returns:
        None: This function mutates the database session.
    """

    session.query(WorkQueueItemLease).filter_by(
        queue_id=queue_id,
        work_id=work_id,
    ).delete()
    if lease is None:
        return
    session.add(
        WorkQueueItemLease(
            queue_id=queue_id,
            work_id=work_id,
            schema_version=lease["schema_version"],
            resource=lease["resource"],
            owner_id=lease["owner_id"],
            lease_work_id=lease["work_id"],
            created_at=lease["created_at"],
            heartbeat_at=lease["heartbeat_at"],
            expires_at=lease["expires_at"],
            created_by=actor_id,
            updated_at=now,
            updated_by=actor_id,
        )
    )


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Upsert work queue tasks into a branch queue.

    Args:
        payload (dict): Command payload containing queue metadata and tasks.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing upsert counts and queue metadata.

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
        bucket = require_string(raw_payload, "bucket", command_name)
        work_type = require_string(raw_payload, "work_type", command_name)
        schema_version = require_int(raw_payload, "schema_version", command_name)
        repo_id = optional_string(raw_payload, "repo_id", command_name=command_name)
        tasks = _require_tasks(raw_payload, command_name)
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

    queue_id = _queue_id(branch_name, bucket, work_type)
    now = utc_now_iso()
    inserted = updated = skipped = 0
    try:
        with sqlite_session(db_path, must_exist=True) as session:
            queue = session.get(WorkQueue, queue_id)
            queue_exists = queue is not None
            if queue is None:
                queue = WorkQueue(
                    queue_id=queue_id,
                    scope=QUEUE_SCOPE,
                    branch_name=branch_name,
                    bucket=bucket,
                    work_kind=work_type,
                    schema_version=schema_version,
                    repo_id=repo_id,
                    created_at=now,
                    created_by=actor_id,
                    updated_at=now,
                    updated_by=actor_id,
                )
                session.add(queue)

            for index, task in enumerate(tasks):
                normalized = _normalize_task(task, index, command_name, now)
                result = _upsert_task_row(session, queue_id, normalized, actor_id, now)
                if result == "inserted":
                    inserted += 1
                elif result == "updated":
                    updated += 1
                else:
                    skipped += 1

            if inserted or updated:
                queue.updated_at = now
                queue.updated_by = actor_id

        return ok_result(
            output={
                "queue_id": queue_id,
                "queue_exists": queue_exists,
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
