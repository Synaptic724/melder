"""
SQL tool script for reading config_context_compass_flags records.

Purpose
- Fetch feature flag rows for a configuration id.
- Provide ordered feature flags for configuration loaders.

Contract
- Requires payload.config_id and actor_id.
- Returns rows ordered by feature_name.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select

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
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import (
    ConfigContextCompassFlag,
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


def _row_to_dict(row: ConfigContextCompassFlag) -> dict[str, Any]:
    """
    Convert a ConfigContextCompassFlag row to a dictionary.

    Args:
        row (ConfigContextCompassFlag): ORM row instance.

    Returns:
        dict[str, Any]: Serialized flag payload.
    """

    return {
        "config_id": row.config_id,
        "feature_name": row.feature_name,
        "enabled": row.enabled,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read config_context_compass_flags rows by config_id.

    Args:
        payload (dict): Command payload containing payload.config_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing ordered flag records.

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
        config_id = require_int(raw_payload, "config_id", command_name)
        if config_id < 1:
            raise PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "config_id",
                    "expected": "integer >= 1",
                    "actual": config_id,
                },
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

    try:
        with sqlite_session(db_path, must_exist=True) as session:
            stmt = (
                select(ConfigContextCompassFlag)
                .where(ConfigContextCompassFlag.config_id == config_id)
                .order_by(ConfigContextCompassFlag.feature_name)
            )
            rows = session.execute(stmt).scalars().all()
            records = [_row_to_dict(row) for row in rows]
        return ok_result(output={"config_id": config_id, "records": records})
    except Exception as exc:
        return exception_result(command_name, exc)
