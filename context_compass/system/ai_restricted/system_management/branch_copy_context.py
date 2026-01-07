"""
Copy context state records from one branch to another.

Purpose
- Copy SQLite-backed repo_state and context artifacts between branches.
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
BRANCH_REGISTRY_READ_ACTION = "by_branch_name"

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1

DEFAULT_LEASE_TTL_SECONDS = 300
DEFAULT_LOCK_WAIT_SECONDS = 10

REPO_STATE_TABLE = "repo_state"
REPO_STATE_ACTION = "by_branch_name"

QUERY_READ_CONTEXT_PROFILES = "read_context_profiles"
QUERY_WRITE_CONTEXT_PROFILES = "write_context_profiles"
QUERY_READ_ARCHITECTURE_CONTEXT = "read_architecture_context"
QUERY_WRITE_ARCHITECTURE_CONTEXT = "write_architecture_context"
QUERY_READ_COMPONENT_CONTEXTS = "read_component_contexts"
QUERY_WRITE_COMPONENT_CONTEXTS = "write_component_contexts"
QUERY_WRITE_REPO_STATE = "write_repo_state"


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
        sqlite_crud.SqliteCrudError: If policy lookup fails.
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


def _context_ids() -> list[str]:
    """
    Return branch context identifiers to copy.

    Returns:
        list[str]: Context identifiers.
    """
    return [
        "repo_state",
        "context_profiles",
        "architecture_context",
        "component_contexts",
        "test_architecture_context",
        "test_component_contexts",
    ]


def _reset_repo_state(payload: dict, repo_root: Path, now: str) -> dict:
    """
    Reset scan counters and timestamps to force a fresh scan.

    Args:
        payload (dict): Repo state payload.
        repo_root (Path): Repository root.
        now (str): Current timestamp.

    Returns:
        dict: Updated repo state payload.
    """
    updated = dict(payload)
    updated["repo_root"] = str(repo_root)
    updated["scan_counter"] = 0
    updated["last_scan_id"] = None
    updated["last_scan_at"] = None
    updated["scanner_version"] = None
    updated["updated_at"] = now
    return updated


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


def _crud_branch_registered(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Determine whether a branch_registry record exists via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if the branch is registered.

    Raises:
        sqlite_crud.SqliteCrudError: If the CRUD request fails unexpectedly.
    """

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=BRANCH_REGISTRY_TABLE,
                action=BRANCH_REGISTRY_READ_ACTION,
                payload={"record_id": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_not_found":
            return False
        raise
    return True


def _crud_read_repo_state(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read repo_state via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: repo_state payload and existence flag.

    Raises:
        ValueError: If the CRUD result payload is invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name=REPO_STATE_TABLE,
            action=REPO_STATE_ACTION,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("repo_state read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("repo_state read returned an invalid exists flag.")
    return record, exists


def _query_write_repo_state(
    repo_root: Path,
    branch_name: str,
    repo_state: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write repo_state via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        repo_state (dict): repo_state payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Returns:
        dict: Stored repo_state payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_WRITE_REPO_STATE,
            payload={
                "branch_name": branch_name,
                "repo_state": repo_state,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("repo_state write returned an invalid record payload.")
    return record


def _query_read_architecture_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read architecture_context payloads via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Context payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_ARCHITECTURE_CONTEXT,
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("architecture_context read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("architecture_context read returned an invalid exists flag.")
    return record, exists


def _query_write_architecture_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    context_payload: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write architecture_context payloads via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        context_payload (dict): Context payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Returns:
        dict: Stored architecture_context payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_WRITE_ARCHITECTURE_CONTEXT,
            payload={
                "branch_name": branch_name,
                "kind": kind,
                "context": context_payload,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("architecture_context write returned an invalid record payload.")
    return record


def _query_read_component_contexts(
    repo_root: Path,
    branch_name: str,
    kind: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read component_contexts payloads via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Context payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_COMPONENT_CONTEXTS,
            payload={"branch_name": branch_name, "kind": kind},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("component_contexts read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("component_contexts read returned an invalid exists flag.")
    return record, exists


def _query_write_component_contexts(
    repo_root: Path,
    branch_name: str,
    kind: str,
    context_payload: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write component_contexts payloads via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        context_payload (dict): Context payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Returns:
        dict: Stored component_contexts payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_WRITE_COMPONENT_CONTEXTS,
            payload={
                "branch_name": branch_name,
                "kind": kind,
                "context": context_payload,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("component_contexts write returned an invalid record payload.")
    return record

def _read_context_profiles(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read context_profiles payload via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Context profiles payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_CONTEXT_PROFILES,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("context_profiles read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("context_profiles read returned an invalid exists flag.")
    return record, exists


def _write_context_profiles(
    repo_root: Path,
    branch_name: str,
    context_profiles: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write context_profiles payload via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        context_profiles (dict): Context profiles payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Returns:
        dict: Stored context profiles payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_WRITE_CONTEXT_PROFILES,
            payload={
                "branch_name": branch_name,
                "context_profiles": context_profiles,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("context_profiles write returned an invalid record payload.")
    return record


def copy_context(
    repo_root: Path,
    source_branch: str,
    dest_branch: str,
    preserve_repo_state: bool,
    owner_id: str,
) -> dict:
    """
    Copy context records from a source branch to a destination branch.

    Args:
        repo_root (Path): Repository root.
        source_branch (str): Source branch name.
        dest_branch (str): Destination branch name.
        preserve_repo_state (bool): Whether to keep scan counters and timestamps.
        owner_id (str): Lock owner id.

    Returns:
        dict: Summary of copied context identifiers.
    """
    policies = _load_policies(repo_root, owner_id)
    now = utc_now_iso()
    if not _crud_branch_registered(repo_root, source_branch, owner_id):
        raise FileNotFoundError(f"Source branch not registered: {source_branch}")
    if not _crud_branch_registered(repo_root, dest_branch, owner_id):
        raise FileNotFoundError(f"Destination branch not registered: {dest_branch}")

    resources: list[Path] = []
    for name in _context_ids():
        if name == "repo_state":
            resources.append(_repo_state_lock_resource(source_branch))
            resources.append(_repo_state_lock_resource(dest_branch))
        elif name == "context_profiles":
            resources.append(_context_profiles_lock_resource(source_branch))
            resources.append(_context_profiles_lock_resource(dest_branch))
        elif name in ("architecture_context", "test_architecture_context"):
            kind = name
            resources.append(_architecture_context_lock_resource(source_branch, kind))
            resources.append(_architecture_context_lock_resource(dest_branch, kind))
        elif name in ("component_contexts", "test_component_contexts"):
            kind = name
            resources.append(_component_contexts_lock_resource(source_branch, kind))
            resources.append(_component_contexts_lock_resource(dest_branch, kind))

    locked = _lock_entries(
        repo_root,
        resources,
        owner_id,
        ttl_seconds=int(policies["lease_ttl_seconds"]),
    )
    copied: list[str] = []
    skipped: list[str] = []
    try:
        for name in _context_ids():
            if name == "repo_state":
                source_record, source_exists = _crud_read_repo_state(
                    repo_root, source_branch, actor_id=owner_id
                )
                if not source_exists:
                    skipped.append(name)
                    continue
                _, dest_exists = _crud_read_repo_state(
                    repo_root, dest_branch, actor_id=owner_id
                )
                payload = source_record
                if not preserve_repo_state:
                    payload = _reset_repo_state(payload, repo_root, now)
                _query_write_repo_state(
                    repo_root,
                    dest_branch,
                    payload,
                    actor_id=owner_id,
                    exists=dest_exists,
                )
                copied.append(name)
            elif name == "context_profiles":
                source_record, source_exists = _read_context_profiles(
                    repo_root, source_branch, actor_id=owner_id
                )
                if not source_exists:
                    skipped.append(name)
                    continue
                _, dest_exists = _read_context_profiles(
                    repo_root, dest_branch, actor_id=owner_id
                )
                _write_context_profiles(
                    repo_root,
                    dest_branch,
                    source_record,
                    actor_id=owner_id,
                    exists=dest_exists,
                )
                copied.append(name)
            elif name in ("architecture_context", "test_architecture_context"):
                kind = name
                source_record, source_exists = _query_read_architecture_context(
                    repo_root, source_branch, kind, actor_id=owner_id
                )
                if not source_exists:
                    skipped.append(name)
                    continue
                _, dest_exists = _query_read_architecture_context(
                    repo_root, dest_branch, kind, actor_id=owner_id
                )
                _query_write_architecture_context(
                    repo_root,
                    dest_branch,
                    kind,
                    source_record,
                    actor_id=owner_id,
                    exists=dest_exists,
                )
                copied.append(name)
            elif name in ("component_contexts", "test_component_contexts"):
                kind = name
                source_record, source_exists = _query_read_component_contexts(
                    repo_root, source_branch, kind, actor_id=owner_id
                )
                if not source_exists:
                    skipped.append(name)
                    continue
                _, dest_exists = _query_read_component_contexts(
                    repo_root, dest_branch, kind, actor_id=owner_id
                )
                _query_write_component_contexts(
                    repo_root,
                    dest_branch,
                    kind,
                    source_record,
                    actor_id=owner_id,
                    exists=dest_exists,
                )
                copied.append(name)
    finally:
        for resource in locked:
            lease.release_lock(repo_root, resource, owner_id)

    return {"copied": copied, "skipped": skipped}


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Copy context records using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing copied and skipped context identifiers.

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
        preserve_repo_state = optional_bool(
            payload, "preserve_repo_state", command_name=command_name, default=False
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_work_mode(repo_root, work_id, "copy branch context state")
        summary = copy_context(
            repo_root=repo_root,
            source_branch=source_branch,
            dest_branch=dest_branch,
            preserve_repo_state=bool(preserve_repo_state),
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
    parser = argparse.ArgumentParser(description="Copy branch context state records.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--source-branch", required=True, help="Source branch name")
    parser.add_argument("--dest-branch", required=True, help="Destination branch name")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument(
        "--preserve-repo-state",
        action="store_true",
        help="Preserve repo_state scan counters and timestamps",
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
        "preserve_repo_state": args.preserve_repo_state,
    }
    context = ExecutionContext(
        command_name="branch_copy_context",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("branch_copy_context failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("copied context records: %s", result.output.get("copied"))


if __name__ == "__main__":
    main()
