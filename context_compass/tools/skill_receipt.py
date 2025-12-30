"""Write deterministic skill read receipts for context_compass."""

import argparse
import logging
import sys
from pathlib import Path

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values used by skill receipt tooling.

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


def _acquire_lock(locks_dir: Path, resource: Path, owner_id: str, ttl_seconds: int) -> None:
    """
    Acquire or steal a lease lock for a resource.

    Args:
        locks_dir (Path): Directory for lock files.
        resource (Path): Resource to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.

    Raises:
        RuntimeError: If a non-expired lock is held by another owner.
    """
    lease.acquire_lock(locks_dir, resource, owner_id, ttl_seconds)


def _release_lock(locks_dir: Path, resource: Path, owner_id: str) -> None:
    """
    Release a lease lock if owned by the caller.

    Args:
        locks_dir (Path): Directory for lock files.
        resource (Path): Resource to unlock.
        owner_id (str): Lock owner id.
    """
    lease.release_lock(locks_dir, resource, owner_id)


def _load_self_context(path: Path) -> dict:
    """
    Load a self-context file.

    Args:
        path (Path): Self-context path.

    Returns:
        dict: Self-context data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Missing self-context file: {path}")
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("Self-context JSON must be an object")
    return data


def _upsert_receipt(self_data: dict, skill_id: str, version: int, summary: str) -> bool:
    """
    Insert or update a skill receipt entry.

    Args:
        self_data (dict): Self-context data.
        skill_id (str): Skill identifier.
        version (int): Skill version.
        summary (str): Agent summary of the skill.

    Returns:
        bool: True if changes were made.
    """
    receipts = self_data.setdefault("skill_receipts", [])
    for entry in receipts:
        if entry.get("skill_id") == skill_id and entry.get("version") == version:
            if entry.get("agent_summary") == summary:
                return False
            entry["agent_summary"] = summary
            entry["read_at"] = utc_now_iso()
            return True
    receipts.append(
        {
            "skill_id": skill_id,
            "version": version,
            "read_at": utc_now_iso(),
            "agent_summary": summary,
        }
    )
    return True


def main() -> None:
    """
    CLI entrypoint for skill receipt updates.
    """
    parser = argparse.ArgumentParser(description="Write context_compass skill receipts")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--skill-id", required=True, help="Skill identifier")
    parser.add_argument("--version", type=int, required=True, help="Skill version")
    parser.add_argument("--summary", required=True, help="Agent summary of the skill")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode="agent",
        current_task_id=None,
        current_target=None,
        notes=None,
        command_name="skill_receipt",
        command_args=sys.argv[1:],
    )
    policies = _load_policies(repo_root)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    self_path = repo_root / "context_compass" / "self_context" / "agents" / f"{args.agent_id}.self.json"

    _acquire_lock(locks_dir, self_path, args.agent_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        data = _load_self_context(self_path)
        changed = _upsert_receipt(data, args.skill_id, args.version, args.summary)
        if changed:
            data["updated_at"] = utc_now_iso()
            write_json_atomic(self_path, data)
            logger.info("skill receipt updated for %s", args.skill_id)
        else:
            logger.info("skill receipt already up to date for %s", args.skill_id)
    finally:
        _release_lock(locks_dir, self_path, args.agent_id)


if __name__ == "__main__":
    main()
