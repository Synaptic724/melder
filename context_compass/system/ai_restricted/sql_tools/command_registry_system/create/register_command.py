"""
SQL tool script for creating command_registry_system records.

Purpose
- Create a new command registry entry in system.db.
- Persist command metadata for registry-backed command discovery.

Contract
- Requires payload.record_id (command_name), payload, and actor_id.
- record_id must be "<command_name>" and non-empty.
- payload must include: category, entry, summary, requires_certification,
  requires_work_id, registry_schema_version.
- Optional payload fields: feature_flag, notes, spec_json, registry_generated_at,
  registry_updated_at.
"""

from __future__ import annotations

from pathlib import Path

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_bool,
    require_int,
    require_string,
)
from context_compass.system.ai_restricted._shared.sql_command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    CommandRegistrySystem,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
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


def _require_payload_command_name(
    raw_payload: dict,
    command_name_value: str,
    command_name: str,
) -> None:
    """
    Ensure payload.command_name matches the record_id, if supplied.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name_value (str): Parsed command_name from record_id.
        command_name (str): Command name for error context.

    Raises:
        PayloadError: If payload.command_name conflicts with record_id.
    """

    payload_command = raw_payload.get("command_name")
    if payload_command is None:
        return
    if not isinstance(payload_command, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "command_name",
                "expected": "string",
                "payload_type": type(payload_command).__name__,
            },
        )
    if payload_command != command_name_value:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "command_name",
                "expected": command_name_value,
                "actual": payload_command,
            },
        )


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Create a command_registry_system record.

    Args:
        payload (dict): Command payload containing command registry data.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the created record.

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
        command_name_value = _parse_record_id(record_id, command_name)
        _require_payload_command_name(raw_payload, command_name_value, command_name)
        category = require_string(raw_payload, "category", command_name)
        entry = require_string(raw_payload, "entry", command_name)
        summary = require_string(raw_payload, "summary", command_name)
        requires_certification = require_bool(
            raw_payload, "requires_certification", command_name
        )
        requires_work_id = require_bool(raw_payload, "requires_work_id", command_name)
        registry_schema_version = require_int(
            raw_payload, "registry_schema_version", command_name
        )
        feature_flag = optional_string(
            raw_payload, "feature_flag", command_name=command_name
        )
        notes = optional_string(raw_payload, "notes", command_name=command_name)
        spec_json = optional_string(raw_payload, "spec_json", command_name=command_name)
        registry_generated_at = optional_string(
            raw_payload, "registry_generated_at", command_name=command_name
        )
        registry_updated_at = optional_string(
            raw_payload, "registry_updated_at", command_name=command_name
        )
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

    now = utc_now_iso()
    if registry_generated_at is None:
        registry_generated_at = now
    if registry_updated_at is None:
        registry_updated_at = now

    try:
        with sqlite_session(db_path, must_exist=True) as session:
            existing = session.get(CommandRegistrySystem, (command_name_value))
            if existing is not None:
                return error_result(
                    code="record_exists",
                    meaning="Record already exists.",
                    details={
                        "command_name": command_name,
                        "record_id": record_id,
                    },
                )
            row = CommandRegistrySystem(
                command_name=command_name_value,
                category=category,
                entry=entry,
                summary=summary,
                requires_certification=requires_certification,
                requires_work_id=requires_work_id,
                feature_flag=feature_flag,
                notes=notes,
                spec_json=spec_json,
                registry_schema_version=registry_schema_version,
                registry_generated_at=registry_generated_at,
                registry_updated_at=registry_updated_at,
            )
            session.add(row)
            session.flush()
            record = _record_to_dict(row)
        return ok_result(output={"record": record})
    except Exception as exc:
        return exception_result(command_name, exc)
