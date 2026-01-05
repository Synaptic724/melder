"""
SQL tool script for listing hook_registry_user records.

Purpose
- Provide hook registry discovery for the command runner.
- Return enabled hook records with optional phase filtering.

Contract
- Requires actor_id.
- Optional payload.enabled_only defaults to true.
- Optional payload.phase filters by hook phase.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
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
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    HookRegistryUser,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


HOOK_PHASES = ("pre", "activation", "post", "on_error")


def _require_payload(payload: dict, command_name: str) -> dict:
    """
    Require and validate the nested payload object.

    Args:
        payload (dict): Command payload containing a nested payload object.
        command_name (str): Command name for error context.

    Returns:
        dict: Nested payload dictionary, or an empty dict when missing.

    Raises:
        PayloadError: If the payload is invalid.
    """

    raw_payload = payload.get("payload")
    if raw_payload is None:
        return {}
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


def _normalize_phase(phase: str | None, command_name: str) -> str | None:
    """
    Normalize and validate the phase filter.

    Args:
        phase (str | None): Phase value supplied in the payload.
        command_name (str): Command name for error context.

    Returns:
        str | None: Normalized phase or None when not provided.

    Raises:
        PayloadError: If the phase is not one of the supported values.
    """

    if phase is None:
        return None
    if phase not in HOOK_PHASES:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "phase",
                "expected": f"one of {list(HOOK_PHASES)}",
                "actual": phase,
            },
        )
    return phase


def _record_to_dict(row: HookRegistryUser) -> dict:
    """
    Convert a hook registry ORM row into a dictionary.

    Args:
        row (HookRegistryUser): ORM row instance.

    Returns:
        dict: Serialized hook registry payload.
    """

    return {
        "record_id": row.hook_id,
        "hook_id": row.hook_id,
        "phase": row.phase,
        "order": row.order,
        "script_kind": row.script_kind,
        "script_path": row.script_path,
        "entrypoint": row.entrypoint,
        "applies_to_json": row.applies_to_json,
        "enabled": row.enabled,
        "notes": row.notes,
        "owner_id": row.owner_id,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    List hook_registry_user records.

    Args:
        payload (dict): Command payload with optional phase filter.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing hook registry records.

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
        enabled_only = optional_bool(
            raw_payload, "enabled_only", command_name=command_name, default=True
        )
        phase = optional_string(raw_payload, "phase", command_name=command_name)
        phase = _normalize_phase(phase, command_name)
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
            stmt = select(HookRegistryUser)
            if enabled_only:
                stmt = stmt.where(HookRegistryUser.enabled.is_(True))
            if phase is not None:
                stmt = stmt.where(HookRegistryUser.phase == phase)
            stmt = stmt.order_by(
                HookRegistryUser.phase,
                HookRegistryUser.order,
                HookRegistryUser.hook_id,
            )
            rows = session.execute(stmt).scalars().all()
            records = [_record_to_dict(row) for row in rows]
        return ok_result(output={"records": records, "count": len(records)})
    except Exception as exc:
        return exception_result(command_name, exc)
