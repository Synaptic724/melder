"""
SQLite query script to delete agent-scoped records across user tables.

Purpose
- Delete agent_profile, self_context, and agent_work_queue rows for an agent_id.
- Provide a single transaction for agent cleanup flows.

Contract
- Requires payload.agent_id.
- actor_id is required for audit logging.
- Returns per-table delete counts and a total_deleted count.
- Errors when the SQLite user database is missing.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

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
    AgentProfile,
    AgentProfileCertification,
    AgentProfileLastCommand,
    AgentProfileLastCommandArg,
    AgentWorkItem,
    AgentWorkItemLease,
    AgentWorkItemReason,
    AgentWorkQueue,
    SelfContext,
    SelfContextNonNegotiable,
    SelfContextOpenQuestion,
    SelfContextOpinionItem,
    SelfContextSkillReceipt,
    SelfContextStyleModelItem,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


DELETE_TARGETS: tuple[tuple[str, type], ...] = (
    ("agent_profile_last_command_args", AgentProfileLastCommandArg),
    ("agent_profile_last_command", AgentProfileLastCommand),
    ("agent_profile_certification", AgentProfileCertification),
    ("agent_profile", AgentProfile),
    ("self_context_non_negotiables", SelfContextNonNegotiable),
    ("self_context_style_model_items", SelfContextStyleModelItem),
    ("self_context_skill_receipts", SelfContextSkillReceipt),
    ("self_context_open_questions", SelfContextOpenQuestion),
    ("self_context_opinion_items", SelfContextOpinionItem),
    ("self_context", SelfContext),
    ("agent_work_item_reasons", AgentWorkItemReason),
    ("agent_work_item_lease", AgentWorkItemLease),
    ("agent_work_items", AgentWorkItem),
    ("agent_work_queue", AgentWorkQueue),
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


def _delete_agent_rows(session: Session, agent_id: str) -> dict[str, int]:
    """
    Delete agent-scoped rows across user tables.

    Args:
        session (Session): Active SQLAlchemy session.
        agent_id (str): Agent identifier.

    Returns:
        dict[str, int]: Map of table name to rows deleted.

    Contract:
        - Deletes child tables before parent tables.
        - Uses synchronize_session=False for deterministic deletes.
    """

    deleted: dict[str, int] = {}
    for table_name, model in DELETE_TARGETS:
        count = (
            session.query(model)
            .filter_by(agent_id=agent_id)
            .delete(synchronize_session=False)
        )
        deleted[table_name] = int(count or 0)
    return deleted


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete agent records for a given agent_id.

    Args:
        payload (dict): Command payload containing payload.agent_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing delete counts for each table.

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
            deleted = _delete_agent_rows(session, agent_id)
        total_deleted = sum(deleted.values())
        return ok_result(
            output={
                "agent_id": agent_id,
                "deleted": deleted,
                "total_deleted": total_deleted,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
