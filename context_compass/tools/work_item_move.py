"""Move a work item between work_management queues."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _work_files() -> dict:
    """
    Return the work_management queue filenames by type.

    Returns:
        dict: Mapping of work types to queue filenames.
    """
    return {"epic": "epics.json", "story": "stories.json", "task": "tasks.json"}


def _aliases() -> dict:
    """
    Return kind aliases that normalize to canonical work types.

    Returns:
        dict: Mapping of kind aliases to canonical work types.
    """
    return {"epic": "epic", "story": "story", "task": "task"}


def _bucket_choices() -> list[str]:
    """
    Return allowed work bucket values.

    Returns:
        list[str]: Allowed bucket values.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


def _state_choices() -> list[str]:
    """
    Return allowed work item state values.

    Returns:
        list[str]: Allowed state values.
    """
    return ["queued", "leased", "in_progress", "done", "failed", "cancelled"]


def _normalize_kind(kind: str) -> tuple[str, Optional[str]]:
    """
    Normalize known kind aliases and infer a work type.

    Args:
        kind (str): Input kind string.

    Returns:
        tuple[str, Optional[str]]: Normalized kind and inferred work type.
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


def _queue_path(repo_root: Path, bucket: str, work_type: str) -> Path:
    """
    Resolve the JSON queue path for a work type in a bucket.

    Args:
        repo_root (Path): Repository root.
        bucket (str): Work bucket.
        work_type (str): Work type.

    Returns:
        Path: Queue file path.
    """
    filename = _work_files()[work_type]
    return branch_paths.work_root(repo_root) / bucket / filename


def _load_or_init_queue(path: Path, now: str) -> dict:
    """
    Load a queue JSON payload or initialize a default structure.

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

    Args:
        queue (list[dict]): Queue list.
        work_id (str): Work identifier to remove.

    Returns:
        Optional[dict]: Removed item or None if not found.
    """
    for index, item in enumerate(queue):
        if item.get("work_id") == work_id:
            return queue.pop(index)
    return None


def move_work_item(
    repo_root: Path,
    work_id: str,
    source_bucket: str,
    dest_bucket: str,
    work_type: str,
    owner_id: str,
    new_state: Optional[str] = None,
) -> tuple[Path, Path]:
    """
    Move a work item between buckets for a given work type.

    Args:
        repo_root (Path): Repository root.
        work_id (str): Work identifier.
        source_bucket (str): Source bucket.
        dest_bucket (str): Destination bucket.
        work_type (str): Work type.
        owner_id (str): Lock owner id.
        new_state (Optional[str]): Optional new state.

    Returns:
        tuple[Path, Path]: Source and destination queue paths.
    """
    ensure_feature_enabled(repo_root, "work_management", "move work items")
    if source_bucket == dest_bucket:
        raise ValueError("source and destination buckets must differ")
    now = utc_now_iso()
    source_path = _queue_path(repo_root, source_bucket, work_type)
    dest_path = _queue_path(repo_root, dest_bucket, work_type)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    policies = agent_presence.load_policies(repo_root)
    resources = sorted({source_path.resolve(), dest_path.resolve()}, key=lambda p: str(p))
    locked: list[Path] = []
    for resource in resources:
        lease.acquire_lock(locks_dir, resource, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
        locked.append(resource)
    try:
        if not source_path.exists():
            raise FileNotFoundError(f"Source queue not found: {source_path}")
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
        for resource in reversed(locked):
            lease.release_lock(locks_dir, resource, owner_id)

    return source_path, dest_path


def main() -> None:
    """
    CLI entrypoint for moving work items between buckets.
    """
    parser = argparse.ArgumentParser(description="Move a work item between work_management queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work item identifier")
    parser.add_argument("--source-bucket", required=True, choices=_bucket_choices(), help="Source bucket")
    parser.add_argument("--dest-bucket", required=True, choices=_bucket_choices(), help="Destination bucket")
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Queue type override")
    parser.add_argument("--kind", default=None, help="Work kind (used to infer work type)")
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

    work_type = args.work_type
    if work_type is None and args.kind:
        _, inferred = _normalize_kind(args.kind)
        if inferred is None:
            raise ValueError(f"Invalid work kind: {args.kind}")
        work_type = inferred
    if work_type is None:
        work_type = "task"

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
        command_name="work_item_move",
        command_args=sys.argv[1:],
    )
    logger.info("moved %s from %s to %s", args.work_id, source_path, dest_path)


if __name__ == "__main__":
    main()
