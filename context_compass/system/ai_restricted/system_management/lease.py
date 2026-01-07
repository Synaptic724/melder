"""
context_compass.system.ai_restricted.lease

Purpose
- Provide cross-process lock leasing for ctx targets and shared state resources.
- Persist leases in system.db for centralized visibility and auditing.

Lease record format (JSON)
- owner_id: unique agent or process id
- work_id: optional work item id
- resource: resource key being locked
- expires_at: ISO timestamp
- heartbeat_at: ISO timestamp

Lease rules
- If no lock exists, create and own it.
- If lock exists and expires_at is in the future, fail for non-owners.
- If lock exists and expires_at has passed, steal by replacing the lease row.
- Re-entrant acquisition is allowed for the same owner_id.

Atomicity
- Uses SQLite transactions to serialize lease updates.
- Unique constraint enforces one active lock per resource key.
"""

import argparse
import hashlib
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared.command_results import error_result
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

CURRENT_BRANCH_TABLE = "current_branch"
CURRENT_BRANCH_ACTION = "by_record_id"
CURRENT_BRANCH_RECORD_ID = "current"

REPO_STATE_TABLE = "repo_state"
REPO_STATE_ACTION = "by_branch_name"

LEASE_LOCKS_TABLE = "lease_locks"
LEASE_ACQUIRE_ACTION = "acquire_lock"
LEASE_RELEASE_ACTION = "release_lock"


def lock_path_for(repo_root: Path, resource: Path) -> Path:
    """
    Compute a stable lock key for deterministic ordering.

    Args:
        repo_root (Path): Repository root used for resource normalization.
        resource (Path): Resource identifier to lock.

    Returns:
        Path: Synthetic lock key path for ordering (never created on disk).
    """
    resolved_type = _infer_resource_type(resource)
    resource_key = _normalize_resource_key(repo_root, resource, resolved_type)
    digest = hashlib.sha256(f"{resolved_type}::{resource_key}".encode("utf-8")).hexdigest()
    return Path(f"lock::{digest}")


def _crud_read_current_branch(repo_root: Path, actor_id: str) -> str | None:
    """
    Read the current_branch record via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        str | None: Current branch name, or None if missing.

    Raises:
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=CURRENT_BRANCH_TABLE,
                action=CURRENT_BRANCH_ACTION,
                payload={"record_id": CURRENT_BRANCH_RECORD_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code in {"record_not_found", "db_missing"}:
            return None
        raise

    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("current_branch read returned an invalid record payload.")
    branch_name = record.get("branch_name")
    if branch_name is None:
        return None
    if not isinstance(branch_name, str):
        raise ValueError("current_branch record contains an invalid branch_name.")
    return branch_name


def _crud_read_repo_state(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
) -> dict | None:
    """
    Read the repo_state payload via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict | None: repo_state record payload if present.

    Raises:
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=REPO_STATE_TABLE,
                action=REPO_STATE_ACTION,
                payload={"branch_name": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code in {"record_not_found", "db_missing"}:
            return None
        raise

    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("repo_state read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("repo_state read returned an invalid exists flag.")
    if not exists:
        return None
    return record


def _resolve_repo_id(repo_root: Path, actor_id: str) -> str:
    """
    Resolve the repo_id for lease scoping.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        str: Repo identifier string.

    Contract:
        - Falls back to the repo_root string if repo_id is not available.
    """

    try:
        branch_name = _crud_read_current_branch(repo_root, actor_id)
    except Exception:
        return str(repo_root)
    if not branch_name:
        return str(repo_root)

    try:
        record = _crud_read_repo_state(repo_root, branch_name, actor_id)
    except Exception:
        return str(repo_root)
    if not isinstance(record, dict):
        return str(repo_root)
    repo_id = record.get("repo_id")
    if isinstance(repo_id, str) and repo_id.strip():
        return repo_id
    return str(repo_root)


def _infer_resource_type(resource: Path) -> str:
    """
    Infer the resource type for a lock.

    Args:
        resource (Path): Resource identifier path.

    Returns:
        str: Resource type label (path or logical).
    """
    if resource.is_absolute() or len(resource.parts) > 1:
        return "path"
    return "logical"


def _normalize_resource_key(repo_root: Path, resource: Path, resource_type: str) -> str:
    """
    Normalize the resource key stored in lease_locks.

    Args:
        repo_root (Path): Repository root path.
        resource (Path): Resource path identifier.
        resource_type (str): Resource type label.

    Returns:
        str: Normalized resource key.
    """
    if resource_type == "path":
        if resource.is_absolute():
            return str(resource)
        return str((repo_root / resource).resolve())
    return str(resource)


def _lock_id(repo_id: str, resource_type: str, resource_key: str) -> str:
    """
    Build a deterministic lock id from resource identity.

    Args:
        repo_id (str): Repository identifier.
        resource_type (str): Resource type label.
        resource_key (str): Normalized resource key.

    Returns:
        str: Deterministic lock id.
    """
    digest = hashlib.sha256(
        f"{repo_id}::{resource_type}::{resource_key}".encode("utf-8")
    ).hexdigest()
    return f"lock_{digest}"


def _lease_payload_from_record(record: dict) -> dict:
    """
    Convert a lease_locks record into the lease payload format.

    Args:
        record (dict): Lease lock record payload.

    Returns:
        dict: Lease payload matching the acquire_lock contract.

    Raises:
        ValueError: If required record fields are missing or invalid.
    """

    schema_version = record.get("schema_version")
    resource_key = record.get("resource_key")
    owner_id = record.get("owner_id")
    created_at = record.get("created_at")
    heartbeat_at = record.get("heartbeat_at")
    expires_at = record.get("expires_at")
    work_id = record.get("work_id")
    if not isinstance(schema_version, int):
        raise ValueError("lease_locks record missing schema_version.")
    if not isinstance(resource_key, str):
        raise ValueError("lease_locks record missing resource_key.")
    if not isinstance(owner_id, str):
        raise ValueError("lease_locks record missing owner_id.")
    if not isinstance(created_at, str):
        raise ValueError("lease_locks record missing created_at.")
    if not isinstance(heartbeat_at, str):
        raise ValueError("lease_locks record missing heartbeat_at.")
    if not isinstance(expires_at, str):
        raise ValueError("lease_locks record missing expires_at.")
    return {
        "schema_version": schema_version,
        "resource": resource_key,
        "owner_id": owner_id,
        "work_id": work_id,
        "created_at": created_at,
        "heartbeat_at": heartbeat_at,
        "expires_at": expires_at,
    }


def acquire_lock(
    repo_root: Path,
    resource: Path,
    owner_id: str,
    ttl_seconds: int,
    work_id: Optional[str] = None,
    *,
    repo_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    ticket_id: Optional[str] = None,
    lock_group_id: Optional[str] = None,
) -> dict:
    """
    Acquire or steal a lease lock for a resource.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resource (Path): Resource to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.
        work_id (Optional[str]): Optional work id.
        repo_id (Optional[str]): Optional repo id override.
        resource_type (Optional[str]): Optional resource type override.
        ticket_id (Optional[str]): Optional ticket id hint.
        lock_group_id (Optional[str]): Optional bundle id for multi-resource locks.

    Returns:
        dict: Lease record payload.

    Raises:
        FileNotFoundError: If the system database is missing.
        RuntimeError: If a non-expired lock is held by another owner.
        Exception: If the database session fails unexpectedly.
    """
    resolved_repo_id = repo_id or _resolve_repo_id(repo_root, owner_id)
    resolved_type = resource_type or _infer_resource_type(resource)
    resource_key = _normalize_resource_key(repo_root, resource, resolved_type)
    lock_id = _lock_id(resolved_repo_id, resolved_type, resource_key)

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope="system",
                table_name=LEASE_LOCKS_TABLE,
                action=LEASE_ACQUIRE_ACTION,
                payload={
                    "record_id": lock_id,
                    "lock_id": lock_id,
                    "repo_id": resolved_repo_id,
                    "resource_type": resolved_type,
                    "resource_key": resource_key,
                    "owner_id": owner_id,
                    "ttl_seconds": ttl_seconds,
                    "work_id": work_id,
                    "ticket_id": ticket_id,
                    "lock_group_id": lock_group_id,
                },
                actor_id=owner_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "db_missing":
            raise FileNotFoundError("System database not found.") from exc
        if exc.code == "lock_held":
            raise RuntimeError(f"Lock already held for {resource_key}") from exc
        raise

    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("lease_locks create returned an invalid record payload.")
    return _lease_payload_from_record(record)


def release_lock(repo_root: Path, resource: Path, owner_id: str) -> None:
    """
    Release a lease lock if owned by the caller.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resource (Path): Resource to unlock.
        owner_id (str): Lock owner id.

    Raises:
        FileNotFoundError: If the system database is missing.
        Exception: If the database session fails unexpectedly.
    """
    resolved_repo_id = _resolve_repo_id(repo_root, owner_id)
    resolved_type = _infer_resource_type(resource)
    resource_key = _normalize_resource_key(repo_root, resource, resolved_type)
    lock_id = _lock_id(resolved_repo_id, resolved_type, resource_key)

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="delete",
                scope="system",
                table_name=LEASE_LOCKS_TABLE,
                action=LEASE_RELEASE_ACTION,
                payload={
                    "record_id": lock_id,
                    "lock_id": lock_id,
                    "repo_id": resolved_repo_id,
                    "resource_type": resolved_type,
                    "resource_key": resource_key,
                    "owner_id": owner_id,
                },
                actor_id=owner_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "db_missing":
            raise FileNotFoundError("System database not found.") from exc
        raise


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Reject direct execution of the lease helper via the command runner.

    Args:
        payload (dict): JSON-serializable kwargs payload (unused).
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Error result indicating the helper is not invokable.

    Raises:
        None: Always returns an error result.

    Contract:
        - The lease module is a library helper, not a runnable command.
        - Callers should use acquire_lock/release_lock directly.
    """

    return error_result(
        code="command_disabled",
        meaning="Lease helper is a library module and cannot be executed as a command.",
        details={
            "command_name": ctx.command_name,
            "reason": "lease module provides acquire_lock/release_lock helpers only",
        },
    )


def main() -> None:
    """
    CLI entrypoint for lease.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: Always, because this command is disabled.
    """

    parser = argparse.ArgumentParser(
        description="Lease helper (library module; not executable)."
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    result = run({}, ExecutionContext(command_name="lease", agent_id=None, work_id=None, correlation_id=None))
    if result.status != "ok":
        logging.getLogger(__name__).error("lease failed: %s", result.errors)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
