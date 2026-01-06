"""
SQL tool script to release lease_locks entries.

Purpose
- Release a lease lock when owned by the caller.
- Ignore missing or mismatched ownership gracefully.

Contract
- Requires payload.repo_id, payload.resource_type, payload.resource_key, payload.owner_id.
- Optional payload fields: lock_id, record_id.
- Returns a deleted flag indicating whether the lease row was removed.
"""

from dataclasses import dataclass
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
from context_compass.system.ai_restricted.database_management.system_orm_models import LeaseLock
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


@dataclass(frozen=True)
class _ReleaseInput:
    """
    Parsed inputs for releasing a lease lock.

    Attributes:
        repo_id (str): Repository identifier.
        resource_type (str): Resource type label.
        resource_key (str): Normalized resource key.
        owner_id (str): Owner identifier.
        lock_id (str | None): Optional lock id.
    """

    repo_id: str
    resource_type: str
    resource_key: str
    owner_id: str
    lock_id: str | None


def _require_payload(payload: dict, command_name: str) -> dict:
    """
    Require and validate the nested payload object.

    Args:
        payload (dict): Outer command payload.
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


def _parse_payload(raw_payload: dict, command_name: str) -> _ReleaseInput:
    """
    Parse the payload into release inputs.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        _ReleaseInput: Parsed release inputs.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    repo_id = require_string(raw_payload, "repo_id", command_name)
    resource_type = require_string(raw_payload, "resource_type", command_name)
    resource_key = require_string(raw_payload, "resource_key", command_name)
    owner_id = require_string(raw_payload, "owner_id", command_name)
    lock_id = optional_string(raw_payload, "lock_id", command_name=command_name)
    record_id = optional_string(raw_payload, "record_id", command_name=command_name)
    if record_id and lock_id and record_id != lock_id:
        raise PayloadError(
            code="payload_invalid",
            details={
                "command_name": command_name,
                "field": "record_id",
                "expected": lock_id,
                "actual": record_id,
            },
        )
    return _ReleaseInput(
        repo_id=repo_id,
        resource_type=resource_type,
        resource_key=resource_key,
        owner_id=owner_id,
        lock_id=lock_id,
    )


def _release_lock(session, release_input: _ReleaseInput) -> bool:
    """
    Release a lease lock when owned by the caller.

    Args:
        session: SQLAlchemy session.
        release_input (_ReleaseInput): Parsed release inputs.

    Returns:
        bool: True if the row was deleted.
    """

    row = (
        session.query(LeaseLock)
        .filter_by(
            repo_id=release_input.repo_id,
            resource_type=release_input.resource_type,
            resource_key=release_input.resource_key,
        )
        .one_or_none()
    )
    if row is None:
        return False
    if row.owner_id != release_input.owner_id:
        return False
    session.delete(row)
    return True


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Release a lease lock for a resource.

    Args:
        payload (dict): Command payload containing payload fields.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing deletion metadata.

    Raises:
        None: All errors are returned in the CommandResult.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        require_string(payload, "actor_id", command_name)
        raw_payload = _require_payload(payload, command_name)
        release_input = _parse_payload(raw_payload, command_name)
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
            deleted = _release_lock(session, release_input)
        return ok_result(output={"deleted": deleted})
    except Exception as exc:
        return exception_result(command_name, exc)


if __name__ == "__main__":
    raise SystemExit("This module is intended to be used via sqlite_crud.")
