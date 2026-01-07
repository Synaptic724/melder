"""
SQLite query script to list active ctx_path values from work queues.

Purpose
- Return ctx_path values referenced by branch work queues and agent queues.
- Support context_profiles survey workflows that need active ctx_paths.

Contract
- Requires payload.branch_name.
- Optional payload.buckets and payload.work_types filter branch queues.
- Optional payload.include_agent_queues toggles agent work queue collection.
- Errors when the SQLite database is missing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from sqlalchemy import select

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_list,
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
    AgentWorkItem,
    WorkQueue,
    WorkQueueItem,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


DEFAULT_BUCKETS = ("ready", "active")
DEFAULT_WORK_TYPES = ("epic", "story", "task")


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

    Contract:
        - Always returns a dict when validation succeeds.
        - Does not mutate the input payload.
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


def _normalize_string_list(
    values: list[object] | None,
    *,
    field: str,
    command_name: str,
    default: Iterable[str],
) -> list[str]:
    """
    Normalize a list payload into non-empty strings.

    Args:
        values (list[object] | None): Raw payload list value.
        field (str): Field name for error context.
        command_name (str): Command name for error context.
        default (Iterable[str]): Default values when list is missing.

    Returns:
        list[str]: Normalized list of strings.

    Raises:
        PayloadError: If list entries are missing or invalid.

    Contract:
        - Returns defaults when values is None.
        - Rejects non-string or empty string entries.
    """

    if values is None:
        return list(default)
    normalized: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value:
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"{field}[{index}]",
                    "expected": "non-empty string",
                    "payload_type": type(value).__name__,
                },
            )
        normalized.append(value)
    return normalized


def _branch_ctx_paths(
    session,
    branch_name: str,
    buckets: list[str],
    work_types: list[str],
) -> list[str]:
    """
    Collect branch work queue ctx_path values using queue filters.

    Args:
        session (Session): Active SQLAlchemy session.
        branch_name (str): Branch identifier.
        buckets (list[str]): Queue bucket filters.
        work_types (list[str]): Work kind filters.

    Returns:
        list[str]: ctx_path values from branch work queues.

    Contract:
        - Preserves ordering by bucket/work_type/position.
        - Skips null ctx_path values.
    """

    if not buckets or not work_types:
        return []
    stmt = (
        select(WorkQueueItem.ctx_path)
        .join(WorkQueue, WorkQueue.queue_id == WorkQueueItem.queue_id)
        .where(
            WorkQueue.scope == "branch",
            WorkQueue.branch_name == branch_name,
            WorkQueue.bucket.in_(buckets),
            WorkQueue.work_kind.in_(work_types),
        )
        .order_by(WorkQueue.bucket, WorkQueue.work_kind, WorkQueueItem.position)
    )
    rows = session.execute(stmt).all()
    return [row[0] for row in rows if row[0]]


def _agent_ctx_paths(session) -> list[str]:
    """
    Collect ctx_path values from agent work items.

    Args:
        session (Session): Active SQLAlchemy session.

    Returns:
        list[str]: ctx_path values from agent work queues.

    Contract:
        - Preserves ordering by agent_id/position.
        - Skips null ctx_path values.
    """

    stmt = select(AgentWorkItem.ctx_path).order_by(
        AgentWorkItem.agent_id,
        AgentWorkItem.position,
    )
    rows = session.execute(stmt).all()
    return [row[0] for row in rows if row[0]]


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    List active ctx_path values from work queues.

    Args:
        payload (dict): Command payload containing payload.branch_name and filters.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing ctx_paths from work queues.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires actor_id in the outer payload for audit logging.
        - Returns ctx_paths as an ordered list.
        - Includes separate branch and agent ctx_path lists in output.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        require_string(payload, "actor_id", command_name)
        raw_payload = _require_payload(payload, command_name)
        branch_name = require_string(raw_payload, "branch_name", command_name)
        buckets_raw = optional_list(raw_payload, "buckets", command_name=command_name)
        work_types_raw = optional_list(raw_payload, "work_types", command_name=command_name)
        include_agent = optional_bool(
            raw_payload,
            "include_agent_queues",
            command_name=command_name,
            default=True,
        )
        buckets = _normalize_string_list(
            buckets_raw,
            field="buckets",
            command_name=command_name,
            default=DEFAULT_BUCKETS,
        )
        work_types = _normalize_string_list(
            work_types_raw,
            field="work_types",
            command_name=command_name,
            default=DEFAULT_WORK_TYPES,
        )
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
            branch_ctx_paths = _branch_ctx_paths(session, branch_name, buckets, work_types)
            agent_ctx_paths = []
            if include_agent:
                agent_ctx_paths = _agent_ctx_paths(session)
        ctx_paths = branch_ctx_paths + agent_ctx_paths
        return ok_result(
            output={
                "branch_name": branch_name,
                "branch_ctx_paths": branch_ctx_paths,
                "agent_ctx_paths": agent_ctx_paths,
                "ctx_paths": ctx_paths,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
