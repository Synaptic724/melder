"""Manage context_compass agent lifecycle (create, archive, delete)."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable

from context_compass.tools import lease, self_context
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values used by agent management.

    Returns:
        dict: Default policy values.
    """
    return {"lease_ttl_seconds": 300}


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
            policies.update({k: v for k, v in data.items() if k in policies})
    return policies


def _load_active_agents(path: Path) -> dict:
    """
    Load active_agents.json or initialize a default structure.

    Args:
        path (Path): active_agents.json path.

    Returns:
        dict: Active agents data.
    """
    if path.exists():
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return {"schema_version": 1, "updated_at": utc_now_iso(), "agents": []}


def _remove_active_agent(active: dict, agent_id: str) -> bool:
    """
    Remove an agent entry from active_agents data.

    Args:
        active (dict): Active agents data.
        agent_id (str): Agent identifier.

    Returns:
        bool: True if an entry was removed.
    """
    agents = active.get("agents", [])
    original = len(agents)
    active["agents"] = [entry for entry in agents if entry.get("agent_id") != agent_id]
    return len(active["agents"]) != original


def _default_worklist(agent_id: str) -> dict:
    """
    Return a default per-agent worklist.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        dict: Worklist payload.
    """
    return {
        "schema_version": 1,
        "agent_id": agent_id,
        "updated_at": utc_now_iso(),
        "queue": [],
    }


def _safe_timestamp() -> str:
    """
    Return a filesystem-safe UTC timestamp.

    Returns:
        str: Timestamp string safe for paths.
    """
    return utc_now_iso().replace(":", "-")


def _acquire_locks(locks_dir: Path, resources: Iterable[Path], owner_id: str, ttl_seconds: int) -> list[Path]:
    """
    Acquire locks for a set of resources in deterministic order.

    Args:
        locks_dir (Path): Lock directory.
        resources (Iterable[Path]): Resources to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        list[Path]: Resources locked.
    """
    locked: list[Path] = []
    for resource in sorted({r.resolve() for r in resources}, key=lambda p: str(p)):
        lease.acquire_lock(locks_dir, resource, owner_id, ttl_seconds)
        locked.append(resource)
    return locked


def _release_locks(locks_dir: Path, resources: Iterable[Path], owner_id: str) -> None:
    """
    Release locks for a set of resources in reverse order.

    Args:
        locks_dir (Path): Lock directory.
        resources (Iterable[Path]): Resources to unlock.
        owner_id (str): Lock owner id.
    """
    for resource in reversed(list(resources)):
        lease.release_lock(locks_dir, resource, owner_id)


def _write_worklist(path: Path, agent_id: str) -> None:
    """
    Create a default worklist if missing.

    Args:
        path (Path): Worklist path.
        agent_id (str): Agent identifier.
    """
    if path.exists():
        return
    write_json_atomic(path, _default_worklist(agent_id))


def _archive_agent_files(archive_root: Path, agent_id: str, files: Iterable[Path]) -> list[Path]:
    """
    Archive agent files under a timestamped directory.

    Args:
        archive_root (Path): Root archive directory.
        agent_id (str): Agent identifier.
        files (Iterable[Path]): Files to archive.

    Returns:
        list[Path]: Archived destination paths.
    """
    timestamp = _safe_timestamp()
    dest_dir = archive_root / "agents" / agent_id / timestamp
    dest_dir.mkdir(parents=True, exist_ok=True)
    archived: list[Path] = []
    for path in files:
        if path.exists():
            dest_path = dest_dir / path.name
            path.replace(dest_path)
            archived.append(dest_path)
    return archived


def create_agent(repo_root: Path, agent_id: str, owner_id: str) -> None:
    """
    Create per-agent self context, worklist, and profile files if missing.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        owner_id (str): Lock owner id.
    """
    policies = _load_policies(repo_root)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    agents_dir = repo_root / "context_compass" / "self_context" / "agents"
    self_path = agents_dir / f"{agent_id}.self.json"
    work_path = agents_dir / f"{agent_id}.work.json"
    profile_path = agents_dir / f"{agent_id}.profile.json"

    agents_dir.mkdir(parents=True, exist_ok=True)
    locked = _acquire_locks(
        locks_dir,
        [self_path, work_path, profile_path],
        owner_id,
        policies["lease_ttl_seconds"],
    )
    try:
        self_context._ensure_self_context(self_path, agent_id)
        _write_worklist(work_path, agent_id)
        agent_presence.ensure_profile_file(profile_path, agent_id)
    finally:
        _release_locks(locks_dir, locked, owner_id)


def delete_agent(repo_root: Path, agent_id: str, owner_id: str) -> None:
    """
    Delete per-agent self context, worklist, and profile files.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        owner_id (str): Lock owner id.
    """
    policies = _load_policies(repo_root)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    agents_dir = repo_root / "context_compass" / "self_context" / "agents"
    active_path = repo_root / "context_compass" / "self_context" / "active_agents.json"
    self_path = agents_dir / f"{agent_id}.self.json"
    work_path = agents_dir / f"{agent_id}.work.json"
    profile_path = agents_dir / f"{agent_id}.profile.json"

    locked = _acquire_locks(
        locks_dir,
        [active_path, self_path, work_path, profile_path],
        owner_id,
        policies["lease_ttl_seconds"],
    )
    try:
        if active_path.exists():
            active = _load_active_agents(active_path)
            if _remove_active_agent(active, agent_id):
                active["updated_at"] = utc_now_iso()
                write_json_atomic(active_path, active)
        if self_path.exists():
            self_path.unlink()
        if work_path.exists():
            work_path.unlink()
        if profile_path.exists():
            profile_path.unlink()
    finally:
        _release_locks(locks_dir, locked, owner_id)


def archive_agent(repo_root: Path, agent_id: str, owner_id: str) -> None:
    """
    Archive per-agent self context, worklist, and profile files.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        owner_id (str): Lock owner id.
    """
    policies = _load_policies(repo_root)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    agents_dir = repo_root / "context_compass" / "self_context" / "agents"
    active_path = repo_root / "context_compass" / "self_context" / "active_agents.json"
    self_path = agents_dir / f"{agent_id}.self.json"
    work_path = agents_dir / f"{agent_id}.work.json"
    profile_path = agents_dir / f"{agent_id}.profile.json"
    archive_root = repo_root / "context_compass" / "archive"

    locked = _acquire_locks(
        locks_dir,
        [active_path, self_path, work_path, profile_path],
        owner_id,
        policies["lease_ttl_seconds"],
    )
    try:
        if active_path.exists():
            active = _load_active_agents(active_path)
            if _remove_active_agent(active, agent_id):
                active["updated_at"] = utc_now_iso()
                write_json_atomic(active_path, active)
        _archive_agent_files(archive_root, agent_id, [self_path, work_path, profile_path])
    finally:
        _release_locks(locks_dir, locked, owner_id)


def main() -> None:
    """
    CLI entrypoint for agent lifecycle management.
    """
    parser = argparse.ArgumentParser(description="Manage context_compass agent lifecycle")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--owner-id", help="Lock owner id (defaults to agent-id)")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("create", help="Create agent files")
    subparsers.add_parser("delete", help="Delete agent files")
    subparsers.add_parser("archive", help="Archive agent files")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)

    owner_id = args.owner_id or args.agent_id
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=owner_id,
        mode=args.mode,
        current_task_id=None,
        current_target=None,
        notes=None,
        command_name="agent_manage",
        command_args=sys.argv[1:],
    )
    if args.command == "create":
        create_agent(repo_root, args.agent_id, owner_id)
        logger.info("agent created: %s", args.agent_id)
    elif args.command == "delete":
        delete_agent(repo_root, args.agent_id, owner_id)
        logger.info("agent deleted: %s", args.agent_id)
    elif args.command == "archive":
        archive_agent(repo_root, args.agent_id, owner_id)
        logger.info("agent archived: %s", args.agent_id)


if __name__ == "__main__":
    main()
