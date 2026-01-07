"""
SQLite query script to persist agent_profile payloads.

Purpose
- Persist agent_profile payloads for a specific agent.
- Return the stored payload after the write.

Contract
- Requires payload.agent_id, payload.agent_profile, and payload.exists.
- Writes are performed within the SQLite transaction scope.
- Returns the stored payload after persistence.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
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
)
from context_compass.system.ai_restricted._shared.certification_state import default_certification_state
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


def _require_profile(raw_payload: dict, command_name: str) -> dict:
    """
    Require the agent_profile payload object.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: Agent profile payload.

    Raises:
        PayloadError: If agent_profile is missing or invalid.

    Contract:
        - agent_profile must be a JSON object.
    """

    profile_payload = raw_payload.get("agent_profile")
    if not isinstance(profile_payload, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "agent_profile",
                "expected": "object",
                "payload_type": type(profile_payload).__name__,
            },
        )
    return profile_payload


def _require_string(payload: dict, key: str) -> str:
    """
    Require a non-empty string payload field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str: Field value.

    Raises:
        ValueError: If the field is missing or not a string.
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"agent_profile.{key} must be a non-empty string.")
    return value


def _optional_string(payload: dict, key: str) -> str | None:
    """
    Return an optional string field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        str | None: Field value if present.

    Raises:
        ValueError: If the field is not a string or null.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"agent_profile.{key} must be a string or null.")
    return value


def _optional_bool(payload: dict, key: str) -> bool | None:
    """
    Return an optional boolean field.

    Args:
        payload (dict): Payload to inspect.
        key (str): Field name to extract.

    Returns:
        bool | None: Field value if present.

    Raises:
        ValueError: If the field is not a boolean or null.
    """

    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"agent_profile.{key} must be a boolean or null.")
    return value


def _parse_last_command(payload: dict) -> tuple[str | None, list[str]]:
    """
    Parse last_command payload fields.

    Args:
        payload (dict): Profile payload.

    Returns:
        tuple[str | None, list[str]]: Command name and args list.

    Raises:
        ValueError: If last_command payload is invalid.
    """

    last_command = payload.get("last_command")
    if last_command is None:
        return None, []
    if not isinstance(last_command, dict):
        raise ValueError("agent_profile.last_command must be an object or null.")
    name = last_command.get("name")
    args = last_command.get("args")
    if not isinstance(name, str) or not name:
        raise ValueError("agent_profile.last_command.name must be a non-empty string.")
    if not isinstance(args, list):
        raise ValueError("agent_profile.last_command.args must be a list.")
    arg_values: list[str] = []
    for value in args:
        if not isinstance(value, str):
            raise ValueError("agent_profile.last_command.args entries must be strings.")
        arg_values.append(value)
    return name, arg_values


def _parse_certification_state(payload: dict) -> dict:
    """
    Parse certification_state payload fields.

    Args:
        payload (dict): Profile payload.

    Returns:
        dict: Certification state payload.

    Raises:
        ValueError: If certification_state payload is invalid.
    """

    state = payload.get("certification_state")
    if state is None:
        return default_certification_state()
    if not isinstance(state, dict):
        raise ValueError("agent_profile.certification_state must be a JSON object.")
    return state


def _parse_profile_payload(agent_id: str, payload: dict) -> dict:
    """
    Validate and normalize an agent_profile payload.

    Args:
        agent_id (str): Expected agent identifier.
        payload (dict): Profile payload to validate.

    Returns:
        dict: Parsed payload fields.

    Raises:
        ValueError: If payload fields are invalid.
    """

    if payload.get("agent_id") != agent_id:
        raise ValueError("agent_profile.agent_id must match the requested agent_id.")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, int) or schema_version < 1:
        raise ValueError("agent_profile.schema_version must be an integer >= 1.")

    status = _require_string(payload, "status")
    agent_role = _require_string(payload, "agent_role")
    created_at = _require_string(payload, "created_at")
    updated_at = _require_string(payload, "updated_at")
    last_checkin_at = _optional_string(payload, "last_checkin_at")
    last_checkout_at = _optional_string(payload, "last_checkout_at")
    agent_kind = _optional_string(payload, "agent_kind")
    model_name = _optional_string(payload, "model_name")
    runtime = _optional_string(payload, "runtime")
    current_task_id = _optional_string(payload, "current_task_id")
    current_target = _optional_string(payload, "current_target")
    notes = _optional_string(payload, "notes")
    command_name, command_args = _parse_last_command(payload)
    certification = _parse_certification_state(payload)

    cert_schema_version = certification.get("schema_version")
    if not isinstance(cert_schema_version, int) or cert_schema_version < 1:
        raise ValueError("agent_profile.certification_state.schema_version must be >= 1.")
    cert_state = _require_string(certification, "state")
    certified = _optional_bool(certification, "certified")
    if certified is None:
        raise ValueError("agent_profile.certification_state.certified must be a boolean.")

    return {
        "schema_version": schema_version,
        "status": status,
        "agent_role": agent_role,
        "created_at": created_at,
        "updated_at": updated_at,
        "last_checkin_at": last_checkin_at,
        "last_checkout_at": last_checkout_at,
        "agent_kind": agent_kind,
        "model_name": model_name,
        "runtime": runtime,
        "current_task_id": current_task_id,
        "current_target": current_target,
        "notes": notes,
        "command_name": command_name,
        "command_args": command_args,
        "cert_schema_version": cert_schema_version,
        "cert_state": cert_state,
        "certified": certified,
        "certified_at": _optional_string(certification, "certified_at"),
        "approved_at": _optional_string(certification, "approved_at"),
        "approval_token": _optional_string(certification, "approval_token"),
        "approved_by": _optional_string(certification, "approved_by"),
        "self_certification_hash": _optional_string(certification, "self_certification_hash"),
        "cert_notes": _optional_string(certification, "notes"),
    }


def _clear_child_rows(session, agent_id: str) -> None:
    """
    Remove child rows for an agent_profile record.

    Args:
        session: SQLAlchemy session scoped to user.db.
        agent_id (str): Agent identifier to clear.
    """

    session.query(AgentProfileCertification).filter_by(agent_id=agent_id).delete()
    session.query(AgentProfileLastCommand).filter_by(agent_id=agent_id).delete()
    session.query(AgentProfileLastCommandArg).filter_by(agent_id=agent_id).delete()


def _write_certification(
    session,
    agent_id: str,
    parsed: dict,
    *,
    created_at: str,
    created_by: str,
    updated_at: str,
    actor_id: str,
) -> None:
    """
    Persist certification rows for an agent profile.

    Args:
        session: SQLAlchemy session scoped to user.db.
        agent_id (str): Agent identifier.
        parsed (dict): Parsed payload fields.
        created_at (str): Created timestamp.
        created_by (str): Created by identifier.
        updated_at (str): Updated timestamp.
        actor_id (str): Actor identifier for updates.
    """

    cert_row = AgentProfileCertification(
        agent_id=agent_id,
        schema_version=parsed["cert_schema_version"],
        state=parsed["cert_state"],
        certified=parsed["certified"],
        certified_at=parsed["certified_at"],
        approved_at=parsed["approved_at"],
        approval_token=parsed["approval_token"],
        approved_by=parsed["approved_by"],
        self_certification_hash=parsed["self_certification_hash"],
        notes=parsed["cert_notes"],
        created_at=created_at,
        created_by=created_by,
        updated_at=updated_at,
        updated_by=actor_id,
    )
    session.add(cert_row)


def _write_last_command(
    session,
    agent_id: str,
    command_name: str | None,
    command_args: list[str],
    *,
    created_at: str,
    created_by: str,
    updated_at: str,
    actor_id: str,
) -> None:
    """
    Persist last command rows for an agent profile.

    Args:
        session: SQLAlchemy session scoped to user.db.
        agent_id (str): Agent identifier.
        command_name (str | None): Command name.
        command_args (list[str]): Command args list.
        created_at (str): Created timestamp.
        created_by (str): Created by identifier.
        updated_at (str): Updated timestamp.
        actor_id (str): Actor identifier for updates.
    """

    if command_name is None:
        return
    command_row = AgentProfileLastCommand(
        agent_id=agent_id,
        name=command_name,
        created_at=created_at,
        created_by=created_by,
        updated_at=updated_at,
        updated_by=actor_id,
    )
    session.add(command_row)
    for idx, arg_value in enumerate(command_args, start=1):
        session.add(
            AgentProfileLastCommandArg(
                agent_id=agent_id,
                position=idx,
                value=arg_value,
                created_at=created_at,
                created_by=created_by,
                updated_at=updated_at,
                updated_by=actor_id,
            )
        )


def _upsert_profile(
    session,
    agent_id: str,
    parsed: dict,
    actor_id: str,
) -> None:
    """
    Upsert the agent_profile record and child rows.

    Args:
        session: SQLAlchemy session scoped to user.db.
        agent_id (str): Agent identifier.
        parsed (dict): Parsed payload fields.
        actor_id (str): Actor identifier for audit logging.
    """

    existing = session.get(AgentProfile, agent_id)
    record_created_at = existing.created_at if existing else parsed["created_at"]
    record_created_by = existing.created_by if existing else actor_id

    core = AgentProfile(
        agent_id=agent_id,
        schema_version=parsed["schema_version"],
        agent_kind=parsed["agent_kind"],
        status=parsed["status"],
        agent_role=parsed["agent_role"],
        model_name=parsed["model_name"],
        runtime=parsed["runtime"],
        current_task_id=parsed["current_task_id"],
        current_target=parsed["current_target"],
        notes=parsed["notes"],
        last_checkin_at=parsed["last_checkin_at"],
        last_checkout_at=parsed["last_checkout_at"],
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=parsed["updated_at"],
        updated_by=actor_id,
    )
    session.merge(core)
    _clear_child_rows(session, agent_id)
    _write_certification(
        session,
        agent_id,
        parsed,
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=parsed["updated_at"],
        actor_id=actor_id,
    )
    _write_last_command(
        session,
        agent_id,
        parsed["command_name"],
        parsed["command_args"],
        created_at=record_created_at,
        created_by=record_created_by,
        updated_at=parsed["updated_at"],
        actor_id=actor_id,
    )


def _build_last_command_payload(session, agent_id: str) -> dict | None:
    """
    Build the last_command payload from persisted rows.

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


def _build_certification_payload(parsed: dict) -> dict:
    """
    Build the certification_state payload from parsed fields.

    Args:
        parsed (dict): Parsed payload fields.

    Returns:
        dict: Certification payload for agent_profile.
    """

    return {
        "schema_version": parsed["cert_schema_version"],
        "state": parsed["cert_state"],
        "certified": parsed["certified"],
        "certified_at": parsed["certified_at"],
        "approved_at": parsed["approved_at"],
        "approval_token": parsed["approval_token"],
        "approved_by": parsed["approved_by"],
        "self_certification_hash": parsed["self_certification_hash"],
        "notes": parsed["cert_notes"],
    }


def _build_record_payload(
    core: AgentProfile,
    *,
    last_command_payload: dict | None,
    certification_payload: dict,
) -> dict:
    """
    Build the agent_profile payload from ORM rows.

    Args:
        core (AgentProfile): Core profile ORM row.
        last_command_payload (dict | None): Parsed last_command payload.
        certification_payload (dict): Parsed certification payload.

    Returns:
        dict: Serialized agent_profile payload.
    """

    return {
        "schema_version": core.schema_version,
        "agent_id": core.agent_id,
        "agent_kind": core.agent_kind,
        "created_at": core.created_at,
        "updated_at": core.updated_at,
        "status": core.status,
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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Persist an agent_profile payload to SQLite.

    Args:
        payload (dict): Command payload containing payload.agent_id/agent_profile.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the stored agent_profile payload.

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
        exists = require_bool(raw_payload, "exists", command_name)
        agent_profile = _require_profile(raw_payload, command_name)
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
        parsed = _parse_profile_payload(agent_id, agent_profile)
        with sqlite_session(db_path, must_exist=True) as session:
            _upsert_profile(session, agent_id, parsed, actor_id)
            session.flush()
            core = session.get(AgentProfile, agent_id)
            if core is None:
                return error_result(
                    code="payload_invalid",
                    meaning="agent_profile write did not persist the record.",
                    details={
                        "command_name": command_name,
                        "agent_id": agent_id,
                    },
                )
            last_command_payload = _build_last_command_payload(session, agent_id)
            certification_payload = _build_certification_payload(parsed)
            record = _build_record_payload(
                core,
                last_command_payload=last_command_payload,
                certification_payload=certification_payload,
            )
        return ok_result(output={"agent_id": agent_id, "record": record, "exists": True})
    except Exception as exc:
        return exception_result(command_name, exc)
