"""Promote a GitHub ticket markdown into work_management queues."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import work_item_add
from context_compass.tools._shared import agent_presence
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json
from context_compass.tools._shared.timeutils import utc_now_iso


def _bucket_choices() -> list[str]:
    """
    Return allowed work bucket values.

    Returns:
        list[str]: Allowed bucket values.
    """
    return ["active", "backlog", "completed", "denied"]


def _state_choices() -> list[str]:
    """
    Return allowed work item state values.

    Returns:
        list[str]: Allowed state values.
    """
    return ["queued", "leased", "in_progress", "done", "failed", "cancelled"]


def _normalize_kind(kind: str) -> tuple[str, Optional[str]]:
    """
    Normalize known kind aliases and infer a work type.

    Args:
        kind (str): Input kind string.

    Returns:
        tuple[str, Optional[str]]: Normalized kind and inferred work type.
    """
    aliases = {"epic": "epic", "story": "story", "task": "task"}
    work_files = {"epic": "epics.json", "story": "stories.json", "task": "tasks.json"}
    normalized = kind.strip()
    lowered = normalized.lower()
    if lowered in aliases:
        canonical = aliases[lowered]
        return canonical, canonical
    if lowered in work_files:
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


def _read_ticket(path: Path) -> str:
    """
    Read and return the ticket markdown content.

    Args:
        path (Path): Ticket path.

    Returns:
        str: Ticket content.

    Raises:
        FileNotFoundError: If the ticket does not exist.
    """
    return path.read_text(encoding="utf-8")


def _default_work_item(now: str, work_id: str, kind: str, target_path: str, ctx_path: str) -> dict:
    """
    Build a default work item payload.

    Args:
        now (str): Current timestamp.
        work_id (str): Work identifier.
        kind (str): Work kind.
        target_path (str): Target path.
        ctx_path (str): Context path.

    Returns:
        dict: Work item payload.
    """
    return {
        "work_id": work_id,
        "state": "queued",
        "kind": kind,
        "target_path": target_path,
        "ctx_path": ctx_path,
        "reason": ["github_intake"],
        "parent_work_id": None,
        "root_work_id": work_id,
        "priority": 50,
        "lease": None,
        "attempts": 0,
        "last_error_ref": None,
        "created_at": now,
        "updated_at": now,
    }


def _coerce_items(plan: object, root_work_id: str, ticket_path: str, bucket: str) -> list[dict]:
    """
    Normalize child items from a plan payload.

    Args:
        plan (object): Plan payload.
        root_work_id (str): Root work id for defaults.
        ticket_path (str): Source ticket path for defaults.
        bucket (str): Default bucket for child items.

    Returns:
        list[dict]: Normalized child specs.
    """
    if isinstance(plan, dict) and "items" in plan:
        items = plan["items"]
    else:
        items = plan
    if not isinstance(items, list):
        raise ValueError("children plan must be a list or {\"items\": [...]}")

    normalized: list[dict] = []
    for raw in items:
        if not isinstance(raw, dict):
            raise ValueError("child item must be an object")
        item = dict(raw)
        item.setdefault("bucket", bucket)
        if item.get("parent_work_id") is None:
            item["parent_work_id"] = root_work_id
        if item.get("root_work_id") is None:
            item["root_work_id"] = root_work_id
        item.setdefault("reason", ["github_intake"])
        item.setdefault("priority", 50)
        item.setdefault("state", "queued")
        item.setdefault("source_ticket", ticket_path)
        normalized.append(item)
    return normalized


def _normalize_child(
    child: dict,
    root_work_id: str,
    ticket_path: str,
    default_bucket: str,
) -> tuple[str, str, dict]:
    """
    Normalize a child item payload.

    Args:
        child (dict): Child payload.
        root_work_id (str): Root work id.
        ticket_path (str): Ticket path for defaults.
        default_bucket (str): Default bucket.

    Returns:
        tuple[str, str, dict]: Bucket, work_type, and payload.
    """
    bucket = child.get("bucket", default_bucket)
    if bucket not in _bucket_choices():
        raise ValueError(f"Invalid bucket: {bucket}")
    kind = child.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ValueError("child item missing kind")
    normalized_kind, inferred_type = _normalize_kind(kind)
    if inferred_type is None:
        raise ValueError(f"Invalid child kind: {kind}")
    work_type = child.get("work_type") or inferred_type
    if work_type not in {"epic", "story", "task"}:
        raise ValueError(f"Invalid work type: {work_type}")
    work_id = child.get("work_id")
    if not work_id:
        raise ValueError("child item missing work_id")
    target_path = child.get("target_path")
    ctx_path = child.get("ctx_path")
    if not target_path or not ctx_path:
        raise ValueError("child item missing target_path or ctx_path")

    payload = dict(child)
    payload["kind"] = normalized_kind
    if payload.get("parent_work_id") is None:
        payload["parent_work_id"] = root_work_id
    if payload.get("root_work_id") is None:
        payload["root_work_id"] = root_work_id
    payload.setdefault("source_ticket", ticket_path)
    return bucket, work_type, payload


def promote_ticket(
    repo_root: Path,
    ticket_path: Path,
    bucket: str,
    work_type: str,
    root_item: dict,
    owner_id: str,
    children: Optional[list[dict]] = None,
) -> list[Path]:
    """
    Promote a ticket into work_management queues.

    Args:
        repo_root (Path): Repository root.
        ticket_path (Path): Ticket path.
        bucket (str): Root bucket.
        work_type (str): Root work type.
        root_item (dict): Root work item payload.
        owner_id (str): Lock owner id.
        children (Optional[list[dict]]): Optional child payloads.

    Returns:
        list[Path]: Queue paths updated.
    """
    ensure_feature_enabled(repo_root, "ticket_intake", "promote tickets")
    ensure_feature_enabled(repo_root, "work_management", "write work queues")
    _read_ticket(ticket_path)
    root_work_id = root_item.get("root_work_id") or root_item.get("work_id")
    if not root_work_id:
        raise ValueError("root work item missing root_work_id or work_id")
    updated_paths = [work_item_add.add_work_item(repo_root, bucket, work_type, root_item, owner_id)]
    if not children:
        return updated_paths

    for child in children:
        child_bucket, child_type, payload = _normalize_child(
            child, root_work_id, str(ticket_path), bucket
        )
        updated_paths.append(work_item_add.add_work_item(repo_root, child_bucket, child_type, payload, owner_id))
    return updated_paths


def main() -> None:
    """
    CLI entrypoint for promoting a ticket into work_management queues.
    """
    parser = argparse.ArgumentParser(description="Promote a GitHub ticket into work_management queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--ticket-path", required=True, help="Ticket markdown path")
    parser.add_argument("--bucket", default="backlog", choices=_bucket_choices(), help="Root bucket")
    parser.add_argument("--work-id", required=True, help="Root work identifier")
    parser.add_argument("--kind", required=True, help="Root kind (epic/story/task allowed)")
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Root work type override")
    parser.add_argument("--state", default="queued", choices=_state_choices(), help="Root state")
    parser.add_argument("--target-path", default=None, help="Root target path (default: ticket)")
    parser.add_argument("--ctx-path", default=None, help="Root ctx path (default: ticket)")
    parser.add_argument("--parent-work-id", default=None, help="Root parent work id")
    parser.add_argument("--root-work-id", default=None, help="Root work id override")
    parser.add_argument("--reason", action="append", default=None, help="Root reason (repeatable)")
    parser.add_argument("--priority", type=int, default=50, help="Root priority")
    parser.add_argument("--children-plan", default=None, help="JSON file describing child items")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.owner_id or args.agent_id)
    ensure_feature_enabled(repo_root, "ticket_intake", "promote tickets")
    ensure_feature_enabled(repo_root, "work_management", "write work queues")
    ensure_work_mode(repo_root, args.work_id, "promote tickets")

    ticket_path = Path(args.ticket_path)
    if not ticket_path.is_absolute():
        ticket_path = (repo_root / ticket_path).resolve()

    normalized_kind, inferred_type = _normalize_kind(args.kind)
    if inferred_type is None:
        raise ValueError(f"Invalid work kind: {args.kind}")
    work_type = args.work_type or inferred_type
    if work_type not in {"epic", "story", "task"}:
        raise ValueError(f"Invalid work type: {work_type}")
    if _requires_parent(normalized_kind) and args.parent_work_id in (None, ""):
        raise ValueError("parent_work_id is required for story kinds")
    target_path = args.target_path or str(ticket_path)
    ctx_path = args.ctx_path or str(ticket_path)
    now = utc_now_iso()
    root_work_id = args.root_work_id or args.work_id
    reasons = args.reason if args.reason else ["github_intake"]
    root_item = _default_work_item(now, args.work_id, normalized_kind, target_path, ctx_path)
    root_item["state"] = args.state
    root_item["parent_work_id"] = args.parent_work_id
    root_item["root_work_id"] = root_work_id
    root_item["priority"] = args.priority
    root_item["reason"] = reasons
    root_item["source_ticket"] = str(ticket_path)

    children = None
    if args.children_plan:
        plan_path = Path(args.children_plan)
        if not plan_path.is_absolute():
            plan_path = (repo_root / plan_path).resolve()
        plan = load_json(plan_path)
        children = _coerce_items(plan, root_work_id, str(ticket_path), args.bucket)

    owner_id = args.owner_id or args.agent_id
    updated = promote_ticket(repo_root, ticket_path, args.bucket, work_type, root_item, owner_id, children=children)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        current_task_id=args.work_id,
        current_target=str(ticket_path),
        notes=None,
        command_name="ticket_promote",
        command_args=sys.argv[1:],
    )
    logger.info("promoted ticket into %s queues", len(updated))


if __name__ == "__main__":
    main()
