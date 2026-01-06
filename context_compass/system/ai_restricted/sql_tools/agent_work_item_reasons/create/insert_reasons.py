"""
SQL tool script to insert agent_work_item_reasons records.

Purpose
- Persist ordered reason entries for an agent work item.

Contract
- Requires payload.agent_id, payload.work_id, and payload.reasons (list).
- Inserts reasons in order with 0-based positions.
- Returns the inserted reasons and count.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_list,
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
    AgentWorkItemReason,
)
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


def _normalize_reasons(raw_payload: dict, command_name: str) -> list[str]:
    """
    Normalize and validate reasons list.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        list[str]: Normalized reasons list.

    Raises:
        PayloadError: If reasons are missing or invalid.
    """

    reasons = optional_list(raw_payload, "reasons", command_name=command_name)
    if reasons is None:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": "reasons",
                "expected": "list of strings",
            },
        )
    normalized: list[str] = []
    for entry in reasons:
        if not isinstance(entry, str) or not entry.strip():
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": "reasons",
                    "expected": "non-empty string entries",
                    "actual": entry,
                },
            )
        normalized.append(entry)
    return normalized


def _existing_reasons(session, agent_id: str, work_id: str) -> bool:
    """
    Check whether reasons already exist for an agent work item.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        work_id (str): Work item identifier.

    Returns:
        bool: True if any reason rows already exist.
    """

    stmt = select(AgentWorkItemReason).where(
        (AgentWorkItemReason.agent_id == agent_id)
        & (AgentWorkItemReason.work_id == work_id)
    )
    return session.execute(stmt).first() is not None


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Insert reason rows for an agent work item.

    Args:
        payload (dict): Command payload containing payload agent_id/work_id/reasons.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing inserted reason entries.

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
        reasons = _normalize_reasons(raw_payload, command_name)
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
            if _existing_reasons(session, agent_id, work_id):
                return error_result(
                    code="record_exists",
                    meaning="Reasons already exist for this agent work item.",
                    details={
                        "command_name": command_name,
                        "agent_id": agent_id,
                        "work_id": work_id,
                    },
                )
            rows: list[dict[str, Any]] = []
            for index, reason in enumerate(reasons):
                row = AgentWorkItemReason(
                    agent_id=agent_id,
                    work_id=work_id,
                    position=index,
                    reason=reason,
                    created_at=created_timestamp,
                    created_by=actor_id,
                    updated_at=created_timestamp,
                    updated_by=actor_id,
                )
                session.add(row)
                rows.append(
                    {
                        "agent_id": agent_id,
                        "work_id": work_id,
                        "position": index,
                        "reason": reason,
                        "created_at": created_timestamp,
                        "created_by": actor_id,
                        "updated_at": created_timestamp,
                        "updated_by": actor_id,
                    }
                )
            session.flush()
            return ok_result(output={"reasons": rows, "count": len(rows)})
    except Exception as exc:
        return exception_result(command_name, exc)
