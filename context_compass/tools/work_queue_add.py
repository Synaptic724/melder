"""Add a work item to a per-agent work queue."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_work_queue(agent_id: str, now: str) -> dict:
    """
    Return a default per-agent work queue.

    Args:
        agent_id (str): Agent identifier.
        now (str): Current timestamp.

    Returns:
        dict: Work queue payload.
    """
    return {
        "schema_version": 1,
        "agent_id": agent_id,
        "updated_at": now,
        "queue": [],
    }


def _build_work_item(
    work_id: str,
    kind: str,
    state: str,
    target_path: str,
    ctx_path: str,
    reason: list[str],
    priority: int,
    created_at: str,
    parent_work_id: Optional[str],
    root_work_id: str,
) -> dict:
    """
    Build a work item for insertion into a queue.

    Args:
        work_id (str): Work item identifier.
        kind (str): Work item kind.
        state (str): Work item state.
        target_path (str): Target path.
        ctx_path (str): Context path.
        reason (list[str]): Reason strings.
        priority (int): Priority value.
        created_at (str): Creation timestamp.
        parent_work_id (Optional[str]): Parent work id.
        root_work_id (str): Root work id.

    Returns:
        dict: Work item payload.
    """
    return {
        "work_id": work_id,
        "state": state,
        "kind": kind,
        "target_path": target_path,
        "ctx_path": ctx_path,
        "reason": reason,
        "parent_work_id": parent_work_id,
        "root_work_id": root_work_id,
        "priority": priority,
        "lease": None,
        "attempts": 0,
        "last_error_ref": None,
        "created_at": created_at,
        "updated_at": created_at,
    }


def _requires_parent(kind: str) -> bool:
    """
    Return True if a kind requires a parent_work_id.

    Args:
        kind (str): Work kind.

    Returns:
        bool: True if a parent is required.
    """
    lowered = kind.strip().lower()
    return lowered == "story"


def add_work_item(repo_root: Path, agent_id: str, item: dict, owner_id: str) -> None:
    """
    Add a work item to a per-agent work queue.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        item (dict): Work item payload.
        owner_id (str): Lock owner identifier.
    """
    ensure_feature_enabled(repo_root, "work_management", "write agent work queues")
    now = utc_now_iso()
    locks_dir = branch_paths.self_context_locks_dir(repo_root)
    locks_dir.mkdir(parents=True, exist_ok=True)
    queue_path = repo_root / "context_compass" / "self_context" / "agents" / f"{agent_id}.work.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    policies = agent_presence.load_policies(repo_root)

    lease.acquire_lock(locks_dir, queue_path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        if queue_path.exists():
            data = load_json(queue_path)
            if not isinstance(data, dict):
                raise ValueError("Work queue must be a JSON object")
        else:
            data = _default_work_queue(agent_id, now)

        queue = data.setdefault("queue", [])
        queue.append(item)
        data["updated_at"] = now
        write_json_atomic(queue_path, data)
    finally:
        lease.release_lock(locks_dir, queue_path, owner_id)


def main() -> None:
    """
    CLI entrypoint for adding a work item to a per-agent queue.
    """
    parser = argparse.ArgumentParser(description="Add a work item to an agent queue")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work item identifier")
    parser.add_argument("--kind", required=True, help="Work item kind")
    parser.add_argument("--state", default="queued", help="Work item state")
    parser.add_argument("--target-path", required=True, help="Target path")
    parser.add_argument("--ctx-path", required=True, help="Context path")
    parser.add_argument("--parent-work-id", default=None, help="Parent work id (optional)")
    parser.add_argument("--root-work-id", default=None, help="Root work id (defaults to work-id)")
    parser.add_argument("--reason", action="append", default=None, help="Reason (repeatable)")
    parser.add_argument("--priority", type=int, default=50, help="Priority value")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.owner_id or args.agent_id)
    ensure_feature_enabled(repo_root, "work_management", "add work items")
    ensure_work_mode(repo_root, args.work_id, "add work items")

    reasons = args.reason if args.reason else ["manual_add"]
    created_at = utc_now_iso()
    root_work_id = args.root_work_id or args.work_id
    if _requires_parent(args.kind) and args.parent_work_id in (None, ""):
        raise ValueError("parent_work_id is required for story kinds")
    item = _build_work_item(
        work_id=args.work_id,
        kind=args.kind,
        state=args.state,
        target_path=args.target_path,
        ctx_path=args.ctx_path,
        reason=reasons,
        priority=args.priority,
        created_at=created_at,
        parent_work_id=args.parent_work_id,
        root_work_id=root_work_id,
    )

    owner_id = args.owner_id or args.agent_id
    add_work_item(repo_root, args.agent_id, item, owner_id)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=args.target_path,
        notes=None,
        command_name="work_queue_add",
        command_args=sys.argv[1:],
    )
    logger.info("work item added to %s queue: %s", args.agent_id, args.work_id)


if __name__ == "__main__":
    main()
