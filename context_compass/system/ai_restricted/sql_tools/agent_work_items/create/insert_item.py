"""
SQL tool script to insert agent_work_items records.

Purpose
- Insert a work item row for a specific agent queue.
- Allocate the next queue position deterministically.

Contract
- Requires payload.agent_id and payload.work_id.
- Requires state, kind, target_path, ctx_path, root_work_id, priority.
- Assigns the next position based on existing queue entries.
- Returns an error when the work_id already exists for the agent.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import func, select

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
    optional_string,
    require_int,
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
from context_compass.system.ai_restricted.database_management.user_orm_models import AgentWorkItem
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


ALLOWED_STATES = ("queued", "leased", "in_progress", "done", "failed", "cancelled")


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


def _require_state(raw_payload: dict, command_name: str) -> str:
    """
    Require a valid work item state.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        str: Validated state value.

    Raises:
        PayloadError: If the state is missing or invalid.
    """

    state = require_string(raw_payload, "state", command_name)
    if state not in ALLOWED_STATES:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "state",
                "expected": f"one of {list(ALLOWED_STATES)}",
                "actual": state,
            },
        )
    return state


def _record_to_dict(row: AgentWorkItem) -> dict:
    """
    Serialize an AgentWorkItem ORM row into a dictionary.

    Args:
        row (AgentWorkItem): ORM row instance.

    Returns:
        dict: Serialized agent work item fields.
    """

    return {
        "agent_id": row.agent_id,
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


def _next_position(session, agent_id: str) -> int:
    """
    Compute the next position for an agent queue.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.

    Returns:
        int: Next queue position (0-based).
    """

    result = session.execute(
        select(func.max(AgentWorkItem.position)).where(AgentWorkItem.agent_id == agent_id)
    )
    max_pos = result.scalar_one_or_none()
    if max_pos is None:
        return 0
    return int(max_pos) + 1


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Insert a work item into an agent work queue.

    Args:
        payload (dict): Command payload containing payload work item fields.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the inserted work item record.

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
        agent_id = require_string(raw_payload, "agent_id", command_name)
        work_id = require_string(raw_payload, "work_id", command_name)
        state = _require_state(raw_payload, command_name)
        kind = require_string(raw_payload, "kind", command_name)
        target_path = require_string(raw_payload, "target_path", command_name)
        ctx_path = require_string(raw_payload, "ctx_path", command_name)
        root_work_id = require_string(raw_payload, "root_work_id", command_name)
        priority = require_int(raw_payload, "priority", command_name)
        attempts = optional_int(raw_payload, "attempts", command_name=command_name, default=0)
        last_error_ref = optional_string(raw_payload, "last_error_ref", command_name=command_name)
        parent_work_id = optional_string(raw_payload, "parent_work_id", command_name=command_name)
        created_at = optional_string(raw_payload, "created_at", command_name=command_name)
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
    created_timestamp = created_at or now
    try:
        with sqlite_session(db_path, must_exist=True) as session:
            existing = session.get(AgentWorkItem, {"agent_id": agent_id, "work_id": work_id})
            if existing is not None:
                return error_result(
                    code="record_exists",
                    meaning="Agent work item already exists.",
                    details={
                        "command_name": command_name,
                        "agent_id": agent_id,
                        "work_id": work_id,
                    },
                )
            position = _next_position(session, agent_id)
            row = AgentWorkItem(
                agent_id=agent_id,
                work_id=work_id,
                parent_work_id=parent_work_id,
                root_work_id=root_work_id,
                state=state,
                kind=kind,
                target_path=target_path,
                ctx_path=ctx_path,
                priority=priority,
                attempts=attempts or 0,
                last_error_ref=last_error_ref,
                position=position,
                created_at=created_timestamp,
                created_by=actor_id,
                updated_at=created_timestamp,
                updated_by=actor_id,
            )
            session.add(row)
            session.flush()
            return ok_result(output={"record": _record_to_dict(row)})
    except Exception as exc:
        return exception_result(command_name, exc)
