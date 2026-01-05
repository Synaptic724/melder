"""
context_compass.system.ai_restricted.scan

Repository scanner for ctx staleness detection and task emission.
"""

import argparse
import logging
import os
import time
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import lease, update_state
from context_compass.system.ai_restricted._shared import architecture_contexts, branch_paths
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
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
from context_compass.system.ai_restricted._shared.context_compass_configuration import load_configuration
from context_compass.system.ai_restricted._shared.feature_guard import (
    FeatureDisabledError,
    RepoStateDisabledError,
    ensure_feature_enabled,
)
from context_compass.system.ai_restricted._shared import policies as policy_store
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.hashing import hash_file, hash_json, hash_subtree
from context_compass.system.ai_restricted._shared.ignore_rules import (
    effective_ignore_config,
    is_code_file,
    is_dir_relevant,
    is_ignored_path,
    is_included_path,
    is_within_include_dirs,
    load_ignore_config,
    load_language_config,
)
from context_compass.system.ai_restricted._shared.paths import repo_relative_dir, repo_relative_path
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)

POLICIES_TABLE_NAME = "config_policies_core"
POLICIES_ACTION = "by_config_id"
POLICIES_CONFIG_ID = 1


def _default_policies() -> dict:
    """
    Return default policy values used by the scanner.

    Returns:
        dict: Default policy values.
    """
    policies = policy_store.default_policies()
    keys = (
        "lease_ttl_seconds",
        "lock_wait_seconds",
        "review_every_n_scans_default",
        "dir_review_every_n_scans_default",
        "max_task_attempts",
        "architecture_context_good_ratio_threshold",
        "architecture_context_stale_ratio_threshold",
        "architecture_context_faulty_ratio_threshold",
    )
    return {key: policies[key] for key in keys}


def _load_policies(repo_root: Path, owner_id: str) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Actor identifier for audit logging.

    Returns:
        dict: Effective policies.

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
    policies = response.output.get("result", {}).get("record", {})
    defaults = _default_policies()
    effective: dict = {}
    for key, default_value in defaults.items():
        value = policies.get(key, default_value)
        if isinstance(default_value, int) and not isinstance(value, int):
            raise ValueError(f"policy {key} must be an integer.")
        if isinstance(default_value, float) and not isinstance(value, (int, float)):
            raise ValueError(f"policy {key} must be a number.")
        effective[key] = value
    return effective


def _scanner_version() -> str:
    """
    Return the scanner version identifier.

    Returns:
        str: Scanner version string.
    """
    return "scanner@v1"


def _template_versions() -> dict:
    """
    Return template version identifiers for ctx artifacts.

    Returns:
        dict: Template version mapping.
    """
    return {"file_ctx": "file_ctx@v1", "dir_ctx": "dir_ctx@v1"}


def _acquire_with_wait(
    repo_root: Path,
    resource: Path,
    owner_id: str,
    ttl_seconds: int,
    wait_seconds: int,
) -> dict:
    """
    Acquire a lock, waiting up to wait_seconds if necessary.

    Args:
        repo_root (Path): Repository root used for lock scoping.
        resource (Path): Resource to lock.
        owner_id (str): Lock owner id.
        ttl_seconds (int): Lease TTL.
        wait_seconds (int): Seconds to wait before failing.

    Returns:
        dict: Lease record.
    """
    deadline = time.time() + wait_seconds
    while True:
        try:
            return lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds)
        except RuntimeError:
            if time.time() >= deadline:
                raise
            time.sleep(1)


def _work_id_for(kind: str, ctx_path: str) -> str:
    """
    Create a stable work_id from kind and ctx_path.

    Args:
        kind (str): Task kind.
        ctx_path (str): Context path.

    Returns:
        str: Work identifier.
    """
    digest = hash_json({"kind": kind, "ctx_path": ctx_path})[:12]
    return f"task_{digest}"


def _default_queue(now: str) -> dict:
    """
    Return a default tasks queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _priority_for_state(state: str) -> int:
    """
    Return a priority value for a given staleness state.

    Args:
        state (str): Staleness state.

    Returns:
        int: Priority value.
    """
    if state == "missing":
        return 95
    if state == "stale":
        return 85
    if state == "needs_review":
        return 60
    if state == "blocked":
        return 90
    if state == "faulty":
        return 95
    return 50


def _architecture_task_kind(kind: str) -> str:
    """
    Map architecture artifact kinds to resurvey task kinds.

    Args:
        kind (str): Artifact kind.

    Returns:
        str: Resurvey task kind.
    """
    mapping = {
        "architecture_context": "resurvey_architecture_context",
        "component_contexts": "resurvey_component_contexts",
        "test_architecture_context": "resurvey_test_architecture_context",
        "test_component_contexts": "resurvey_test_component_contexts",
    }
    task_kind = mapping.get(kind)
    if not task_kind:
        raise ValueError(f"Unknown architecture context kind: {kind}")
    return task_kind


def _needs_review(scan_counter: int, review_every: int, last_review_scan_id: Optional[int]) -> bool:
    """
    Determine whether a review is due.

    Args:
        scan_counter (int): Current scan counter.
        review_every (int): Review interval.
        last_review_scan_id (Optional[int]): Last review scan id.

    Returns:
        bool: True if review is due.
    """
    if review_every <= 0:
        return False
    last_scan = last_review_scan_id or 0
    return (scan_counter - last_scan) >= review_every


def _current_branch(repo_root: Path) -> str:
    """
    Load the active branch name for SQLite-backed state access.

    Args:
        repo_root (Path): Repository root.

    Returns:
        str: Active branch name.
    """
    return branch_paths.load_current_branch(repo_root)


def _context_ref(branch_name: str, kind: str) -> str:
    """
    Build a stable reference string for branch-scoped context records.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        str: Context reference string used in work queue entries.
    """
    return f"sqlite:branch:{branch_name}:{kind}"


def _file_ctx_lock_resource(branch_name: str, file_path: str) -> Path:
    """
    Build a synthetic lock resource path for file_ctx updates.

    Args:
        branch_name (str): Branch identifier.
        file_path (str): Repo-relative file path.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"file_ctx::{branch_name}::{file_path}")


def _dir_ctx_lock_resource(branch_name: str, dir_path: str) -> Path:
    """
    Build a synthetic lock resource path for dir_ctx updates.

    Args:
        branch_name (str): Branch identifier.
        dir_path (str): Repo-relative directory path.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"dir_ctx::{branch_name}::{dir_path}")


def _architecture_context_lock_resource(branch_name: str, kind: str) -> Path:
    """
    Build a synthetic lock resource path for architecture context updates.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_architecture_context::{branch_name}::{kind}")


def _component_context_lock_resource(branch_name: str, kind: str) -> Path:
    """
    Build a synthetic lock resource path for component context updates.

    Args:
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_component_contexts::{branch_name}::{kind}")


def _work_queue_lock_resource(branch_name: str, bucket: str, work_type: str) -> Path:
    """
    Build a synthetic lock resource path for branch work queues.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_work_queue::{branch_name}::{bucket}::{work_type}")


def _scan_record_lock_resource(branch_name: str, scan_id: str) -> Path:
    """
    Build a synthetic lock resource path for scan records.

    Args:
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_scan::{branch_name}::{scan_id}")


def _error_record_lock_resource(branch_name: str, error_id: str) -> Path:
    """
    Build a synthetic lock resource path for error records.

    Args:
        branch_name (str): Branch identifier.
        error_id (str): Error identifier.

    Returns:
        Path: Resource path for lease locks.
    """

    return Path(f"branch_error_record::{branch_name}::{error_id}")


def _read_repo_state(
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
        ValueError: If the CRUD response payload is invalid.
        sqlite_crud.SqliteCrudError: If the CRUD request fails.
    """

    response = sqlite_crud.execute_request(
        repo_root,
        sqlite_crud.SqliteCrudRequest(
            operation="read",
            scope="user",
            table_name="repo_state",
            action="by_branch_name",
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


def _read_file_ctx_by_ctx_path(
    repo_root: Path,
    branch_name: str,
    ctx_path: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read file_ctx by ctx_path via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        ctx_path (str): Repo-relative ctx path.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: file_ctx payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="read_file_ctx_by_ctx_path",
            payload={"branch_name": branch_name, "ctx_path": ctx_path},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("file_ctx read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("file_ctx read returned an invalid exists flag.")
    return record, exists


def _write_file_ctx(
    repo_root: Path,
    branch_name: str,
    file_ctx: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write file_ctx via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        file_ctx (dict): file_ctx payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the file_ctx record already exists.

    Returns:
        dict: Updated file_ctx payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_file_ctx",
            payload={
                "branch_name": branch_name,
                "file_ctx": file_ctx,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("file_ctx write returned an invalid record payload.")
    return record


def _read_dir_ctx_by_ctx_path(
    repo_root: Path,
    branch_name: str,
    ctx_path: str,
    actor_id: str,
) -> tuple[dict, bool]:
    """
    Read dir_ctx by ctx_path via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        ctx_path (str): Repo-relative ctx path.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: dir_ctx payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="read_dir_ctx_by_ctx_path",
            payload={"branch_name": branch_name, "ctx_path": ctx_path},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    exists = result.get("exists")
    if not isinstance(record, dict):
        raise ValueError("dir_ctx read returned an invalid record payload.")
    if not isinstance(exists, bool):
        raise ValueError("dir_ctx read returned an invalid exists flag.")
    return record, exists


def _write_dir_ctx(
    repo_root: Path,
    branch_name: str,
    dir_ctx: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write dir_ctx via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        dir_ctx (dict): dir_ctx payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the dir_ctx record already exists.

    Returns:
        dict: Updated dir_ctx payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_dir_ctx",
            payload={
                "branch_name": branch_name,
                "dir_ctx": dir_ctx,
                "exists": exists,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    record = result.get("record")
    if not isinstance(record, dict):
        raise ValueError("dir_ctx write returned an invalid record payload.")
    return record


def _read_architecture_context(
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
        kind (str): Context kind.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: architecture_context payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="read_architecture_context",
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


def _write_architecture_context(
    repo_root: Path,
    branch_name: str,
    kind: str,
    payload: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write architecture_context payloads via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind.
        payload (dict): Context payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Returns:
        dict: Updated architecture_context payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_architecture_context",
            payload={
                "branch_name": branch_name,
                "kind": kind,
                "context": payload,
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


def _read_component_contexts(
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
        kind (str): Context kind.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: component_contexts payload and existence flag.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="read_component_contexts",
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


def _write_component_contexts(
    repo_root: Path,
    branch_name: str,
    kind: str,
    payload: dict,
    actor_id: str,
    exists: bool,
) -> dict:
    """
    Write component_contexts payloads via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind.
        payload (dict): Context payload to persist.
        actor_id (str): Actor identifier for audit logging.
        exists (bool): Whether the record already exists.

    Returns:
        dict: Updated component_contexts payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_component_contexts",
            payload={
                "branch_name": branch_name,
                "kind": kind,
                "context": payload,
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


def _write_scan_record(
    repo_root: Path,
    branch_name: str,
    scan_id: str,
    payload: dict,
    actor_id: str,
) -> None:
    """
    Persist scan records via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        scan_id (str): Scan identifier.
        payload (dict): Scan record payload.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: This helper raises on failure.

    Raises:
        sqlite_query.SqliteQueryError: If the query request fails.
        ValueError: If the query response payload is invalid.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="write_scan_record",
            payload={
                "branch_name": branch_name,
                "scan_id": scan_id,
                "scan_record": payload,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    if not isinstance(result, dict):
        raise ValueError("scan_record write returned an invalid result payload.")


def _upsert_work_queue_tasks(
    repo_root: Path,
    branch_name: str,
    bucket: str,
    work_type: str,
    tasks: list[dict],
    actor_id: str,
    schema_version: int,
    repo_id: str | None,
) -> dict:
    """
    Upsert work queue tasks via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work type name.
        tasks (list[dict]): Task payloads to upsert.
        actor_id (str): Actor identifier for audit logging.
        schema_version (int): Queue schema version.
        repo_id (str | None): Optional repository identifier.

    Returns:
        dict: Upsert counts and queue metadata.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="upsert_work_queue_tasks",
            payload={
                "branch_name": branch_name,
                "bucket": bucket,
                "work_type": work_type,
                "schema_version": schema_version,
                "repo_id": repo_id,
                "tasks": tasks,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    if not isinstance(result, dict):
        raise ValueError("work_queue upsert returned an invalid result payload.")
    return result


def _write_error_record(
    repo_root: Path,
    owner_id: str,
    target_path: Optional[str],
    ctx_path: Optional[str],
    category: str,
    message: str,
    details: dict,
) -> str:
    """
    Write an error record and return its identifier.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Error owner id.
        target_path (Optional[str]): Target path.
        ctx_path (Optional[str]): Context path.
        category (str): Error category.
        message (str): Error message.
        details (dict): Error details.

    Returns:
        str: Error record identifier.
    """
    now = utc_now_iso()
    error_id = f"error_{hash_json({'target': target_path, 'ctx': ctx_path, 'when': now})[:12]}"
    record = {
        "schema_version": 1,
        "error_id": error_id,
        "when": now,
        "owner_id": owner_id,
        "work_id": None,
        "target_path": target_path,
        "ctx_path": ctx_path,
        "category": category,
        "message": message,
        "details": details,
    }
    branch_name = _current_branch(repo_root)
    policies = _load_policies(repo_root, owner_id)
    resource = _error_record_lock_resource(branch_name, error_id)
    _acquire_with_wait(
        repo_root,
        resource,
        owner_id,
        policies["lease_ttl_seconds"],
        policies["lock_wait_seconds"],
    )
    try:
        sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="create",
                scope="user",
                table_name="scan_error_records",
                action="write_error_record",
                payload={
                    "branch_name": branch_name,
                    "error_id": error_id,
                    "error_record": record,
                },
                actor_id=owner_id,
            ),
        )
    finally:
        lease.release_lock(repo_root, resource, owner_id)
    return error_id


def _build_task(
    kind: str,
    target_path: str,
    ctx_path: str,
    reason: list[str],
    priority: int,
    now: str,
    last_error_ref: Optional[str] = None,
) -> dict:
    """
    Build a task payload for work_management.

    Args:
        kind (str): Task kind.
        target_path (str): Target path.
        ctx_path (str): Context path.
        reason (list[str]): Reason list.
        priority (int): Priority value.
        now (str): Timestamp for created/updated.
        last_error_ref (Optional[str]): Error record reference.

    Returns:
        dict: Task payload.
    """
    work_id = _work_id_for(kind, ctx_path)
    return {
        "work_id": work_id,
        "state": "queued",
        "kind": kind,
        "target_path": target_path,
        "ctx_path": ctx_path,
        "reason": reason,
        "parent_work_id": None,
        "root_work_id": work_id,
        "priority": priority,
        "lease": None,
        "attempts": 0,
        "last_error_ref": last_error_ref,
        "created_at": now,
        "updated_at": now,
    }


def _code_skip_reason(path: Path) -> Optional[str]:
    """
    Return a skip reason for code scanning when the file is excluded.

    Args:
        path (Path): File path.

    Returns:
        Optional[str]: "init" for __init__.py, "excluded" for generated ctx.
    """
    name = path.name
    if name == "__init__.py":
        return "init"
    if os.name == "nt" and name.lower() == "__init__.py":
        return "init"
    if name.startswith("__") and name.endswith(".json"):
        return "excluded"
    if name.startswith("__") and name.endswith(".dir.json"):
        return "excluded"
    return None


def _empty_skip_summary() -> dict:
    """
    Return a skip summary template for scanner enumeration.

    Returns:
        dict: Skip counters for init/excluded/unknown files.
    """
    return {"init": 0, "excluded": 0, "unknown": 0}


def _walk_repo(
    repo_root: Path,
    ignore_config: dict,
    language_config: dict,
) -> tuple[list[Path], list[Path], dict]:
    """
    Walk the repo and collect directories and code files.

    Args:
        repo_root (Path): Repository root.
        ignore_config (dict): Ignore configuration.
        language_config (dict): Language configuration.

    Returns:
        tuple[list[Path], list[Path], dict]: (directories, code files, skip summary).
    """
    directories: list[Path] = []
    code_files: list[Path] = []
    skip_summary = _empty_skip_summary()
    include_dirs = ignore_config.get("include_dirs", [])

    for dirpath, dirnames, filenames in os.walk(repo_root):
        current_dir = Path(dirpath)
        rel_dir = repo_relative_dir(repo_root, current_dir)
        if not is_dir_relevant(rel_dir, include_dirs):
            dirnames[:] = []
            continue
        if is_ignored_path(repo_root, current_dir, ignore_config):
            dirnames[:] = []
            continue

        if not include_dirs or is_within_include_dirs(repo_root, current_dir, include_dirs):
            directories.append(current_dir)
        pruned_dirs = []
        for name in dirnames:
            candidate = current_dir / name
            rel_candidate = repo_relative_dir(repo_root, candidate)
            if not is_dir_relevant(rel_candidate, include_dirs):
                continue
            if is_ignored_path(repo_root, candidate, ignore_config):
                continue
            pruned_dirs.append(name)
        dirnames[:] = pruned_dirs

        for filename in filenames:
            path = current_dir / filename
            skip_reason = _code_skip_reason(path)
            if skip_reason:
                skip_summary[skip_reason] += 1
                continue
            if is_ignored_path(repo_root, path, ignore_config):
                skip_summary["excluded"] += 1
                continue
            if not is_included_path(repo_root, path, ignore_config):
                skip_summary["excluded"] += 1
                continue
            is_code, _language = is_code_file(path, ignore_config, language_config)
            if is_code:
                code_files.append(path)
            else:
                skip_summary["unknown"] += 1
    return directories, code_files, skip_summary


def _ctx_semantic_hash(ctx: dict) -> str:
    """
    Compute the semantic hash for a ctx payload.

    Args:
        ctx (dict): Ctx payload.

    Returns:
        str: SHA256 hash of agent.* content.
    """
    agent_section = ctx.get("agent", {})
    if not isinstance(agent_section, dict):
        agent_section = {}
    return hash_json(agent_section)


def _update_computed(
    ctx: dict,
    new_state: str,
    reasons: list[str],
    checksums: dict,
    review: dict,
    scan_id: str,
    scanned_at: str,
) -> dict:
    """
    Build a new computed block for a ctx payload.

    Args:
        ctx (dict): Existing ctx payload.
        new_state (str): Freshness state.
        reasons (list[str]): Staleness reasons.
        checksums (dict): Checksums block.
        review (dict): Review block.
        scan_id (str): Scan identifier.
        scanned_at (str): Scan timestamp.

    Returns:
        dict: Updated ctx payload.
    """
    computed = dict(ctx.get("computed", {}))
    computed["freshness_state"] = new_state
    computed["staleness_reasons"] = reasons
    computed["checksums"] = checksums
    computed["last_scan"] = {"scan_id": scan_id, "scanned_at": scanned_at}
    computed["review"] = review
    ctx["computed"] = computed
    return ctx


def _write_file_ctx_if_changed(
    repo_root: Path,
    branch_name: str,
    file_path: str,
    ctx: dict,
    original_computed: dict,
    new_computed: dict,
    owner_id: str,
    policies: dict,
    *,
    exists: bool,
) -> bool:
    """
    Write file_ctx records if computed content changed.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        file_path (str): Repo-relative file path.
        ctx (dict): Updated ctx payload.
        original_computed (dict): Original computed block.
        new_computed (dict): New computed block.
        owner_id (str): Lock owner id.
        policies (dict): Policy values.
        exists (bool): Whether the record already exists.

    Returns:
        bool: True if SQLite was updated.
    """
    if original_computed == new_computed:
        return False
    resource = _file_ctx_lock_resource(branch_name, file_path)
    _acquire_with_wait(
        repo_root,
        resource,
        owner_id,
        policies["lease_ttl_seconds"],
        policies["lock_wait_seconds"],
    )
    try:
        _write_file_ctx(repo_root, branch_name, ctx, owner_id, exists)
    finally:
        lease.release_lock(repo_root, resource, owner_id)
    return True


def _write_dir_ctx_if_changed(
    repo_root: Path,
    branch_name: str,
    dir_path: str,
    ctx: dict,
    original_computed: dict,
    new_computed: dict,
    owner_id: str,
    policies: dict,
    *,
    exists: bool,
) -> bool:
    """
    Write dir_ctx records if computed content changed.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        dir_path (str): Repo-relative directory path.
        ctx (dict): Updated ctx payload.
        original_computed (dict): Original computed block.
        new_computed (dict): New computed block.
        owner_id (str): Lock owner id.
        policies (dict): Policy values.
        exists (bool): Whether the record already exists.

    Returns:
        bool: True if SQLite was updated.
    """
    if original_computed == new_computed:
        return False
    resource = _dir_ctx_lock_resource(branch_name, dir_path)
    _acquire_with_wait(
        repo_root,
        resource,
        owner_id,
        policies["lease_ttl_seconds"],
        policies["lock_wait_seconds"],
    )
    try:
        _write_dir_ctx(repo_root, branch_name, ctx, owner_id, exists)
    finally:
        lease.release_lock(repo_root, resource, owner_id)
    return True


def _write_architecture_if_changed(
    repo_root: Path,
    branch_name: str,
    kind: str,
    payload: dict,
    original_computed: dict,
    updated_computed: dict,
    owner_id: str,
    policies: dict,
    *,
    exists: bool,
) -> None:
    """
    Write architecture/component context records if computed content changed.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        kind (str): Context kind identifier.
        payload (dict): Updated payload.
        original_computed (dict): Original computed block.
        updated_computed (dict): Updated computed block.
        owner_id (str): Lock owner id.
        policies (dict): Policy values.
        exists (bool): Whether the record already exists.
    """
    if original_computed == updated_computed:
        return
    if kind in ("architecture_context", "test_architecture_context"):
        resource = _architecture_context_lock_resource(branch_name, kind)
        writer = _write_architecture_context
    else:
        resource = _component_context_lock_resource(branch_name, kind)
        writer = _write_component_contexts
    lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        writer(repo_root, branch_name, kind, payload, owner_id, exists)
    finally:
        lease.release_lock(repo_root, resource, owner_id)


def _check_architecture_artifact(
    repo_root: Path,
    kind: str,
    policies: dict,
    scan_id_value: str,
    now: str,
    update_ctx: bool,
    agent_id: str,
    tasks: list[dict],
    scan_record: dict,
    error_records: list[str],
) -> None:
    """
    Evaluate an architecture/component context artifact and emit tasks if stale.

    Args:
        repo_root (Path): Repository root.
        kind (str): Artifact kind.
        policies (dict): Policy values.
        scan_id_value (str): Scan identifier.
        now (str): Timestamp.
        update_ctx (bool): Whether to update computed fields.
        agent_id (str): Agent identifier.
        tasks (list[dict]): Task accumulator.
        scan_record (dict): Scan record payload.
        error_records (list[str]): Error id accumulator.
    """
    branch_name = _current_branch(repo_root)
    rel_target = _context_ref(branch_name, kind)
    task_kind = _architecture_task_kind(kind)
    if kind in ("architecture_context", "test_architecture_context"):
        record, exists = _read_architecture_context(
            repo_root,
            branch_name,
            kind,
            actor_id=agent_id,
        )
    else:
        record, exists = _read_component_contexts(
            repo_root,
            branch_name,
            kind,
            actor_id=agent_id,
        )

    if not exists:
        tasks.append(
            _build_task(
                task_kind,
                rel_target,
                rel_target,
                ["missing_architecture_context"],
                _priority_for_state("missing"),
                now,
            )
        )
        scan_record.setdefault("architecture_contexts", []).append(
            {
                "path": rel_target,
                "kind": kind,
                "state": "missing",
                "reasons": ["missing_architecture_context"],
            }
        )
        return

    payload = record
    if not isinstance(payload, dict):
        error_ref = _write_error_record(
            repo_root,
            agent_id,
            target_path=rel_target,
            ctx_path=rel_target,
            category="parse_error",
            message="invalid architecture context payload",
            details={"error": "payload must be an object"},
        )
        error_records.append(error_ref)
        tasks.append(
            _build_task(
                task_kind,
                rel_target,
                rel_target,
                ["ctx_parse_error"],
                _priority_for_state("blocked"),
                now,
                last_error_ref=error_ref,
            )
        )
        scan_record.setdefault("architecture_contexts", []).append(
            {"path": rel_target, "kind": kind, "state": "blocked", "reasons": ["ctx_parse_error"]}
        )
        return

    computed = payload.get("computed", {})
    matrix = computed.get("matrix", []) if isinstance(computed, dict) else []
    if not isinstance(matrix, list):
        matrix = []

    evaluation = architecture_contexts.evaluate_matrix(
        repo_root, branch_name, matrix, agent_id
    )
    thresholds = architecture_contexts.thresholds_from_policies(policies)
    state = architecture_contexts.derive_state(evaluation["good_ratio"], thresholds)
    reasons = evaluation["staleness_reasons"]

    scan_record.setdefault("architecture_contexts", []).append(
        {"path": rel_target, "kind": kind, "state": state, "reasons": reasons}
    )

    if state in ("stale", "faulty", "blocked"):
        tasks.append(
            _build_task(
                task_kind,
                rel_target,
                rel_target,
                reasons or ["stale_architecture_context"],
                _priority_for_state(state),
                now,
            )
        )

    if update_ctx:
        original_computed = dict(computed) if isinstance(computed, dict) else {}
        updated_computed = dict(original_computed)
        updated_computed.update(
            {
                "freshness_state": state,
                "holes_count": evaluation["holes_count"],
                "holes_ratio": evaluation["holes_ratio"],
                "good_ratio": evaluation["good_ratio"],
                "inputs_hash": evaluation["inputs_hash"],
                "last_checked_at": now,
                "matrix": evaluation["matrix"],
                "staleness_reasons": reasons,
            }
        )
        payload["computed"] = updated_computed
        payload["updated_at"] = now
        _write_architecture_if_changed(
            repo_root,
            branch_name,
            kind,
            payload,
            original_computed,
            updated_computed,
            agent_id,
            policies,
            exists=exists,
        )
    return True


def _evaluate_file_ctx(
    ctx: dict,
    code_hash: str,
    scan_counter: int,
    scan_id: str,
    scanned_at: str,
    policies: dict,
) -> tuple[str, list[str], dict, dict]:
    """
    Evaluate staleness for a file ctx payload.

    Args:
        ctx (dict): Ctx payload.
        code_hash (str): Current code hash.
        scan_counter (int): Current scan counter.
        scan_id (str): Scan identifier.
        scanned_at (str): Scan timestamp.
        policies (dict): Policy values.

    Returns:
        tuple[str, list[str], dict, dict]: (state, reasons, checksums, review).
    """
    computed = ctx.get("computed", {})
    checksums = dict(computed.get("checksums", {}))
    previous_hash = checksums.get("code_hash_sha256")

    reasons: list[str] = []
    if previous_hash != code_hash:
        reasons.append("code_hash_mismatch")

    review = dict(computed.get("review", {}))
    review_every = review.get("review_every_n_scans")
    if review_every is None:
        review_every = int(policies["review_every_n_scans_default"])
    last_review_scan_id = review.get("last_review_scan_id")
    review_due = _needs_review(scan_counter, int(review_every), last_review_scan_id)
    if review_due and not reasons:
        reasons.append("review_due")

    state = "fresh"
    if reasons:
        state = "needs_review" if "review_due" in reasons and len(reasons) == 1 else "stale"

    checksums["code_hash_sha256"] = code_hash
    checksums["ctx_semantic_hash_sha256"] = _ctx_semantic_hash(ctx)
    checksums.setdefault("template_version", _template_versions()["file_ctx"])
    checksums["analyzer_version"] = _scanner_version()

    review["review_every_n_scans"] = int(review_every)
    if "scan_counter" not in review:
        review["scan_counter"] = scan_counter
    if "last_review_scan_id" not in review:
        review["last_review_scan_id"] = last_review_scan_id
    if state != computed.get("freshness_state"):
        review["scan_counter"] = scan_counter

    return state, reasons, checksums, review


def _evaluate_dir_ctx(
    ctx: dict,
    subtree_hash: str,
    scan_counter: int,
    scan_id: str,
    scanned_at: str,
    policies: dict,
) -> tuple[str, list[str], dict, dict]:
    """
    Evaluate staleness for a directory ctx payload.

    Args:
        ctx (dict): Ctx payload.
        subtree_hash (str): Current subtree hash.
        scan_counter (int): Current scan counter.
        scan_id (str): Scan identifier.
        scanned_at (str): Scan timestamp.
        policies (dict): Policy values.

    Returns:
        tuple[str, list[str], dict, dict]: (state, reasons, checksums, review).
    """
    computed = ctx.get("computed", {})
    checksums = dict(computed.get("checksums", {}))
    previous_hash = checksums.get("subtree_hash_sha256")

    reasons: list[str] = []
    if previous_hash != subtree_hash:
        reasons.append("subtree_hash_mismatch")

    review = dict(computed.get("review", {}))
    review_every = review.get("review_every_n_scans")
    if review_every is None:
        review_every = int(policies["dir_review_every_n_scans_default"])
    last_review_scan_id = review.get("last_review_scan_id")
    review_due = _needs_review(scan_counter, int(review_every), last_review_scan_id)
    if review_due and not reasons:
        reasons.append("review_due")

    state = "fresh"
    if reasons:
        state = "needs_review" if "review_due" in reasons and len(reasons) == 1 else "stale"

    checksums["subtree_hash_sha256"] = subtree_hash
    checksums["ctx_semantic_hash_sha256"] = _ctx_semantic_hash(ctx)
    checksums.setdefault("template_version", _template_versions()["dir_ctx"])
    checksums["analyzer_version"] = _scanner_version()

    review["review_every_n_scans"] = int(review_every)
    if "scan_counter" not in review:
        review["scan_counter"] = scan_counter
    if "last_review_scan_id" not in review:
        review["last_review_scan_id"] = last_review_scan_id
    if state != computed.get("freshness_state"):
        review["scan_counter"] = scan_counter

    return state, reasons, checksums, review


def scan_repo(
    repo_root: Path,
    agent_id: str,
    scan_id: Optional[str],
    work_id: Optional[str],
    dry_run: bool,
    emit_tasks: bool,
    update_ctx: bool,
) -> dict:
    """
    Scan the repository for staleness and emit tasks.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        scan_id (Optional[str]): Scan identifier override.
        work_id (Optional[str]): Work identifier for hard mode enforcement.
        dry_run (bool): If True, do not write outputs.
        emit_tasks (bool): If True, write tasks queue updates.
        update_ctx (bool): If True, update computed fields in ctx files.

    Returns:
        dict: Scan record payload.
    """
    now = utc_now_iso()
    policies = _load_policies(repo_root, agent_id)
    ignore_config = load_ignore_config(repo_root)
    language_config = load_language_config(repo_root)
    branch_name = _current_branch(repo_root)
    repo_state, _ = _read_repo_state(repo_root, branch_name, agent_id)
    if not isinstance(repo_state, dict):
        repo_state = {"scan_counter": 0}

    scan_counter = int(repo_state.get("scan_counter") or 0) + 1
    scan_id_value = scan_id or f"scan_{scan_counter:06d}"

    directories, code_files, skip_summary = _walk_repo(repo_root, ignore_config, language_config)

    dir_entries: dict[str, list[str]] = {}
    file_hashes: dict[str, str] = {}
    for file_path in code_files:
        rel_path = repo_relative_path(repo_root, file_path)
        code_hash = hash_file(file_path)
        file_hashes[rel_path] = code_hash
        dir_entries.setdefault("", []).append(f"{rel_path}:{code_hash}")
        parts = rel_path.split("/")
        if len(parts) > 1:
            for idx in range(len(parts) - 1):
                key = "/".join(parts[: idx + 1])
                dir_entries.setdefault(key, []).append(f"{rel_path}:{code_hash}")

    scan_record = {
        "schema_version": 1,
        "scan_id": scan_id_value,
        "scanned_at": now,
        "repo_root": str(repo_root),
        "repo_id": repo_state.get("repo_id"),
        "git_head": repo_state.get("git", {}).get("head") if isinstance(repo_state.get("git"), dict) else None,
        "scanner_version": _scanner_version(),
        "files": [],
        "directories": [],
        "emitted_tasks": [],
        "errors": [],
        "summary": {
            "files_scanned": len(code_files),
            "dirs_scanned": len(directories),
            "files_skipped": skip_summary,
            "tasks_emitted": 0,
            "missing": 0,
            "stale": 0,
            "needs_review": 0,
            "blocked": 0,
        },
        "effective_ignore_config": effective_ignore_config(ignore_config),
    }

    tasks: list[dict] = []
    error_records: list[str] = []

    for file_path in code_files:
        rel_path = repo_relative_path(repo_root, file_path)
        ctx_path = file_path.parent / f"__{file_path.stem}__.json"
        rel_ctx = repo_relative_path(repo_root, ctx_path)
        code_hash = file_hashes[rel_path]

        record, exists = _read_file_ctx_by_ctx_path(
            repo_root, branch_name, rel_ctx, actor_id=agent_id
        )
        if not exists:
            scan_record["summary"]["missing"] += 1
            tasks.append(
                _build_task(
                    "generate_file_ctx",
                    rel_path,
                    rel_ctx,
                    ["missing_ctx"],
                    _priority_for_state("missing"),
                    now,
                )
            )
            scan_record["files"].append(
                {"path": rel_path, "ctx_path": rel_ctx, "state": "missing", "reasons": ["missing_ctx"]}
            )
            continue

        ctx = record
        if not isinstance(ctx, dict):
            error_ref = _write_error_record(
                repo_root,
                agent_id,
                target_path=rel_path,
                ctx_path=rel_ctx,
                category="parse_error",
                message="invalid ctx payload",
                details={"error": "ctx payload must be an object"},
            )
            error_records.append(error_ref)
            scan_record["summary"]["blocked"] += 1
            tasks.append(
                _build_task(
                    "resolve_blocked_ctx",
                    rel_path,
                    rel_ctx,
                    ["ctx_parse_error"],
                    _priority_for_state("blocked"),
                    now,
                    last_error_ref=error_ref,
                )
            )
            scan_record["files"].append(
                {"path": rel_path, "ctx_path": rel_ctx, "state": "blocked", "reasons": ["ctx_parse_error"]}
            )
            continue

        state, reasons, checksums, review = _evaluate_file_ctx(
            ctx, code_hash, scan_counter, scan_id_value, now, policies
        )
        scan_record["files"].append(
            {"path": rel_path, "ctx_path": rel_ctx, "state": state, "reasons": reasons}
        )
        if state == "stale":
            scan_record["summary"]["stale"] += 1
            tasks.append(
                _build_task(
                    "refresh_file_ctx",
                    rel_path,
                    rel_ctx,
                    reasons,
                    _priority_for_state("stale"),
                    now,
                )
            )
        elif state == "needs_review":
            scan_record["summary"]["needs_review"] += 1
            tasks.append(
                _build_task(
                    "review_file_ctx",
                    rel_path,
                    rel_ctx,
                    reasons,
                    _priority_for_state("needs_review"),
                    now,
                )
            )

        if update_ctx:
            original_computed = dict(ctx.get("computed", {}))
            updated = _update_computed(ctx, state, reasons, checksums, review, scan_id_value, now)
            _write_file_ctx_if_changed(
                repo_root,
                branch_name,
                rel_path,
                updated,
                original_computed,
                updated.get("computed", {}),
                agent_id,
                policies,
                exists=exists,
            )

    for directory in directories:
        rel_dir = repo_relative_dir(repo_root, directory)
        dir_name = directory.name
        ctx_path = directory / f"__{dir_name}__.dir.json"
        rel_ctx = repo_relative_path(repo_root, ctx_path)
        subtree_entries = dir_entries.get(rel_dir, [])
        subtree_hash = hash_subtree(subtree_entries)

        record, exists = _read_dir_ctx_by_ctx_path(
            repo_root, branch_name, rel_ctx, actor_id=agent_id
        )
        if not exists:
            scan_record["summary"]["missing"] += 1
            tasks.append(
                _build_task(
                    "generate_dir_ctx",
                    rel_dir or ".",
                    rel_ctx,
                    ["missing_ctx"],
                    _priority_for_state("missing"),
                    now,
                )
            )
            scan_record["directories"].append(
                {"path": rel_dir, "ctx_path": rel_ctx, "state": "missing", "reasons": ["missing_ctx"]}
            )
            continue

        ctx = record
        if not isinstance(ctx, dict):
            error_ref = _write_error_record(
                repo_root,
                agent_id,
                target_path=rel_dir,
                ctx_path=rel_ctx,
                category="parse_error",
                message="invalid ctx payload",
                details={"error": "ctx payload must be an object"},
            )
            error_records.append(error_ref)
            scan_record["summary"]["blocked"] += 1
            tasks.append(
                _build_task(
                    "resolve_blocked_ctx",
                    rel_dir or ".",
                    rel_ctx,
                    ["ctx_parse_error"],
                    _priority_for_state("blocked"),
                    now,
                    last_error_ref=error_ref,
                )
            )
            scan_record["directories"].append(
                {"path": rel_dir, "ctx_path": rel_ctx, "state": "blocked", "reasons": ["ctx_parse_error"]}
            )
            continue

        state, reasons, checksums, review = _evaluate_dir_ctx(
            ctx, subtree_hash, scan_counter, scan_id_value, now, policies
        )
        scan_record["directories"].append(
            {"path": rel_dir, "ctx_path": rel_ctx, "state": state, "reasons": reasons}
        )
        if state == "stale":
            scan_record["summary"]["stale"] += 1
            tasks.append(
                _build_task(
                    "refresh_dir_ctx",
                    rel_dir or ".",
                    rel_ctx,
                    reasons,
                    _priority_for_state("stale"),
                    now,
                )
            )
        elif state == "needs_review":
            scan_record["summary"]["needs_review"] += 1
            tasks.append(
                _build_task(
                    "review_dir_architecture",
                    rel_dir or ".",
                    rel_ctx,
                    reasons,
                    _priority_for_state("needs_review"),
                    now,
                )
            )

        if update_ctx:
            original_computed = dict(ctx.get("computed", {}))
            updated = _update_computed(ctx, state, reasons, checksums, review, scan_id_value, now)
            _write_dir_ctx_if_changed(
                repo_root,
                branch_name,
                rel_dir or ".",
                updated,
                original_computed,
                updated.get("computed", {}),
                agent_id,
                policies,
                exists=exists,
            )

    config = load_configuration(repo_root)
    allow_arch_contexts = config.get("features", {}).get("architecture_contexts", True)
    if allow_arch_contexts:
        try:
            ensure_feature_enabled(repo_root, "architecture_contexts", "check architecture contexts")
        except (FeatureDisabledError, RepoStateDisabledError):
            allow_arch_contexts = False
    if allow_arch_contexts:
        for kind in (
            "architecture_context",
            "component_contexts",
            "test_architecture_context",
            "test_component_contexts",
        ):
            _check_architecture_artifact(
                repo_root,
                kind,
                policies,
                scan_id_value,
                now,
                update_ctx,
                agent_id,
                tasks,
                scan_record,
                error_records,
            )

    scan_record["summary"]["tasks_emitted"] = len(tasks)
    scan_record["emitted_tasks"] = [task["work_id"] for task in tasks]
    scan_record["errors"] = error_records

    if not dry_run and emit_tasks and tasks:
        resource = _work_queue_lock_resource(branch_name, "ready", "task")
        _acquire_with_wait(
            repo_root,
            resource,
            agent_id,
            policies["lease_ttl_seconds"],
            policies["lock_wait_seconds"],
        )
        try:
            _upsert_work_queue_tasks(
                repo_root,
                branch_name,
                "ready",
                "task",
                tasks,
                agent_id,
                schema_version=1,
                repo_id=repo_state.get("repo_id"),
            )
        finally:
            lease.release_lock(repo_root, resource, agent_id)

    if not dry_run:
        resource = _scan_record_lock_resource(branch_name, scan_id_value)
        _acquire_with_wait(
            repo_root,
            resource,
            agent_id,
            policies["lease_ttl_seconds"],
            policies["lock_wait_seconds"],
        )
        try:
            _write_scan_record(
                repo_root,
                branch_name,
                scan_id_value,
                scan_record,
                agent_id,
            )
        finally:
            lease.release_lock(repo_root, resource, agent_id)

        update_state.bump_scan_state(
            repo_root,
            scan_id=scan_id_value,
            scanned_at=now,
            scanner_version=_scanner_version(),
            repo_id=repo_state.get("repo_id"),
            git_head=repo_state.get("git", {}).get("head") if isinstance(repo_state.get("git"), dict) else None,
            template_versions=_template_versions(),
            owner_id=agent_id,
        )

    return scan_record


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Execute a repository scan using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the scan record payload.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id.
        - Enforces certification, feature flags, and work mode guards.
        - Allows toggling task emission and ctx updates.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        scan_id = optional_string(payload, "scan_id", command_name=command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        dry_run = optional_bool(payload, "dry_run", command_name=command_name, default=False)
        emit_tasks = optional_bool(
            payload, "emit_tasks", command_name=command_name, default=True
        )
        update_ctx = optional_bool(
            payload, "update_ctx", command_name=command_name, default=True
        )
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "scan", "run scanner")
        if emit_tasks:
            ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
        ensure_work_mode(repo_root, work_id, "run scanner")
        record = scan_repo(
            repo_root,
            agent_id=agent_id,
            scan_id=scan_id,
            work_id=work_id,
            dry_run=bool(dry_run),
            emit_tasks=bool(emit_tasks),
            update_ctx=bool(update_ctx),
        )
        return ok_result(output={"scan_record": record})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for scanner execution.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Scan repository for ctx staleness")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--scan-id", default=None, help="Scan identifier override")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--dry-run", action="store_true", help="Do not write outputs")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Disable task emission")
    parser.add_argument("--no-update-ctx", action="store_true", help="Do not update ctx computed fields")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "scan_id": args.scan_id,
        "work_id": args.work_id,
        "dry_run": args.dry_run,
        "emit_tasks": not args.no_emit_tasks,
        "update_ctx": not args.no_update_ctx,
    }
    context = ExecutionContext(
        command_name="scan",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("scan failed: %s", result.errors)
        raise SystemExit(1)
    record = result.output.get("scan_record", {})
    summary = record.get("summary", {})
    logger.info(
        "scan summary: files=%s skipped=%s dirs=%s",
        summary.get("files_scanned"),
        summary.get("files_skipped"),
        summary.get("dirs_scanned"),
    )
    logger.info("scan ignore config: %s", record.get("effective_ignore_config"))
    logger.info("scan completed: %s", record.get("scan_id"))


if __name__ == "__main__":
    main()
