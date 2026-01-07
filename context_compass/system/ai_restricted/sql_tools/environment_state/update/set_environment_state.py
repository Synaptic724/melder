"""
SQL tool script for updating environment_state records.

Purpose
- Persist a single environment_state snapshot in system.db.
- Upsert the "current" record for environment checks.

Contract
- Requires payload.record_id, payload.schema_version, payload.checked_at,
  payload.os, payload.python, and payload.tools.
- record_id must be "current".
- actor_id is required for audit logging.
- Uses checked_at for created_at/updated_at timestamps.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import EnvironmentState
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


CURRENT_RECORD_ID = "current"


def _require_payload(payload: dict, command_name: str) -> dict:
    """
    Require the nested payload object.

    Args:
        payload (dict): Command payload containing nested payload object.
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


def _require_mapping(payload: dict, field: str, command_name: str) -> dict:
    """
    Require a nested mapping field within the payload.

    Args:
        payload (dict): Parent payload mapping.
        field (str): Field name to require.
        command_name (str): Command name for error context.

    Returns:
        dict: Nested mapping value.

    Raises:
        PayloadError: If the field is missing or not a mapping.
    """

    value = payload.get(field)
    if not isinstance(value, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": field,
                "expected": "object",
                "actual_type": type(value).__name__,
            },
        )
    return value


def _parse_record_id(record_id: str, command_name: str) -> str:
    """
    Validate the record_id for environment_state operations.

    Args:
        record_id (str): Record id string.
        command_name (str): Command name for error context.

    Returns:
        str: Normalized record id.

    Raises:
        PayloadError: If record_id is invalid or not supported.
    """

    if not record_id.strip() or record_id != CURRENT_RECORD_ID:
        raise PayloadError(
            code="record_id_invalid",
            details={
                "command_name": command_name,
                "record_id": record_id,
                "expected": CURRENT_RECORD_ID,
            },
        )
    return record_id


def _parse_version_info(version_info: Any, command_name: str) -> tuple[int, int, int]:
    """
    Parse python version_info entries from the payload.

    Args:
        version_info (Any): Raw version_info value.
        command_name (str): Command name for error context.

    Returns:
        tuple[int, int, int]: Parsed major/minor/patch values.

    Raises:
        PayloadError: If version_info is missing or invalid.
    """

    if not isinstance(version_info, list) or len(version_info) < 3:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "python.version_info",
                "expected": "list of three integers",
            },
        )
    major, minor, patch = version_info[0:3]
    if not isinstance(major, int) or not isinstance(minor, int) or not isinstance(patch, int):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "python.version_info",
                "expected": "list of three integers",
            },
        )
    return int(major), int(minor), int(patch)


def _parse_tool_entry(
    tools_payload: dict, name: str, command_name: str
) -> tuple[bool, str | None]:
    """
    Parse a tool availability entry from the payload.

    Args:
        tools_payload (dict): Tools payload mapping.
        name (str): Tool name key (git/rg/pytest).
        command_name (str): Command name for error context.

    Returns:
        tuple[bool, str | None]: Availability flag and optional path.

    Raises:
        PayloadError: If the tool entry is missing or invalid.
    """

    entry = _require_mapping(tools_payload, name, command_name)
    available = require_bool(entry, "available", command_name)
    path = optional_string(entry, "path", command_name=command_name)
    return bool(available), path


def _extract_environment_fields(raw_payload: dict, command_name: str) -> dict:
    """
    Extract normalized EnvironmentState fields from the payload.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict: Flattened EnvironmentState field values.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    record_id = _parse_record_id(
        require_string(raw_payload, "record_id", command_name), command_name
    )
    schema_version = require_int(raw_payload, "schema_version", command_name)
    if schema_version < 1:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "schema_version",
                "expected": "integer >= 1",
                "actual": schema_version,
            },
        )
    checked_at = require_string(raw_payload, "checked_at", command_name)

    os_payload = _require_mapping(raw_payload, "os", command_name)
    python_payload = _require_mapping(raw_payload, "python", command_name)
    tools_payload = _require_mapping(raw_payload, "tools", command_name)

    os_name = require_string(os_payload, "name", command_name)
    os_platform = require_string(os_payload, "platform", command_name)
    os_release = require_string(os_payload, "release", command_name)
    os_version = require_string(os_payload, "version", command_name)
    os_machine = require_string(os_payload, "machine", command_name)
    os_processor = require_string(os_payload, "processor", command_name)
    os_is_windows = require_bool(os_payload, "is_windows", command_name)
    os_is_linux = require_bool(os_payload, "is_linux", command_name)
    os_is_macos = require_bool(os_payload, "is_macos", command_name)

    python_available = require_bool(python_payload, "available", command_name)
    python_executable = optional_string(
        python_payload, "executable", command_name=command_name
    )
    python_version = optional_string(python_payload, "version", command_name=command_name)
    python_implementation = optional_string(
        python_payload, "implementation", command_name=command_name
    )
    major, minor, patch = _parse_version_info(
        python_payload.get("version_info"), command_name
    )

    git_available, git_path = _parse_tool_entry(tools_payload, "git", command_name)
    rg_available, rg_path = _parse_tool_entry(tools_payload, "rg", command_name)
    pytest_available, pytest_path = _parse_tool_entry(tools_payload, "pytest", command_name)

    return {
        "record_id": record_id,
        "schema_version": schema_version,
        "checked_at": checked_at,
        "os_name": os_name,
        "os_platform": os_platform,
        "os_release": os_release,
        "os_version": os_version,
        "os_machine": os_machine,
        "os_processor": os_processor,
        "os_is_windows": bool(os_is_windows),
        "os_is_linux": bool(os_is_linux),
        "os_is_macos": bool(os_is_macos),
        "python_available": bool(python_available),
        "python_executable": python_executable,
        "python_version": python_version,
        "python_version_major": major,
        "python_version_minor": minor,
        "python_version_patch": patch,
        "python_implementation": python_implementation,
        "tools_git_available": bool(git_available),
        "tools_git_path": git_path,
        "tools_rg_available": bool(rg_available),
        "tools_rg_path": rg_path,
        "tools_pytest_available": bool(pytest_available),
        "tools_pytest_path": pytest_path,
    }


def _record_to_dict(row: EnvironmentState) -> dict:
    """
    Convert an EnvironmentState ORM row into a dictionary.

    Args:
        row (EnvironmentState): ORM row instance.

    Returns:
        dict: Serialized environment_state payload.
    """

    return {
        "record_id": row.record_id,
        "schema_version": row.schema_version,
        "checked_at": row.checked_at,
        "os_name": row.os_name,
        "os_platform": row.os_platform,
        "os_release": row.os_release,
        "os_version": row.os_version,
        "os_machine": row.os_machine,
        "os_processor": row.os_processor,
        "os_is_windows": row.os_is_windows,
        "os_is_linux": row.os_is_linux,
        "os_is_macos": row.os_is_macos,
        "python_available": row.python_available,
        "python_executable": row.python_executable,
        "python_version": row.python_version,
        "python_version_major": row.python_version_major,
        "python_version_minor": row.python_version_minor,
        "python_version_patch": row.python_version_patch,
        "python_implementation": row.python_implementation,
        "tools_git_available": row.tools_git_available,
        "tools_git_path": row.tools_git_path,
        "tools_rg_available": row.tools_rg_available,
        "tools_rg_path": row.tools_rg_path,
        "tools_pytest_available": row.tools_pytest_available,
        "tools_pytest_path": row.tools_pytest_path,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def _upsert_environment_state(
    repo_root: Path, *, fields: dict, actor_id: str
) -> dict:
    """
    Upsert the environment_state record.

    Args:
        repo_root (Path): Repository root.
        fields (dict): Flattened environment_state values.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Serialized environment_state record.

    Raises:
        FileNotFoundError: If the system database is missing.
    """

    db_path = system_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(f"System database not found: {db_path}")

    now = fields["checked_at"]
    with sqlite_session(db_path, must_exist=True) as session:
        row = session.get(EnvironmentState, fields["record_id"])
        if row is None:
            row = EnvironmentState(
                record_id=fields["record_id"],
                schema_version=fields["schema_version"],
                checked_at=fields["checked_at"],
                os_name=fields["os_name"],
                os_platform=fields["os_platform"],
                os_release=fields["os_release"],
                os_version=fields["os_version"],
                os_machine=fields["os_machine"],
                os_processor=fields["os_processor"],
                os_is_windows=fields["os_is_windows"],
                os_is_linux=fields["os_is_linux"],
                os_is_macos=fields["os_is_macos"],
                python_available=fields["python_available"],
                python_executable=fields["python_executable"],
                python_version=fields["python_version"],
                python_version_major=fields["python_version_major"],
                python_version_minor=fields["python_version_minor"],
                python_version_patch=fields["python_version_patch"],
                python_implementation=fields["python_implementation"],
                tools_git_available=fields["tools_git_available"],
                tools_git_path=fields["tools_git_path"],
                tools_rg_available=fields["tools_rg_available"],
                tools_rg_path=fields["tools_rg_path"],
                tools_pytest_available=fields["tools_pytest_available"],
                tools_pytest_path=fields["tools_pytest_path"],
                created_at=now,
                created_by=actor_id,
                updated_at=now,
                updated_by=actor_id,
            )
            session.add(row)
        else:
            row.schema_version = fields["schema_version"]
            row.checked_at = fields["checked_at"]
            row.os_name = fields["os_name"]
            row.os_platform = fields["os_platform"]
            row.os_release = fields["os_release"]
            row.os_version = fields["os_version"]
            row.os_machine = fields["os_machine"]
            row.os_processor = fields["os_processor"]
            row.os_is_windows = fields["os_is_windows"]
            row.os_is_linux = fields["os_is_linux"]
            row.os_is_macos = fields["os_is_macos"]
            row.python_available = fields["python_available"]
            row.python_executable = fields["python_executable"]
            row.python_version = fields["python_version"]
            row.python_version_major = fields["python_version_major"]
            row.python_version_minor = fields["python_version_minor"]
            row.python_version_patch = fields["python_version_patch"]
            row.python_implementation = fields["python_implementation"]
            row.tools_git_available = fields["tools_git_available"]
            row.tools_git_path = fields["tools_git_path"]
            row.tools_rg_available = fields["tools_rg_available"]
            row.tools_rg_path = fields["tools_rg_path"]
            row.tools_pytest_available = fields["tools_pytest_available"]
            row.tools_pytest_path = fields["tools_pytest_path"]
            row.updated_at = now
            row.updated_by = actor_id
        session.flush()
        record = _record_to_dict(row)
    return record


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Set the current environment_state record.

    Args:
        payload (dict): Command payload containing payload environment fields.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the updated environment_state record.

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
        fields = _extract_environment_fields(raw_payload, command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        record = _upsert_environment_state(
            repo_root, fields=fields, actor_id=actor_id
        )
        return ok_result(output={"record": record})
    except FileNotFoundError as exc:
        return error_result(
            code="db_missing",
            meaning=str(exc),
            details={
                "command_name": command_name,
                "db_path": str(system_db_path(repo_root)),
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)
