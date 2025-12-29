"""Manage context_compass self-context and active agent registry."""

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
    Return default policy values used by self-context tooling.

    Returns:
        dict: Default policy values.
    """
    return {
        "lease_ttl_seconds": 300,
        "lease_heartbeat_seconds": 30,
        "lock_wait_seconds": 10,
    }


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


def _acquire_lock(locks_dir: Path, resource: Path, owner_id: str, ttl_seconds: int) -> dict:
    """
    Acquire or steal a lease lock for a resource.

    Args:
        locks_dir (Path): Directory for lock files.
        resource (Path): Resource to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        dict: Lease record.

    Raises:
        RuntimeError: If a non-expired lock is held by another owner.
    """
    return lease.acquire_lock(locks_dir, resource, owner_id, ttl_seconds)


def _release_lock(locks_dir: Path, resource: Path, owner_id: str) -> None:
    """
    Release a lease lock if owned by the caller.

    Args:
        locks_dir (Path): Directory for lock files.
        resource (Path): Resource to unlock.
        owner_id (str): Lock owner id.
    """
    lease.release_lock(locks_dir, resource, owner_id)


def _ensure_self_context(self_path: Path, agent_id: str) -> None:
    """
    Create a self-context file if it does not exist.

    Args:
        self_path (Path): Target self-context path.
        agent_id (str): Agent identifier.
    """
    if self_path.exists():
        return
    now = utc_now_iso()
    template = {
        "schema_version": 1,
        "agent_id": agent_id,
        "created_at": now,
        "updated_at": now,
        "understanding": {
            "repo_purpose": "TODO: describe repo purpose",
            "non_negotiables": [],
            "style_model": {},
        },
        "skill_receipts": [],
        "open_questions": [],
        "opinions": {
            "what_is_working": [],
            "what_is_confusing": [],
            "suggested_skill_improvements": [],
        },
    }
    write_json_atomic(self_path, template)


def main() -> None:
    """
    CLI entrypoint for self-context management.
    """
    parser = argparse.ArgumentParser(description="Manage context_compass self context")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode")
    parser.add_argument("--current-task-id", default=None, help="Current task id")
    parser.add_argument("--current-target", default=None, help="Current target path")
    parser.add_argument("--notes", default=None, help="Optional notes")
    parser.add_argument("--init-self", action="store_true", help="Initialize self context if missing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    policies = _load_policies(repo_root)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)

    self_path = repo_root / "context_compass" / "self_context" / "agents" / f"{args.agent_id}.self.json"

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.current_task_id,
        current_target=args.current_target,
        notes=args.notes,
        command_name="self_context",
        command_args=sys.argv[1:],
    )

    if args.init_self:
        self_path.parent.mkdir(parents=True, exist_ok=True)
        _acquire_lock(locks_dir, self_path, args.agent_id, policies["lease_ttl_seconds"])
        try:
            _ensure_self_context(self_path, args.agent_id)
        finally:
            _release_lock(locks_dir, self_path, args.agent_id)

    logger.info("self_context updated for agent %s", args.agent_id)


if __name__ == "__main__":
    main()
