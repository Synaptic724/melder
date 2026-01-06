"""
SQL tool script to update work_queues timestamps.

Purpose
- Touch a work queue record to reflect item mutations.

Contract
- Requires payload.queue_id and actor_id.
- Updates updated_at/updated_by on the queue row.
- Returns an error if the queue does not exist.
"""

from __future__ import annotations

from pathlib import Path

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
from context_compass.system.ai_restricted.database_management.user_orm_models import WorkQueue
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
    Touch a work queue record.

    Args:
        payload (dict): Command payload containing payload.queue_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the updated queue record.

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
            row = session.get(WorkQueue, queue_id)
            if row is None:
                return error_result(
                    code="record_missing",
                    meaning="Work queue record not found.",
                    details={
                        "command_name": command_name,
                        "queue_id": queue_id,
                    },
                )
            row.updated_at = now
            row.updated_by = actor_id
            session.flush()
            return ok_result(output={"record": _record_to_dict(row)})
    except Exception as exc:
        return exception_result(command_name, exc)
