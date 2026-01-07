"""
SQL tool script to ensure a work_queues record exists.

Purpose
- Create a branch/global work queue row when missing.
- Preserve existing rows without mutation when already present.

Contract
- Requires payload.queue_id, payload.scope, payload.bucket, payload.work_kind,
  payload.schema_version, and actor_id.
- scope must be "branch" or "global".
- branch scopes require payload.branch_name.
- Returns the persisted record and whether it already existed.
"""

from __future__ import annotations

from pathlib import Path

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
    WorkQueue,
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


def _parse_queue_payload(raw_payload: dict, command_name: str) -> dict:
    """
    Parse queue fields from the raw payload.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict: Parsed queue fields.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    queue_id = require_string(raw_payload, "queue_id", command_name)
    scope = require_choice(raw_payload, "scope", command_name, SCOPES)
    branch_name = optional_string(raw_payload, "branch_name", command_name=command_name)
    bucket = require_string(raw_payload, "bucket", command_name)
    work_kind = require_string(raw_payload, "work_kind", command_name)
    schema_version = require_int(raw_payload, "schema_version", command_name)
    repo_id = optional_string(raw_payload, "repo_id", command_name=command_name)

    if scope == "branch" and not branch_name:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": "branch_name",
                "expected": "branch_name for branch scope",
            },
        )
    if scope == "global" and branch_name is not None:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "branch_name",
                "expected": "null for global scope",
                "actual": branch_name,
            },
        )

    return {
        "queue_id": queue_id,
        "scope": scope,
        "branch_name": branch_name,
        "bucket": bucket,
        "work_kind": work_kind,
        "schema_version": schema_version,
        "repo_id": repo_id,
    }


def _record_to_dict(row: WorkQueue) -> dict:
    """
    Serialize a WorkQueue ORM row into a dictionary.

    Args:
        row (WorkQueue): ORM row instance.

    Returns:
        dict: Serialized work queue fields.
    """

    return {
        "queue_id": row.queue_id,
        "scope": row.scope,
        "branch_name": row.branch_name,
        "bucket": row.bucket,
        "work_kind": row.work_kind,
        "schema_version": row.schema_version,
        "repo_id": row.repo_id,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Ensure a work_queues record exists for a queue_id.

    Args:
        payload (dict): Command payload containing payload.queue fields.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the queue record and existence flag.

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
        queue_fields = _parse_queue_payload(raw_payload, command_name)
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
            existing = session.get(WorkQueue, queue_fields["queue_id"])
            if existing is not None:
                return ok_result(
                    output={
                        "record": _record_to_dict(existing),
                        "exists": True,
                    }
                )
            row = WorkQueue(
                queue_id=queue_fields["queue_id"],
                scope=queue_fields["scope"],
                branch_name=queue_fields["branch_name"],
                bucket=queue_fields["bucket"],
                work_kind=queue_fields["work_kind"],
                schema_version=queue_fields["schema_version"],
                repo_id=queue_fields["repo_id"],
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
            session.add(row)
            session.flush()
            return ok_result(
                output={
                    "record": _record_to_dict(row),
                    "exists": False,
                }
            )
    except Exception as exc:
        return exception_result(command_name, exc)
