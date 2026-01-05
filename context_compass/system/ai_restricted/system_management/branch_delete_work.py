"""
Clear work_management queues for a branch.

Purpose
- Reset SQLite-backed branch work queues to empty payloads.
"""

import argparse
import logging
from pathlib import Path
from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)

BRANCH_REGISTRY_TABLE = "branch_registry"
CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1
DEFAULT_LEASE_TTL_SECONDS = 300
DEFAULT_LOCK_WAIT_SECONDS = 10


def _default_policies() -> dict:
    """
    Return default policy values for branch delete operations.

    Returns:
        dict: Policy defaults for lease TTL and lock wait.
    """
    return {
        "lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS,
        "lock_wait_seconds": DEFAULT_LOCK_WAIT_SECONDS,
    }


def _load_policies(repo_root: Path, actor_id: str) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies for lease TTL and lock wait.

    Raises:
        ValueError: If policy values are invalid.
        sqlite_crud.SqliteCrudError: If the policy lookup fails.
    """
    policies = _default_policies()
    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="system",
            table_name=CONFIG_POLICIES_TABLE,
            action=CONFIG_POLICIES_ACTION,
            payload={"config_id": CONFIG_POLICIES_ID},
            actor_id=actor_id,
        ),
    )
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_policies_core read returned an invalid record payload.")
    lease_ttl = record.get("lease_ttl_seconds")
    lock_wait = record.get("lock_wait_seconds")
    if isinstance(lease_ttl, int):
        policies["lease_ttl_seconds"] = lease_ttl
    if isinstance(lock_wait, int):
        policies["lock_wait_seconds"] = lock_wait
    return policies


def _bucket_names() -> list[str]:
    """
    Return work bucket names.

    Returns:
        list[str]: Bucket names.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


def _work_files() -> list[str]:
    """
    Return work queue types.

    Returns:
        list[str]: Queue type names.
    """
    return ["epic", "story", "task"]


def _default_queue(now: str) -> dict:
    """
    Return a default queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _branch_work_queue_lock_resource(branch_name: str, bucket: str, work_type: str) -> Path:
    """
    Build a synthetic lock resource path for a branch work queue.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work queue type.

    Returns:
        Path: Resource path for lease locks.
    """
    return Path(f"branch_work_queue::{branch_name}::{bucket}::{work_type}")


def _lock_entries(repo_root: Path, resources: list[Path], owner_id: str, ttl_seconds: int) -> list[Path]:
    """
    Acquire locks for the provided resources in deterministic order.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resources (list[Path]): Resources to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL seconds.

    Returns:
        list[Path]: Locked resources.
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


def _require_branch_registered(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Ensure a branch exists in the system branch_registry table.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name to check.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        FileNotFoundError: If the branch is not registered or the DB is missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=BRANCH_REGISTRY_TABLE,
                action="by_branch_name",
                payload={"record_id": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code in {"record_not_found", "db_missing"}:
            raise FileNotFoundError(f"Branch not registered: {branch_name}") from exc
        raise


def _read_queue(
    repo_root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read a branch work queue payload via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Queue payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="read_branch_work_queue",
            payload={
                "branch_name": branch_name,
                "bucket": bucket,
                "work_type": work_type,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    queue = result.get("queue")
    exists = result.get("exists")
    if not isinstance(queue, dict):
        raise ValueError("work_queue read returned an invalid queue payload.")
    if not isinstance(exists, bool):
        raise ValueError("work_queue read returned an invalid exists flag.")
    return queue, exists


def _write_queue(
    repo_root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    queue_payload: dict,
    actor_id: str,
    exists: bool,
) -> None:
    """
    Persist a branch work queue payload via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.
        queue_payload (dict): Queue payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the queue record already exists.

    Raises:
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_branch_work_queue",
            payload={
                "branch_name": branch_name,
                "bucket": bucket,
                "work_type": work_type,
                "queue_payload": queue_payload,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )


def clear_work(
    repo_root: Path,
    branch_name: str,
    owner_id: str,
) -> dict:
    """
    Clear all work queues for the specified branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        owner_id (str): Lock owner id.

    Returns:
        dict: Summary of cleared queues.
    """
    policies = _load_policies(repo_root, owner_id)
    now = utc_now_iso()
    _require_branch_registered(repo_root, branch_name, owner_id)

    resources: list[Path] = []
    for bucket in _bucket_names():
        for work_type in _work_files():
            resources.append(_branch_work_queue_lock_resource(branch_name, bucket, work_type))

    locked = _lock_entries(
        repo_root,
        resources,
        owner_id,
        ttl_seconds=int(policies["lease_ttl_seconds"]),
    )
    cleared: list[str] = []
    try:
        for bucket in _bucket_names():
            for work_type in _work_files():
                _, exists = _read_queue(
                    repo_root,
                    branch_name,
                    bucket,
                    work_type,
                    actor_id=owner_id,
                )
                _write_queue(
                    repo_root,
                    branch_name,
                    bucket,
                    work_type,
                    _default_queue(now),
                    actor_id=owner_id,
                    exists=exists,
                )
                cleared.append(f"{bucket}/{work_type}")
    finally:
        for resource in locked:
            lease.release_lock(repo_root, resource, owner_id)

    return {"cleared": cleared}


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Clear branch work queues using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing cleared queue identifiers.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id and branch_name.
        - Enforces certification and work mode guards.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        branch_name = require_string(payload, "branch_name", command_name)
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_work_mode(repo_root, work_id, "clear branch work queues")
        summary = clear_work(
            repo_root=repo_root,
            branch_name=branch_name,
            owner_id=agent_id,
        )
        return ok_result(output=summary)
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Clear branch work queues.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--branch-name", required=True, help="Branch name to modify")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "branch_name": args.branch_name,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
    }
    context = ExecutionContext(
        command_name="branch_delete_work",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("branch_delete_work failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("cleared work queues: %s", result.output.get("cleared"))


if __name__ == "__main__":
    main()
