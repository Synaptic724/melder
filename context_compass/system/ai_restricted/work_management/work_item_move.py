"""
Move a work item between work_management queues.

Purpose
- Provide a command-safe API for moving a work item between work buckets.
- Enforce certification, feature flags, and work mode guards.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import branch_paths
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
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
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
    normalized = kind.strip()
    lowered = normalized.lower()
    aliases = _aliases()
    if lowered in aliases:
        canonical = aliases[lowered]
        return canonical, canonical
    if lowered in _work_files():
        return lowered, lowered
    return normalized, None


def _queue_id(branch_name: str, bucket: str, work_type: str) -> str:
    """
    Build a branch queue_id for work_queues rows.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type key.

    Returns:
        str: Queue identifier for work_queues.
    """

    return f"{BRANCH_QUEUE_SCOPE}:{branch_name}:{bucket}:{work_type}"


def _work_queue_table_name() -> str:
    """
    Return the SQLite table name for branch/global work queues.

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


def _build_move_payload(
    *,
    source_queue_id: str,
    dest_queue_id: str,
    work_id: str,
    dest_scope: str,
    dest_branch_name: str,
    dest_bucket: str,
    dest_work_kind: str,
    dest_schema_version: int,
    dest_repo_id: str | None,
    new_state: str | None,
) -> dict:
    """
    Build a payload for the move_work_queue_item query.

    Args:
        source_queue_id (str): Source queue identifier.
        dest_queue_id (str): Destination queue identifier.
        work_id (str): Work identifier to move.
        dest_scope (str): Destination queue scope.
        dest_branch_name (str): Destination branch name.
        dest_bucket (str): Destination bucket.
        dest_work_kind (str): Destination work type.
        dest_schema_version (int): Destination schema version.
        dest_repo_id (str | None): Optional repo identifier.
        new_state (str | None): Optional new state override.

    Returns:
        dict: Query payload fields.
    """

    payload = {
        "source_queue_id": source_queue_id,
        "dest_queue_id": dest_queue_id,
        "work_id": work_id,
        "dest_scope": dest_scope,
        "dest_branch_name": dest_branch_name,
        "dest_bucket": dest_bucket,
        "dest_work_kind": dest_work_kind,
        "dest_schema_version": dest_schema_version,
        "dest_repo_id": dest_repo_id,
    }
    if new_state is not None:
        payload["new_state"] = new_state
    return payload


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


def move_work_item(
    repo_root: Path,
    work_id: str,
    source_bucket: str,
    dest_bucket: str,
    work_type: str,
    owner_id: str,
    new_state: Optional[str] = None,
) -> tuple[Path, Path]:
    """
    Move a work item between buckets for a given work type.

    Args:
        repo_root (Path): Repository root.
        work_id (str): Work identifier.
        source_bucket (str): Source bucket.
        dest_bucket (str): Destination bucket.
        work_type (str): Work type.
        owner_id (str): Lock owner id.
        new_state (Optional[str]): Optional new state.

    Returns:
        tuple[Path, Path]: Logical source and destination queue identifiers.
    """
    ensure_feature_enabled(repo_root, "work_management", "move work items")
    if source_bucket == dest_bucket:
        raise ValueError("source and destination buckets must differ")
    branch_name = branch_paths.load_current_branch(repo_root)
    source_queue_id = _queue_id(branch_name, source_bucket, work_type)
    dest_queue_id = _queue_id(branch_name, dest_bucket, work_type)
    source_table = _work_queue_table_name()
    dest_table = _work_queue_table_name()
    policies = _load_policies(repo_root, owner_id)
    lock_targets: list[tuple[str, Path]] = []
    for resource in {
        _branch_lock_resource(branch_name, source_bucket, work_type),
        _branch_lock_resource(branch_name, dest_bucket, work_type),
    }:
        lock_key = lease.lock_path_for(repo_root, resource)
        lock_targets.append((str(lock_key), resource))
    lock_targets.sort(key=lambda item: item[0])
    locked: list[Path] = []
    for _, resource in lock_targets:
        lease.acquire_lock(
            repo_root,
            resource,
            owner_id,
            ttl_seconds=policies["lease_ttl_seconds"],
        )
        locked.append(resource)
    try:
        move_payload = _build_move_payload(
            source_queue_id=source_queue_id,
            dest_queue_id=dest_queue_id,
            work_id=work_id,
            dest_scope="branch",
            dest_branch_name=branch_name,
            dest_bucket=dest_bucket,
            dest_work_kind=work_type,
            dest_schema_version=1,
            dest_repo_id=None,
            new_state=new_state,
        )
        sqlite_query.execute_request(
            repo_root,
            sqlite_query.SqliteQueryRequest(
                scope="user",
                query_name="move_work_queue_item",
                payload=move_payload,
                actor_id=owner_id,
            ),
        )
    finally:
        for resource in reversed(locked):
            lease.release_lock(repo_root, resource, owner_id)

    return Path(source_table), Path(dest_table)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Move a work item using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result with source/destination queue details on success.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, work_id, source_bucket, and dest_bucket.
        - Enforces certification, feature flag, and work mode policies.
        - Defaults work_type to "task" when not provided or inferred.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = require_string(payload, "work_id", command_name)
        source_bucket = require_choice(
            payload, "source_bucket", command_name, _bucket_choices()
        )
        dest_bucket = require_choice(
            payload, "dest_bucket", command_name, _bucket_choices()
        )
        work_type = optional_string(payload, "work_type", command_name=command_name)
        kind = optional_string(payload, "kind", command_name=command_name)
        state = optional_string(payload, "state", command_name=command_name)
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

    inferred_kind = None
    if work_type is None and kind:
        normalized, inferred = _normalize_kind(kind)
        inferred_kind = normalized
        if inferred is None:
            return payload_error_result(
                command_name,
                PayloadError(
                    code="payload_value_error",
                    details={
                        "command_name": command_name,
                        "field": "kind",
                        "expected": "epic, story, or task",
                        "actual": kind,
                        "normalized": normalized,
                    },
                ),
            )
        work_type = inferred

    if work_type is None:
        work_type = "task"

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
    try:
        ensure_certified(repo_root, effective_owner)
        ensure_feature_enabled(repo_root, "work_management", "move work items")
        ensure_work_mode(repo_root, work_id, "move work items")
        source_path, dest_path = move_work_item(
            repo_root=repo_root,
            work_id=work_id,
            source_bucket=source_bucket,
            dest_bucket=dest_bucket,
            work_type=work_type,
            owner_id=effective_owner,
            new_state=state,
        )
        return ok_result(
            output={
                "work_id": work_id,
                "work_type": work_type,
                "kind": inferred_kind,
                "source_bucket": source_bucket,
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
    CLI entrypoint for moving work items between buckets.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Move a work item between work_management queues")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", required=True, help="Work item identifier")
    parser.add_argument("--source-bucket", required=True, choices=_bucket_choices(), help="Source bucket")
    parser.add_argument("--dest-bucket", required=True, choices=_bucket_choices(), help="Destination bucket")
    parser.add_argument("--work-type", choices=["epic", "story", "task"], help="Queue type override")
    parser.add_argument("--kind", default=None, help="Work kind (used to infer work type)")
    parser.add_argument("--state", default=None, choices=_state_choices(), help="Optional new state")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "source_bucket": args.source_bucket,
        "dest_bucket": args.dest_bucket,
        "work_type": args.work_type,
        "kind": args.kind,
        "state": args.state,
        "owner_id": args.owner_id,
    }
    context = ExecutionContext(
        command_name="work_item_move",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("work_item_move failed: %s", result.errors)
        raise SystemExit(1)
    logger.info(
        "moved %s from %s to %s",
        result.output.get("work_id"),
        result.output.get("source_path"),
        result.output.get("dest_path"),
    )


if __name__ == "__main__":
    main()
