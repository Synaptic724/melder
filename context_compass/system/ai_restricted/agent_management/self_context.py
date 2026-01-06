"""Manage context_compass self-context records."""

import argparse
import logging
from pathlib import Path

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import self_context_store
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
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
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1
DEFAULT_LEASE_TTL_SECONDS = 300
DEFAULT_LEASE_HEARTBEAT_SECONDS = 30
DEFAULT_LOCK_WAIT_SECONDS = 10
QUERY_READ_SELF_CONTEXT = "read_self_context"
QUERY_WRITE_SELF_CONTEXT = "write_self_context"


def _default_policies() -> dict:
    """
    Return default policy values used by self-context tooling.

    Returns:
        dict: Default policy values for lease TTL, heartbeat, and lock wait.
    """
    return {
        "lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS,
        "lease_heartbeat_seconds": DEFAULT_LEASE_HEARTBEAT_SECONDS,
        "lock_wait_seconds": DEFAULT_LOCK_WAIT_SECONDS,
    }


def _load_policies(repo_root: Path, actor_id: str) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Effective policies for lease TTL, heartbeat, and lock wait.

    Raises:
        ValueError: If policy values are invalid.
        sqlite_crud.SqliteCrudError: If the policy lookup fails.
    """
    defaults = _default_policies()
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
    lease_heartbeat = record.get("lease_heartbeat_seconds")
    lock_wait = record.get("lock_wait_seconds")
    if isinstance(lease_ttl, int):
        defaults["lease_ttl_seconds"] = lease_ttl
    if isinstance(lease_heartbeat, int):
        defaults["lease_heartbeat_seconds"] = lease_heartbeat
    if isinstance(lock_wait, int):
        defaults["lock_wait_seconds"] = lock_wait
    return defaults


def _acquire_lock(repo_root: Path, resource: Path, owner_id: str, ttl_seconds: int) -> dict:
    """
    Acquire or steal a lease lock for a resource.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resource (Path): Resource to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        dict: Lease record.

    Raises:
        RuntimeError: If a non-expired lock is held by another owner.
    """
    return lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds)


def _release_lock(repo_root: Path, resource: Path, owner_id: str) -> None:
    """
    Release a lease lock if owned by the caller.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resource (Path): Resource to unlock.
        owner_id (str): Lock owner id.
    """
    lease.release_lock(repo_root, resource, owner_id)


def _self_context_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for a self-context record.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"self_context::{agent_id}")


def _read_self_context(repo_root: Path, agent_id: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read a self_context payload via the SQLite query API.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Self-context payload and existence flag.

    Raises:
        ValueError: If the query returns an invalid payload structure.
        sqlite_query.SqliteQueryError: If the query execution fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_SELF_CONTEXT,
            payload={"agent_id": agent_id},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("self_context read returned an invalid result payload.")
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("self_context read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("self_context read returned an invalid exists flag.")
    return record, exists


def _write_self_context(
    repo_root: Path,
    agent_id: str,
    self_context: dict,
    actor_id: str,
    exists: bool,
) -> None:
    """
    Persist a self_context payload via the SQLite query API.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        self_context (dict): Self-context payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the self-context record already exists.

    Raises:
        ValueError: If the query returns an invalid payload structure.
        sqlite_query.SqliteQueryError: If the query execution fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_WRITE_SELF_CONTEXT,
            payload={
                "agent_id": agent_id,
                "self_context": self_context,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("self_context write returned an invalid result payload.")
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("self_context write returned an invalid record payload.")


def _ensure_self_context(repo_root: Path, agent_id: str, actor_id: str) -> None:
    """
    Create a self-context record in SQLite if it does not exist.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.
    """

    _, exists = _read_self_context(repo_root, agent_id, actor_id)
    if exists:
        return
    now = utc_now_iso()
    payload = self_context_store.default_self_context(agent_id, now)
    _write_self_context(repo_root, agent_id, payload, actor_id, exists=False)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Initialize or update self-context records using the runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result indicating whether initialization occurred.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id in the payload.
        - init_self controls whether the self context file is created.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        init_self = optional_bool(
            payload, "init_self", command_name=command_name, default=False
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        policies = _load_policies(repo_root, agent_id)
        if init_self:
            resource = _self_context_lock_resource(agent_id)
            _acquire_lock(repo_root, resource, agent_id, policies["lease_ttl_seconds"])
            try:
                _ensure_self_context(repo_root, agent_id, actor_id=agent_id)
            finally:
                _release_lock(repo_root, resource, agent_id)
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"agent_id": agent_id, "init_self": init_self},
        )

    return ok_result(output={"agent_id": agent_id, "initialized": bool(init_self)})


def main() -> None:
    """
    CLI entrypoint for self-context management.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Manage context_compass self context")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--current-task-id", default=None, help="Current task id")
    parser.add_argument("--current-target", default=None, help="Current target path")
    parser.add_argument("--notes", default=None, help="Optional notes")
    parser.add_argument("--init-self", action="store_true", help="Initialize self context if missing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "current_task_id": args.current_task_id,
        "current_target": args.current_target,
        "notes": args.notes,
        "init_self": args.init_self,
    }
    context = ExecutionContext(
        command_name="self_context",
        agent_id=args.agent_id,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("self_context failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("self_context updated for agent %s", result.output.get("agent_id"))


if __name__ == "__main__":
    main()
