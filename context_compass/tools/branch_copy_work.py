"""
Copy work_management queues from one branch to another.
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
    Return default policy values for branch copy operations.

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


def _work_files() -> list[str]:
    """
    Return the work_management queue filenames.

    Returns:
        list[str]: Queue file names.
    """
    return ["epics.json", "stories.json", "tasks.json"]


def _bucket_names() -> list[str]:
    """
    Return the work_management bucket names.

    Returns:
        list[str]: Bucket names.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


def _default_queue(now: str) -> dict:
    """
    Return a default queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _normalize_queue(data: dict, now: str, preserve_state: bool) -> dict:
    """
    Normalize a work queue for copy operations.

    Args:
        data (dict): Source queue payload.
        now (str): Current timestamp.
        preserve_state (bool): Keep state/leases if True.

    Returns:
        dict: Normalized queue payload.
    """
    queue = data.get("queue", [])
    if not isinstance(queue, list):
        queue = []
    normalized: list[dict] = []
    for item in queue:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        if not preserve_state:
            if entry.get("state") in ("leased", "in_progress"):
                entry["state"] = "queued"
            entry["lease"] = None
        entry["updated_at"] = now
        normalized.append(entry)
    return {
        "schema_version": int(data.get("schema_version") or 1),
        "repo_id": data.get("repo_id"),
        "updated_at": now,
        "queue": normalized,
    }


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


def copy_work(
    repo_root: Path,
    source_branch: str,
    dest_branch: str,
    preserve_state: bool,
    owner_id: str,
) -> dict:
    """
    Copy work_management queues from source to destination branch.

    Args:
        repo_root (Path): Repository root.
        source_branch (str): Source branch name.
        dest_branch (str): Destination branch name.
        preserve_state (bool): Preserve leases and in_progress states if True.
        owner_id (str): Lock owner id.

    Returns:
        dict: Summary of copied files.
    """
    policies = _load_policies(repo_root)
    now = utc_now_iso()
    source_root = branch_paths.work_root(repo_root, source_branch)
    dest_root = branch_paths.work_root(repo_root, dest_branch)
    if not source_root.exists():
        raise FileNotFoundError(f"Source branch work queues do not exist: {source_root}")
    dest_root.mkdir(parents=True, exist_ok=True)

    src_locks = branch_paths.state_root(repo_root, source_branch) / "locks"
    dest_locks = branch_paths.state_root(repo_root, dest_branch) / "locks"
    dest_locks.mkdir(parents=True, exist_ok=True)

    entries: list[tuple[Path, Path]] = []
    for bucket in _bucket_names():
        for filename in _work_files():
            src_path = source_root / bucket / filename
            dest_path = dest_root / bucket / filename
            if src_path.exists():
                entries.append((src_locks, src_path))
            entries.append((dest_locks, dest_path))

    locked = _lock_entries(entries, owner_id, ttl_seconds=int(policies["lease_ttl_seconds"]))
    copied: list[str] = []
    skipped: list[str] = []
    try:
        for bucket in _bucket_names():
            for filename in _work_files():
                src_path = source_root / bucket / filename
                dest_path = dest_root / bucket / filename
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                if not src_path.exists():
                    write_json_atomic(dest_path, _default_queue(now))
                    skipped.append(f"{bucket}/{filename}")
                    continue
                data = load_json(src_path)
                if not isinstance(data, dict):
                    write_json_atomic(dest_path, _default_queue(now))
                    skipped.append(f"{bucket}/{filename}")
                    continue
                normalized = _normalize_queue(data, now, preserve_state)
                write_json_atomic(dest_path, normalized)
                copied.append(f"{bucket}/{filename}")
    finally:
        for locks_dir, resource in locked:
            lease.release_lock(locks_dir, resource, owner_id)

    return {"copied": copied, "skipped": skipped}


def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Copy branch work queues.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--source-branch", required=True, help="Source branch name")
    parser.add_argument("--dest-branch", required=True, help="Destination branch name")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode label")
    parser.add_argument(
        "--preserve-state",
        action="store_true",
        help="Preserve lease and in_progress states",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    ensure_work_mode(repo_root, args.work_id, "copy branch work queues")

    summary = copy_work(
        repo_root=repo_root,
        source_branch=args.source_branch,
        dest_branch=args.dest_branch,
        preserve_state=args.preserve_state,
        owner_id=args.agent_id,
    )

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=f"branch_work_copy:{args.source_branch}->{args.dest_branch}",
        notes=None,
        command_name="branch_copy_work",
        command_args=sys.argv[1:],
    )
    logger.info("copied work queues: %s", summary["copied"])


if __name__ == "__main__":
    main()
