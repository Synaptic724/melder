"""
SQL tool script for updating command_registry_user records.

Purpose
- Update command registry fields for a user command entry.
- Maintain registry_updated_at timestamps.

Contract
- Requires payload.record_id (command_name), payload, and actor_id.
- record_id must be "<command_name>" and non-empty.
- At least one updatable field must be supplied in payload.
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
    user_db_path,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    CommandRegistryUser,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


UPDATABLE_FIELDS = (
    "category",
    "entry",
    "summary",
    "requires_certification",
    "requires_work_id",
    "feature_flag",
    "notes",
    "spec_json",
    "registry_schema_version",
    "registry_generated_at",
    "registry_updated_at",
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


def _record_to_dict(row: CommandRegistryUser) -> dict:
    """
    Convert a command registry ORM row into a dictionary.

    Args:
        row (CommandRegistryUser): ORM row instance.

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


def _require_update_payload(raw_payload: dict, command_name: str) -> None:
    """
    Require that at least one updatable field is present.

    Args:
        raw_payload (dict): Parsed payload object.
        command_name (str): Command name for error context.

    Raises:
        PayloadError: If no updatable fields are present.
    """

    if not any(field in raw_payload for field in UPDATABLE_FIELDS):
        raise PayloadError(
            code="payload_empty",
            details={
                "command_name": command_name,
                "expected": f"payload includes one of {UPDATABLE_FIELDS}",
            },
        )


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
    Update a command_registry_user record.

    Args:
        payload (dict): Command payload containing payload.record_id and updates.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the updated record.

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
        actor_id = require_string(payload, "actor_id", command_name)
        command_name_value = _parse_record_id(record_id, command_name)
        _require_payload_command_name(raw_payload, command_name_value, command_name)
        _require_update_payload(raw_payload, command_name)
        category = (
            require_string(raw_payload, "category", command_name)
            if "category" in raw_payload
            else None
        )
        entry = (
            require_string(raw_payload, "entry", command_name)
            if "entry" in raw_payload
            else None
        )
        summary = (
            require_string(raw_payload, "summary", command_name)
            if "summary" in raw_payload
            else None
        )
        requires_certification = (
            require_bool(raw_payload, "requires_certification", command_name)
            if "requires_certification" in raw_payload
            else None
        )
        requires_work_id = (
            require_bool(raw_payload, "requires_work_id", command_name)
            if "requires_work_id" in raw_payload
            else None
        )
        registry_schema_version = (
            require_int(raw_payload, "registry_schema_version", command_name)
            if "registry_schema_version" in raw_payload
            else None
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
    try:
        with sqlite_session(db_path, must_exist=True) as session:
            row = session.get(CommandRegistryUser, (command_name_value))
            if row is None:
                return error_result(
                    code="record_not_found",
                    meaning="Record not found.",
                    details={
                        "command_name": command_name,
                        "record_id": record_id,
                    },
                )
            if category is not None:
                row.category = category
            if entry is not None:
                row.entry = entry
            if summary is not None:
                row.summary = summary
            if requires_certification is not None:
                row.requires_certification = requires_certification
            if requires_work_id is not None:
                row.requires_work_id = requires_work_id
            if registry_schema_version is not None:
                row.registry_schema_version = registry_schema_version
            if "feature_flag" in raw_payload:
                row.feature_flag = feature_flag
            if "notes" in raw_payload:
                row.notes = notes
            if "spec_json" in raw_payload:
                row.spec_json = spec_json
            if "registry_generated_at" in raw_payload:
                row.registry_generated_at = registry_generated_at
            if "registry_updated_at" in raw_payload:
                row.registry_updated_at = registry_updated_at
            else:
                row.registry_updated_at = now
            session.flush()
            record = _record_to_dict(row)
        return ok_result(output={"record": record})
    except Exception as exc:
        return exception_result(command_name, exc)
