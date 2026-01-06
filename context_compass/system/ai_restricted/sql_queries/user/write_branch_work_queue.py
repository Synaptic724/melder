"""
SQLite query script to write a branch work queue payload.

Purpose
- Persist branch-scoped work queue payloads across normalized work_queue tables.
- Provide atomic queue writes for branch work copy/delete flows.

Contract
- Requires payload.branch_name, payload.bucket, payload.work_type.
- Requires payload.queue_payload (dict) and payload.exists (bool).
- actor_id is required for audit logging.
- Replaces queue child rows with the provided payload state.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
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
    Parse and validate queue write fields.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict: Parsed payload values for branch_name, bucket, work_type, payload, exists.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    branch_name = require_string(raw_payload, "branch_name", command_name)
    bucket = require_string(raw_payload, "bucket", command_name)
    work_type = require_string(raw_payload, "work_type", command_name)
    queue_payload = raw_payload.get("queue_payload")
    if not isinstance(queue_payload, dict):
        raise PayloadError(
            code="payload_invalid",
            details={
                "command_name": command_name,
                "field": "queue_payload",
                "expected": "object",
                "payload_type": type(queue_payload).__name__,
            },
        )
    exists = require_bool(raw_payload, "exists", command_name)
    return {
        "branch_name": branch_name,
        "bucket": bucket,
        "work_type": work_type,
        "queue_payload": queue_payload,
        "exists": exists,
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


def _require_string_field(payload: dict, field: str, command_name: str, context: str) -> str:
    """
    Require a non-empty string field in a nested payload.

    Args:
        payload (dict): Payload to inspect.
        field (str): Field name to require.
        command_name (str): Command name for error context.
        context (str): Context prefix for the field.

    Returns:
        str: Field value.

    Raises:
        PayloadError: If the field is missing or invalid.
    """

    if field not in payload:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "string",
            },
        )
    value = payload[field]
    if not isinstance(value, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "string",
                "actual_type": type(value).__name__,
            },
        )
    if not value:
        raise PayloadError(
            code="payload_empty",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "non-empty string",
            },
        )
    return value


def _optional_string_field(payload: dict, field: str, command_name: str, context: str) -> str | None:
    """
    Return an optional string field from a nested payload.

    Args:
        payload (dict): Payload to inspect.
        field (str): Field name to read.
        command_name (str): Command name for error context.
        context (str): Context prefix for the field.

    Returns:
        str | None: Field value or None when missing.

    Raises:
        PayloadError: If the field value is not a string or null.
    """

    value = payload.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "string|null",
                "actual_type": type(value).__name__,
            },
        )
    return value


def _require_int_field(payload: dict, field: str, command_name: str, context: str) -> int:
    """
    Require an integer field in a nested payload.

    Args:
        payload (dict): Payload to inspect.
        field (str): Field name to require.
        command_name (str): Command name for error context.
        context (str): Context prefix for the field.

    Returns:
        int: Field value.

    Raises:
        PayloadError: If the field is missing or invalid.
    """

    if field not in payload:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "integer",
            },
        )
    value = payload[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "integer",
                "actual_type": type(value).__name__,
            },
        )
    return value


def _require_list_field(payload: dict, field: str, command_name: str, context: str) -> list[Any]:
    """
    Require a list field in a nested payload.

    Args:
        payload (dict): Payload to inspect.
        field (str): Field name to require.
        command_name (str): Command name for error context.
        context (str): Context prefix for the field.

    Returns:
        list[Any]: Field value.

    Raises:
        PayloadError: If the field is missing or invalid.
    """

    if field not in payload:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "list",
            },
        )
    value = payload[field]
    if not isinstance(value, list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.{field}",
                "expected": "list",
                "actual_type": type(value).__name__,
            },
        )
    return value


def _parse_lease_payload(lease_payload: dict, command_name: str, context: str) -> dict:
    """
    Parse a lease payload for a queue item.

    Args:
        lease_payload (dict): Lease payload to validate.
        command_name (str): Command name for error context.
        context (str): Context prefix for the lease fields.

    Returns:
        dict: Validated lease payload.

    Raises:
        PayloadError: If the lease payload is invalid.
    """

    schema_version = _require_int_field(lease_payload, "schema_version", command_name, context)
    if schema_version < 1:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": f"{context}.schema_version",
                "expected": "integer >= 1",
                "actual": schema_version,
            },
        )
    resource = _require_string_field(lease_payload, "resource", command_name, context)
    owner_id = _require_string_field(lease_payload, "owner_id", command_name, context)
    created_at = _require_string_field(lease_payload, "created_at", command_name, context)
    heartbeat_at = _require_string_field(lease_payload, "heartbeat_at", command_name, context)
    expires_at = _require_string_field(lease_payload, "expires_at", command_name, context)
    lease_work_id = _optional_string_field(lease_payload, "work_id", command_name, context)
    return {
        "schema_version": schema_version,
        "resource": resource,
        "owner_id": owner_id,
        "created_at": created_at,
        "heartbeat_at": heartbeat_at,
        "expires_at": expires_at,
        "work_id": lease_work_id,
    }


def _parse_queue_item(item: dict, command_name: str, now: str) -> dict:
    """
    Parse a queue item payload entry.

    Args:
        item (dict): Queue item payload entry.
        command_name (str): Command name for error context.
        now (str): Timestamp to use for defaults.

    Returns:
        dict: Validated queue item payload.

    Raises:
        PayloadError: If the item payload is invalid.
    """

    context = "queue_payload.queue"
    work_id = _require_string_field(item, "work_id", command_name, context)
    parent_work_id = _optional_string_field(item, "parent_work_id", command_name, context)
    root_work_id = _require_string_field(item, "root_work_id", command_name, context)
    state = _require_string_field(item, "state", command_name, context)
    kind = _require_string_field(item, "kind", command_name, context)
    target_path = _require_string_field(item, "target_path", command_name, context)
    ctx_path = _require_string_field(item, "ctx_path", command_name, context)
    priority = _require_int_field(item, "priority", command_name, context)
    attempts = _require_int_field(item, "attempts", command_name, context)
    last_error_ref = _optional_string_field(item, "last_error_ref", command_name, context)
    reason_list = _require_list_field(item, "reason", command_name, context)
    if any(not isinstance(reason, str) for reason in reason_list):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.reason",
                "expected": "list[str]",
            },
        )
    created_at = item.get("created_at") or now
    updated_at = item.get("updated_at") or now
    if not isinstance(created_at, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.created_at",
                "expected": "string|null",
                "actual_type": type(created_at).__name__,
            },
        )
    if not isinstance(updated_at, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"{context}.updated_at",
                "expected": "string|null",
                "actual_type": type(updated_at).__name__,
            },
        )
    lease_payload = item.get("lease")
    lease = None
    if lease_payload is not None:
        if not isinstance(lease_payload, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"{context}.lease",
                    "expected": "object|null",
                    "actual_type": type(lease_payload).__name__,
                },
            )
        lease = _parse_lease_payload(lease_payload, command_name, f"{context}.lease")
    return {
        "work_id": work_id,
        "parent_work_id": parent_work_id,
        "root_work_id": root_work_id,
        "state": state,
        "kind": kind,
        "target_path": target_path,
        "ctx_path": ctx_path,
        "priority": priority,
        "attempts": attempts,
        "last_error_ref": last_error_ref,
        "reason": list(reason_list),
        "created_at": created_at,
        "updated_at": updated_at,
        "lease": lease,
    }


def _parse_queue_payload(queue_payload: dict, command_name: str, now: str) -> dict:
    """
    Parse and validate a queue payload structure.

    Args:
        queue_payload (dict): Queue payload to validate.
        command_name (str): Command name for error context.
        now (str): Timestamp to use for defaults.

    Returns:
        dict: Validated queue payload with parsed queue items.

    Raises:
        PayloadError: If the payload is invalid.
    """

    schema_version = _require_int_field(queue_payload, "schema_version", command_name, "queue_payload")
    if schema_version < 1:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "queue_payload.schema_version",
                "expected": "integer >= 1",
                "actual": schema_version,
            },
        )
    repo_id = _optional_string_field(queue_payload, "repo_id", command_name, "queue_payload")
    updated_at = queue_payload.get("updated_at") or now
    if not isinstance(updated_at, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "queue_payload.updated_at",
                "expected": "string|null",
                "actual_type": type(updated_at).__name__,
            },
        )
    queue = _require_list_field(queue_payload, "queue", command_name, "queue_payload")
    items: list[dict] = []
    for entry in queue:
        if not isinstance(entry, dict):
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": "queue_payload.queue",
                    "expected": "list[object]",
                    "actual_type": type(entry).__name__,
                },
            )
        items.append(_parse_queue_item(entry, command_name, now))
    return {
        "schema_version": schema_version,
        "repo_id": repo_id,
        "updated_at": updated_at,
        "queue": items,
    }


def _delete_queue_rows(session: Any, queue_id: str) -> None:
    """
    Delete child rows for a queue_id.

    Args:
        session (Any): SQLAlchemy session.
        queue_id (str): Queue identifier.

    Returns:
        None: Rows are deleted in-place.
    """

    session.query(WorkQueueItemReason).filter_by(queue_id=queue_id).delete()
    session.query(WorkQueueItemLease).filter_by(queue_id=queue_id).delete()
    session.query(WorkQueueItem).filter_by(queue_id=queue_id).delete()


def _write_queue_rows(
    session: Any,
    branch_name: str,
    bucket: str,
    work_type: str,
    queue_payload: dict,
    actor_id: str,
    now: str,
) -> None:
    """
    Persist queue rows for a branch work queue.

    Args:
        session (Any): SQLAlchemy session.
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.
        queue_payload (dict): Parsed queue payload.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for default created_at values.

    Returns:
        None: Rows are written to the database.
    """

    queue_id = _queue_id(branch_name, bucket, work_type)
    existing = session.get(WorkQueue, queue_id)
    record_created_at = existing.created_at if existing else now
    record_created_by = existing.created_by if existing else actor_id
    core = WorkQueue(
        queue_id=queue_id,
        scope="branch",
        branch_name=branch_name,
        bucket=bucket,
        work_kind=work_type,
        schema_version=queue_payload["schema_version"],
        repo_id=queue_payload["repo_id"],
        updated_at=queue_payload["updated_at"],
        created_at=record_created_at,
        created_by=record_created_by,
        updated_by=actor_id,
    )
    session.merge(core)

    _delete_queue_rows(session, queue_id)

    for position, item in enumerate(queue_payload["queue"], start=1):
        session.add(
            WorkQueueItem(
                queue_id=queue_id,
                work_id=item["work_id"],
                parent_work_id=item["parent_work_id"],
                root_work_id=item["root_work_id"],
                state=item["state"],
                kind=item["kind"],
                target_path=item["target_path"],
                ctx_path=item["ctx_path"],
                priority=item["priority"],
                attempts=item["attempts"],
                last_error_ref=item["last_error_ref"],
                position=position,
                created_at=item["created_at"],
                created_by=record_created_by,
                updated_at=item["updated_at"],
                updated_by=actor_id,
            )
        )
        for reason_pos, reason in enumerate(item["reason"], start=1):
            session.add(
                WorkQueueItemReason(
                    queue_id=queue_id,
                    work_id=item["work_id"],
                    position=reason_pos,
                    reason=reason,
                    created_at=item["created_at"],
                    created_by=record_created_by,
                    updated_at=item["updated_at"],
                    updated_by=actor_id,
                )
            )
        lease = item["lease"]
        if lease is not None:
            session.add(
                WorkQueueItemLease(
                    queue_id=queue_id,
                    work_id=item["work_id"],
                    schema_version=lease["schema_version"],
                    resource=lease["resource"],
                    owner_id=lease["owner_id"],
                    lease_work_id=lease["work_id"],
                    created_at=lease["created_at"],
                    heartbeat_at=lease["heartbeat_at"],
                    expires_at=lease["expires_at"],
                    created_by=record_created_by,
                    updated_at=item["updated_at"],
                    updated_by=actor_id,
                )
            )


def _write_queue(
    repo_root: Path,
    payload: dict,
    actor_id: str,
    now: str,
    command_name: str,
) -> None:
    """
    Persist a branch work queue payload using ORM rows.

    Args:
        repo_root (Path): Repository root.
        payload (dict): Parsed payload with branch_name, bucket, work_type, queue_payload, exists.
        actor_id (str): Actor identifier for audit logging.
        now (str): Timestamp for default fields.
        command_name (str): Command name for error context.
    """

    queue_payload = _parse_queue_payload(payload["queue_payload"], command_name, now)
    with sqlite_session(user_db_path(repo_root), must_exist=True) as session:
        _write_queue_rows(
            session,
            payload["branch_name"],
            payload["bucket"],
            payload["work_type"],
            queue_payload,
            actor_id,
            now,
        )


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Write a branch work queue payload for the given branch/bucket/work_type.

    Args:
        payload (dict): Command payload containing payload branch metadata.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing write metadata.

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
        _write_queue(repo_root, parsed, actor_id, now, command_name)
        return ok_result(
            output={
                "branch_name": parsed["branch_name"],
                "bucket": parsed["bucket"],
                "work_type": parsed["work_type"],
                "exists": parsed["exists"],
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
