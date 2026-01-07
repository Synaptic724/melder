"""
Add a work item to a per-agent work queue.

Purpose
- Provide a command-safe API for agent queue inserts.
- Enforce certification, feature flags, and work mode guards.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
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
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.work_ids import generate_work_id
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

AGENT_QUEUE_TABLE_NAME = "agent_work_queue"
POLICIES_TABLE_NAME = "config_policies_core"
POLICIES_ACTION = "by_config_id"
POLICIES_CONFIG_ID = 1


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


def _queue_payload(agent_id: str) -> dict:
    """
    Build payload fields for ensuring an agent_work_queue row.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        dict: Payload fields for agent_work_queue ensure action.
    """

    return {"agent_id": agent_id, "schema_version": 1}


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


def _agent_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for an agent queue lock.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"{AGENT_QUEUE_TABLE_NAME}::{agent_id}")


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
    policies = _load_policies(repo_root, owner_id)
    lock_resource = _agent_lock_resource(agent_id)

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
                table_name="agent_work_queue",
                action="ensure_queue",
                payload=_queue_payload(agent_id),
                actor_id=owner_id,
            ),
        )
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope="user",
                table_name="agent_work_items",
                action="insert_item",
                payload={
                    "agent_id": agent_id,
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
                table_name="agent_work_item_reasons",
                action="insert_reasons",
                payload={
                    "agent_id": agent_id,
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
                table_name="agent_work_queue",
                action="touch_queue",
                payload={"agent_id": agent_id},
                actor_id=owner_id,
            ),
        )
    finally:
        lease.release_lock(repo_root, lock_resource, owner_id)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Add a work item to a per-agent queue using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the created work_id.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, kind, target_path, and ctx_path.
        - Generates work_id when omitted.
        - Enforces certification, feature flags, and work mode policies.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        kind = require_string(payload, "kind", command_name)
        state = optional_string(payload, "state", command_name=command_name, default="queued")
        target_path = require_string(payload, "target_path", command_name)
        ctx_path = require_string(payload, "ctx_path", command_name)
        parent_work_id = optional_string(payload, "parent_work_id", command_name=command_name)
        root_work_id = optional_string(payload, "root_work_id", command_name=command_name)
        reason = optional_list(payload, "reason", command_name=command_name)
        priority = optional_int(payload, "priority", command_name=command_name, default=50)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    effective_work_id = work_id or generate_work_id()
    if _requires_parent(kind) and not parent_work_id:
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

    reasons = reason if reason else ["manual_add"]
    created_at = utc_now_iso()
    root_id = root_work_id or effective_work_id
    item = _build_work_item(
        work_id=effective_work_id,
        kind=kind,
        state=state,
        target_path=target_path,
        ctx_path=ctx_path,
        reason=reasons,
        priority=priority or 50,
        created_at=created_at,
        parent_work_id=parent_work_id,
        root_work_id=root_id,
    )

    effective_owner = owner_id or agent_id
    try:
        ensure_certified(repo_root, effective_owner)
        ensure_feature_enabled(repo_root, "work_management", "add work items")
        ensure_work_mode(repo_root, effective_work_id, "add work items")
        add_work_item(repo_root, agent_id, item, effective_owner)
        return ok_result(
            output={
                "work_id": effective_work_id,
                "agent_id": agent_id,
                "kind": kind,
                "state": state,
                "target_path": target_path,
                "ctx_path": ctx_path,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for adding a work item to a per-agent queue.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Add a work item to an agent queue")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work item identifier (auto-generated if omitted)")
    parser.add_argument("--kind", required=True, help="Work item kind")
    parser.add_argument("--state", default="queued", help="Work item state")
    parser.add_argument("--target-path", required=True, help="Target path")
    parser.add_argument("--ctx-path", required=True, help="Context path")
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
        "work_id": args.work_id,
        "kind": args.kind,
        "state": args.state,
        "target_path": args.target_path,
        "ctx_path": args.ctx_path,
        "parent_work_id": args.parent_work_id,
        "root_work_id": args.root_work_id,
        "reason": args.reason,
        "priority": args.priority,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="work_queue_add",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_queue_add failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(
        "work item added to %s queue: %s",
        result.output.get("agent_id"),
        result.output.get("work_id"),
    )


if __name__ == "__main__":
    main()
