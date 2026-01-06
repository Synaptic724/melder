"""
SQL tool script for reading config_ctx_artifact_output_core records.

Purpose
- Fetch a ctx artifact output configuration record by config_id.
- Provide ctx emission toggles to callers.

Contract
- Requires payload.config_id and actor_id.
- Returns a single configuration record payload.
"""

from __future__ import annotations

from pathlib import Path

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
    user_db_path,
)
from context_compass.system.ai_restricted.database_management.user_orm_models import (
    ConfigCtxArtifactOutputCore,
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


def _record_to_dict(row: ConfigCtxArtifactOutputCore) -> dict:
    """
    Convert a ConfigCtxArtifactOutputCore ORM row into a dictionary.

    Args:
        row (ConfigCtxArtifactOutputCore): ORM row instance.

    Returns:
        dict: Serialized configuration payload.
    """

    return {
        "config_id": row.config_id,
        "schema_version": row.schema_version,
        "emit_to_repo": row.emit_to_repo,
        "emit_file_ctx": row.emit_file_ctx,
        "emit_dir_ctx": row.emit_dir_ctx,
        "emit_architecture_context": row.emit_architecture_context,
        "emit_component_contexts": row.emit_component_contexts,
        "notes": row.notes,
        "created_at": row.created_at,
        "created_by": row.created_by,
        "updated_at": row.updated_at,
        "updated_by": row.updated_by,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a config_ctx_artifact_output_core record by config_id.

    Args:
        payload (dict): Command payload containing payload.config_id.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the configuration record.

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
            row = session.get(ConfigCtxArtifactOutputCore, (config_id))
            if row is None:
                return error_result(
                    code="record_not_found",
                    meaning="Record not found.",
                    details={
                        "command_name": command_name,
                        "config_id": config_id,
                    },
                )
            record = _record_to_dict(row)
        return ok_result(output={"record": record})
    except Exception as exc:
        return exception_result(command_name, exc)
