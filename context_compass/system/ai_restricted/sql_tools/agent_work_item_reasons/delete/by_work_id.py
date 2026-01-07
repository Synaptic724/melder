"""
SQL tool script to delete agent_work_item_reasons by work_id.

Purpose
- Remove reason rows for an agent work item.

Contract
- Requires payload.agent_id and payload.work_id.
- Returns removed count and missing flag.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import delete, select

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
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
    AgentWorkItemReason,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
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


def _count_rows(session, agent_id: str, work_id: str) -> int:
    """
    Count matching agent work item reason rows.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.
        work_id (str): Work item identifier.

    Returns:
        int: Number of matching rows.
    """

    stmt = select(AgentWorkItemReason).where(
        (AgentWorkItemReason.agent_id == agent_id)
        & (AgentWorkItemReason.work_id == work_id)
    )
    return len(session.execute(stmt).scalars().all())


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete agent work item reasons by agent_id and work_id.

    Args:
        payload (dict): Command payload containing payload agent_id/work_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing removed count and missing flag.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        require_string(payload, "actor_id", command_name)
        raw_payload = _require_payload(payload, command_name)
        agent_id = require_string(raw_payload, "agent_id", command_name)
        work_id = require_string(raw_payload, "work_id", command_name)
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
            count = _count_rows(session, agent_id, work_id)
            if count == 0:
                return ok_result(
                    output={
                        "removed": 0,
                        "missing": True,
                        "agent_id": agent_id,
                        "work_id": work_id,
                    }
                )
            session.execute(
                delete(AgentWorkItemReason).where(
                    (AgentWorkItemReason.agent_id == agent_id)
                    & (AgentWorkItemReason.work_id == work_id)
                )
            )
            return ok_result(
                output={
                    "removed": count,
                    "missing": False,
                    "agent_id": agent_id,
                    "work_id": work_id,
                }
            )
    except Exception as exc:
        return exception_result(command_name, exc)
