"""Add a work item to work_management queues."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_ids import generate_work_id


def _work_files() -> dict:
    """
    Return the work_management queue filenames by type.

    Returns:
        dict: Mapping of work types to queue filenames.
    """
    return {"epic": "epics.json", "story": "stories.json", "task": "tasks.json"}


def _aliases() -> dict:
    """
    Return kind aliases that normalize to canonical work types.

    Returns:
        dict: Mapping of kind aliases to canonical work types.
    """
    return {"epic": "epic", "story": "story", "task": "task"}


def _normalize_kind(kind: str) -> Tuple[str, Optional[str]]:
    """
    Normalize known kind aliases and infer a work type.

    Args:
        kind (str): Input kind string.

    Returns:
        Tuple[str, Optional[str]]: Normalized kind and inferred work type.
    """
    normalized = kind.strip()
    lowered = normalized.lower()
    aliases = _aliases()
    if lowered in aliases:
        canonical = aliases[lowered]
        return canonical, canonical
    if lowered in _work_files():
        return lowered, lowered
    return normalized, None


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


def _default_queue(now: str) -> dict:
    """
    Return a default work_management queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _state_choices() -> list[str]:
    """
    Return allowed work item state values.

    Returns:
        list[str]: Allowed state values.
    """
    return ["queued", "leased", "in_progress", "done", "failed", "cancelled"]


def _queue_path(repo_root: Path, bucket: str, work_type: str) -> Path:
    """
    Resolve the JSON queue path for a work type in a bucket.

    Args:
        repo_root (Path): Repository root.
        bucket (str): Work bucket (ready/active/backlog/completed/denied).
        work_type (str): Work type (epic/story/task).

    Returns:
        Path: Queue file path.
    """
    filename = _work_files()[work_type]
    return branch_paths.work_root(repo_root) / bucket / filename


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
    source_ticket: Optional[str],
) -> dict:
    """
    Build a work item payload for work_management queues.

    Args:
        work_id (str): Work identifier.
        kind (str): Work kind.
        state (str): Work state.
        target_path (str): Target path.
        ctx_path (str): Context path.
        reason (list[str]): Reason list.
        priority (int): Priority value.
        created_at (str): Creation timestamp.
        parent_work_id (Optional[str]): Parent work id.
        root_work_id (str): Root work id.
        source_ticket (Optional[str]): Source ticket path or identifier.

    Returns:
        dict: Work item payload.
    """
    item = {
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
    if source_ticket is not None:
        item["source_ticket"] = source_ticket
    return item


def add_work_item(
    repo_root: Path,
    bucket: str,
    work_type: str,
    item: dict,
    owner_id: str,
) -> Path:
    """
    Add a work item to a work_management queue.

    Args:
        repo_root (Path): Repository root.
        bucket (str): Work bucket.
        work_type (str): Work type.
        item (dict): Work item payload.
        owner_id (str): Lock owner id.

    Returns:
        Path: Queue path written.
    """
    ensure_feature_enabled(repo_root, "work_management", "write work queues")
    now = utc_now_iso()
    queue_path = _queue_path(repo_root, bucket, work_type)
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    policies = agent_presence.load_policies(repo_root)

    lease.acquire_lock(locks_dir, queue_path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        if queue_path.exists():
            data = load_json(queue_path)
            if not isinstance(data, dict):
                raise ValueError("Queue must be a JSON object")
        else:
            data = _default_queue(now)

        queue = data.setdefault("queue", [])
        if any(existing.get("work_id") == item.get("work_id") for existing in queue):
            raise ValueError(f"Work item already exists: {item.get('work_id')}")
        queue.append(item)
        data["updated_at"] = now
        write_json_atomic(queue_path, data)
    finally:
        lease.release_lock(locks_dir, queue_path, owner_id)
    return queue_path


def _resolve_paths(ticket_path: Optional[str], target_path: Optional[str], ctx_path: Optional[str]) -> tuple[str, str]:
    """
    Resolve target and context paths with ticket fallback.

    Args:
        ticket_path (Optional[str]): Ticket path fallback.
        target_path (Optional[str]): Target path.
        ctx_path (Optional[str]): Context path.

    Returns:
        tuple[str, str]: Resolved target and context paths.

    Raises:
        ValueError: If required paths are missing.
    """
    if target_path is None and ticket_path is not None:
        target_path = ticket_path
    if ctx_path is None and ticket_path is not None:
        ctx_path = ticket_path
    if target_path is None or ctx_path is None:
        raise ValueError("target_path and ctx_path are required (or supply --ticket-path)")
    return target_path, ctx_path


def main() -> None:
    """
    CLI entrypoint for adding a work item to work_management queues.
    """
    parser = argparse.ArgumentParser(description="Add a work item to work_management queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument(
        "--bucket",
        default="ready",
        choices=["ready", "active", "backlog", "completed", "denied"],
        help="Work bucket",
    )
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Queue type override")
    parser.add_argument("--work-id", default=None, help="Work item identifier (auto-generated if omitted)")
    parser.add_argument("--kind", required=True, help="Work item kind (epic/story/task allowed)")
    parser.add_argument("--state", default="queued", choices=_state_choices(), help="Work item state")
    parser.add_argument("--target-path", default=None, help="Target path")
    parser.add_argument("--ctx-path", default=None, help="Context path")
    parser.add_argument("--ticket-path", default=None, help="Ticket path fallback")
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
    work_id = args.work_id or generate_work_id()
    ensure_work_mode(repo_root, work_id, "add work items")

    normalized_kind, inferred_type = _normalize_kind(args.kind)
    work_type = args.work_type or inferred_type or "task"
    if work_type not in _work_files():
        raise ValueError(f"Invalid work type: {work_type}")

    if inferred_type is None:
        raise ValueError(f"Invalid work kind: {args.kind}")

    if _requires_parent(normalized_kind) and args.parent_work_id in (None, ""):
        raise ValueError("parent_work_id is required for story kinds")

    target_path, ctx_path = _resolve_paths(args.ticket_path, args.target_path, args.ctx_path)
    reasons = args.reason if args.reason else (["github_intake"] if args.ticket_path else ["manual_add"])
    created_at = utc_now_iso()
    root_work_id = args.root_work_id or work_id
    item = _build_work_item(
        work_id=work_id,
        kind=normalized_kind,
        state=args.state,
        target_path=target_path,
        ctx_path=ctx_path,
        reason=reasons,
        priority=args.priority,
        created_at=created_at,
        parent_work_id=args.parent_work_id,
        root_work_id=root_work_id,
        source_ticket=args.ticket_path,
    )

    owner_id = args.owner_id or args.agent_id
    queue_path = add_work_item(repo_root, args.bucket, work_type, item, owner_id)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=work_id,
        current_target=target_path,
        notes=None,
        command_name="work_item_add",
        command_args=sys.argv[1:],
    )
    logger.info("work item added to %s: %s", queue_path, work_id)


if __name__ == "__main__":
    main()
