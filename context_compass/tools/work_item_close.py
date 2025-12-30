"""Close a work item and remove it from per-agent queues."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import lease, work_item_move
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _bucket_choices() -> list[str]:
    """
    Return allowed work bucket values.

    Returns:
        list[str]: Allowed bucket values.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


def _state_choices() -> list[str]:
    """
    Return allowed close state values.

    Returns:
        list[str]: Allowed close state values.
    """
    return ["done", "failed", "cancelled"]


def _remove_from_agent_queue(repo_root: Path, agent_id: str, work_id: str, owner_id: str) -> bool:
    """
    Remove a work item from a per-agent queue.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        work_id (str): Work identifier to remove.
        owner_id (str): Lock owner id.

    Returns:
        bool: True if an item was removed.
    """
    queue_path = repo_root / "context_compass" / "self_context" / "agents" / f"{agent_id}.work.json"
    if not queue_path.exists():
        return False
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    policies = agent_presence.load_policies(repo_root)
    lease.acquire_lock(locks_dir, queue_path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        data = load_json(queue_path)
        if not isinstance(data, dict):
            return False
        queue = data.get("queue", [])
        if not isinstance(queue, list):
            return False
        original = len(queue)
        queue = [item for item in queue if item.get("work_id") != work_id]
        if len(queue) == original:
            return False
        data["queue"] = queue
        data["updated_at"] = utc_now_iso()
        write_json_atomic(queue_path, data)
        return True
    finally:
        lease.release_lock(locks_dir, queue_path, owner_id)


def close_work_item(
    repo_root: Path,
    work_id: str,
    work_type: str,
    source_bucket: str,
    dest_bucket: str,
    owner_id: str,
    new_state: str,
    queue_agent_id: Optional[str],
) -> None:
    """
    Close a work item and remove it from a per-agent queue.

    Args:
        repo_root (Path): Repository root.
        work_id (str): Work identifier.
        work_type (str): Work type.
        source_bucket (str): Source bucket.
        dest_bucket (str): Destination bucket.
        owner_id (str): Lock owner id.
        new_state (str): New state to set on close.
        queue_agent_id (Optional[str]): Agent queue to clean up.
    """
    ensure_feature_enabled(repo_root, "work_management", "close work items")
    work_item_move.move_work_item(
        repo_root,
        work_id,
        source_bucket,
        dest_bucket,
        work_type,
        owner_id,
        new_state=new_state,
    )
    if queue_agent_id:
        _remove_from_agent_queue(repo_root, queue_agent_id, work_id, owner_id)


def main() -> None:
    """
    CLI entrypoint for closing a work item and clearing per-agent queues.
    """
    parser = argparse.ArgumentParser(description="Close a work item and clear per-agent queue entries")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work item identifier")
    parser.add_argument("--work-type", required=True, choices=["epic", "story", "task"], help="Work type")
    parser.add_argument("--source-bucket", default="active", choices=_bucket_choices(), help="Source bucket")
    parser.add_argument("--dest-bucket", default="completed", choices=_bucket_choices(), help="Destination bucket")
    parser.add_argument("--state", default="done", choices=_state_choices(), help="Close state")
    parser.add_argument("--queue-agent-id", default=None, help="Agent queue to remove work from")
    parser.add_argument("--skip-queue-removal", action="store_true", help="Do not remove from agent queues")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.owner_id or args.agent_id)
    ensure_feature_enabled(repo_root, "work_management", "close work items")
    ensure_work_mode(repo_root, args.work_id, "close work items")

    owner_id = args.owner_id or args.agent_id
    queue_agent_id = None if args.skip_queue_removal else (args.queue_agent_id or args.agent_id)
    close_work_item(
        repo_root,
        args.work_id,
        args.work_type,
        args.source_bucket,
        args.dest_bucket,
        owner_id,
        args.state,
        queue_agent_id,
    )
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=args.work_id,
        notes=None,
        command_name="work_item_close",
        command_args=sys.argv[1:],
    )
    logger.info("closed work item: %s", args.work_id)


if __name__ == "__main__":
    main()
