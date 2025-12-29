"""
context_compass.tools.lease

Purpose
- Provide cross-process lock leasing for ctx targets and shared state files.
- Lock directory is provided by callers (branch state or self_context).

Lease record format (JSON)
- owner_id: unique agent or process id
- work_id: optional work item id
- resource: path being locked
- expires_at: ISO timestamp
- heartbeat_at: ISO timestamp

Lease rules
- If no lock exists, create and own it.
- If lock exists and expires_at is in the future, fail or wait (tool-specific).
- If lock exists and expires_at has passed, steal by replacing the file.

Atomicity
- Use exclusive create when possible, and os.replace when stealing.
- All lock files must be minified JSON.
"""

import hashlib
import os
from pathlib import Path
from typing import Optional

from context_compass.tools._shared.json_io import dump_minified, load_json, write_json_atomic
from context_compass.tools._shared.timeutils import parse_iso8601, utc_now_iso


def lock_path_for(locks_dir: Path, resource: Path) -> Path:
    """
    Compute a stable lock file path for a resource.

    Args:
        locks_dir (Path): Directory for lock files.
        resource (Path): Resource path to lock.

    Returns:
        Path: Lock file path.
    """
    digest = hashlib.sha256(str(resource).encode("utf-8")).hexdigest()
    return locks_dir / f"{digest}.lock.json"


def _build_lease(resource: Path, owner_id: str, ttl_seconds: int, work_id: Optional[str]) -> dict:
    """
    Build a lease record for a resource.

    Args:
        resource (Path): Resource being locked.
        owner_id (str): Lease owner identifier.
        ttl_seconds (int): Lease time-to-live in seconds.
        work_id (Optional[str]): Optional work id.

    Returns:
        dict: Lease record.
    """
    now = utc_now_iso()
    expires_at = (parse_iso8601(now) + _seconds_delta(ttl_seconds)).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": 1,
        "resource": str(resource),
        "owner_id": owner_id,
        "work_id": work_id,
        "created_at": now,
        "heartbeat_at": now,
        "expires_at": expires_at,
    }


def acquire_lock(
    locks_dir: Path, resource: Path, owner_id: str, ttl_seconds: int, work_id: Optional[str] = None
) -> dict:
    """
    Acquire or steal a lease lock for a resource.

    Args:
        locks_dir (Path): Directory for lock files.
        resource (Path): Resource to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.
        work_id (Optional[str]): Optional work id.

    Returns:
        dict: Lease record.

    Raises:
        RuntimeError: If a non-expired lock is held by another owner.
    """
    locks_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_path_for(locks_dir, resource)
    lease = _build_lease(resource, owner_id, ttl_seconds, work_id)
    now = lease["created_at"]

    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        existing = load_json(lock_path)
        if isinstance(existing, dict) and "expires_at" in existing:
            if parse_iso8601(existing["expires_at"]) <= parse_iso8601(now):
                write_json_atomic(lock_path, lease)
                return lease
        raise RuntimeError(f"Lock already held for {resource}")

    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(dump_minified(lease))
    return lease


def release_lock(locks_dir: Path, resource: Path, owner_id: str) -> None:
    """
    Release a lease lock if owned by the caller.

    Args:
        locks_dir (Path): Directory for lock files.
        resource (Path): Resource to unlock.
        owner_id (str): Lock owner id.
    """
    lock_path = lock_path_for(locks_dir, resource)
    if not lock_path.exists():
        return
    record = load_json(lock_path)
    if isinstance(record, dict) and record.get("owner_id") == owner_id:
        lock_path.unlink()


def _seconds_delta(seconds: int):
    """
    Return a timedelta for the given number of seconds.

    Args:
        seconds (int): Number of seconds.

    Returns:
        timedelta: timedelta instance.
    """
    from datetime import timedelta

    return timedelta(seconds=seconds)
