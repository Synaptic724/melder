"""
Delete branch context records from SQLite.

Purpose
- Remove repo_state and context artifacts for a branch in SQLite.
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
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


BRANCH_REGISTRY_TABLE = "branch_registry"
BRANCH_REGISTRY_ACTION = "by_branch_name"

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1

QUERY_DELETE_CONTEXT_PROFILES = "delete_context_profiles"
QUERY_DELETE_REPO_STATE = "delete_repo_state"
QUERY_DELETE_ARCHITECTURE_CONTEXT = "delete_architecture_context"
QUERY_DELETE_COMPONENT_CONTEXTS = "delete_component_contexts"

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


def _context_ids(include_repo_state: bool) -> list[str]:
    """
    Return the context identifiers to delete.

    Args:
        include_repo_state (bool): Include repo_state record if True.

    Returns:
        list[str]: Context identifiers.
    """
    names = [
        "context_profiles",
        "architecture_context",
        "component_contexts",
        "test_architecture_context",
        "test_component_contexts",
    ]
    if include_repo_state:
        names.append("repo_state")
    return names


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


def _context_profiles_lock_resource(branch_name: str) -> Path:
    """
    Build a synthetic lock resource path for context_profiles operations.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        Path: Resource path for context_profiles locks.
    """

    return Path(f"branch_context_profiles::{branch_name}")


def _repo_state_lock_resource(branch_name: str) -> Path:
    """
    Build a synthetic lock resource path for repo_state operations.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        Path: Resource path for repo_state locks.
    """

    return Path(f"branch_repo_state::{branch_name}")


def _architecture_context_lock_resource(branch_name: str, kind: str) -> Path:
    """
    Build a synthetic lock resource path for architecture context operations.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        Path: Resource path for architecture context locks.
    """

    return Path(f"branch_architecture_context::{branch_name}::{kind}")


def _component_contexts_lock_resource(branch_name: str, kind: str) -> Path:
    """
    Build a synthetic lock resource path for component context operations.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        Path: Resource path for component context locks.
    """

    return Path(f"branch_component_contexts::{branch_name}::{kind}")


def _delete_context_profiles(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Delete context_profiles records via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if context_profiles rows were deleted.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_CONTEXT_PROFILES,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("context_profiles delete returned an invalid deleted flag.")
    return deleted


def _delete_repo_state(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Delete repo_state records via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if repo_state rows were deleted.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_REPO_STATE,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("repo_state delete returned an invalid deleted flag.")
    return deleted


def _delete_architecture_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> bool:
    """
    Delete architecture_context records via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if architecture_context rows were deleted.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_ARCHITECTURE_CONTEXT,
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("architecture_context delete returned an invalid deleted flag.")
    return deleted


def _delete_component_contexts(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> bool:
    """
    Delete component_contexts records via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if component_contexts rows were deleted.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_COMPONENT_CONTEXTS,
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("component_contexts delete returned an invalid deleted flag.")
    return deleted


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
                action=BRANCH_REGISTRY_ACTION,
                payload={"record_id": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code in {"record_not_found", "db_missing"}:
            raise FileNotFoundError(f"Branch not registered: {branch_name}") from exc
        raise


def _delete_record(
    repo_root: Path,
    scope: str,
    table_name: str,
    record_id: str,
    actor_id: str,
) -> bool:
    """
    Delete a SQLite record using the branch-name action if it exists.

    Args:
        repo_root (Path): Repository root.
        scope (str): SQLite scope ("system" or "user").
        table_name (str): Target SQLite table name.
        record_id (str): Record identifier to delete (branch_name for branch_registry).
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if a record was deleted, False if not found.

    Raises:
        sqlite_crud.SqliteCrudError: If the delete operation fails.
    """

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="delete",
                scope=scope,
                table_name=table_name,
                action="by_branch_name",
                payload={"record_id": record_id},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_not_found":
            return False
        raise
    return True


def delete_context(
    repo_root: Path,
    branch_name: str,
    include_repo_state: bool,
    owner_id: str,
) -> dict:
    """
    Delete branch context records in SQLite for the branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        include_repo_state (bool): Delete repo_state record if True.
        owner_id (str): Lock owner id.

    Returns:
        dict: Summary of deleted context identifiers.
    """
    policies = _load_policies(repo_root, owner_id)
    _require_branch_registered(repo_root, branch_name, owner_id)
    resources: list[Path] = []
    for name in _context_ids(include_repo_state):
        if name == "repo_state":
            resources.append(_repo_state_lock_resource(branch_name))
        elif name == "context_profiles":
            resources.append(_context_profiles_lock_resource(branch_name))
        elif name in ("architecture_context", "test_architecture_context"):
            kind = name
            resources.append(_architecture_context_lock_resource(branch_name, kind))
        elif name in ("component_contexts", "test_component_contexts"):
            kind = name
            resources.append(_component_contexts_lock_resource(branch_name, kind))

    locked = _lock_entries(
        repo_root,
        resources,
        owner_id,
        ttl_seconds=int(policies["lease_ttl_seconds"]),
    )
    deleted: list[str] = []
    skipped: list[str] = []
    try:
        for name in _context_ids(include_repo_state):
            if name == "repo_state":
                if _delete_repo_state(repo_root, branch_name, owner_id):
                    deleted.append(name)
                else:
                    skipped.append(name)
            elif name == "context_profiles":
                if _delete_context_profiles(repo_root, branch_name, owner_id):
                    deleted.append(name)
                else:
                    skipped.append(name)
            elif name in ("architecture_context", "test_architecture_context"):
                kind = name
                if _delete_architecture_context(repo_root, branch_name, kind, owner_id):
                    deleted.append(name)
                else:
                    skipped.append(name)
            elif name in ("component_contexts", "test_component_contexts"):
                kind = name
                if _delete_component_contexts(repo_root, branch_name, kind, owner_id):
                    deleted.append(name)
                else:
                    skipped.append(name)
    finally:
        for resource in locked:
            lease.release_lock(repo_root, resource, owner_id)

    return {"deleted": deleted, "skipped": skipped}


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Delete branch context records using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing deleted and skipped context identifiers.

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
        include_repo_state = optional_bool(
            payload, "include_repo_state", command_name=command_name, default=False
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_work_mode(repo_root, work_id, "delete branch context state")
        summary = delete_context(
            repo_root=repo_root,
            branch_name=branch_name,
            include_repo_state=bool(include_repo_state),
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
    parser = argparse.ArgumentParser(description="Delete branch context records.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--branch-name", required=True, help="Branch name to modify")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument(
        "--include-repo-state",
        action="store_true",
        help="Also delete repo_state record",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "branch_name": args.branch_name,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "include_repo_state": args.include_repo_state,
    }
    context = ExecutionContext(
        command_name="branch_delete_context",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("branch_delete_context failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("deleted context records: %s", result.output.get("deleted"))


if __name__ == "__main__":
    main()
