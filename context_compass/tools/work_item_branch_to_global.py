"""
Move a work item from the active branch work_management queues into the global queues.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_mode_guard import ensure_work_mode


def _work_files() -> dict:
    """
    Return the work_management queue filenames by type.

    Purpose:
    - Centralize the mapping from work types to queue filenames.

    Contract:
    - Only epic/story/task are supported queue types.

    Returns:
        dict: Mapping of work types to filenames.
    """
    return {"epic": "epics.json", "story": "stories.json", "task": "tasks.json"}


def _bucket_choices() -> list[str]:
    """
    Return allowed work bucket values.

    Purpose:
    - Enforce the canonical backlog/active/completed/denied buckets.

    Returns:
        list[str]: Allowed bucket values.
    """
    return ["active", "backlog", "completed", "denied"]


def _state_choices() -> list[str]:
    """
    Return allowed work item state values.

    Purpose:
    - Keep work item state transitions within the approved enum.

    Returns:
        list[str]: Allowed state values.
    """
    return ["queued", "leased", "in_progress", "done", "failed", "cancelled"]


def _aliases() -> dict:
    """
    Return kind aliases that normalize to canonical work types.

    Purpose:
    - Normalize user input so queue selection is deterministic.

    Returns:
        dict: Mapping of kind aliases to canonical work types.
    """
    return {"epic": "epic", "story": "story", "task": "task"}


def _normalize_kind(kind: str) -> Tuple[str, Optional[str]]:
    """
    Normalize a kind string and infer a work type.

    Purpose:
    - Accept canonical work types and normalize common aliases.

    Contract:
    - Returns (normalized_kind, inferred_type) where inferred_type may be None.

    Args:
        kind (str): Input kind string.

    Returns:
        Tuple[str, Optional[str]]: Normalized kind and inferred work type.
    """
    normalized = kind.strip()
    lowered = normalized.lower()
    aliases = _aliases()
    if lowered in aliases:
        canonical = aliases[lowered]
        return canonical, canonical
    if lowered in _work_files():
        return lowered, lowered
    return normalized, None


def _resolve_work_type(work_type: Optional[str], kind: Optional[str]) -> str:
    """
    Resolve the queue work_type from explicit input or kind inference.

    Purpose:
    - Ensure the caller chooses a concrete queue file.

    Args:
        work_type (Optional[str]): Explicit work type override.
        kind (Optional[str]): Kind to infer from.

    Returns:
        str: Resolved work type.

    Raises:
        ValueError: If the work type cannot be inferred.
    """
    if work_type:
        return work_type
    if kind:
        _, inferred = _normalize_kind(kind)
        if inferred:
            return inferred
        raise ValueError(f"Invalid work kind: {kind}")
    return "task"


def _global_work_root(repo_root: Path) -> Path:
    """
    Resolve the global work_management root.

    Purpose:
    - Keep global queue paths centralized for clarity.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Global work_management root.
    """
    return repo_root / "context_compass" / "work_management"


def _global_locks_dir(repo_root: Path) -> Path:
    """
    Resolve the global locks directory for work_management.

    Purpose:
    - Provide a shared lock location for global queues.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Global locks directory.
    """
    return _global_work_root(repo_root) / "locks"


def _queue_path(repo_root: Path, scope: str, bucket: str, work_type: str) -> Path:
    """
    Resolve a queue path for the given scope, bucket, and work type.

    Purpose:
    - Provide deterministic queue locations across global and branch scopes.

    Args:
        repo_root (Path): Repository root.
        scope (str): "global" or "branch".
        bucket (str): Work bucket.
        work_type (str): Work type.

    Returns:
        Path: Queue file path.

    Raises:
        ValueError: If scope is invalid.
    """
    filename = _work_files()[work_type]
    if scope == "global":
        return _global_work_root(repo_root) / bucket / filename
    if scope == "branch":
        return branch_paths.work_root(repo_root) / bucket / filename
    raise ValueError(f"Invalid scope: {scope}")


def _load_or_init_queue(path: Path, now: str) -> dict:
    """
    Load a queue JSON payload or initialize a default structure.

    Purpose:
    - Ensure queues are always valid objects with a queue list.

    Args:
        path (Path): Queue path.
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """
    if path.exists():
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _pop_work_item(queue: list[dict], work_id: str) -> Optional[dict]:
    """
    Remove and return a work item from a queue by work_id.

    Purpose:
    - Provide deterministic removal semantics for move operations.

    Args:
        queue (list[dict]): Queue list.
        work_id (str): Work identifier.

    Returns:
        Optional[dict]: Removed item or None if not found.
    """
    for index, item in enumerate(queue):
        if item.get("work_id") == work_id:
            return queue.pop(index)
    return None


def _acquire_locks(
    entries: list[tuple[Path, Path]],
    owner_id: str,
    ttl_seconds: int,
) -> list[tuple[Path, Path]]:
    """
    Acquire locks for queue resources in deterministic order.

    Purpose:
    - Prevent concurrent writers from corrupting queues.

    Args:
        entries (list[tuple[Path, Path]]): Tuples of (locks_dir, resource_path).
        owner_id (str): Lock owner identifier.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        list[tuple[Path, Path]]: Locked entries for release.
    """
    lock_targets: list[tuple[str, Path, Path]] = []
    for locks_dir, resource in entries:
        locks_dir.mkdir(parents=True, exist_ok=True)
        lock_path = lease.lock_path_for(locks_dir, resource)
        lock_targets.append((str(lock_path), locks_dir, resource))

    lock_targets.sort(key=lambda item: item[0])
    locked: list[tuple[Path, Path]] = []
    for _, locks_dir, resource in lock_targets:
        lease.acquire_lock(locks_dir, resource, owner_id, ttl_seconds=ttl_seconds)
        locked.append((locks_dir, resource))
    return locked


def _release_locks(entries: list[tuple[Path, Path]], owner_id: str) -> None:
    """
    Release locks in reverse acquisition order.

    Args:
        entries (list[tuple[Path, Path]]): Locked entries to release.
        owner_id (str): Lock owner identifier.
    """
    for locks_dir, resource in reversed(entries):
        lease.release_lock(locks_dir, resource, owner_id)


def move_work_item(
    repo_root: Path,
    work_id: str,
    source_bucket: str,
    dest_bucket: str,
    work_type: str,
    owner_id: str,
    new_state: Optional[str] = None,
) -> Tuple[Path, Path]:
    """
    Move a work item from branch queues into the global queues.

    Purpose:
    - Promote completed or shared branch work into the global history.

    Contract:
    - Locks source and destination queues before reading/writing.
    - Removes the item from the branch queue and appends to global queue.
    - Writes JSON atomically with updated timestamps.

    Args:
        repo_root (Path): Repository root.
        work_id (str): Work identifier to move.
        source_bucket (str): Branch source bucket.
        dest_bucket (str): Global destination bucket.
        work_type (str): Queue work type (epic/story/task).
        owner_id (str): Lock owner identifier.
        new_state (Optional[str]): Optional new state for the moved item.

    Returns:
        Tuple[Path, Path]: Source and destination queue paths.

    Raises:
        FileNotFoundError: If the source queue does not exist.
        ValueError: If the item is missing or already exists in destination.
    """
    ensure_feature_enabled(repo_root, "work_management", "move work items")
    now = utc_now_iso()
    source_path = _queue_path(repo_root, "branch", source_bucket, work_type)
    dest_path = _queue_path(repo_root, "global", dest_bucket, work_type)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if not source_path.exists():
        raise FileNotFoundError(f"Source queue not found: {source_path}")

    locks_dir_source = branch_paths.state_root(repo_root) / "locks"
    locks_dir_dest = _global_locks_dir(repo_root)
    policies = agent_presence.load_policies(repo_root)
    locked = _acquire_locks(
        [(locks_dir_source, source_path.resolve()), (locks_dir_dest, dest_path.resolve())],
        owner_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        source_data = _load_or_init_queue(source_path, now)
        dest_data = _load_or_init_queue(dest_path, now)

        source_queue = source_data.setdefault("queue", [])
        dest_queue = dest_data.setdefault("queue", [])
        item = _pop_work_item(source_queue, work_id)
        if item is None:
            raise ValueError(f"Work item not found: {work_id}")
        if any(existing.get("work_id") == work_id for existing in dest_queue):
            raise ValueError(f"Destination already has work item: {work_id}")

        if new_state is not None:
            item["state"] = new_state
        item["updated_at"] = now
        source_data["updated_at"] = now
        dest_data["updated_at"] = now
        dest_queue.append(item)

        write_json_atomic(source_path, source_data)
        write_json_atomic(dest_path, dest_data)
    finally:
        _release_locks(locked, owner_id)

    return source_path, dest_path


def main() -> None:
    """
    CLI entrypoint for moving a branch work item into the global queues.
    """
    parser = argparse.ArgumentParser(description="Move a work item from branch to global queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work item identifier")
    parser.add_argument("--source-bucket", required=True, choices=_bucket_choices(), help="Branch source bucket")
    parser.add_argument("--dest-bucket", required=True, choices=_bucket_choices(), help="Global destination bucket")
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Work type override")
    parser.add_argument("--kind", default=None, help="Kind to infer work type from")
    parser.add_argument("--state", default=None, choices=_state_choices(), help="Optional new state")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.owner_id or args.agent_id)
    ensure_feature_enabled(repo_root, "work_management", "move work items")
    ensure_work_mode(repo_root, args.work_id, "move work items")

    work_type = _resolve_work_type(args.work_type, args.kind)
    if work_type not in _work_files():
        raise ValueError(f"Invalid work type: {work_type}")

    owner_id = args.owner_id or args.agent_id
    source_path, dest_path = move_work_item(
        repo_root,
        args.work_id,
        args.source_bucket,
        args.dest_bucket,
        work_type,
        owner_id,
        new_state=args.state,
    )
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=str(dest_path),
        notes=None,
        command_name="work_item_branch_to_global",
        command_args=sys.argv[1:],
    )
    logger.info("moved %s from %s to %s", args.work_id, source_path, dest_path)


if __name__ == "__main__":
    main()
