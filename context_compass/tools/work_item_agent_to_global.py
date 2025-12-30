"""
Move a work item from a per-agent queue into the global work queues.
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


def _infer_work_type(item: dict, work_type: Optional[str]) -> str:
    """
    Infer the destination work_type from an item or explicit override.

    Purpose:
    - Ensure the destination queue file is explicit and deterministic.

    Args:
        item (dict): Work item payload from the agent queue.
        work_type (Optional[str]): Explicit work type override.

    Returns:
        str: Resolved work type.

    Raises:
        ValueError: If the work type cannot be inferred.
    """
    if work_type:
        if work_type not in _work_files():
            raise ValueError(f"Invalid work_type: {work_type}")
        return work_type
    kind = item.get("kind")
    if isinstance(kind, str):
        _, inferred = _normalize_kind(kind)
        if inferred:
            return inferred
    raise ValueError("work_type is required when item kind is not epic/story/task")


def _agent_queue_path(repo_root: Path, agent_id: str) -> Path:
    """
    Resolve the per-agent work queue path.

    Purpose:
    - Centralize per-agent queue path construction.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.

    Returns:
        Path: Agent queue path.
    """
    return repo_root / "context_compass" / "self_context" / "agents" / f"{agent_id}.work.json"


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


def _load_agent_queue(path: Path) -> dict:
    """
    Load a per-agent work queue.

    Purpose:
    - Ensure agent queues are present and valid before moving items.

    Args:
        path (Path): Agent queue path.

    Returns:
        dict: Agent queue payload.

    Raises:
        FileNotFoundError: If the agent queue is missing.
        ValueError: If the queue is not a JSON object.
    """
    if not path.exists():
        raise FileNotFoundError(f"Agent queue not found: {path}")
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("Agent queue must be a JSON object")
    return data


def _peek_agent_item(path: Path, work_id: str) -> Optional[dict]:
    """
    Peek at a work item in an agent queue without mutating state.

    Purpose:
    - Infer destination queue type before acquiring multiple locks.

    Contract:
    - Returns None if the queue or item does not exist.

    Args:
        path (Path): Agent queue path.
        work_id (str): Work identifier to search for.

    Returns:
        Optional[dict]: Work item payload or None if not found.
    """
    if not path.exists():
        return None
    data = load_json(path)
    if not isinstance(data, dict):
        return None
    queue = data.get("queue", [])
    if not isinstance(queue, list):
        return None
    for item in queue:
        if item.get("work_id") == work_id:
            return item
    return None


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
    source_agent_id: str,
    work_id: str,
    dest_bucket: str,
    owner_id: str,
    work_type: Optional[str] = None,
    new_state: Optional[str] = None,
) -> Tuple[Path, Path]:
    """
    Move a work item from an agent queue into global work queues.

    Purpose:
    - Publish agent-owned work items into the global shared history.

    Contract:
    - Locks the agent queue and destination queue before reading/writing.
    - Removes the item from the agent queue and appends it to the global queue.
    - Writes JSON atomically with updated timestamps.

    Args:
        repo_root (Path): Repository root.
        source_agent_id (str): Agent queue owner to read from.
        work_id (str): Work identifier to move.
        dest_bucket (str): Destination bucket in global queues.
        owner_id (str): Lock owner identifier.
        work_type (Optional[str]): Work type override (epic/story/task).
        new_state (Optional[str]): Optional new state for the moved item.

    Returns:
        Tuple[Path, Path]: Source agent queue path and destination queue path.

    Raises:
        FileNotFoundError: If the agent queue does not exist.
        ValueError: If the item is missing or destination already has it.
    """
    ensure_feature_enabled(repo_root, "work_management", "move work items")
    now = utc_now_iso()
    source_path = _agent_queue_path(repo_root, source_agent_id)

    preview_item = _peek_agent_item(source_path, work_id)
    if preview_item is None and work_type is None:
        raise FileNotFoundError(f"Agent queue missing work item: {work_id}")
    resolved_type = _infer_work_type(preview_item or {}, work_type)
    dest_path = _global_work_root(repo_root) / dest_bucket / _work_files()[resolved_type]

    locks_dir_source = branch_paths.self_context_locks_dir(repo_root)
    locks_dir_dest = _global_locks_dir(repo_root)
    policies = agent_presence.load_policies(repo_root)
    locked = _acquire_locks(
        [(locks_dir_source, source_path.resolve()), (locks_dir_dest, dest_path.resolve())],
        owner_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        source_data = _load_agent_queue(source_path)
        source_queue = source_data.get("queue", [])
        if not isinstance(source_queue, list):
            raise ValueError("Agent queue must contain a list")

        item = _pop_work_item(source_queue, work_id)
        if item is None:
            raise ValueError(f"Work item not found: {work_id}")

        locked_type = _infer_work_type(item, work_type)
        if locked_type != resolved_type:
            raise ValueError("work_type changed after lock; retry with explicit --work-type")
        dest_path = _global_work_root(repo_root) / dest_bucket / _work_files()[resolved_type]
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_data = _load_or_init_queue(dest_path, now)
        dest_queue = dest_data.setdefault("queue", [])
        if any(existing.get("work_id") == work_id for existing in dest_queue):
            raise ValueError(f"Destination already has work item: {work_id}")

        if new_state is not None:
            item["state"] = new_state
        item["updated_at"] = now
        source_data["queue"] = source_queue
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
    CLI entrypoint for moving an agent work item into global queues.
    """
    parser = argparse.ArgumentParser(description="Move a work item from an agent queue to global queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier (actor)")
    parser.add_argument("--source-agent-id", default=None, help="Source agent queue id (defaults to agent-id)")
    parser.add_argument("--work-id", required=True, help="Work item identifier")
    parser.add_argument("--dest-bucket", required=True, choices=_bucket_choices(), help="Global destination bucket")
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Work type override")
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

    source_agent_id = args.source_agent_id or args.agent_id
    owner_id = args.owner_id or args.agent_id
    source_path, dest_path = move_work_item(
        repo_root,
        source_agent_id,
        args.work_id,
        args.dest_bucket,
        owner_id,
        work_type=args.work_type,
        new_state=args.state,
    )
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=str(dest_path),
        notes=None,
        command_name="work_item_agent_to_global",
        command_args=sys.argv[1:],
    )
    logger.info("moved %s from %s to %s", args.work_id, source_path, dest_path)


if __name__ == "__main__":
    main()
