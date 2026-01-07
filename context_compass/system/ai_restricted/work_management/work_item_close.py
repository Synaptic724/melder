"""
Close a work item and remove it from per-agent queues.

Purpose
- Move a work item to a terminal bucket and state.
- Optionally remove the work item from per-agent queues.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted.work_management import work_item_move
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
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
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

AGENT_QUEUE_TABLE_NAME = "agent_work_queue"
POLICIES_TABLE_NAME = "config_policies_core"
POLICIES_ACTION = "by_config_id"
POLICIES_CONFIG_ID = 1


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


def _execute_delete(
    repo_root: Path,
    owner_id: str,
    table_name: str,
    action: str,
    payload: dict,
) -> dict:
    """
    Execute a delete action against an SQLite table via CRUD.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Actor identifier for audit logging.
        table_name (str): CRUD table name.
        action (str): CRUD action name.
        payload (dict): CRUD payload for the delete script.

    Returns:
        dict: Script result payload returned by sqlite_crud.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="delete",
            scope="user",
            table_name=table_name,
            action=action,
            payload=payload,
            actor_id=owner_id,
        ),
    )
    return response.output.get("result", {})


def _touch_agent_queue(repo_root: Path, agent_id: str, owner_id: str) -> None:
    """
    Touch an agent work queue row after deletions.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        owner_id (str): Actor identifier for audit logging.

    Raises:
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    try:
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
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_missing":
            return
        raise


def _agent_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for an agent queue lock.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"{AGENT_QUEUE_TABLE_NAME}::{agent_id}")


def _remove_from_agent_queue(repo_root: Path, agent_id: str, work_id: str, owner_id: str) -> bool:
    """
    Remove a work item from a per-agent queue.

    Purpose:
    - Ensure closed work items are removed from agent queue tables via CRUD.

    Contract:
    - Returns False when the queue is missing or the item is absent.
    - Touches the agent queue row when deletions occur.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        work_id (str): Work identifier to remove.
        owner_id (str): Lock owner id.

    Returns:
        bool: True if an item was removed.
    """
    policies = _load_policies(repo_root, owner_id)
    lock_resource = _agent_lock_resource(agent_id)
    lease.acquire_lock(
        repo_root,
        lock_resource,
        owner_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        removed_total = 0
        for table_name, action in (
            ("agent_work_item_reasons", "by_work_id"),
            ("agent_work_item_lease", "by_work_id"),
            ("agent_work_items", "by_work_id"),
        ):
            result = _execute_delete(
                repo_root,
                owner_id,
                table_name,
                action,
                {"agent_id": agent_id, "work_id": work_id},
            )
            removed = result.get("removed")
            if isinstance(removed, int):
                removed_total += removed
        if removed_total > 0:
            _touch_agent_queue(repo_root, agent_id, owner_id)
        return removed_total > 0
    finally:
        lease.release_lock(repo_root, lock_resource, owner_id)


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


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Close a work item using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result describing the closed work item.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, work_id, and work_type.
        - Enforces certification, feature flags, and work mode guards.
        - Defaults source/dest buckets and close state when omitted.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = require_string(payload, "work_id", command_name)
        work_type = require_choice(
            payload, "work_type", command_name, ["epic", "story", "task"]
        )
        source_bucket = optional_string(
            payload, "source_bucket", command_name=command_name, default="active"
        )
        dest_bucket = optional_string(
            payload, "dest_bucket", command_name=command_name, default="completed"
        )
        state = optional_string(payload, "state", command_name=command_name, default="done")
        queue_agent_id = optional_string(
            payload, "queue_agent_id", command_name=command_name
        )
        skip_queue_removal = optional_bool(
            payload, "skip_queue_removal", command_name=command_name, default=False
        )
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if source_bucket not in _bucket_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "source_bucket",
                    "expected": f"one of {_bucket_choices()}",
                    "actual": source_bucket,
                },
            ),
        )
    if dest_bucket not in _bucket_choices():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "dest_bucket",
                    "expected": f"one of {_bucket_choices()}",
                    "actual": dest_bucket,
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

    effective_owner = owner_id or agent_id
    if skip_queue_removal:
        queue_agent = None
    else:
        queue_agent = queue_agent_id or agent_id
    try:
        ensure_certified(repo_root, effective_owner)
        ensure_feature_enabled(repo_root, "work_management", "close work items")
        ensure_work_mode(repo_root, work_id, "close work items")
        close_work_item(
            repo_root=repo_root,
            work_id=work_id,
            work_type=work_type,
            source_bucket=source_bucket,
            dest_bucket=dest_bucket,
            owner_id=effective_owner,
            new_state=state,
            queue_agent_id=queue_agent,
        )
        return ok_result(
            output={
                "work_id": work_id,
                "work_type": work_type,
                "source_bucket": source_bucket,
                "dest_bucket": dest_bucket,
                "state": state,
                "queue_agent_id": queue_agent,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for closing a work item and clearing per-agent queues.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
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
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "work_type": args.work_type,
        "source_bucket": args.source_bucket,
        "dest_bucket": args.dest_bucket,
        "state": args.state,
        "queue_agent_id": args.queue_agent_id,
        "skip_queue_removal": args.skip_queue_removal,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="work_item_close",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_item_close failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("closed work item: %s", result.output.get("work_id"))


if __name__ == "__main__":
    main()
