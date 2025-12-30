"""
Clear work_management queues for a branch.
"""

import argparse
import logging
import sys
from pathlib import Path
from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_mode_guard import ensure_work_mode


def _default_policies() -> dict:
    """
    Return default policy values for branch delete operations.

    Returns:
        dict: Policy defaults.
    """
    return {"lease_ttl_seconds": 300, "lock_wait_seconds": 10}


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies.
    """
    policies = _default_policies()
    config_path = repo_root / "context_compass" / "config" / "policies.json"
    if config_path.exists():
        data = load_json(config_path)
        if isinstance(data, dict):
            policies.update({key: value for key, value in data.items() if key in policies})
    return policies


def _bucket_names() -> list[str]:
    """
    Return work bucket names.

    Returns:
        list[str]: Bucket names.
    """
    return ["active", "backlog", "completed", "denied"]


def _work_files() -> list[str]:
    """
    Return work queue filenames.

    Returns:
        list[str]: Queue filenames.
    """
    return ["epics.json", "stories.json", "tasks.json"]


def _default_queue(now: str) -> dict:
    """
    Return a default queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _lock_entries(entries: list[tuple[Path, Path]], owner_id: str, ttl_seconds: int) -> list[tuple[Path, Path]]:
    """
    Acquire locks for the provided resources in deterministic order.

    Args:
        entries (list[tuple[Path, Path]]): (locks_dir, resource) tuples.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL seconds.

    Returns:
        list[tuple[Path, Path]]: Locked entries.
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


def clear_work(
    repo_root: Path,
    branch_name: str,
    owner_id: str,
) -> dict:
    """
    Clear all work queues for the specified branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        owner_id (str): Lock owner id.

    Returns:
        dict: Summary of cleared files.
    """
    policies = _load_policies(repo_root)
    now = utc_now_iso()
    work_root = branch_paths.work_root(repo_root, branch_name)
    if not work_root.exists():
        raise FileNotFoundError(f"Branch work root does not exist: {work_root}")

    locks_dir = branch_paths.state_root(repo_root, branch_name) / "locks"
    entries: list[tuple[Path, Path]] = []
    for bucket in _bucket_names():
        for filename in _work_files():
            entries.append((locks_dir, work_root / bucket / filename))

    locked = _lock_entries(entries, owner_id, ttl_seconds=int(policies["lease_ttl_seconds"]))
    cleared: list[str] = []
    try:
        for bucket in _bucket_names():
            for filename in _work_files():
                queue_path = work_root / bucket / filename
                queue_path.parent.mkdir(parents=True, exist_ok=True)
                write_json_atomic(queue_path, _default_queue(now))
                cleared.append(f"{bucket}/{filename}")
    finally:
        for lock_dir, resource in locked:
            lease.release_lock(lock_dir, resource, owner_id)

    return {"cleared": cleared}


def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Clear branch work queues.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--branch-name", required=True, help="Branch name to modify")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode label")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    ensure_work_mode(repo_root, args.work_id, "clear branch work queues")

    summary = clear_work(
        repo_root=repo_root,
        branch_name=args.branch_name,
        owner_id=args.agent_id,
    )

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=f"branch_work_clear:{args.branch_name}",
        notes=None,
        command_name="branch_delete_work",
        command_args=sys.argv[1:],
    )
    logger.info("cleared work queues: %s", summary["cleared"])


if __name__ == "__main__":
    main()
