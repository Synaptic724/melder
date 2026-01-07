"""
Hard-delete a branch from SQLite and clear its branch-scoped state.

Purpose
- Remove branch-scoped rows from shared SQLite tables and the branch registry record.
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
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management import sqlite_query
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


BRANCH_DELETE_RESOURCE_PREFIX = "branch_delete"
BRANCH_REGISTRY_TABLE = "branch_registry"
BRANCH_REGISTRY_ACTION = "by_branch_name"

CURRENT_BRANCH_TABLE = "current_branch"
CURRENT_BRANCH_ACTION = "by_record_id"
CURRENT_BRANCH_RECORD_ID = "current"

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1

QUERY_DELETE_CONTEXT_PROFILES = "delete_context_profiles"
QUERY_DELETE_REPO_STATE = "delete_repo_state"
QUERY_DELETE_ARCHITECTURE_CONTEXT = "delete_architecture_context"
QUERY_DELETE_COMPONENT_CONTEXTS = "delete_component_contexts"
QUERY_DELETE_FILE_CTX = "delete_file_ctx_by_branch"
QUERY_DELETE_DIR_CTX = "delete_dir_ctx_by_branch"
QUERY_DELETE_BRANCH_WORK_QUEUES = "delete_branch_work_queues"
QUERY_DELETE_SCAN_RECORDS = "delete_scan_records_by_branch"
QUERY_DELETE_SCAN_ERROR_RECORDS = "delete_scan_error_records_by_branch"

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


def _lock_resource(branch_name: str) -> Path:
    """
    Build the synthetic lock resource path for branch delete operations.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"{BRANCH_DELETE_RESOURCE_PREFIX}::{branch_name}")


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


def _read_current_branch(repo_root: Path, actor_id: str) -> str | None:
    """
    Read the current branch pointer from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        str | None: Current branch name, or None if not set.

    Raises:
        sqlite_crud.SqliteCrudError: If the CRUD request fails unexpectedly.
        ValueError: If the CRUD response payload is invalid.
    """

    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="user",
                table_name=CURRENT_BRANCH_TABLE,
                action=CURRENT_BRANCH_ACTION,
                payload={"record_id": CURRENT_BRANCH_RECORD_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code in {"record_not_found", "db_missing"}:
            return None
        raise

    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("current_branch read returned an invalid record payload.")
    branch_name = record.get("branch_name")
    if branch_name is None:
        return None
    if not isinstance(branch_name, str):
        raise ValueError("current_branch record contains an invalid branch_name.")
    return branch_name


def _delete_branch_ctx_rows(repo_root: Path, branch_name: str, actor_id: str) -> dict:
    """
    Delete branch-scoped rows from shared ctx tables and repo_state.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Summary containing deleted and skipped ctx records.
    """

    deleted: list[str] = []
    skipped: list[str] = []

    if _delete_repo_state(repo_root, branch_name, actor_id):
        deleted.append("repo_state")
    else:
        skipped.append("repo_state")

    if _delete_context_profiles(repo_root, branch_name, actor_id):
        deleted.append("context_profiles")
    else:
        skipped.append("context_profiles")

    if _delete_file_ctx(repo_root, branch_name, actor_id):
        deleted.append("file_ctx")
    else:
        skipped.append("file_ctx")
    if _delete_dir_ctx(repo_root, branch_name, actor_id):
        deleted.append("dir_ctx")
    else:
        skipped.append("dir_ctx")

    for kind in ("architecture_context", "test_architecture_context"):
        if _delete_architecture_context(repo_root, branch_name, kind, actor_id):
            deleted.append(kind)
        else:
            skipped.append(kind)
    for kind in ("component_contexts", "test_component_contexts"):
        if _delete_component_contexts(repo_root, branch_name, kind, actor_id):
            deleted.append(kind)
        else:
            skipped.append(kind)

    return {"deleted": deleted, "skipped": skipped}


def _delete_context_profiles(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Delete context_profiles rows via sqlite_query.

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
    Delete repo_state rows via sqlite_query.

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
    Delete architecture_context rows via sqlite_query.

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
    Delete component_contexts rows via sqlite_query.

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


def _delete_file_ctx(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Delete file_ctx rows via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if file_ctx rows were deleted.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_FILE_CTX,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("file_ctx delete returned an invalid deleted flag.")
    return deleted


def _delete_dir_ctx(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Delete dir_ctx rows via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if dir_ctx rows were deleted.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_DIR_CTX,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    deleted = result.get("deleted")
    if not isinstance(deleted, bool):
        raise ValueError("dir_ctx delete returned an invalid deleted flag.")
    return deleted


def _delete_branch_work_queues(repo_root: Path, branch_name: str, actor_id: str) -> list[str]:
    """
    Delete branch work queues from shared queue tables.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[str]: Queue ids removed for the branch.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_BRANCH_WORK_QUEUES,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    queue_ids = result.get("queue_ids")
    if not isinstance(queue_ids, list) or not all(
        isinstance(entry, str) for entry in queue_ids
    ):
        raise ValueError("branch_work_queues delete returned invalid queue_ids.")
    return queue_ids


def _delete_branch_scan_rows(repo_root: Path, branch_name: str, actor_id: str) -> dict:
    """
    Delete branch-scoped scan records from shared scan tables.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Summary containing deleted scan row groups.
    """

    deleted: list[str] = []
    _delete_scan_records(repo_root, branch_name, actor_id)
    deleted.append("scan_registry")
    _delete_scan_error_records(repo_root, branch_name, actor_id)
    deleted.append("scan_error_records")
    return {"deleted": deleted}


def _delete_scan_records(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Delete scan records for a branch via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: Raises on query failure.

    Raises:
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_SCAN_RECORDS,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )


def _delete_scan_error_records(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Delete scan error records for a branch via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: Raises on query failure.

    Raises:
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_DELETE_SCAN_ERROR_RECORDS,
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )


def _remove_branch_registry_record(repo_root: Path, branch_name: str, actor_id: str) -> bool:
    """
    Remove the branch registry record in the system database.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        bool: True if the registry record was removed.

    Raises:
        sqlite_crud.SqliteCrudError: If the delete operation fails.
    """

    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="delete",
                scope="system",
                table_name=BRANCH_REGISTRY_TABLE,
                action=BRANCH_REGISTRY_ACTION,
                payload={"record_id": branch_name},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        if exc.code == "record_not_found":
            return False
        raise
    return True


def delete_branch(
    repo_root: Path,
    branch_name: str,
    owner_id: str,
) -> dict:
    """
    Hard-delete a branch by removing branch-scoped rows and registry entries.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        owner_id (str): Actor identifier for audit logging and locks.

    Returns:
        dict: Summary including removed queue ids, ctx deletions, and lock cleanup.

    Raises:
        FileNotFoundError: If the branch is not registered or databases are missing.
        RuntimeError: If attempting to delete the active branch.
        sqlite_crud.SqliteCrudError: If registry removal fails.

    Contract:
        - The active branch cannot be deleted.
        - Branch work queues are deleted from shared work queue tables.
        - Shared ctx rows (repo_state/context_profiles/file_ctx/dir_ctx/architecture/component) are deleted.
        - Shared scan/error rows are deleted for the branch.
        - Branch registry entries are removed from system.db.
    """

    policies = _load_policies(repo_root, owner_id)
    _require_branch_registered(repo_root, branch_name, owner_id)

    active_branch = _read_current_branch(repo_root, owner_id)
    if active_branch == branch_name:
        raise RuntimeError("Cannot delete the active branch; switch branches first.")

    resource = _lock_resource(branch_name)
    lease.acquire_lock(
        repo_root,
        resource,
        owner_id,
        ttl_seconds=int(policies["lease_ttl_seconds"]),
    )
    try:
        work_queue_ids = _delete_branch_work_queues(repo_root, branch_name, owner_id)
        ctx_summary = _delete_branch_ctx_rows(repo_root, branch_name, owner_id)
        scan_summary = _delete_branch_scan_rows(repo_root, branch_name, owner_id)
        registry_removed = _remove_branch_registry_record(repo_root, branch_name, owner_id)
    finally:
        lease.release_lock(repo_root, resource, owner_id)

    return {
        "branch_name": branch_name,
        "work_queues_deleted": work_queue_ids,
        "ctx_rows_deleted": ctx_summary["deleted"],
        "ctx_rows_skipped": ctx_summary["skipped"],
        "scan_rows_deleted": scan_summary["deleted"],
        "branch_registry_deleted": registry_removed,
    }


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Hard-delete a branch using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing delete summary data.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id and branch_name.
        - Enforces certification and work mode guards.
        - Deletes branch-scoped work queues from shared tables.
        - Deletes scan/error rows stored in shared scan tables.
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
        ensure_work_mode(repo_root, work_id, "delete branch")
        summary = delete_branch(
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

    parser = argparse.ArgumentParser(
        description="Hard-delete a branch (remove branch-scoped rows and registry records)."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--branch-name", required=True, help="Branch name to delete")
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
        command_name="branch_delete",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("branch_delete failed: %s", result.errors)
        raise SystemExit(1)
    logger.info("branch_delete completed: %s", result.output.get("branch_name"))


if __name__ == "__main__":
    main()
