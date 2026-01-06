"""Manage context_compass agent lifecycle (create, archive, delete)."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable

from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import (
    agent_careers,
    agent_presence,
    agent_profile_store,
    self_context_store,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_list,
    optional_string,
    require_choice,
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
AGENT_WORK_QUEUE_SCHEMA_VERSION = 1
CRUD_AGENT_WORK_QUEUE_TABLE = "agent_work_queue"
CRUD_AGENT_WORK_QUEUE_ACTION = "ensure_queue"
QUERY_READ_AGENT_PROFILE = "read_agent_profile"
QUERY_WRITE_AGENT_PROFILE = "write_agent_profile"
QUERY_READ_SELF_CONTEXT = "read_self_context"
QUERY_WRITE_SELF_CONTEXT = "write_self_context"
QUERY_DELETE_AGENT_RECORDS = "delete_agent_records"


def _default_policies() -> dict:
    """
    Return default policy values used by agent management.

    Returns:
        dict: Default policy values for lease TTL.
    """
    return {"lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS}


def _load_policies(repo_root: Path, actor_id: str) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Effective policies for lease TTL.

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
    if isinstance(lease_ttl, int):
        defaults["lease_ttl_seconds"] = lease_ttl
    return defaults


def _load_careers(repo_root: Path) -> list[str]:
    """
    Load available careers from onboarding content.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Sorted list of valid careers.

    Raises:
        ValueError: If career discovery fails.
    """

    return agent_careers.list_careers(repo_root)


def _validate_career_choice(command_name: str, career: str, careers: list[str]) -> str:
    """
    Validate a career choice against the available careers list.

    Args:
        command_name (str): Command name for error context.
        career (str): Career value to validate.
        careers (list[str]): Allowed career values.

    Returns:
        str: Validated career value.

    Raises:
        PayloadError: If the career is not an allowed value.
    """

    if career not in careers:
        raise PayloadError(
            code="payload_value_error",
            details={
                "command_name": command_name,
                "field": "agent_role",
                "expected": f"one of {careers}",
                "actual": career,
            },
        )
    return career


def _resolve_agent_role(
    repo_root: Path,
    agent_id: str,
    actor_id: str,
    command_name: str,
    action: str,
    agent_role: str | None,
    careers: list[str],
) -> str:
    """
    Resolve the agent career for lifecycle operations.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.
        command_name (str): Command name for error context.
        action (str): Lifecycle action (create/archive/delete).
        agent_role (str | None): Optional career label from payload.
        careers (list[str]): Allowed career values.

    Returns:
        str: Resolved career label.

    Raises:
        PayloadError: If the career is missing or invalid.
        ValueError: If the agent profile read returns an invalid payload.
        sqlite_query.SqliteQueryError: If the profile lookup fails.
    """

    if action == "create":
        if agent_role is None:
            raise PayloadError(
                code="payload_missing",
                details={
                    "command_name": command_name,
                    "field": "agent_role",
                    "expected": f"one of {careers}",
                },
            )
        return _validate_career_choice(command_name, agent_role, careers)

    if agent_role is not None:
        return _validate_career_choice(command_name, agent_role, careers)

    profile, exists = _read_agent_profile(repo_root, agent_id, actor_id)
    if not exists:
        raise PayloadError(
            code="payload_missing",
            details={
                "command_name": command_name,
                "field": "agent_role",
                "expected": f"one of {careers}",
                "detail": "agent profile missing; create with a career first",
            },
        )
    stored_role = profile.get("agent_role")
    if not isinstance(stored_role, str) or not stored_role.strip():
        raise PayloadError(
            code="payload_type_error",
            details={
                "command_name": command_name,
                "field": "agent_role",
                "expected": "non-empty string",
                "actual_type": type(stored_role).__name__,
            },
        )
    return _validate_career_choice(command_name, stored_role, careers)


def _acquire_locks(repo_root: Path, resources: Iterable[Path], owner_id: str, ttl_seconds: int) -> list[Path]:
    """
    Acquire locks for a set of resources in deterministic order.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resources (Iterable[Path]): Resources to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL in seconds.

    Returns:
        list[Path]: Resources locked.
    """
    lock_targets: list[tuple[str, Path]] = []
    for resource in resources:
        lock_key = lease.lock_path_for(repo_root, resource)
        lock_targets.append((str(lock_key), resource))
    lock_targets.sort(key=lambda item: item[0])
    locked: list[Path] = []
    for _, resource in lock_targets:
        lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds)
        locked.append(resource)
    return locked


def _release_locks(repo_root: Path, resources: Iterable[Path], owner_id: str) -> None:
    """
    Release locks for a set of resources in reverse order.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resources (Iterable[Path]): Resources to unlock.
        owner_id (str): Lock owner id.
    """
    for resource in reversed(list(resources)):
        lease.release_lock(repo_root, resource, owner_id)


def _agent_profile_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for an agent profile.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"agent_profile::{agent_id}")


def _self_context_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for a self-context record.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"self_context::{agent_id}")


def _agent_work_queue_lock_resource(agent_id: str) -> Path:
    """
    Build a synthetic lock resource path for an agent work queue.

    Args:
        agent_id (str): Agent identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"agent_work::{agent_id}")


def _read_agent_profile(repo_root: Path, agent_id: str, actor_id: str) -> tuple[dict, bool]:
    """
    Read an agent profile payload via the SQLite query API.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Agent profile payload and existence flag.

    Raises:
        ValueError: If the query returns an invalid payload structure.
        sqlite_query.SqliteQueryError: If the query execution fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_AGENT_PROFILE,
            payload={"agent_id": agent_id},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("agent_profile read returned an invalid result payload.")
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("agent_profile read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("agent_profile read returned an invalid exists flag.")
    return record, exists


def _write_agent_profile(
    repo_root: Path,
    agent_id: str,
    profile: dict,
    actor_id: str,
    exists: bool,
) -> None:
    """
    Persist an agent profile payload via the SQLite query API.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        profile (dict): Agent profile payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the profile already exists.

    Raises:
        ValueError: If the query returns an invalid payload structure.
        sqlite_query.SqliteQueryError: If the query execution fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_WRITE_AGENT_PROFILE,
            payload={
                "agent_id": agent_id,
                "agent_profile": profile,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("agent_profile write returned an invalid result payload.")
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("agent_profile write returned an invalid record payload.")


def _ensure_agent_profile(repo_root: Path, agent_id: str, actor_id: str, agent_role: str) -> None:
    """
    Ensure an agent profile payload exists for an agent_id.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.
        agent_role (str): Career label to store on creation.
    """

    profile, exists = _read_agent_profile(repo_root, agent_id, actor_id)
    if exists:
        return
    now = utc_now_iso()
    default_profile = agent_profile_store.default_profile(agent_id, now, agent_role=agent_role)
    _write_agent_profile(repo_root, agent_id, default_profile, actor_id, exists=False)


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
    Ensure a self_context payload exists for an agent_id.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.
    """

    _, exists = _read_self_context(repo_root, agent_id, actor_id)
    if exists:
        return
    now = utc_now_iso()
    default_payload = self_context_store.default_self_context(agent_id, now)
    _write_self_context(repo_root, agent_id, default_payload, actor_id, exists=False)


def _ensure_agent_work_queue(repo_root: Path, agent_id: str, owner_id: str) -> None:
    """
    Ensure the per-agent work queue record exists in SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        owner_id (str): Actor identifier for audit logging.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="create",
            scope="user",
            table_name=CRUD_AGENT_WORK_QUEUE_TABLE,
            action=CRUD_AGENT_WORK_QUEUE_ACTION,
            payload={
                "agent_id": agent_id,
                "schema_version": AGENT_WORK_QUEUE_SCHEMA_VERSION,
            },
            actor_id=owner_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("agent_work_queue create returned an invalid result payload.")
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("agent_work_queue create returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("agent_work_queue create returned an invalid exists flag.")


def _delete_agent_records(repo_root: Path, agent_id: str, actor_id: str) -> dict:
    """
    Delete agent-scoped rows via the SQLite query API.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Deleted row counts by table name.

    Raises:
        ValueError: If the query returns an invalid payload structure.
        sqlite_query.SqliteQueryError: If the query execution fails.

    Contract:
        - Returns per-table delete counts for reporting.
        - Leaves detailed deletion logic to the query script implementation.
    """
    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_AGENT_RECORDS,
            payload={"agent_id": agent_id},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result")
    if not isinstance(result, dict):
        raise ValueError("delete_agent_records returned an invalid result payload.")
    deleted = result.get("deleted")
    if not isinstance(deleted, dict):
        raise ValueError("delete_agent_records returned invalid delete counts.")
    return deleted


def create_agent(repo_root: Path, agent_id: str, owner_id: str, agent_role: str) -> None:
    """
    Create per-agent self-context, work queue, and profile records in SQLite.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        owner_id (str): Lock owner id.
        agent_role (str): Career label to store on creation.
    """
    policies = _load_policies(repo_root, owner_id)
    locked = _acquire_locks(
        repo_root,
        [
            _self_context_lock_resource(agent_id),
            _agent_work_queue_lock_resource(agent_id),
            _agent_profile_lock_resource(agent_id),
        ],
        owner_id,
        policies["lease_ttl_seconds"],
    )
    try:
        _ensure_self_context(repo_root, agent_id, owner_id)
        _ensure_agent_work_queue(repo_root, agent_id, owner_id)
        _ensure_agent_profile(repo_root, agent_id, owner_id, agent_role)
    finally:
        _release_locks(repo_root, locked, owner_id)


def delete_agent(repo_root: Path, agent_id: str, owner_id: str) -> None:
    """
    Delete per-agent SQLite records from static tables.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        owner_id (str): Lock owner id.
    """
    policies = _load_policies(repo_root, owner_id)
    locked = _acquire_locks(
        repo_root,
        [
            _self_context_lock_resource(agent_id),
            _agent_work_queue_lock_resource(agent_id),
            _agent_profile_lock_resource(agent_id),
        ],
        owner_id,
        policies["lease_ttl_seconds"],
    )
    try:
        _delete_agent_records(repo_root, agent_id, owner_id)
    finally:
        _release_locks(repo_root, locked, owner_id)


def archive_agent(repo_root: Path, agent_id: str, owner_id: str) -> None:
    """
    Archive per-agent SQLite records without writing JSON snapshots.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        owner_id (str): Lock owner id.

    Contract:
        - Removes agent-scoped rows from SQLite tables.
        - Does not write JSON archives to disk.
    """
    policies = _load_policies(repo_root, owner_id)
    locked = _acquire_locks(
        repo_root,
        [
            _self_context_lock_resource(agent_id),
            _agent_work_queue_lock_resource(agent_id),
            _agent_profile_lock_resource(agent_id),
        ],
        owner_id,
        policies["lease_ttl_seconds"],
    )
    try:
        _delete_agent_records(repo_root, agent_id, owner_id)
    finally:
        _release_locks(repo_root, locked, owner_id)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Manage agent lifecycle using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the action and agent id.

    Raises:
        None: All errors are returned as CommandResult payloads.

    Contract:
        - Requires agent_id and action in the payload.
        - action must be create, archive, or delete.
        - create requires agent_role to be one of the available careers.
        - Records lifecycle updates on the acting agent profile.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        owner_id = optional_string(payload, "owner_id", command_name=command_name)
        agent_role = optional_string(payload, "agent_role", command_name=command_name)
        action = require_choice(payload, "action", command_name, ["create", "archive", "delete"])
        command_args = optional_list(payload, "command_args", command_name=command_name)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    lock_owner = owner_id or agent_id
    try:
        careers = _load_careers(repo_root)
        agent_role = _resolve_agent_role(
            repo_root,
            agent_id,
            lock_owner,
            command_name,
            action,
            agent_role,
            careers,
        )
        ensure_certified(repo_root, lock_owner)
        agent_presence.record_lifecycle_update(
            repo_root,
            agent_id=lock_owner,
            agent_role=agent_role,
            current_task_id=None,
            current_target=None,
            notes=None,
            command_name=command_name,
            command_args=[str(arg) for arg in command_args] if command_args else None,
        )
        if action == "create":
            create_agent(repo_root, agent_id, lock_owner, agent_role)
        elif action == "delete":
            delete_agent(repo_root, agent_id, lock_owner)
        elif action == "archive":
            archive_agent(repo_root, agent_id, lock_owner)
    except Exception as exc:
        return exception_result(
            command_name,
            exc,
            details={"agent_id": agent_id, "action": action, "owner_id": lock_owner},
        )

    return ok_result(output={"agent_id": agent_id, "action": action})


def main() -> None:
    """
    CLI entrypoint for agent lifecycle management.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Manage context_compass agent lifecycle")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--owner-id", help="Lock owner id (defaults to agent-id)")
    parser.add_argument(
        "--agent-role",
        default=None,
        help="Career label for the agent (developer/analyst/project_manager)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("create", help="Create agent records")
    subparsers.add_parser("delete", help="Delete agent records")
    subparsers.add_parser("archive", help="Archive agent records")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "owner_id": args.owner_id,
        "agent_role": args.agent_role,
        "action": args.command,
        "command_args": sys.argv[1:],
    }
    context = ExecutionContext(
        command_name="agent_manage",
        agent_id=args.agent_id,
        work_id=None,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("agent_manage failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("agent %s: %s", result.output.get("action"), result.output.get("agent_id"))


if __name__ == "__main__":
    main()
