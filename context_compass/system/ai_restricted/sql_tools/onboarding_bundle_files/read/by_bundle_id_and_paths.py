"""
SQL tool script to read onboarding_bundle_files rows by bundle_id and paths.

Purpose
- Fetch bundle file rows for a specific bundle_id and path list.
- Support onboarding bundle restore workflows.

Contract
- Requires payload.bundle_id, payload.paths, and actor_id.
- Returns records ordered by position for deterministic restores.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_list,
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
    OnboardingBundleFile,
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


def _normalize_paths(paths: list[Any], command_name: str) -> list[str]:
    """
    Normalize and validate a list of bundle paths.

    Args:
        paths (list[Any]): Raw path entries.
        command_name (str): Command name for error context.

    Returns:
        list[str]: Normalized path strings.

    Raises:
        PayloadError: If any path is invalid.
    """

    normalized: list[str] = []
    for index, item in enumerate(paths):
        if not isinstance(item, str) or not item:
            raise PayloadError(
                code="payload_type_error",
                details={
                    "command_name": command_name,
                    "field": f"payload.paths[{index}]",
                    "expected": "non-empty string",
                    "actual_type": type(item).__name__,
                },
            )
        normalized.append(item)
    return normalized


def _row_to_dict(row: OnboardingBundleFile) -> dict[str, Any]:
    """
    Convert an OnboardingBundleFile ORM row into a dictionary.

    Args:
        row (OnboardingBundleFile): ORM row instance.

    Returns:
        dict[str, Any]: Serialized onboarding bundle file row.
    """

    return {
        "bundle_id": row.bundle_id,
        "position": row.position,
        "path": row.path,
        "sha256": row.sha256,
        "content": row.content,
        "content_bytes": row.content_bytes,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read onboarding_bundle_files rows for a bundle_id and paths.

    Args:
        payload (dict): Command payload containing bundle_id and paths.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing matching file rows.

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
        raw_paths = require_list(raw_payload, "paths", command_name)
        paths = _normalize_paths(raw_paths, command_name)
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
            stmt = (
                select(OnboardingBundleFile)
                .where(OnboardingBundleFile.bundle_id == bundle_id)
                .where(OnboardingBundleFile.path.in_(paths))
                .order_by(OnboardingBundleFile.position)
            )
            rows = session.execute(stmt).scalars().all()
            records = [_row_to_dict(row) for row in rows]
            return ok_result(
                output={
                    "bundle_id": bundle_id,
                    "records": records,
                }
            )
    except Exception as exc:
        return exception_result(command_name, exc)
