"""
Delete context state files from a branch.
"""

import argparse
import logging
import sys
from pathlib import Path
from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.json_io import load_json
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


def _context_filenames(include_repo_state: bool) -> list[str]:
    """
    Return the context file names to delete.

    Args:
        include_repo_state (bool): Include repo_state.json if True.

    Returns:
        list[str]: File names.
    """
    names = [
        "context_profiles.json",
        "architecture_context.json",
        "component_contexts.json",
        "test_architecture_context.json",
        "test_component_contexts.json",
    ]
    if include_repo_state:
        names.append("repo_state.json")
    return names


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


def delete_context(
    repo_root: Path,
    branch_name: str,
    include_repo_state: bool,
    owner_id: str,
) -> dict:
    """
    Delete context state files from the branch state root.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        include_repo_state (bool): Delete repo_state.json if True.
        owner_id (str): Lock owner id.

    Returns:
        dict: Summary of deleted files.
    """
    policies = _load_policies(repo_root)
    state_root = branch_paths.state_root(repo_root, branch_name)
    if not state_root.exists():
        raise FileNotFoundError(f"Branch state root does not exist: {state_root}")
    locks_dir = state_root / "locks"

    entries: list[tuple[Path, Path]] = []
    for name in _context_filenames(include_repo_state):
        entries.append((locks_dir, state_root / name))

    locked = _lock_entries(entries, owner_id, ttl_seconds=int(policies["lease_ttl_seconds"]))
    deleted: list[str] = []
    skipped: list[str] = []
    try:
        for name in _context_filenames(include_repo_state):
            path = state_root / name
            if not path.exists():
                skipped.append(name)
                continue
            path.unlink()
            deleted.append(name)
    finally:
        for lock_dir, resource in locked:
            lease.release_lock(lock_dir, resource, owner_id)

    return {"deleted": deleted, "skipped": skipped}


def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Delete branch context state files.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--branch-name", required=True, help="Branch name to modify")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode label")
    parser.add_argument(
        "--include-repo-state",
        action="store_true",
        help="Also delete repo_state.json",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_work_mode(repo_root, args.work_id, "delete branch context state")

    summary = delete_context(
        repo_root=repo_root,
        branch_name=args.branch_name,
        include_repo_state=args.include_repo_state,
        owner_id=args.agent_id,
    )

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=f"branch_context_delete:{args.branch_name}",
        notes=None,
        command_name="branch_delete_context",
        command_args=sys.argv[1:],
    )
    logger.info("deleted context files: %s", summary["deleted"])


if __name__ == "__main__":
    main()
