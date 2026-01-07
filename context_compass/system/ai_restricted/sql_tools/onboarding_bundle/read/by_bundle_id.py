"""
SQL tool script to read onboarding_bundle by bundle_id.

Purpose
- Fetch onboarding bundle header metadata for a bundle_id.
- Provide a consistent read path for bundle existence checks.

Contract
- Requires payload.bundle_id and actor_id.
- Returns the onboarding_bundle record or a record_not_found error.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
    OnboardingBundle,
)
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


def _row_to_dict(row: OnboardingBundle) -> dict[str, Any]:
    """
    Convert an OnboardingBundle ORM row into a dictionary.

    Args:
        row (OnboardingBundle): ORM row instance.

    Returns:
        dict[str, Any]: Serialized onboarding bundle header record.
    """

    return {
        "bundle_id": row.bundle_id,
        "schema_version": row.schema_version,
        "bundle_format": row.bundle_format,
        "generated_at": row.generated_at,
        "file_count": row.file_count,
        "missing_count": row.missing_count,
        "error_count": row.error_count,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read onboarding_bundle metadata by bundle_id.

    Args:
        payload (dict): Command payload containing payload.bundle_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the onboarding_bundle record.

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
        bundle_id = require_string(raw_payload, "bundle_id", command_name)
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
            row = session.get(OnboardingBundle, bundle_id)
            if row is None:
                return error_result(
                    code="record_not_found",
                    meaning="Record not found.",
                    details={
                        "command_name": command_name,
                        "bundle_id": bundle_id,
                    },
                )
            return ok_result(output={"record": _row_to_dict(row)})
    except Exception as exc:
        return exception_result(command_name, exc)
