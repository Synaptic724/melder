"""Add a work item to work_management queues."""

import argparse
import logging
from pathlib import Path
from typing import Optional, Tuple

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_int,
    optional_list,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.work_ids import generate_work_id
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

WORK_QUEUE_TABLE_NAME = "work_queues"
BRANCH_QUEUE_SCOPE = "branch"
POLICIES_TABLE_NAME = "config_policies_core"
POLICIES_ACTION = "by_config_id"
POLICIES_CONFIG_ID = 1


def _work_files() -> dict:
    """
    Return supported work_management queue types.

    Returns:
        dict: Mapping of work types to canonical names.
    """
    return {"epic": "epic", "story": "story", "task": "task"}


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


def _state_choices() -> list[str]:
    """
    Return allowed work item state values.

    Returns:
        list[str]: Allowed state values.
    """
    return ["queued", "leased", "in_progress", "done", "failed", "cancelled"]


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


def _queue_id(branch_name: str, bucket: str, work_type: str) -> str:
    """
    Build a branch queue_id for work_queues rows.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Queue bucket name.
        work_type (str): Work type key.

    Returns:
        str: Queue identifier for work_queues.
    """

    return f"{BRANCH_QUEUE_SCOPE}:{branch_name}:{bucket}:{work_type}"


def _work_queue_table_name() -> str:
    """
    Return the SQLite table name for branch work queues.

    Purpose:
    - Keep table name resolution local to avoid store module dependencies.

    Returns:
        str: SQLite table name for work queues.
    """

    return WORK_QUEUE_TABLE_NAME


def _branch_lock_resource(branch_name: str, bucket: str, work_type: str) -> Path:
    """
    Build a synthetic lock resource path for a branch queue lock.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type key.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_work_queue::{branch_name}::{bucket}::{work_type}")


def _queue_payload(
    queue_id: str,
    branch_name: str,
    bucket: str,
    work_type: str,
) -> dict:
    """
    Build payload fields for ensuring a work_queues row.

    Args:
        queue_id (str): Queue identifier.
        branch_name (str): Branch identifier.
        bucket (str): Queue bucket name.
        work_type (str): Work type key.

    Returns:
        dict: Payload fields for work_queues ensure action.
    """

    return {
        "queue_id": queue_id,
        "scope": "branch",
        "branch_name": branch_name,
        "bucket": bucket,
        "work_kind": work_type,
        "schema_version": 1,
        "repo_id": None,
    }


def _load_policies(repo_root: Path, owner_id: str) -> dict:
    """
    Load policy configuration values via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Actor identifier for audit logging.

    Returns:
        dict: Policy values including lease_ttl_seconds and lock_wait_seconds.

    Raises:
        ValueError: If required policy fields are missing or invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="system",
            table_name=POLICIES_TABLE_NAME,
            action=POLICIES_ACTION,
            payload={"config_id": POLICIES_CONFIG_ID},
            actor_id=owner_id,
        ),
    )
    record = response.output.get("result", {}).get("record", {})
    lease_ttl = record.get("lease_ttl_seconds")
    lock_wait = record.get("lock_wait_seconds")
    if not isinstance(lease_ttl, int) or lease_ttl < 1:
        raise ValueError("lease_ttl_seconds must be an integer >= 1.")
    if not isinstance(lock_wait, int) or lock_wait < 0:
        raise ValueError("lock_wait_seconds must be an integer >= 0.")
    return {
        "lease_ttl_seconds": lease_ttl,
        "lock_wait_seconds": lock_wait,
    }


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
        Path: Logical queue identifier for the SQLite table.
    """
    ensure_feature_enabled(repo_root, "work_management", "write work queues")
    branch_name = branch_paths.load_current_branch(repo_root)
    table_name = _work_queue_table_name()
    queue_id = _queue_id(branch_name, bucket, work_type)
    policies = _load_policies(repo_root, owner_id)
    lock_resource = _branch_lock_resource(branch_name, bucket, work_type)

    lease.acquire_lock(
        repo_root,
        lock_resource,
        owner_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope="user",
                table_name="work_queues",
                action="ensure_queue",
                payload=_queue_payload(queue_id, branch_name, bucket, work_type),
                actor_id=owner_id,
            ),
        )
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope="user",
                table_name="work_queue_items",
                action="insert_item",
                payload={
                    "queue_id": queue_id,
                    "work_id": item["work_id"],
                    "parent_work_id": item["parent_work_id"],
                    "root_work_id": item["root_work_id"],
                    "state": item["state"],
                    "kind": item["kind"],
                    "target_path": item["target_path"],
                    "ctx_path": item["ctx_path"],
                    "priority": item["priority"],
                    "attempts": item["attempts"],
                    "last_error_ref": item["last_error_ref"],
                    "created_at": item["created_at"],
                },
                actor_id=owner_id,
            ),
        )
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope="user",
                table_name="work_queue_item_reasons",
                action="insert_reasons",
                payload={
                    "queue_id": queue_id,
                    "work_id": item["work_id"],
                    "reasons": item["reason"],
                    "created_at": item["created_at"],
                },
                actor_id=owner_id,
            ),
        )
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="update",
                scope="user",
                table_name="work_queues",
                action="touch_queue",
                payload={"queue_id": queue_id},
                actor_id=owner_id,
            ),
        )
    finally:
        lease.release_lock(repo_root, lock_resource, owner_id)
    return Path(table_name)


def _resolve_paths(
    ticket_path: Optional[str],
    target_path: Optional[str],
    ctx_path: Optional[str],
) -> tuple[str, str]:
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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Add a work item using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing work_id and queue path.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and kind in the payload.
        - Ensures certification and work mode requirements are met.
        - Uses default bucket/state when not provided.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
        bucket = optional_string(
            payload, "bucket", command_name=command_name, default="ready"
        )
        work_type = optional_string(payload, "work_type", command_name=command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        kind = require_string(payload, "kind", command_name)
        state = optional_string(
            payload, "state", command_name=command_name, default="queued"
        )
        target_path = optional_string(payload, "target_path", command_name=command_name)
        ctx_path = optional_string(payload, "ctx_path", command_name=command_name)
        ticket_path = optional_string(payload, "ticket_path", command_name=command_name)
        parent_work_id = optional_string(
            payload, "parent_work_id", command_name=command_name
        )
        root_work_id = optional_string(
            payload, "root_work_id", command_name=command_name
        )
        reason = optional_list(payload, "reason", command_name=command_name)
        priority = optional_int(payload, "priority", command_name=command_name, default=50)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    allowed_buckets = ["ready", "active", "backlog", "completed", "denied"]
    if bucket not in allowed_buckets:
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "bucket",
                    "expected": f"one of {allowed_buckets}",
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

    if work_type is not None and work_type not in _work_files():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "work_type",
                    "expected": f"one of {list(_work_files().keys())}",
                    "actual": work_type,
                },
            ),
        )

    try:
        ensure_certified(repo_root, owner_id or agent_id)
        ensure_feature_enabled(repo_root, "work_management", "add work items")
        resolved_work_id = work_id or generate_work_id()
        ensure_work_mode(repo_root, resolved_work_id, "add work items")

        normalized_kind, inferred_type = _normalize_kind(kind)
        if inferred_type is None:
            raise ValueError(f"Invalid work kind: {kind}")
        resolved_type = work_type or inferred_type or "task"
        if resolved_type not in _work_files():
            raise ValueError(f"Invalid work type: {resolved_type}")

        if _requires_parent(normalized_kind) and parent_work_id in (None, ""):
            raise ValueError("parent_work_id is required for story kinds")

        resolved_target, resolved_ctx = _resolve_paths(
            ticket_path, target_path, ctx_path
        )
        reasons = (
            reason if reason else (["github_intake"] if ticket_path else ["manual_add"])
        )
        created_at = utc_now_iso()
        resolved_root = root_work_id or resolved_work_id
        item = _build_work_item(
            work_id=resolved_work_id,
            kind=normalized_kind,
            state=state,
            target_path=resolved_target,
            ctx_path=resolved_ctx,
            reason=reasons,
            priority=priority or 0,
            created_at=created_at,
            parent_work_id=parent_work_id,
            root_work_id=resolved_root,
            source_ticket=ticket_path,
        )

        queue_path = add_work_item(
            repo_root, bucket, resolved_type, item, owner_id or agent_id
        )
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"agent_id": agent_id, "bucket": bucket},
        )

    return ok_result(
        output={
            "work_id": resolved_work_id,
            "queue_path": queue_path.as_posix(),
            "bucket": bucket,
            "work_type": resolved_type,
        }
    )


def main() -> None:
    """
    CLI entrypoint for adding a work item to work_management queues.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
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
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "bucket": args.bucket,
        "work_type": args.work_type,
        "work_id": args.work_id,
        "kind": args.kind,
        "state": args.state,
        "target_path": args.target_path,
        "ctx_path": args.ctx_path,
        "ticket_path": args.ticket_path,
        "parent_work_id": args.parent_work_id,
        "root_work_id": args.root_work_id,
        "reason": args.reason,
        "priority": args.priority,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="work_item_add",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_item_add failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(
        "work item added to %s: %s",
        result.output.get("queue_path"),
        result.output.get("work_id"),
    )


if __name__ == "__main__":
    main()
