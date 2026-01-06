"""
Promote a GitHub ticket markdown into work_management queues.

Purpose
- Normalize ticket data into work items.
- Seed root and child work items into work queues.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.work_management import work_item_add
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
    optional_list,
    optional_string,
    require_choice,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.work_ids import generate_work_id
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


def _bucket_choices() -> list[str]:
    """
    Return allowed work bucket values.

    Returns:
        list[str]: Allowed bucket values.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


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
    normalized = kind.strip()
    lowered = normalized.lower()
    if lowered in aliases:
        canonical = aliases[lowered]
        return canonical, canonical
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
    Normalize child items from a payload list.

    Args:
        plan (object): Child items payload.
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
        raise ValueError("child_items must be a list or {\"items\": [...]}")

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
        if item.get("work_id") in (None, ""):
            item["work_id"] = generate_work_id()
        item.setdefault("reason", ["github_intake"])
        item.setdefault("priority", 50)
        item.setdefault("state", "queued")
        item.setdefault("source_ticket", ticket_path)
        normalized.append(item)
    return normalized


def _parse_child_items_json(raw: Optional[str]) -> Optional[list[dict]]:
    """
    Parse child items from a CLI JSON string.

    Purpose:
    - Allow CLI callers to submit child items without reading JSON files.

    Contract:
    - Returns None when no value is supplied.
    - Requires a JSON array of objects.

    Args:
        raw (Optional[str]): JSON string representing child items.

    Returns:
        Optional[list[dict]]: Parsed child item objects or None.

    Raises:
        ValueError: If the JSON is invalid or not a list of objects.
    """
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("child_items_json must be valid JSON") from exc
    if not isinstance(value, list):
        raise ValueError("child_items_json must be a JSON list")
    for entry in value:
        if not isinstance(entry, dict):
            raise ValueError("child_items_json entries must be objects")
    return value


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

    Contract:
        - Fills missing queue fields to satisfy work queue defaults.
        - Leaves explicitly provided values intact.
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
        work_id = generate_work_id()
    target_path = child.get("target_path")
    ctx_path = child.get("ctx_path")
    if not target_path or not ctx_path:
        raise ValueError("child item missing target_path or ctx_path")

    payload = dict(child)
    payload["work_id"] = work_id
    payload["kind"] = normalized_kind
    if payload.get("parent_work_id") is None:
        payload["parent_work_id"] = root_work_id
    if payload.get("root_work_id") is None:
        payload["root_work_id"] = root_work_id
    payload.setdefault("source_ticket", ticket_path)
    now = utc_now_iso()
    payload.setdefault("state", "queued")
    payload.setdefault("priority", 50)
    payload.setdefault("reason", ["github_intake"])
    payload.setdefault("lease", None)
    payload.setdefault("attempts", 0)
    payload.setdefault("last_error_ref", None)
    payload.setdefault("created_at", now)
    payload.setdefault("updated_at", now)
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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Promote a ticket into work queues using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing updated queue paths.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, ticket_path, and kind.
        - Enforces certification, feature flags, and work mode guards.
        - Supports optional child_items payload (list of dicts).
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        ticket_path_value = require_string(payload, "ticket_path", command_name)
        bucket = optional_string(payload, "bucket", command_name=command_name, default="ready")
        work_id = optional_string(payload, "work_id", command_name=command_name)
        kind = require_string(payload, "kind", command_name)
        work_type = optional_string(payload, "work_type", command_name=command_name)
        state = optional_string(payload, "state", command_name=command_name, default="queued")
        target_path = optional_string(payload, "target_path", command_name=command_name)
        ctx_path = optional_string(payload, "ctx_path", command_name=command_name)
        parent_work_id = optional_string(payload, "parent_work_id", command_name=command_name)
        root_work_id = optional_string(payload, "root_work_id", command_name=command_name)
        reason = optional_list(payload, "reason", command_name=command_name)
        priority = optional_int(payload, "priority", command_name=command_name, default=50)
        child_items = optional_list(payload, "child_items", command_name=command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if bucket not in _bucket_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "bucket",
                    "expected": f"one of {_bucket_choices()}",
                    "actual": bucket,
                },
            ),
        )
    if state not in _state_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "state",
                    "expected": f"one of {_state_choices()}",
                    "actual": state,
                },
            ),
        )

    normalized_kind, inferred_type = _normalize_kind(kind)
    if inferred_type is None:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "kind",
                    "expected": "epic, story, or task",
                    "actual": kind,
                },
            ),
        )
    resolved_work_type = work_type or inferred_type
    if resolved_work_type not in {"epic", "story", "task"}:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "work_type",
                    "expected": "epic, story, or task",
                    "actual": resolved_work_type,
                },
            ),
        )
    if _requires_parent(normalized_kind) and not parent_work_id:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_missing",
                details={
                    "command_name": command_name,
                    "field": "parent_work_id",
                    "expected": "parent_work_id for story kinds",
                },
            ),
        )

    effective_work_id = work_id or generate_work_id()
    ticket_path = Path(ticket_path_value)
    if not ticket_path.is_absolute():
        ticket_path = (repo_root / ticket_path).resolve()
    target_path = target_path or str(ticket_path)
    ctx_path = ctx_path or str(ticket_path)
    now = utc_now_iso()
    root_id = root_work_id or effective_work_id
    reasons = reason if reason else ["github_intake"]

    root_item = _default_work_item(now, effective_work_id, normalized_kind, target_path, ctx_path)
    root_item["state"] = state
    root_item["parent_work_id"] = parent_work_id
    root_item["root_work_id"] = root_id
    root_item["priority"] = priority or 50
    root_item["reason"] = reasons
    root_item["source_ticket"] = str(ticket_path)

    effective_owner = owner_id or agent_id
    try:
        ensure_certified(repo_root, effective_owner)
        ensure_feature_enabled(repo_root, "ticket_intake", "promote tickets")
        ensure_feature_enabled(repo_root, "work_management", "write work queues")
        ensure_work_mode(repo_root, effective_work_id, "promote tickets")
        children = None
        if child_items is not None:
            children = _coerce_items(child_items, root_id, str(ticket_path), bucket)
        updated = promote_ticket(
            repo_root=repo_root,
            ticket_path=ticket_path,
            bucket=bucket,
            work_type=resolved_work_type,
            root_item=root_item,
            owner_id=effective_owner,
            children=children,
        )
        return ok_result(
            output={
                "work_id": effective_work_id,
                "ticket_path": str(ticket_path),
                "bucket": bucket,
                "work_type": resolved_work_type,
                "updated_paths": [str(path) for path in updated],
                "children_count": 0 if not children else len(children),
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for promoting a ticket into work_management queues.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Promote a GitHub ticket into work_management queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--ticket-path", required=True, help="Ticket markdown path")
    parser.add_argument("--bucket", default="ready", choices=_bucket_choices(), help="Root bucket")
    parser.add_argument("--work-id", default=None, help="Root work identifier (auto-generated if omitted)")
    parser.add_argument("--kind", required=True, help="Root kind (epic/story/task allowed)")
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Root work type override")
    parser.add_argument("--state", default="queued", choices=_state_choices(), help="Root state")
    parser.add_argument("--target-path", default=None, help="Root target path (default: ticket)")
    parser.add_argument("--ctx-path", default=None, help="Root ctx path (default: ticket)")
    parser.add_argument("--parent-work-id", default=None, help="Root parent work id")
    parser.add_argument("--root-work-id", default=None, help="Root work id override")
    parser.add_argument("--reason", action="append", default=None, help="Root reason (repeatable)")
    parser.add_argument("--priority", type=int, default=50, help="Root priority")
    parser.add_argument(
        "--child-items-json",
        default=None,
        help="JSON array of child item objects (no file reads)",
    )
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        child_items = _parse_child_items_json(args.child_items_json)
    except ValueError as exc:
        logger.error("ticket_promote failed: %s", exc)
        raise SystemExit(1)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "ticket_path": args.ticket_path,
        "bucket": args.bucket,
        "work_id": args.work_id,
        "kind": args.kind,
        "work_type": args.work_type,
        "state": args.state,
        "target_path": args.target_path,
        "ctx_path": args.ctx_path,
        "parent_work_id": args.parent_work_id,
        "root_work_id": args.root_work_id,
        "reason": args.reason,
        "priority": args.priority,
        "child_items": child_items,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="ticket_promote",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("ticket_promote failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(
        "promoted ticket into %s queues",
        len(result.output.get("updated_paths", [])),
    )


if __name__ == "__main__":
    main()
