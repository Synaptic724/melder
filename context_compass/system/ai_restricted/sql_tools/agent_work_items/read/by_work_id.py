"""
SQL tool script to read an agent_work_items record by work_id.

Purpose
- Fetch a specific agent work item for downstream queue moves.

Contract
- Requires payload.agent_id and payload.work_id.
- Returns an error if the item does not exist.
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
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    user_db_path,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import AgentWorkItem
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


def _row_to_dict(row: AgentWorkItem) -> dict[str, Any]:
    """
    Convert an AgentWorkItem row to a dictionary.

    Args:
        row (AgentWorkItem): ORM row instance.

    Returns:
        dict[str, Any]: Serialized agent work item row.
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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read an agent work item by agent_id and work_id.

    Args:
        payload (dict): Command payload containing payload.agent_id/work_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the agent work item record.

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
            row = session.get(AgentWorkItem, {"agent_id": agent_id, "work_id": work_id})
            if row is None:
                return error_result(
                    code="record_missing",
                    meaning="Agent work item not found.",
                    details={
                        "command_name": command_name,
                        "agent_id": agent_id,
                        "work_id": work_id,
                    },
                )
            return ok_result(output={"record": _row_to_dict(row)})
    except Exception as exc:
        return exception_result(command_name, exc)
