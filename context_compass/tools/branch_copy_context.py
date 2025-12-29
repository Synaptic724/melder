"""
Copy context state files from one branch to another.
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


def _context_filenames() -> list[str]:
    """
    Return branch state context filenames to copy.

    Returns:
        list[str]: Context file names.
    """
    return [
        "repo_state.json",
        "context_profiles.json",
        "architecture_context.json",
        "component_contexts.json",
        "test_architecture_context.json",
        "test_component_contexts.json",
    ]


def _reset_repo_state(payload: dict, repo_root: Path, now: str) -> dict:
    """
    Reset scan counters and timestamps to force a fresh scan.

    Args:
        payload (dict): Repo state payload.
        repo_root (Path): Repository root.
        now (str): Current timestamp.

    Returns:
        dict: Updated repo state payload.
    """
    updated = dict(payload)
    updated["repo_root"] = str(repo_root)
    updated["scan_counter"] = 0
    updated["last_scan_id"] = None
    updated["last_scan_at"] = None
    updated["scanner_version"] = None
    updated["updated_at"] = now
    return updated


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


def copy_context(
    repo_root: Path,
    source_branch: str,
    dest_branch: str,
    preserve_repo_state: bool,
    owner_id: str,
) -> dict:
    """
    Copy context state files from a source branch to a destination branch.

    Args:
        repo_root (Path): Repository root.
        source_branch (str): Source branch name.
        dest_branch (str): Destination branch name.
        preserve_repo_state (bool): Whether to keep scan counters and timestamps.
        owner_id (str): Lock owner id.

    Returns:
        dict: Summary of copied files.
    """
    policies = _load_policies(repo_root)
    now = utc_now_iso()
    source_root = branch_paths.state_root(repo_root, source_branch)
    dest_root = branch_paths.state_root(repo_root, dest_branch)
    if not source_root.exists():
        raise FileNotFoundError(f"Source branch state does not exist: {source_root}")
    dest_root.mkdir(parents=True, exist_ok=True)
    (dest_root / "locks").mkdir(parents=True, exist_ok=True)

    src_locks = source_root / "locks"
    dest_locks = dest_root / "locks"

    entries: list[tuple[Path, Path]] = []
    for name in _context_filenames():
        src_path = source_root / name
        dest_path = dest_root / name
        if src_path.exists():
            entries.append((src_locks, src_path))
        entries.append((dest_locks, dest_path))

    locked = _lock_entries(entries, owner_id, ttl_seconds=int(policies["lease_ttl_seconds"]))
    copied: list[str] = []
    skipped: list[str] = []
    try:
        for name in _context_filenames():
            src_path = source_root / name
            dest_path = dest_root / name
            if not src_path.exists():
                skipped.append(name)
                continue
            data = load_json(src_path)
            if not isinstance(data, dict):
                skipped.append(name)
                continue
            if name == "repo_state.json" and not preserve_repo_state:
                data = _reset_repo_state(data, repo_root, now)
            write_json_atomic(dest_path, data)
            copied.append(name)
    finally:
        for locks_dir, resource in locked:
            lease.release_lock(locks_dir, resource, owner_id)

    return {"copied": copied, "skipped": skipped}


def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Copy branch context state files.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--source-branch", required=True, help="Source branch name")
    parser.add_argument("--dest-branch", required=True, help="Destination branch name")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode label")
    parser.add_argument(
        "--preserve-repo-state",
        action="store_true",
        help="Preserve repo_state scan counters and timestamps",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_work_mode(repo_root, args.work_id, "copy branch context state")

    summary = copy_context(
        repo_root=repo_root,
        source_branch=args.source_branch,
        dest_branch=args.dest_branch,
        preserve_repo_state=args.preserve_repo_state,
        owner_id=args.agent_id,
    )

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=f"branch_context_copy:{args.source_branch}->{args.dest_branch}",
        notes=None,
        command_name="branch_copy_context",
        command_args=sys.argv[1:],
    )
    logger.info("copied context files: %s", summary["copied"])


if __name__ == "__main__":
    main()
