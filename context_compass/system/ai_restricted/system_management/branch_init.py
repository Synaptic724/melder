"""
Initialize branch-scoped state and work queues in SQLite.

Purpose
- Register branches in the system database.
- Seed branch-scoped SQLite records for repo state, context, and queues.
- Update the active branch pointer for the user scope.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

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
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)


BRANCH_REGISTRY_TABLE = "branch_registry"
BRANCH_REGISTRY_CREATE_ACTION = "register_branch"
BRANCH_REGISTRY_READ_ACTION = "by_branch_name"
BRANCH_REGISTRY_UPDATE_ACTION = "by_branch_name"

CURRENT_BRANCH_TABLE = "current_branch"
CURRENT_BRANCH_ACTION = "set_current_branch"
CURRENT_BRANCH_RECORD_ID = "current"

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1

REPO_STATE_TABLE = "repo_state"
REPO_STATE_ACTION = "by_branch_name"

QUERY_READ_CONTEXT_PROFILES = "read_context_profiles"
QUERY_WRITE_CONTEXT_PROFILES = "write_context_profiles"
QUERY_READ_ARCHITECTURE_CONTEXT = "read_architecture_context"
QUERY_WRITE_ARCHITECTURE_CONTEXT = "write_architecture_context"
QUERY_READ_COMPONENT_CONTEXTS = "read_component_contexts"
QUERY_WRITE_COMPONENT_CONTEXTS = "write_component_contexts"
QUERY_READ_BRANCH_WORK_QUEUE = "read_branch_work_queue"
QUERY_WRITE_BRANCH_WORK_QUEUE = "write_branch_work_queue"
QUERY_WRITE_REPO_STATE = "write_repo_state"


def _default_context_profile_limits() -> dict:
    """
    Return default context profile limits.

    Returns:
        dict: Default limits for context profiles.
    """
    return {"max_items_per_profile": 25, "max_bytes_per_profile": 120000}


def _default_context_profiles(now: str, limits: dict) -> dict:
    """
    Return a default context_profiles payload.

    Args:
        now (str): Current timestamp.
        limits (dict): Limits payload.

    Returns:
        dict: Default context profiles payload.
    """
    return {
        "schema_version": 1,
        "updated_at": now,
        "rules_version": "context_profiles@v1",
        "limits": limits,
        "profiles": [],
    }


def _load_limits(repo_root: Path, actor_id: str) -> dict:
    """
    Load context profile limits from policy configuration.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Limits payload.

    Raises:
        ValueError: If policy values are invalid.
        sqlite_crud.SqliteCrudError: If the policy lookup fails.
    """
    limits = _default_context_profile_limits()
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
    max_items = record.get("context_profiles_max_items_per_profile")
    max_bytes = record.get("context_profiles_max_bytes_per_profile")
    if isinstance(max_items, int):
        limits["max_items_per_profile"] = max_items
    if isinstance(max_bytes, int):
        limits["max_bytes_per_profile"] = max_bytes
    return limits


def _queue_buckets() -> tuple[str, ...]:
    """
    Return the canonical work queue bucket names.

    Returns:
        tuple[str, ...]: Bucket identifiers in stable order.
    """

    return ("ready", "active", "backlog", "completed", "denied")


def _queue_kinds() -> tuple[str, ...]:
    """
    Return the canonical work queue kinds.

    Returns:
        tuple[str, ...]: Work item kind identifiers.
    """

    return ("epic", "story", "task")


def _crud_branch_registered(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Determine whether a branch_registry record exists.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if the branch is registered in system scope.

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


def _crud_register_branch(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Create a branch_registry record via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="create",
            scope="system",
            table_name=BRANCH_REGISTRY_TABLE,
            action=BRANCH_REGISTRY_CREATE_ACTION,
            payload={
                "record_id": branch_name,
                "branch_name": branch_name,
                "schema_version": 1,
                "status": "active",
                "notes": None,
            },
            actor_id=actor_id,
        ),
    )


def _crud_update_branch(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Update a branch_registry record via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="update",
            scope="system",
            table_name=BRANCH_REGISTRY_TABLE,
            action=BRANCH_REGISTRY_UPDATE_ACTION,
            payload={
                "record_id": branch_name,
                "schema_version": 1,
                "status": "active",
                "notes": None,
            },
            actor_id=actor_id,
        ),
    )


def _crud_set_current_branch(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Set the active branch pointer via sqlite_crud.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Raises:
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="update",
            scope="user",
            table_name=CURRENT_BRANCH_TABLE,
            action=CURRENT_BRANCH_ACTION,
            payload={
                "record_id": CURRENT_BRANCH_RECORD_ID,
                "branch_name": branch_name,
                "notes": None,
            },
            actor_id=actor_id,
        ),
    )


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
        kind (str): Context kind (architecture_context/test_architecture_context).
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
        kind (str): Context kind (architecture_context/test_architecture_context).
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
        kind (str): Context kind (component_contexts/test_component_contexts).
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
        kind (str): Context kind (component_contexts/test_component_contexts).
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


def _query_read_branch_work_queue(
    repo_root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read branch work queue payloads via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        bucket (str): Queue bucket name.
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
    queue_payload = result.get("queue")
    exists = result.get("exists")
    if not isinstance(queue_payload, dict):
        raise ValueError("branch work queue read returned an invalid queue payload.")
    if not isinstance(exists, bool):
        raise ValueError("branch work queue read returned an invalid exists flag.")
    return queue_payload, exists


def _query_write_branch_work_queue(
    repo_root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    queue_payload: dict,
    actor_id: str,
    exists: bool,
) -> None:
    """
    Write branch work queue payloads via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        bucket (str): Queue bucket name.
        work_type (str): Work type name.
        queue_payload (dict): Queue payload.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

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


def _seed_branch_repo_state(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Seed repo_state in SQLite for a branch if missing.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: This function writes the repo_state record when absent.
    """

    record, exists = _crud_read_repo_state(repo_root, branch_name, actor_id)
    if exists:
        return
    _query_write_repo_state(
        repo_root,
        branch_name,
        record,
        actor_id,
        exists=exists,
    )


def _seed_context_profiles(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Seed context_profiles in SQLite for a branch if missing.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: This function writes the context_profiles record when absent.
    """

    record, exists = _read_context_profiles(repo_root, branch_name, actor_id)
    if exists:
        return
    limits = _load_limits(repo_root, actor_id)
    payload = _default_context_profiles(utc_now_iso(), limits)
    _write_context_profiles(repo_root, branch_name, payload, actor_id, exists=exists)


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


def _seed_architecture_contexts(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Seed architecture context records in SQLite for a branch if missing.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: This function writes missing architecture context records.
    """

    for kind in ("architecture_context", "test_architecture_context"):
        record, exists = _query_read_architecture_context(
            repo_root,
            branch_name,
            kind,
            actor_id,
        )
        if exists:
            continue
        _query_write_architecture_context(
            repo_root,
            branch_name,
            kind,
            record,
            actor_id,
            exists=exists,
        )


def _seed_component_contexts(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Seed component context records in SQLite for a branch if missing.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: This function writes missing component context records.
    """

    for kind in ("component_contexts", "test_component_contexts"):
        record, exists = _query_read_component_contexts(
            repo_root,
            branch_name,
            kind,
            actor_id,
        )
        if exists:
            continue
        _query_write_component_contexts(
            repo_root,
            branch_name,
            kind,
            record,
            actor_id,
            exists=exists,
        )


def _seed_branch_queues(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Seed empty branch work queues in SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: This function writes empty queues for each bucket/kind.
    """

    for bucket in _queue_buckets():
        for work_type in _queue_kinds():
            queue_payload, exists = _query_read_branch_work_queue(
                repo_root,
                branch_name,
                bucket,
                work_type,
                actor_id,
            )
            _query_write_branch_work_queue(
                repo_root,
                branch_name,
                bucket,
                work_type,
                queue_payload,
                actor_id,
                exists=exists,
            )


def init_branch(
    repo_root: Path,
    branch_name: str,
    agent_id: str,
    work_id: Optional[str],
) -> None:
    """
    Initialize a branch in SQLite and mark it as active.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        agent_id (str): Agent id for certification checks.
        work_id (Optional[str]): Work id for work_mode enforcement.

    Contract:
        - Registers the branch in the system branch registry.
        - Seeds SQLite records for repo state, contexts, and work queues.
        - Updates the active branch pointer in the user database.
    """
    ensure_certified(repo_root, agent_id)
    ensure_work_mode(repo_root, work_id, "initialize branch management state")
    actor_id = f"agent:{agent_id}"
    if _crud_branch_registered(repo_root, branch_name, actor_id):
        _crud_update_branch(repo_root, branch_name, actor_id)
    else:
        _crud_register_branch(repo_root, branch_name, actor_id)
    _crud_set_current_branch(repo_root, branch_name, actor_id)
    _seed_branch_repo_state(repo_root, branch_name, actor_id)
    _seed_context_profiles(repo_root, branch_name, actor_id)
    _seed_architecture_contexts(repo_root, branch_name, actor_id)
    _seed_component_contexts(repo_root, branch_name, actor_id)
    _seed_branch_queues(repo_root, branch_name, actor_id)


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Initialize branch state using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the initialized branch name.

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
        init_branch(
            repo_root=repo_root,
            branch_name=branch_name,
            agent_id=agent_id,
            work_id=work_id,
        )
        return ok_result(output={"branch_name": branch_name})
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
    parser = argparse.ArgumentParser(description="Initialize branch-scoped context_compass state.")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--branch-name", required=True, help="Branch name to initialize.")
    parser.add_argument("--agent-id", required=True, help="Agent id for certification checks.")
    parser.add_argument("--work-id", default=None, help="Work id for hard work_mode enforcement.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    payload = {
        "repo_root": args.repo_root,
        "branch_name": args.branch_name,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
    }
    context = ExecutionContext(
        command_name="branch_init",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logging.getLogger(__name__).error("branch_init failed: %s", result.errors)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
