"""
SQL tool script to write scan_error_records entries.

Purpose
- Persist scan error record payloads to user.db.
- Replace existing error records with the same (branch_name, error_id).

Contract
- Requires payload.branch_name, payload.error_id, payload.error_record.
- error_record.error_id must match payload.error_id.
- details are stored as minified JSON text.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_int,
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
    ScanErrorRecord,
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


def _require_error_record(raw_payload: dict, command_name: str) -> dict:
    """
    Require the error_record payload object.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        dict: Error record payload.

    Raises:
        PayloadError: If error_record is missing or invalid.
    """

    record = raw_payload.get("error_record")
    if not isinstance(record, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "error_record",
                "expected": "object",
                "payload_type": type(record).__name__,
            },
        )
    return record


def _require_record_string(
    record: dict,
    field: str,
    command_name: str,
) -> str:
    """
    Require a string field within an error_record payload.

    Args:
        record (dict): Error record payload.
        field (str): Field name to extract.
        command_name (str): Command name for error context.

    Returns:
        str: Field value.

    Raises:
        PayloadError: If the field is missing or invalid.
    """

    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": f"error_record.{field}",
                "expected": "non-empty string",
                "actual": value,
            },
        )
    return value


def _optional_record_string(record: dict, field: str, command_name: str) -> str | None:
    """
    Read an optional string field within an error_record payload.

    Args:
        record (dict): Error record payload.
        field (str): Field name to extract.
        command_name (str): Command name for error context.

    Returns:
        str | None: Field value or None if missing.

    Raises:
        PayloadError: If the field is not a string when provided.
    """

    if field not in record:
        return None
    value = record.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": f"error_record.{field}",
                "expected": "string or null",
                "payload_type": type(value).__name__,
            },
        )
    return value


def _normalize_details(record: dict, command_name: str) -> dict[str, Any]:
    """
    Normalize the details payload for an error record.

    Args:
        record (dict): Error record payload.
        command_name (str): Command name for error context.

    Returns:
        dict[str, Any]: Details payload.

    Raises:
        PayloadError: If details is not a mapping.
    """

    details = record.get("details", {})
    if not isinstance(details, dict):
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "error_record.details",
                "expected": "object",
                "payload_type": type(details).__name__,
            },
        )
    return details


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Write a scan error record to SQLite.

    Args:
        payload (dict): Command payload containing error record fields.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the persisted error record payload.

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
        branch_name = require_string(raw_payload, "branch_name", command_name)
        error_id = require_string(raw_payload, "error_id", command_name)
        record = _require_error_record(raw_payload, command_name)
        record_error_id = _require_record_string(record, "error_id", command_name)
        if record_error_id != error_id:
            raise PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "error_record.error_id",
                    "expected": error_id,
                    "actual": record_error_id,
                },
            )
        schema_version = require_int(record, "schema_version", command_name)
        occurred_at = _require_record_string(record, "when", command_name)
        owner_id = _require_record_string(record, "owner_id", command_name)
        work_id = _optional_record_string(record, "work_id", command_name)
        target_path = _optional_record_string(record, "target_path", command_name)
        ctx_path = _optional_record_string(record, "ctx_path", command_name)
        category = _require_record_string(record, "category", command_name)
        message = _require_record_string(record, "message", command_name)
        details = _normalize_details(record, command_name)
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

    details_json = json.dumps(details, separators=(",", ":"))
    now = utc_now_iso()
    try:
        with sqlite_session(db_path, must_exist=True) as session:
            session.query(ScanErrorRecord).filter_by(
                branch_name=branch_name,
                error_id=error_id,
            ).delete()
            session.add(
                ScanErrorRecord(
                    branch_name=branch_name,
                    error_id=error_id,
                    schema_version=schema_version,
                    occurred_at=occurred_at,
                    owner_id=owner_id,
                    work_id=work_id,
                    target_path=target_path,
                    ctx_path=ctx_path,
                    category=category,
                    message=message,
                    details_json=details_json,
                    created_at=now,
                    created_by=actor_id,
                    updated_at=now,
                    updated_by=actor_id,
                )
            )
        return ok_result(
            output={
                "branch_name": branch_name,
                "error_id": error_id,
                "record": record,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)
