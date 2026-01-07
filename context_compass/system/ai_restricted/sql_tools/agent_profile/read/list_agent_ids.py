"""
SQL tool script to list agent_id values from agent_profile.

Purpose
- Provide a lightweight listing of agent identifiers with profiles.
- Support validation workflows that enumerate agent profile records.

Contract
- actor_id is required for audit logging.
- payload is optional and ignored.
- Returns agent_ids in ascending order.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

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
from context_compass.system.ai_restricted.database_management.user_orm_models import AgentProfile
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _fetch_agent_ids(repo_root: Path) -> list[str]:
    """
    Fetch sorted agent identifiers from agent_profile.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Sorted list of agent identifiers.
    """

    db_path = user_db_path(repo_root)
    with sqlite_session(db_path, must_exist=True) as session:
        result = session.execute(select(AgentProfile.agent_id).order_by(AgentProfile.agent_id))
        return [row[0] for row in result.fetchall()]


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    List agent_ids present in agent_profile.

    Args:
        payload (dict): Command payload (payload field ignored).
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing a list of agent_ids.

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
        agent_ids = _fetch_agent_ids(repo_root)
        return ok_result(output={"agent_ids": agent_ids})
    except Exception as exc:
        return exception_result(command_name, exc)
