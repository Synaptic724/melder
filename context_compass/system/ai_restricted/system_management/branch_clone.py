"""
Clone branch state and work queues from a source branch into a new branch.

Purpose
- Copy SQLite-backed branch records and queues into a new branch.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.system_management import branch_copy_context, branch_copy_work
from context_compass.system.ai_restricted.system_management import branch_delete
from context_compass.system.ai_restricted._shared import architecture_contexts
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
from context_compass.system.ai_restricted.system_management import branch_switch
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)


BRANCH_REGISTRY_TABLE = "branch_registry"
BRANCH_REGISTRY_CREATE_ACTION = "register_branch"
BRANCH_REGISTRY_READ_ACTION = "by_branch_name"

REPO_STATE_TABLE = "repo_state"
REPO_STATE_ACTION = "by_branch_name"

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1

QUERY_READ_CONTEXT_PROFILES = "read_context_profiles"
QUERY_WRITE_CONTEXT_PROFILES = "write_context_profiles"
QUERY_READ_ARCHITECTURE_CONTEXT = "read_architecture_context"
QUERY_WRITE_ARCHITECTURE_CONTEXT = "write_architecture_context"
QUERY_READ_COMPONENT_CONTEXTS = "read_component_contexts"
QUERY_WRITE_COMPONENT_CONTEXTS = "write_component_contexts"
QUERY_READ_BRANCH_WORK_QUEUE = "read_branch_work_queue"
QUERY_WRITE_BRANCH_WORK_QUEUE = "write_branch_work_queue"
QUERY_WRITE_REPO_STATE = "write_repo_state"

DEFAULT_CONTEXT_PROFILES_MAX_ITEMS = 25
DEFAULT_CONTEXT_PROFILES_MAX_BYTES = 120000


def _default_limits() -> dict[str, int]:
    """
    Return default context profile limits.

    Returns:
        dict[str, int]: Default limits payload.
    """

    return {
        "max_items_per_profile": DEFAULT_CONTEXT_PROFILES_MAX_ITEMS,
        "max_bytes_per_profile": DEFAULT_CONTEXT_PROFILES_MAX_BYTES,
    }


def _default_profiles(now: str, limits: dict[str, int]) -> dict:
    """
    Return a default context_profiles payload.

    Args:
        now (str): Current timestamp.
        limits (dict[str, int]): Limits payload.

    Returns:
        dict: Context profiles payload.
    """

    return {
        "schema_version": 1,
        "updated_at": now,
        "rules_version": "context_profiles@v1",
        "limits": limits,
        "profiles": [],
    }


def _ensure_source_branch(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Ensure the source branch exists.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Source branch name.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: This function validates branch existence.

    Raises:
        FileNotFoundError: If the branch is not registered.
    """
    if not _crud_branch_registered(repo_root, branch_name, actor_id):
        raise FileNotFoundError(f"Source branch not registered: {branch_name}")


def _prepare_destination(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
    force: bool,
) -> None:
    """
    Prepare a destination branch by hard deleting when forced.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Destination branch name.
        actor_id (str): Actor identifier for audit logging.
        force (bool): Whether to delete an existing destination.

    Returns:
        None: This function validates or removes the destination branch.

    Raises:
        FileExistsError: If destination exists and force is False.
    """
    if _crud_branch_registered(repo_root, branch_name, actor_id):
        if not force:
            raise FileExistsError(f"Destination branch already exists: {branch_name}")
        branch_delete.delete_branch(repo_root, branch_name, actor_id)


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

    limits = _default_limits()
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


def _default_repo_state(repo_root: Path, now: str) -> dict:
    """
    Return a default repo_state payload.

    Args:
        repo_root (Path): Repository root.
        now (str): Current timestamp.

    Returns:
        dict: Repo state payload.
    """

    return {
        "schema_version": 1,
        "repo_id": None,
        "repo_root": str(repo_root),
        "git": {"head": None},
        "scan_counter": 0,
        "last_scan_id": None,
        "last_scan_at": None,
        "scanner_version": None,
        "template_versions": {"file_ctx": None, "dir_ctx": None},
        "lifecycle": {
            "stage": "new",
            "assessment": "Initial assessment pending",
            "confidence": 0.0,
            "assessed_at": None,
        },
        "tooling_policy": {
            "mode": "restricted",
            "disabled_features": ["scan", "context_profiles"],
            "notes": "Auto-restricted for new repos; update repo_state to enable.",
            "updated_at": now,
        },
        "created_at": now,
        "updated_at": now,
    }


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
    if exists:
        return record, exists
    now = utc_now_iso()
    return _default_repo_state(repo_root, now), exists


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


def _seed_repo_state(repo_root: Path, branch_name: str, actor_id: str) -> None:
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
    _query_write_repo_state(repo_root, branch_name, record, actor_id, exists=exists)


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
    payload = _default_profiles(utc_now_iso(), limits)
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
        payload = architecture_contexts.default_architecture_context(kind, utc_now_iso())
        _query_write_architecture_context(
            repo_root,
            branch_name,
            kind,
            payload,
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
        payload = architecture_contexts.default_component_contexts(kind, utc_now_iso())
        _query_write_component_contexts(
            repo_root,
            branch_name,
            kind,
            payload,
            actor_id,
            exists=exists,
        )


def _default_queue(now: str) -> dict:
    """
    Return a default queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """

    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _queue_buckets() -> tuple[str, ...]:
    """
    Return the branch work queue bucket names.

    Returns:
        tuple[str, ...]: Bucket identifiers.
    """

    return ("ready", "active", "backlog", "completed", "denied")


def _queue_kinds() -> tuple[str, ...]:
    """
    Return the branch work queue kinds.

    Returns:
        tuple[str, ...]: Work item kind identifiers.
    """

    return ("epic", "story", "task")


def _read_branch_queue(
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


def _write_branch_queue(
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
            queue_payload, exists = _read_branch_queue(
                repo_root,
                branch_name,
                bucket,
                work_type,
                actor_id,
            )
            if not exists:
                queue_payload = _default_queue(utc_now_iso())
            _write_branch_queue(
                repo_root,
                branch_name,
                bucket,
                work_type,
                queue_payload,
                actor_id,
                exists=exists,
            )


def _seed_branch_state(repo_root: Path, branch_name: str, actor_id: str) -> None:
    """
    Seed branch state records in SQLite when missing.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        None: This function seeds branch tables when missing.
    """

    _seed_repo_state(repo_root, branch_name, actor_id)
    _seed_context_profiles(repo_root, branch_name, actor_id)
    _seed_architecture_contexts(repo_root, branch_name, actor_id)
    _seed_component_contexts(repo_root, branch_name, actor_id)
    _seed_branch_queues(repo_root, branch_name, actor_id)


def clone_branch(
    repo_root: Path,
    source_branch: str,
    dest_branch: str,
    agent_id: str,
    work_id: Optional[str],
    copy_context: bool,
    copy_work: bool,
    preserve_repo_state: bool,
    preserve_work_state: bool,
    activate: bool,
    force: bool,
) -> None:
    """
    Clone branch context and work queues into a destination branch.

    Args:
        repo_root (Path): Repository root.
        source_branch (str): Source branch name.
        dest_branch (str): Destination branch name.
        agent_id (str): Agent identifier.
        work_id (Optional[str]): Work id for work_mode enforcement.
        copy_context (bool): Copy context files if True.
        copy_work (bool): Copy work queues if True.
        preserve_repo_state (bool): Preserve scan counters/timestamps.
        preserve_work_state (bool): Preserve leases/in_progress if True.
        activate (bool): Switch active branch to the destination if True.
        force (bool): Overwrite destination branch if it exists.
    """
    ensure_certified(repo_root, agent_id)
    ensure_work_mode(repo_root, work_id, "clone branch state")
    actor_id = f"agent:{agent_id}"
    _ensure_source_branch(repo_root, source_branch, actor_id)
    _prepare_destination(repo_root, dest_branch, actor_id, force)

    _crud_register_branch(repo_root, dest_branch, actor_id)
    _seed_branch_state(repo_root, dest_branch, actor_id)

    if copy_context:
        branch_copy_context.copy_context(
            repo_root=repo_root,
            source_branch=source_branch,
            dest_branch=dest_branch,
            preserve_repo_state=preserve_repo_state,
            owner_id=agent_id,
        )
    if copy_work:
        branch_copy_work.copy_work(
            repo_root=repo_root,
            source_branch=source_branch,
            dest_branch=dest_branch,
            preserve_state=preserve_work_state,
            owner_id=agent_id,
        )

    if activate:
        branch_switch.switch_branch(
            repo_root=repo_root,
            branch_name=dest_branch,
            agent_id=agent_id,
            work_id=work_id,
        )



def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Clone a branch using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the destination branch name.

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
        copy_context = optional_bool(
            payload, "copy_context", command_name=command_name, default=True
        )
        copy_work = optional_bool(
            payload, "copy_work", command_name=command_name, default=True
        )
        preserve_repo_state = optional_bool(
            payload, "preserve_repo_state", command_name=command_name, default=False
        )
        preserve_work_state = optional_bool(
            payload, "preserve_work_state", command_name=command_name, default=False
        )
        activate = optional_bool(payload, "activate", command_name=command_name, default=False)
        force = optional_bool(payload, "force", command_name=command_name, default=False)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        clone_branch(
            repo_root=repo_root,
            source_branch=source_branch,
            dest_branch=dest_branch,
            agent_id=agent_id,
            work_id=work_id,
            copy_context=bool(copy_context),
            copy_work=bool(copy_work),
            preserve_repo_state=bool(preserve_repo_state),
            preserve_work_state=bool(preserve_work_state),
            activate=bool(activate),
            force=bool(force),
        )
        return ok_result(output={"branch_name": dest_branch})
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
    parser = argparse.ArgumentParser(description="Clone branch state and work queues.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--source-branch", required=True, help="Source branch name")
    parser.add_argument("--dest-branch", required=True, help="Destination branch name")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--no-context", action="store_true", help="Do not copy context state")
    parser.add_argument("--no-work", action="store_true", help="Do not copy work queues")
    parser.add_argument(
        "--preserve-repo-state",
        action="store_true",
        help="Preserve scan counters and timestamps",
    )
    parser.add_argument(
        "--preserve-work-state",
        action="store_true",
        help="Preserve leases and in_progress states",
    )
    parser.add_argument("--activate", action="store_true", help="Switch to the destination branch")
    parser.add_argument("--force", action="store_true", help="Overwrite destination branch if it exists")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    payload = {
        "repo_root": args.repo_root,
        "source_branch": args.source_branch,
        "dest_branch": args.dest_branch,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "copy_context": not args.no_context,
        "copy_work": not args.no_work,
        "preserve_repo_state": args.preserve_repo_state,
        "preserve_work_state": args.preserve_work_state,
        "activate": args.activate,
        "force": args.force,
    }
    context = ExecutionContext(
        command_name="branch_clone",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logging.getLogger(__name__).error("branch_clone failed: %s", result.errors)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
