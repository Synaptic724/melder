"""
Copy work_management queues from one branch to another.

Purpose
- Copy SQLite-backed branch work queues between branches.
"""

import argparse
import logging
from pathlib import Path
from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
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
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

BRANCH_REGISTRY_TABLE = "branch_registry"

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1

QUERY_READ_BRANCH_WORK_QUEUE = "read_branch_work_queue"
QUERY_WRITE_BRANCH_WORK_QUEUE = "write_branch_work_queue"

DEFAULT_LEASE_TTL_SECONDS = 300
DEFAULT_LOCK_WAIT_SECONDS = 10


def _default_policies() -> dict:
    """
    Return default policy values for branch copy operations.

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
        actor_id (str): Actor identifier for audit logging.

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
    if isinstance(lease_ttl, int) and lease_ttl > 0:
        policies["lease_ttl_seconds"] = lease_ttl
    lock_wait = record.get("lock_wait_seconds")
    if isinstance(lock_wait, int) and lock_wait >= 0:
        policies["lock_wait_seconds"] = lock_wait
    return policies


def _work_files() -> list[str]:
    """
    Return the work_management queue types.

    Returns:
        list[str]: Queue work type names.
    """
    return ["epic", "story", "task"]


def _bucket_names() -> list[str]:
    """
    Return the work_management bucket names.

    Returns:
        list[str]: Bucket names.
    """
    return ["ready", "active", "backlog", "completed", "denied"]


def _default_queue(now: str) -> dict:
    """
    Return a default queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _work_queue_lock_resource(branch_name: str, bucket: str, work_type: str) -> Path:
    """
    Build a synthetic lock resource path for a branch work queue.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_work_queue::{branch_name}::{bucket}::{work_type}")


def _normalize_queue(data: dict, now: str, preserve_state: bool) -> dict:
    """
    Normalize a work queue for copy operations.

    Args:
        data (dict): Source queue payload.
        now (str): Current timestamp.
        preserve_state (bool): Keep state/leases if True.

    Returns:
        dict: Normalized queue payload.
    """
    queue = data.get("queue", [])
    if not isinstance(queue, list):
        queue = []
    normalized: list[dict] = []
    for item in queue:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        if not preserve_state:
            if entry.get("state") in ("leased", "in_progress"):
                entry["state"] = "queued"
            entry["lease"] = None
        entry["updated_at"] = now
        normalized.append(entry)
    return {
        "schema_version": int(data.get("schema_version") or 1),
        "repo_id": data.get("repo_id"),
        "updated_at": now,
        "queue": normalized,
    }


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
            query_name=QUERY_READ_BRANCH_WORK_QUEUE,
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
            query_name=QUERY_WRITE_BRANCH_WORK_QUEUE,
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


def copy_work(
    repo_root: Path,
    source_branch: str,
    dest_branch: str,
    preserve_state: bool,
    owner_id: str,
) -> dict:
    """
    Copy work_management queues from source to destination branch.

    Args:
        repo_root (Path): Repository root.
        source_branch (str): Source branch name.
        dest_branch (str): Destination branch name.
        preserve_state (bool): Preserve leases and in_progress states if True.
        owner_id (str): Lock owner id.

    Returns:
        dict: Summary of copied queues.
    """
    policies = _load_policies(repo_root, owner_id)
    now = utc_now_iso()
    _require_branch_registered(repo_root, source_branch, owner_id)
    _require_branch_registered(repo_root, dest_branch, owner_id)

    resources: list[Path] = []
    for bucket in _bucket_names():
        for work_type in _work_files():
            resources.append(_work_queue_lock_resource(source_branch, bucket, work_type))
            resources.append(_work_queue_lock_resource(dest_branch, bucket, work_type))

    locked = _lock_entries(
        repo_root,
        resources,
        owner_id,
        ttl_seconds=int(policies["lease_ttl_seconds"]),
    )
    copied: list[str] = []
    skipped: list[str] = []
    try:
        for bucket in _bucket_names():
            for work_type in _work_files():
                source_payload, source_exists = _read_queue(
                    repo_root,
                    source_branch,
                    bucket,
                    work_type,
                    actor_id=owner_id,
                )
                _, dest_exists = _read_queue(
                    repo_root,
                    dest_branch,
                    bucket,
                    work_type,
                    actor_id=owner_id,
                )
                if not source_exists:
                    normalized = _default_queue(now)
                    skipped.append(f"{bucket}/{work_type}")
                else:
                    normalized = _normalize_queue(
                        source_payload,
                        now,
                        preserve_state,
                    )
                    copied.append(f"{bucket}/{work_type}")
                _write_queue(
                    repo_root,
                    dest_branch,
                    bucket,
                    work_type,
                    normalized,
                    actor_id=owner_id,
                    exists=dest_exists,
                )
    finally:
        for resource in locked:
            lease.release_lock(repo_root, resource, owner_id)

    return {"copied": copied, "skipped": skipped}


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Copy work queues using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing copied and skipped queue lists.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, source_branch, and dest_branch.
        - Enforces certification and work mode guards.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        source_branch = require_string(payload, "source_branch", command_name)
        dest_branch = require_string(payload, "dest_branch", command_name)
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        preserve_state = optional_bool(
            payload, "preserve_state", command_name=command_name, default=False
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_work_mode(repo_root, work_id, "copy branch work queues")
        summary = copy_work(
            repo_root=repo_root,
            source_branch=source_branch,
            dest_branch=dest_branch,
            preserve_state=bool(preserve_state),
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
    parser = argparse.ArgumentParser(description="Copy branch work queues.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--source-branch", required=True, help="Source branch name")
    parser.add_argument("--dest-branch", required=True, help="Destination branch name")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument(
        "--preserve-state",
        action="store_true",
        help="Preserve lease and in_progress states",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "source_branch": args.source_branch,
        "dest_branch": args.dest_branch,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "preserve_state": args.preserve_state,
    }
    context = ExecutionContext(
        command_name="branch_copy_work",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("branch_copy_work failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("copied work queues: %s", result.output.get("copied"))


if __name__ == "__main__":
    main()
