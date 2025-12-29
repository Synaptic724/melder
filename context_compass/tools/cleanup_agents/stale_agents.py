"""Cleanup stale agents from active registry and archive if configured."""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.tools import agent_manage, lease, work_item_move
from context_compass.tools._shared import branch_paths
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import parse_iso8601, utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values used by stale agent cleanup.

    Returns:
        dict: Default policy values.
    """
    return {
        "agent_heartbeat_stale_seconds": 14400,
        "agent_archive_after_seconds": 86400,
        "lease_ttl_seconds": 300,
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


def _load_or_init_active_agents(path: Path, now: str) -> dict:
    """
    Load active_agents.json or initialize a default structure.

    Args:
        path (Path): active_agents.json path.
        now (str): Current timestamp.

    Returns:
        dict: Active agents data.
    """
    if path.exists():
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return {"schema_version": 1, "updated_at": now, "agents": []}


def _is_stale(last_heartbeat_at: Optional[str], now: str, stale_seconds: int) -> bool:
    """
    Return True if the heartbeat age exceeds the stale threshold.

    Args:
        last_heartbeat_at (Optional[str]): Last heartbeat timestamp.
        now (str): Current timestamp.
        stale_seconds (int): Stale threshold in seconds.

    Returns:
        bool: True if stale.
    """
    if not last_heartbeat_at:
        return False
    elapsed = (parse_iso8601(now) - parse_iso8601(last_heartbeat_at)).total_seconds()
    return elapsed >= stale_seconds


def _eligible_for_archive(last_heartbeat_at: Optional[str], now: str, archive_seconds: Optional[int]) -> bool:
    """
    Return True if the heartbeat age exceeds the archive threshold.

    Args:
        last_heartbeat_at (Optional[str]): Last heartbeat timestamp.
        now (str): Current timestamp.
        archive_seconds (Optional[int]): Archive threshold in seconds.

    Returns:
        bool: True if eligible for archive.
    """
    if archive_seconds is None or archive_seconds < 0:
        return False
    if not last_heartbeat_at:
        return False
    elapsed = (parse_iso8601(now) - parse_iso8601(last_heartbeat_at)).total_seconds()
    return elapsed >= archive_seconds


def _infer_work_type(kind: Optional[str]) -> str:
    """
    Infer a work_management queue type from a kind.

    Args:
        kind (Optional[str]): Work kind string.

    Returns:
        str: Work type (epic/story/task).
    """
    if not kind:
        return "task"
    lowered = kind.strip().lower()
    if lowered == "epic":
        return "epic"
    if lowered == "story":
        return "story"
    if lowered == "task":
        return "task"
    return "task"


def _load_work_queue(path: Path) -> list[dict]:
    """
    Load a per-agent work queue list from a worklist file.

    Args:
        path (Path): Worklist file path.

    Returns:
        list[dict]: Work queue items.
    """
    if not path.exists():
        return []
    data = load_json(path)
    if not isinstance(data, dict):
        return []
    queue = data.get("queue", [])
    return queue if isinstance(queue, list) else []


def _requeue_active_work(repo_root: Path, stale_ids: set[str], runner_id: str, now: str) -> None:
    """
    Move active work items for stale agents back to backlog.

    Args:
        repo_root (Path): Repository root.
        stale_ids (set[str]): Stale agent identifiers.
        runner_id (str): Cleanup runner id for locks.
        now (str): Current timestamp.
    """
    if not stale_ids:
        return

    logger = logging.getLogger(__name__)
    policies = _load_policies(repo_root)
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    agents_dir = repo_root / "context_compass" / "self_context" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    for stale_id in sorted(stale_ids):
        queue_path = agents_dir / f"{stale_id}.work.json"
        if not queue_path.exists():
            continue
        try:
            lease.acquire_lock(locks_dir, queue_path, runner_id, policies["lease_ttl_seconds"])
            queue = _load_work_queue(queue_path)
        finally:
            lease.release_lock(locks_dir, queue_path, runner_id)

        for item in queue:
            work_id = item.get("work_id")
            if not work_id:
                continue
            work_type = _infer_work_type(item.get("kind"))
            try:
                work_item_move.move_work_item(
                    repo_root,
                    work_id,
                    "active",
                    "backlog",
                    work_type,
                    runner_id,
                    new_state="queued",
                )
            except (FileNotFoundError, ValueError) as exc:
                logger.info("skip requeue for %s: %s", work_id, exc)
            except Exception as exc:
                logger.exception("failed to requeue work item %s: %s", work_id, exc)


def cleanup(repo_root: Path, agent_id: str, now: Optional[str] = None) -> None:
    """
    Mark stale agents and optionally archive them.

    Contract:
    - Removes stale agents from active_agents.json.
    - Marks profiles as stale with updated timestamps.
    - Requeues active work items for stale agents into backlog.
    - Archives agent files if archive threshold is met.
    - Thresholds come from context_compass/config/policies.json.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent id executing cleanup.
        now (Optional[str]): Override current timestamp.
    """
    current = now or utc_now_iso()
    policies = _load_policies(repo_root)
    stale_seconds = int(policies["agent_heartbeat_stale_seconds"])
    archive_seconds = policies.get("agent_archive_after_seconds")
    if archive_seconds is not None:
        archive_seconds = int(archive_seconds)

    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    active_path = repo_root / "context_compass" / "self_context" / "active_agents.json"
    agents_dir = repo_root / "context_compass" / "self_context" / "agents"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    agents_dir.mkdir(parents=True, exist_ok=True)
    profile_paths = sorted(agents_dir.glob("*.profile.json"), key=lambda p: str(p))

    resources = [active_path, *profile_paths]
    locked: list[Path] = []
    for resource in sorted({r.resolve() for r in resources}, key=lambda p: str(p)):
        lease.acquire_lock(locks_dir, resource, agent_id, policies["lease_ttl_seconds"])
        locked.append(resource)

    stale_ids: set[str] = set()
    archive_ids: set[str] = set()
    try:
        active = _load_or_init_active_agents(active_path, current)
        active_agents = active.get("agents", [])
        remaining_active = []

        for entry in active_agents:
            last_heartbeat = entry.get("last_heartbeat_at")
            entry_id = entry.get("agent_id")
            if entry_id and _is_stale(last_heartbeat, current, stale_seconds):
                stale_ids.add(entry_id)
                if _eligible_for_archive(last_heartbeat, current, archive_seconds):
                    archive_ids.add(entry_id)
            else:
                remaining_active.append(entry)

        if remaining_active != active_agents:
            active["agents"] = remaining_active
            active["updated_at"] = current
            write_json_atomic(active_path, active)

        for path in profile_paths:
            data = load_json(path)
            if not isinstance(data, dict):
                continue
            profile_id = data.get("agent_id")
            last_heartbeat = data.get("last_heartbeat_at")
            is_profile_stale = profile_id in stale_ids
            if not is_profile_stale and data.get("status") == "active":
                if _is_stale(last_heartbeat, current, stale_seconds):
                    is_profile_stale = True
                    stale_ids.add(profile_id)
            if is_profile_stale:
                data["status"] = "stale"
                data["updated_at"] = current
                if _eligible_for_archive(last_heartbeat, current, archive_seconds):
                    archive_ids.add(profile_id)
                write_json_atomic(path, data)
    finally:
        for resource in reversed(locked):
            lease.release_lock(locks_dir, resource, agent_id)

    _requeue_active_work(repo_root, stale_ids, agent_id, current)

    for stale_id in sorted(archive_ids):
        agent_manage.archive_agent(repo_root, stale_id, agent_id)


def main() -> None:
    """
    CLI entrypoint for stale agent cleanup.
    """
    parser = argparse.ArgumentParser(description="Cleanup stale agents")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--now", default=None, help="Override current timestamp (ISO-8601)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    cleanup(repo_root, args.agent_id, now=args.now)
    logger.info("stale agent cleanup completed (runner: %s)", args.agent_id)


if __name__ == "__main__":
    main()
