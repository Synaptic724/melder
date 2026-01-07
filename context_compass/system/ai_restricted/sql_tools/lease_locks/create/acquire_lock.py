"""
SQL tool script to acquire lease_locks entries.

Purpose
- Acquire, renew, or steal a lease lock for a resource.
- Enforce lease ownership and expiration semantics in system.db.

Contract
- Requires payload.repo_id, payload.resource_type, payload.resource_key, payload.lock_id,
  payload.owner_id, and payload.ttl_seconds.
- Optional payload fields: work_id, ticket_id, lock_group_id, record_id.
- Returns the persisted lease_locks record.
"""

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_int,
    require_string,
)
from context_compass.system.ai_restricted._shared.sql_command_results import (
    error_result,
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.timeutils import parse_iso8601, utc_now_iso
from context_compass.system.ai_restricted.database_management.orm_session import (
    sqlite_session,
    system_db_path,
)
from context_compass.system.ai_restricted.database_management.system_orm_models import LeaseLock
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

SCHEMA_VERSION = 1


class _LockHeldError(Exception):
    """
    Raised when a lease lock is held by another owner and not expired.
    """


@dataclass(frozen=True)
class _LeaseInput:
    """
    Parsed lease inputs for lock acquisition.

    Attributes:
        repo_id (str): Repository identifier for lock scoping.
        resource_type (str): Resource type label.
        resource_key (str): Normalized resource key.
        lock_id (str): Deterministic lock identifier.
        owner_id (str): Owner identifier.
        ttl_seconds (int): Lease TTL in seconds.
        work_id (str | None): Optional work id.
        ticket_id (str | None): Optional ticket id.
        lock_group_id (str | None): Optional lock group id.
    """

    repo_id: str
    resource_type: str
    resource_key: str
    lock_id: str
    owner_id: str
    ttl_seconds: int
    work_id: str | None
    ticket_id: str | None
    lock_group_id: str | None


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


def _require_positive_ttl(value: int, command_name: str) -> int:
    """
    Validate that the TTL value is a positive integer.

    Args:
        value (int): TTL value in seconds.
        command_name (str): Command name for error context.

    Returns:
        int: Positive TTL value.

    Raises:
        PayloadError: If the TTL is invalid.
    """

    if value <= 0:
        raise PayloadError(
            code="payload_invalid",
            details={
                "command_name": command_name,
                "field": "ttl_seconds",
                "expected": "positive integer",
                "actual": value,
            },
        )
    return value


def _parse_payload(raw_payload: dict, command_name: str) -> _LeaseInput:
    """
    Parse the payload into a normalized lease input.

    Args:
        raw_payload (dict): Nested payload dictionary.
        command_name (str): Command name for error context.

    Returns:
        _LeaseInput: Parsed lease input data.

    Raises:
        PayloadError: If required fields are missing or invalid.
    """

    repo_id = require_string(raw_payload, "repo_id", command_name)
    resource_type = require_string(raw_payload, "resource_type", command_name)
    resource_key = require_string(raw_payload, "resource_key", command_name)
    lock_id = require_string(raw_payload, "lock_id", command_name)
    owner_id = require_string(raw_payload, "owner_id", command_name)
    ttl_value = require_int(raw_payload, "ttl_seconds", command_name)
    ttl_seconds = _require_positive_ttl(ttl_value, command_name)
    record_id = optional_string(raw_payload, "record_id", command_name=command_name)
    if record_id and record_id != lock_id:
        raise PayloadError(
            code="payload_invalid",
            details={
                "command_name": command_name,
                "field": "record_id",
                "expected": lock_id,
                "actual": record_id,
            },
        )
    return _LeaseInput(
        repo_id=repo_id,
        resource_type=resource_type,
        resource_key=resource_key,
        lock_id=lock_id,
        owner_id=owner_id,
        ttl_seconds=ttl_seconds,
        work_id=optional_string(raw_payload, "work_id", command_name=command_name),
        ticket_id=optional_string(raw_payload, "ticket_id", command_name=command_name),
        lock_group_id=optional_string(raw_payload, "lock_group_id", command_name=command_name),
    )


def _expires_at(now: str, ttl_seconds: int) -> str:
    """
    Compute the expires_at timestamp for a lease.

    Args:
        now (str): Current timestamp.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        str: ISO-8601 expiry timestamp.
    """

    from datetime import timedelta

    expiry = parse_iso8601(now) + timedelta(seconds=ttl_seconds)
    return expiry.isoformat().replace("+00:00", "Z")


def _record_to_dict(row: LeaseLock) -> dict:
    """
    Convert a LeaseLock ORM row to a record dictionary.

    Args:
        row (LeaseLock): ORM row.

    Returns:
        dict: Serialized lease_locks record.
    """

    return {
        "record_id": row.lock_id,
        "lock_id": row.lock_id,
        "repo_id": row.repo_id,
        "resource_type": row.resource_type,
        "resource_key": row.resource_key,
        "owner_id": row.owner_id,
        "schema_version": row.schema_version,
        "work_id": row.work_id,
        "ticket_id": row.ticket_id,
        "lock_group_id": row.lock_group_id,
        "created_at": row.created_at,
        "heartbeat_at": row.heartbeat_at,
        "expires_at": row.expires_at,
        "updated_at": row.updated_at,
        "created_by": row.created_by,
        "updated_by": row.updated_by,
    }


def _lock_expired(row: LeaseLock, now: str) -> bool:
    """
    Check whether a lease lock is expired.

    Args:
        row (LeaseLock): Lease lock row.
        now (str): Current timestamp.

    Returns:
        bool: True when the lease is expired.
    """

    return parse_iso8601(row.expires_at) <= parse_iso8601(now)


def _apply_lease_update(
    row: LeaseLock,
    *,
    owner_id: str,
    work_id: str | None,
    ticket_id: str | None,
    lock_group_id: str | None,
    now: str,
    expires_at: str,
    steal: bool,
) -> None:
    """
    Apply lease updates to an existing row.

    Args:
        row (LeaseLock): Existing row to update.
        owner_id (str): New owner identifier.
        work_id (str | None): Optional work id.
        ticket_id (str | None): Optional ticket id.
        lock_group_id (str | None): Optional lock group id.
        now (str): Current timestamp.
        expires_at (str): New expiration timestamp.
        steal (bool): Whether the update is a lock steal.

    Returns:
        None: Mutates the row in-place.
    """

    row.owner_id = owner_id
    row.schema_version = SCHEMA_VERSION
    row.work_id = work_id
    row.ticket_id = ticket_id
    row.lock_group_id = lock_group_id
    row.heartbeat_at = now
    row.expires_at = expires_at
    row.updated_at = now
    row.updated_by = owner_id
    if steal:
        row.created_at = now
        row.created_by = owner_id


def _create_row(
    *,
    lease_input: _LeaseInput,
    now: str,
    expires_at: str,
) -> LeaseLock:
    """
    Build a LeaseLock ORM row for insertion.

    Args:
        lease_input (_LeaseInput): Parsed lease inputs.
        now (str): Current timestamp.
        expires_at (str): Expiration timestamp.

    Returns:
        LeaseLock: ORM row ready for insertion.
    """

    return LeaseLock(
        lock_id=lease_input.lock_id,
        repo_id=lease_input.repo_id,
        resource_type=lease_input.resource_type,
        resource_key=lease_input.resource_key,
        owner_id=lease_input.owner_id,
        schema_version=SCHEMA_VERSION,
        work_id=lease_input.work_id,
        ticket_id=lease_input.ticket_id,
        lock_group_id=lease_input.lock_group_id,
        created_at=now,
        heartbeat_at=now,
        expires_at=expires_at,
        updated_at=now,
        created_by=lease_input.owner_id,
        updated_by=lease_input.owner_id,
    )


def _acquire_lease(session, lease_input: _LeaseInput) -> dict:
    """
    Acquire or update a lease lock.

    Args:
        session: SQLAlchemy session.
        lease_input (_LeaseInput): Parsed lease inputs.

    Returns:
        dict: Serialized lease lock record.

    Raises:
        _LockHeldError: If the lock is held by another owner.
    """

    now = utc_now_iso()
    expires_at = _expires_at(now, lease_input.ttl_seconds)
    row = (
        session.query(LeaseLock)
        .filter_by(
            repo_id=lease_input.repo_id,
            resource_type=lease_input.resource_type,
            resource_key=lease_input.resource_key,
        )
        .one_or_none()
    )
    if row is None:
        try:
            row = _create_row(lease_input=lease_input, now=now, expires_at=expires_at)
            session.add(row)
            session.flush()
        except IntegrityError:
            session.rollback()
            row = (
                session.query(LeaseLock)
                .filter_by(
                    repo_id=lease_input.repo_id,
                    resource_type=lease_input.resource_type,
                    resource_key=lease_input.resource_key,
                )
                .one_or_none()
            )

    if row is None:
        raise _LockHeldError("Unable to acquire lease lock.")

    if row.owner_id == lease_input.owner_id:
        _apply_lease_update(
            row,
            owner_id=lease_input.owner_id,
            work_id=lease_input.work_id,
            ticket_id=lease_input.ticket_id,
            lock_group_id=lease_input.lock_group_id,
            now=now,
            expires_at=expires_at,
            steal=False,
        )
        return _record_to_dict(row)

    if _lock_expired(row, now):
        row.lock_id = lease_input.lock_id
        row.repo_id = lease_input.repo_id
        row.resource_type = lease_input.resource_type
        row.resource_key = lease_input.resource_key
        _apply_lease_update(
            row,
            owner_id=lease_input.owner_id,
            work_id=lease_input.work_id,
            ticket_id=lease_input.ticket_id,
            lock_group_id=lease_input.lock_group_id,
            now=now,
            expires_at=expires_at,
            steal=True,
        )
        return _record_to_dict(row)

    raise _LockHeldError("Lock already held for resource.")


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Acquire a lease lock for a resource.

    Args:
        payload (dict): Command payload containing payload fields.
        ctx (ExecutionContext): Execution context with actor metadata.

    Returns:
        CommandResult: Result containing the lease lock record.

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
        lease_input = _parse_payload(raw_payload, command_name)
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
            record = _acquire_lease(session, lease_input)
        return ok_result(output={"record": record})
    except _LockHeldError as exc:
        return error_result(
            code="lock_held",
            meaning=str(exc),
            details={
                "command_name": command_name,
                "repo_id": lease_input.repo_id,
                "resource_key": lease_input.resource_key,
                "owner_id": lease_input.owner_id,
            },
        )
    except Exception as exc:
        return exception_result(command_name, exc)


if __name__ == "__main__":
    raise SystemExit("This module is intended to be used via sqlite_crud.")
