"""
Remove a memory entry from the user or system memory store.
"""

import argparse
import logging
import sys
from pathlib import Path

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.memory_store import load_store, memory_locks_dir, write_store
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json


def _default_policies() -> dict:
    """
    Return default policy values for memory deletes.

    Returns:
        dict: Default policy values.
    """
    return {"lease_ttl_seconds": 300, "lock_wait_seconds": 10}


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy values from config with defaults.

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


def remove_memory(repo_root: Path, store: str, memory_id: str) -> bool:
    """
    Remove a memory entry by id.

    Args:
        repo_root (Path): Repository root.
        store (str): Store name (user/system).
        memory_id (str): Memory identifier.

    Returns:
        bool: True if the entry was removed.
    """
    now = utc_now_iso()
    store_path, data = load_store(repo_root, store)
    memories = data.get("memories", [])
    if not isinstance(memories, list):
        memories = []
    original = len(memories)
    data["memories"] = [entry for entry in memories if entry.get("memory_id") != memory_id]
    if len(data["memories"]) == original:
        return False
    data["updated_at"] = now
    write_store(store_path, data)
    return True


def main() -> None:
    """
    CLI entrypoint for memory removals.
    """
    parser = argparse.ArgumentParser(description="Remove a memory entry")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--store", required=True, choices=["user", "system"], help="Memory store name")
    parser.add_argument("--memory-id", required=True, help="Memory identifier")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_feature_enabled(repo_root, "memory", "remove memory")
    ensure_work_mode(repo_root, args.work_id, "remove memory")

    policies = _load_policies(repo_root)
    locks_dir = memory_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    store_path, _ = load_store(repo_root, args.store)
    lease.acquire_lock(locks_dir, store_path, args.agent_id, policies["lease_ttl_seconds"], args.work_id)
    try:
        removed = remove_memory(repo_root, args.store, args.memory_id)
    finally:
        lease.release_lock(locks_dir, store_path, args.agent_id)

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=str(store_path),
        notes=None,
        command_name="memory_remove",
        command_args=sys.argv[1:],
    )

    if not removed:
        logger.error("memory_id not found: %s", args.memory_id)
        raise SystemExit(1)
    logger.info("memory removed: %s", args.memory_id)


if __name__ == "__main__":
    main()
