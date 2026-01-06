"""
SQL tool script for reading command_registry_system records.

Purpose
- Fetch a command registry entry by command_name.
- Return the stored command registry payload.

Contract
- Requires payload.record_id and actor_id.
- record_id must be "<command_name>" and non-empty.
"""

from __future__ import annotations

from pathlib import Path

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
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    CommandRegistrySystem,
)
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _parse_record_id(record_id: str, command_name: str) -> str:
    """
    Parse the record_id into key components.

    Args:
        record_id (str): Record id string in "<command_name>" form.
        command_name (str): Command name for error context.

    Returns:
        str: Parsed command name.

    Raises:
        PayloadError: If record_id is invalid.
    """

    if not record_id.strip():
        raise PayloadError(
            code="record_id_invalid",
            details={
                "command_name": command_name,
                "record_id": record_id,
                "expected": "non-empty record_id",
            },
        )
    return record_id


def _record_id(command_name: str) -> str:
    """
    Build a canonical record_id for a command registry entry.

    Args:
        command_name (str): Command name primary key.

    Returns:
        str: Canonical record_id string.
    """

    return command_name


def _record_to_dict(row: CommandRegistrySystem) -> dict:
    """
    Convert a command registry ORM row into a dictionary.

    Args:
        row (CommandRegistrySystem): ORM row instance.

    Returns:
        dict: Serialized command registry payload.
    """

    record_id = _record_id(row.command_name)
    return {
        "record_id": record_id,
        "command_name": row.command_name,
        "category": row.category,
        "entry": row.entry,
        "summary": row.summary,
        "requires_certification": row.requires_certification,
        "requires_work_id": row.requires_work_id,
        "feature_flag": row.feature_flag,
        "notes": row.notes,
        "spec_json": row.spec_json,
        "registry_schema_version": row.registry_schema_version,
        "registry_generated_at": row.registry_generated_at,
        "registry_updated_at": row.registry_updated_at,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a command_registry_system record.

    Args:
        payload (dict): Command payload containing payload.record_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the command registry record.

    Raises:
        None: All errors are returned as CommandResult payloads.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
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
        record_id = require_string(raw_payload, "record_id", command_name)
        require_string(payload, "actor_id", command_name)
        command_name_value = _parse_record_id(record_id, command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    db_path = system_db_path(repo_root)
    if not db_path.exists():
        return error_result(
            code="db_missing",
            meaning="System database does not exist.",
            details={
                "command_name": command_name,
                "db_path": str(db_path),
            },
        )

    try:
        with sqlite_session(db_path, must_exist=True) as session:
            row = session.get(CommandRegistrySystem, (command_name_value))
            if row is None:
                return error_result(
                    code="record_not_found",
                    meaning="Record not found.",
                    details={
                        "command_name": command_name,
                        "record_id": record_id,
                    },
                )
            record = _record_to_dict(row)
        return ok_result(output={"record": record})
    except Exception as exc:
        return exception_result(command_name, exc)
