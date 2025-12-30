"""
Archive or delete a branch management directory.
"""

import argparse
import logging
import shutil
import sys
from pathlib import Path
from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.json_io import load_json
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_mode_guard import ensure_work_mode


def _default_policies() -> dict:
    """
    Return default policy values for branch cleanup operations.

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


def _archive_path(repo_root: Path, branch_name: str, now: str) -> Path:
    """
    Build an archive path for the branch directory.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        now (str): Current timestamp.

    Returns:
        Path: Archive path.
    """
    safe_stamp = now.replace(":", "-").replace("Z", "Z")
    archive_root = branch_paths.branch_management_root(repo_root) / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    return archive_root / f"{branch_name}__{safe_stamp}"


def _lock_branch(repo_root: Path, branch_name: str, owner_id: str, ttl_seconds: int) -> Path:
    """
    Acquire a lock for branch cleanup operations.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL seconds.

    Returns:
        Path: Lock directory.
    """
    locks_dir = branch_paths.branch_management_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lease.acquire_lock(locks_dir, branch_paths.branch_root(repo_root, branch_name), owner_id, ttl_seconds=ttl_seconds)
    return locks_dir


def cleanup_branch(
    repo_root: Path,
    branch_name: str,
    owner_id: str,
    archive: bool,
    force: bool,
) -> Path:
    """
    Archive or delete the branch directory.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        owner_id (str): Lock owner id.
        archive (bool): Archive instead of delete when True.
        force (bool): Overwrite existing archive if needed.

    Returns:
        Path: Destination path (archive or deleted branch root).
    """
    policies = _load_policies(repo_root)
    branch_root = branch_paths.branch_root(repo_root, branch_name)
    if not branch_root.exists():
        raise FileNotFoundError(f"Branch directory does not exist: {branch_root}")

    active_branch = branch_paths.load_current_branch(repo_root)
    if active_branch == branch_name:
        raise RuntimeError("Cannot cleanup the active branch; switch branches first.")

    locks_dir = _lock_branch(repo_root, branch_name, owner_id, ttl_seconds=int(policies["lease_ttl_seconds"]))
    try:
        if archive:
            now = utc_now_iso()
            archive_path = _archive_path(repo_root, branch_name, now)
            if archive_path.exists():
                if not force:
                    raise FileExistsError(f"Archive already exists: {archive_path}")
                shutil.rmtree(archive_path)
            shutil.move(str(branch_root), str(archive_path))
            return archive_path
        shutil.rmtree(branch_root)
        return branch_root
    finally:
        lease.release_lock(locks_dir, branch_paths.branch_root(repo_root, branch_name), owner_id)


def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Archive or delete a branch directory.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--branch-name", required=True, help="Branch name to clean up")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode label")
    parser.add_argument("--no-archive", action="store_true", help="Delete instead of archive")
    parser.add_argument("--force", action="store_true", help="Overwrite existing archive if needed")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    ensure_work_mode(repo_root, args.work_id, "cleanup branch state")

    destination = cleanup_branch(
        repo_root=repo_root,
        branch_name=args.branch_name,
        owner_id=args.agent_id,
        archive=not args.no_archive,
        force=args.force,
    )

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=f"branch_cleanup:{args.branch_name}",
        notes=None,
        command_name="branch_cleanup",
        command_args=sys.argv[1:],
    )
    logger.info("branch cleanup completed: %s", destination)


if __name__ == "__main__":
    main()
