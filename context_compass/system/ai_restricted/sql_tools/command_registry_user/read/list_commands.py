"""
SQL tool script to list command_registry_user records.

Purpose
- Return all user command registry rows in command_name order.
- Support validation workflows that scan command registry entries.

Contract
- actor_id is required for audit logging.
- payload is optional and ignored.
- Returns full command registry records in output.records.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

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
    CommandRegistryUser,
)
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


def _record_id(command_name: str) -> str:
    """
    Build the canonical record_id for a command registry entry.

    Args:
        command_name (str): Command name primary key.

    Returns:
        str: Canonical record_id string.

    Raises:
        None: This helper does not raise.
    """

    return command_name


def _record_to_dict(row: CommandRegistryUser) -> dict:
    """
    Convert a command registry ORM row into a dictionary.

    Args:
        row (CommandRegistryUser): ORM row instance.

    Returns:
        dict: Serialized command registry payload.

    Raises:
        None: This helper does not raise.
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


def _fetch_records(repo_root: Path) -> list[dict]:
    """
    Fetch command registry records for the user scope.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[dict]: Ordered list of command registry records.

    Raises:
        Exception: Propagates database errors from the ORM session.
    """

    db_path = user_db_path(repo_root)
    with sqlite_session(db_path, must_exist=True) as session:
        result = session.execute(
            select(CommandRegistryUser).order_by(CommandRegistryUser.command_name)
        )
        return [_record_to_dict(row) for row in result.scalars().all()]


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    List command_registry_user records.

    Args:
        payload (dict): Command payload (payload field ignored).
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing command registry records.

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
        records = _fetch_records(repo_root)
        return ok_result(output={"records": records})
    except Exception as exc:
        return exception_result(command_name, exc)
