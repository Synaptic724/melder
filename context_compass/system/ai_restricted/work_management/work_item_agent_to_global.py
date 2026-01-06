"""
Move a work item from a per-agent queue into the global work queues.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional, Tuple

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
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
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)

WORK_QUEUE_TABLE_NAME = "work_queues"
AGENT_QUEUE_TABLE_NAME = "agent_work_queue"
GLOBAL_QUEUE_SCOPE = "global"
POLICIES_TABLE_NAME = "config_policies_core"
POLICIES_ACTION = "by_config_id"
POLICIES_CONFIG_ID = 1


def _work_files() -> dict:
    """
    Return supported work queue types.

    Purpose:
    - Centralize the allowed work types for queue selection.

    Contract:
    - Only epic/story/task are supported queue types.

    Returns:
        dict: Mapping of work types to canonical names.
    """
    return {"epic": "epic", "story": "story", "task": "task"}


def _bucket_choices() -> list[str]:
    """
    Return allowed work bucket values.

    Purpose:
    - Enforce the canonical backlog/active/completed/denied buckets.

    Returns:
        list[str]: Allowed bucket values.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


def _state_choices() -> list[str]:
    """
    Return allowed work item state values.

    Purpose:
    - Keep work item state transitions within the approved enum.

    Returns:
        list[str]: Allowed state values.
    """
    return ["queued", "leased", "in_progress", "done", "failed", "cancelled"]


def _aliases() -> dict:
    """
    Return kind aliases that normalize to canonical work types.

    Purpose:
    - Normalize user input so queue selection is deterministic.

    Returns:
        dict: Mapping of kind aliases to canonical work types.
    """
    return {"epic": "epic", "story": "story", "task": "task"}


def _normalize_kind(kind: str) -> Tuple[str, Optional[str]]:
    """
    Normalize a kind string and infer a work type.

    Purpose:
    - Accept canonical work types and normalize common aliases.

    Contract:
    - Returns (normalized_kind, inferred_type) where inferred_type may be None.

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


def _resolve_work_type(work_type: Optional[str], item: Optional[dict]) -> str:
    """
    Resolve the destination work_type from an item or explicit override.

    Purpose:
    - Ensure the destination queue file is explicit and deterministic.

    Args:
        work_type (Optional[str]): Explicit work type override.
        item (Optional[dict]): Agent work item record for inference.

    Returns:
        str: Resolved work type.

    Raises:
        ValueError: If the work type cannot be inferred.
    """
    if work_type:
        if work_type not in _work_files():
            raise ValueError(f"Invalid work_type: {work_type}")
        return work_type
    if not item:
        raise ValueError("work_type is required when item kind is not epic/story/task")
    kind = item.get("kind")
    if isinstance(kind, str):
        _, inferred = _normalize_kind(kind)
        if inferred:
            return inferred
    raise ValueError("work_type is required when item kind is not epic/story/task")


def _agent_queue_id(agent_id: str) -> Path:
    """
    Return the logical agent queue identifier.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Logical queue identifier for the SQLite table.
    """
    return Path(f"{AGENT_QUEUE_TABLE_NAME}::{agent_id}")


def _work_queue_table_name() -> str:
    """
    Return the SQLite table name for branch/global work queues.

    Purpose:
    - Keep table name resolution local to avoid store module dependencies.

    Returns:
        str: SQLite table name for work queues.
    """

    return WORK_QUEUE_TABLE_NAME


def _agent_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for an agent queue lock.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"agent_work::{agent_id}")


def _global_lock_resource(bucket: str, work_type: str) -> Path:
    """
    Build a synthetic lock resource path for a global queue lock.

    Args:
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"global_work_queue::{bucket}::{work_type}")


def _global_queue_id(bucket: str, work_type: str) -> str:
    """
    Build the queue_id for a global queue.

    Args:
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        str: Queue identifier for the global queue.
    """

    return f"{GLOBAL_QUEUE_SCOPE}:global:{bucket}:{work_type}"


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


def _build_move_payload(
    *,
    agent_id: str,
    work_id: str,
    dest_queue_id: str,
    dest_bucket: str,
    dest_work_kind: str,
    dest_schema_version: int,
    dest_repo_id: str | None,
    new_state: str | None,
) -> dict:
    """
    Build a payload for the move_agent_work_item_to_queue query.

    Args:
        agent_id (str): Source agent identifier.
        work_id (str): Work identifier to move.
        dest_queue_id (str): Destination queue identifier.
        dest_bucket (str): Destination bucket name.
        dest_work_kind (str): Destination work type.
        dest_schema_version (int): Schema version for destination queue.
        dest_repo_id (str | None): Optional repo identifier.
        new_state (str | None): Optional new state override.

    Returns:
        dict: Query payload fields.
    """

    payload = {
        "agent_id": agent_id,
        "work_id": work_id,
        "dest_queue_id": dest_queue_id,
        "dest_scope": "global",
        "dest_branch_name": None,
        "dest_bucket": dest_bucket,
        "dest_work_kind": dest_work_kind,
        "dest_schema_version": dest_schema_version,
        "dest_repo_id": dest_repo_id,
    }
    if new_state is not None:
        payload["new_state"] = new_state
    return payload


def _fetch_agent_item(
    repo_root: Path,
    agent_id: str,
    work_id: str,
    actor_id: str,
) -> Optional[dict]:
    """
    Fetch an agent work item record for work_type inference.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        work_id (str): Work identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        Optional[dict]: Agent work item record or None when missing.

    Raises:
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name="agent_work_items",
                action="by_work_id",
                payload={"agent_id": agent_id, "work_id": work_id},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_missing":
            return None
        raise
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise sqlite_crud.SqliteCrudError(
            code="record_invalid",
            meaning="Agent work item read returned invalid record payload.",
            details={"agent_id": agent_id, "work_id": work_id},
        )
    return record


def _acquire_locks(
    repo_root: Path,
    resources: list[Path],
    owner_id: str,
    ttl_seconds: int,
) -> list[Path]:
    """
    Acquire locks for queue resources in deterministic order.

    Purpose:
    - Prevent concurrent writers from corrupting queues.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resources (list[Path]): Resource paths to lock.
        owner_id (str): Lock owner identifier.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        list[Path]: Locked resources for release.
    """
    lock_targets: list[tuple[str, Path]] = []
    for resource in resources:
        lock_path = lease.lock_path_for(repo_root, resource)
        lock_targets.append((str(lock_path), resource))

    lock_targets.sort(key=lambda item: item[0])
    locked: list[Path] = []
    for _, resource in lock_targets:
        lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds=ttl_seconds)
        locked.append(resource)
    return locked


def _release_locks(repo_root: Path, entries: list[Path], owner_id: str) -> None:
    """
    Release locks in reverse acquisition order.

    Args:
        entries (list[Path]): Locked resources to release.
        owner_id (str): Lock owner identifier.
    """
    for resource in reversed(entries):
        lease.release_lock(repo_root, resource, owner_id)


def move_work_item(
    repo_root: Path,
    source_agent_id: str,
    work_id: str,
    dest_bucket: str,
    owner_id: str,
    work_type: Optional[str] = None,
    new_state: Optional[str] = None,
) -> Tuple[Path, Path]:
    """
    Move a work item from an agent queue into global work queues.

    Purpose:
    - Publish agent-owned work items into the global shared history.

    Contract:
    - Locks the agent queue and destination queue before issuing the move query.
    - Delegates row movement to the SQLite query script.

    Args:
        repo_root (Path): Repository root.
        source_agent_id (str): Agent queue owner to read from.
        work_id (str): Work identifier to move.
        dest_bucket (str): Destination bucket in global queues.
        owner_id (str): Lock owner identifier.
        work_type (Optional[str]): Work type override (epic/story/task).
        new_state (Optional[str]): Optional new state for the moved item.

    Returns:
        Tuple[Path, Path]: Logical source and destination queue identifiers.

    Raises:
        FileNotFoundError: If the work item is missing and work_type is not provided.
        ValueError: If the work type cannot be resolved.
    """
    ensure_feature_enabled(repo_root, "work_management", "move work items")
    source_id = _agent_queue_id(source_agent_id)
    preview_item = None
    if work_type is None:
        preview_item = _fetch_agent_item(repo_root, source_agent_id, work_id, owner_id)
        if preview_item is None:
            raise FileNotFoundError(f"Agent queue missing work item: {work_id}")
    resolved_type = _resolve_work_type(work_type, preview_item)
    dest_queue_id = _global_queue_id(dest_bucket, resolved_type)
    dest_table = _work_queue_table_name()

    policies = _load_policies(repo_root, owner_id)
    locked = _acquire_locks(
        repo_root,
        [
            _agent_lock_resource(source_agent_id),
            _global_lock_resource(dest_bucket, resolved_type),
        ],
        owner_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        payload = _build_move_payload(
            agent_id=source_agent_id,
            work_id=work_id,
            dest_queue_id=dest_queue_id,
            dest_bucket=dest_bucket,
            dest_work_kind=resolved_type,
            dest_schema_version=1,
            dest_repo_id=None,
            new_state=new_state,
        )
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name="move_agent_work_item_to_queue",
                payload=payload,
                actor_id=owner_id,
            ),
        )
    finally:
        _release_locks(repo_root, locked, owner_id)

    return source_id, Path(dest_table)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Move a work item from an agent queue into global queues via the runner.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing source and destination queue paths.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, work_id, and dest_bucket.
        - Enforces certification, feature flags, and work mode guards.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = require_string(payload, "work_id", command_name)
        dest_bucket = require_choice(
            payload, "dest_bucket", command_name, _bucket_choices()
        )
        work_type = optional_string(payload, "work_type", command_name=command_name)
        state = optional_string(payload, "state", command_name=command_name)
        source_agent_id = optional_string(
            payload, "source_agent_id", command_name=command_name
        )
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if work_type is not None and work_type not in _work_files():
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "work_type",
                    "expected": f"one of {sorted(_work_files())}",
                    "actual": work_type,
                },
            ),
        )
    if state is not None and state not in _state_choices():
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
    effective_source = source_agent_id or agent_id
    try:
        ensure_certified(repo_root, effective_owner)
        ensure_feature_enabled(repo_root, "work_management", "move work items")
        ensure_work_mode(repo_root, work_id, "move work items")
        source_path, dest_path = move_work_item(
            repo_root=repo_root,
            source_agent_id=effective_source,
            work_id=work_id,
            dest_bucket=dest_bucket,
            owner_id=effective_owner,
            work_type=work_type,
            new_state=state,
        )
        return ok_result(
            output={
                "work_id": work_id,
                "source_agent_id": effective_source,
                "dest_bucket": dest_bucket,
                "source_path": str(source_path),
                "dest_path": str(dest_path),
                "state": state,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for moving an agent work item into global queues.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Move a work item from an agent queue to global queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier (actor)")
    parser.add_argument("--source-agent-id", default=None, help="Source agent queue id (defaults to agent-id)")
    parser.add_argument("--work-id", required=True, help="Work item identifier")
    parser.add_argument("--dest-bucket", required=True, choices=_bucket_choices(), help="Global destination bucket")
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Work type override")
    parser.add_argument("--state", default=None, choices=_state_choices(), help="Optional new state")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "source_agent_id": args.source_agent_id,
        "work_id": args.work_id,
        "dest_bucket": args.dest_bucket,
        "work_type": args.work_type,
        "state": args.state,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="work_item_agent_to_global",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_item_agent_to_global failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(
        "moved %s from %s to %s",
        result.output.get("work_id"),
        result.output.get("source_path"),
        result.output.get("dest_path"),
    )


if __name__ == "__main__":
    main()
