"""
SQLite query script to read agent_profile payloads.

Purpose
- Load agent_profile payloads by agent_id.
- Return a complete payload reconstructed from normalized tables.

Contract
- Requires payload.agent_id.
- actor_id is required for audit logging.
- Returns record payload and exists flag.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.agent_profile_store import default_profile
from context_compass.system.ai_restricted._shared.certification_state import default_certification_state
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
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    AgentProfile,
    AgentProfileCertification,
    AgentProfileLastCommand,
    AgentProfileLastCommandArg,
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


def _load_last_command_payload(session, agent_id: str) -> dict | None:
    """
    Load the last_command payload for an agent profile.

    Args:
        session: SQLAlchemy session scoped to user.db.
        agent_id (str): Agent identifier.

    Returns:
        dict | None: last_command payload or None when absent.
    """

    last_command = session.get(AgentProfileLastCommand, agent_id)
    if last_command is None or not last_command.name:
        return None
    args = (
        session.query(AgentProfileLastCommandArg)
        .filter_by(agent_id=agent_id)
        .order_by(AgentProfileLastCommandArg.position)
        .all()
    )
    return {
        "name": last_command.name,
        "args": [row.value for row in args],
    }


def _load_certification_payload(cert: AgentProfileCertification | None) -> dict:
    """
    Load certification payload from the ORM row or defaults.

    Args:
        cert (AgentProfileCertification | None): Certification ORM row.

    Returns:
        dict: Certification payload for agent_profile.
    """

    if cert is None:
        return default_certification_state()
    return {
        "schema_version": cert.schema_version,
        "state": cert.state,
        "certified": cert.certified,
        "certified_at": cert.certified_at,
        "approved_at": cert.approved_at,
        "approval_token": cert.approval_token,
        "approved_by": cert.approved_by,
        "self_certification_hash": cert.self_certification_hash,
        "notes": cert.notes,
    }


def _build_profile_payload(
    core: AgentProfile,
    *,
    now: str,
    last_command_payload: dict | None,
    certification_payload: dict,
) -> dict:
    """
    Build the agent_profile payload from ORM rows.

    Args:
        core (AgentProfile): Core profile ORM row.
        now (str): Fallback timestamp when stored fields are missing.
        last_command_payload (dict | None): Parsed last_command payload.
        certification_payload (dict): Parsed certification payload.

    Returns:
        dict: Serialized agent_profile payload.
    """

    return {
        "schema_version": core.schema_version,
        "agent_id": core.agent_id,
        "agent_kind": core.agent_kind,
        "created_at": core.created_at or now,
        "updated_at": core.updated_at or now,
        "status": core.status or "inactive",
        "last_checkin_at": core.last_checkin_at,
        "last_checkout_at": core.last_checkout_at,
        "agent_role": core.agent_role,
        "model_name": core.model_name,
        "current_task_id": core.current_task_id,
        "current_target": core.current_target,
        "notes": core.notes,
        "runtime": core.runtime,
        "last_command": last_command_payload,
        "certification_state": certification_payload,
    }


def _load_profile_snapshot(
    session,
    agent_id: str,
    now: str,
) -> tuple[dict, bool]:
    """
    Load agent_profile payload data from ORM rows.

    Args:
        session: SQLAlchemy session scoped to user.db.
        agent_id (str): Agent identifier.
        now (str): Current timestamp for default payloads.

    Returns:
        tuple[dict, bool]: Agent profile payload and exists flag.
    """

    core = session.get(AgentProfile, agent_id)
    if core is None:
        return default_profile(agent_id, now, agent_role="unassigned"), False
    cert = session.get(AgentProfileCertification, agent_id)
    last_command_payload = _load_last_command_payload(session, agent_id)
    certification_payload = _load_certification_payload(cert)
    payload = _build_profile_payload(
        core,
        now=now,
        last_command_payload=last_command_payload,
        certification_payload=certification_payload,
    )
    return payload, True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read an agent_profile payload by agent_id.

    Args:
        payload (dict): Command payload containing payload.agent_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing agent_profile payload and existence flag.

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
        with sqlite_session(db_path, must_exist=True) as session:
            record, exists = _load_profile_snapshot(session, agent_id, now)
        if not isinstance(record, dict):
            return error_result(
                code="payload_invalid",
                meaning="agent_profile record returned invalid payload.",
                details={
                    "command_name": command_name,
                    "agent_id": agent_id,
                    "payload_type": type(record).__name__,
                },
            )
        return ok_result(output={"agent_id": agent_id, "record": record, "exists": exists})
    except Exception as exc:
        return exception_result(command_name, exc)
