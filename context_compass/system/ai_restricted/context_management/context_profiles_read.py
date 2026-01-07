"""
Read a context profile and return consolidated context payloads.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.context_management import context_profiles_survey
from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_int,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.hashing import hash_json
from context_compass.system.ai_restricted._shared.ignore_rules import load_ignore_config, load_language_config
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1
DEFAULT_LEASE_TTL_SECONDS = 300
DEFAULT_LOCK_WAIT_SECONDS = 10
DEFAULT_MAX_ITEMS_PER_PROFILE = 25
DEFAULT_MAX_BYTES_PER_PROFILE = 120000


def _default_policies() -> dict:
    """
    Return default policy values for context profile reading.

    Contract:
    - Only includes keys consumed by this module.
    - Values act as safe defaults when policy tables are unavailable.

    Returns:
        dict: Default policy values for context profile reading.
    """
    return {
        "lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS,
        "lock_wait_seconds": DEFAULT_LOCK_WAIT_SECONDS,
        "context_profiles_max_items_per_profile": DEFAULT_MAX_ITEMS_PER_PROFILE,
        "context_profiles_max_bytes_per_profile": DEFAULT_MAX_BYTES_PER_PROFILE,
    }


def _load_policies(repo_root: Path, actor_id: str) -> dict:
    """
    Load policy configuration with defaults applied.

    Contract:
    - Requires policy tables in system.db.
    - Only whitelisted keys are returned to callers.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies for context profile reading.

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
    lock_wait = record.get("lock_wait_seconds")
    max_items = record.get("context_profiles_max_items_per_profile")
    max_bytes = record.get("context_profiles_max_bytes_per_profile")
    if isinstance(lease_ttl, int):
        defaults["lease_ttl_seconds"] = lease_ttl
    if isinstance(lock_wait, int):
        defaults["lock_wait_seconds"] = lock_wait
    if isinstance(max_items, int):
        defaults["context_profiles_max_items_per_profile"] = max_items
    if isinstance(max_bytes, int):
        defaults["context_profiles_max_bytes_per_profile"] = max_bytes
    return defaults


def _current_branch(repo_root: Path) -> str:
    """
    Load the active branch name for SQLite-backed profile reads.

    Args:
        repo_root (Path): Repository root.

    Returns:
        str: Active branch name.
    """
    return branch_paths.load_current_branch(repo_root)


def _profiles_ref(branch_name: str) -> str:
    """
    Build a reference string for branch context_profiles records.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        str: Context profiles reference for work queue tasks.
    """
    return f"sqlite:branch:{branch_name}:context_profiles"


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
            query_name="read_context_profiles",
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
            query_name="write_context_profiles",
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


def _profiles_lock_resource(branch_name: str) -> Path:
    """
    Build a synthetic lock resource path for context_profiles writes.

    Args:
        branch_name (str): Branch identifier.

    Returns:
        Path: Resource path for lease locks.

    Contract:
        - Matches the lock resource format used by context_profiles writers.
        - Does not touch the filesystem.
    """

    return Path(f"branch_context_profiles::{branch_name}")


def _work_queue_lock_resource(branch_name: str, bucket: str, work_type: str) -> Path:
    """
    Build a synthetic lock resource path for branch work queue writes.

    Args:
        branch_name (str): Branch identifier.
        bucket (str): Work bucket name.
        work_type (str): Work kind name.

    Returns:
        Path: Resource path for lease locks.

    Contract:
        - Matches the lock resource format used by branch work queues.
        - Does not touch the filesystem.
    """

    return Path(f"branch_work_queue::{branch_name}::{bucket}::{work_type}")


def _load_profiles(repo_root: Path, branch_name: str, actor_id: str) -> tuple[dict, bool]:
    """
    Load context profiles data from SQLite.

    Contract:
    - Returns a JSON object payload on success.
    - Raises on missing records or invalid payloads.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Context profiles payload and existence flag.

    Raises:
        FileNotFoundError: If the profiles record is missing.
        ValueError: If the profiles payload is invalid.
    """
    record, exists = _read_context_profiles(repo_root, branch_name, actor_id)
    if not exists:
        raise FileNotFoundError("Missing context profiles record.")
    if not isinstance(record, dict):
        raise ValueError("Context profiles payload must be an object")
    return record, exists


def _find_profile(data: dict, profile_name: str) -> dict:
    """
    Locate a profile by name.

    Contract:
    - Returns the first matching profile payload.
    - Raises KeyError when no match exists.

    Args:
        data (dict): Context profiles data.
        profile_name (str): Profile name.

    Returns:
        dict: Profile payload.

    Raises:
        KeyError: If the profile does not exist.
    """
    for profile in data.get("profiles", []):
        if isinstance(profile, dict) and profile.get("name") == profile_name:
            return profile
    raise KeyError(f"Context profile not found: {profile_name}")


def _resolve_limit(policy_value: int, override_value: Optional[int]) -> int:
    """
    Resolve a limit value, clamped to the policy default.

    Contract:
    - Overrides cannot exceed policy defaults.
    - Non-positive overrides fall back to the policy value.

    Args:
        policy_value (int): Policy limit value.
        override_value (Optional[int]): Optional override.

    Returns:
        int: Effective limit value.
    """
    if override_value is None:
        return int(policy_value)
    if override_value <= 0:
        return int(policy_value)
    return min(int(policy_value), int(override_value))


def _task_work_id(kind: str, profile_name: str) -> str:
    """
    Build a stable work id for resurvey tasks.

    Args:
        kind (str): Task kind.
        profile_name (str): Profile name.

    Returns:
        str: Work identifier.
    """
    digest = hash_json({"kind": kind, "profile": profile_name})[:12]
    return f"task_{digest}"


def _default_tasks_queue(now: str) -> dict:
    """
    Return a default work_management tasks queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Tasks queue payload.
    """
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _upsert_task(queue: list[dict], task: dict, now: str) -> bool:
    """
    Insert or update a task in the queue.

    Contract:
    - Does not override leased or in_progress tasks.

    Args:
        queue (list[dict]): Task queue.
        task (dict): Task payload.
        now (str): Current timestamp.

    Returns:
        bool: True if queue was modified.
    """
    for existing in queue:
        if existing.get("work_id") != task.get("work_id"):
            continue
        if existing.get("state") in ("leased", "in_progress"):
            return False
        existing["state"] = "queued"
        existing["reason"] = task["reason"]
        existing["priority"] = task["priority"]
        existing["lease"] = None
        existing["last_error_ref"] = task.get("last_error_ref")
        existing["updated_at"] = now
        return True
    queue.append(task)
    return True


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


def _priority_for_state(state: str) -> int:
    """
    Return a priority value for a given staleness state.

    Args:
        state (str): Freshness state.

    Returns:
        int: Priority value.
    """
    if state == "blocked":
        return 90
    if state == "stale":
        return 80
    if state == "needs_review":
        return 60
    return 50


def _emit_resurvey_task(
    repo_root: Path,
    profile_name: str,
    freshness_state: str,
    staleness_reasons: list[str],
    owner_id: str,
) -> Optional[str]:
    """
    Emit a resurvey_context_profile task.

    Args:
        repo_root (Path): Repository root.
        profile_name (str): Profile name.
        freshness_state (str): Current freshness state.
        staleness_reasons (list[str]): Staleness reasons.
        owner_id (str): Lock owner id.

    Returns:
        Optional[str]: Work id emitted or None.
    """
    if freshness_state == "fresh":
        return None

    branch_name = _current_branch(repo_root)
    now = utc_now_iso()
    work_id = _task_work_id("resurvey_context_profile", profile_name)
    task = {
        "work_id": work_id,
        "state": "queued",
        "kind": "resurvey_context_profile",
        "target_path": f"context_profile:{profile_name}",
        "ctx_path": _profiles_ref(branch_name),
        "reason": [f"profile:{profile_name}", f"state:{freshness_state}"] + staleness_reasons,
        "parent_work_id": None,
        "root_work_id": work_id,
        "priority": _priority_for_state(freshness_state),
        "lease": None,
        "attempts": 0,
        "last_error_ref": None,
        "created_at": now,
        "updated_at": now,
    }

    queue: list[dict] = []
    _upsert_task(queue, task, now)

    policies = _load_policies(repo_root, owner_id)
    resource = _work_queue_lock_resource(branch_name, "ready", "task")
    lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        _upsert_work_queue_tasks(
            repo_root,
            branch_name,
            "ready",
            "task",
            queue,
            owner_id,
            schema_version=1,
            repo_id=None,
        )
    finally:
        lease.release_lock(repo_root, resource, owner_id)

    return work_id


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


def _read_ctx_item(
    repo_root: Path,
    branch_name: str,
    rel_path: str,
    actor_id: str,
) -> tuple[Optional[dict], int, Optional[str]]:
    """
    Read a ctx payload from SQLite and return its payload and size.

    Contract:
    - Returns a payload, size_bytes, and optional error string.
    - Does not raise on parse errors; returns an error message instead.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        rel_path (str): Repo-relative ctx path.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[Optional[dict], int, Optional[str]]: Payload, size bytes, error message.
    """
    file_payload, file_exists = _read_file_ctx_by_ctx_path(
        repo_root, branch_name, rel_path, actor_id
    )
    if file_exists:
        if not isinstance(file_payload, dict):
            return None, 0, "ctx payload must be an object"
        data = json.dumps(
            file_payload,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return file_payload, len(data.encode("utf-8")), None

    dir_payload, dir_exists = _read_dir_ctx_by_ctx_path(
        repo_root, branch_name, rel_path, actor_id
    )
    if dir_exists:
        if not isinstance(dir_payload, dict):
            return None, 0, "ctx payload must be an object"
        data = json.dumps(
            dir_payload,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return dir_payload, len(data.encode("utf-8")), None

    return None, 0, "missing"


def read_profile(
    repo_root: Path,
    profile_name: str,
    agent_id: str,
    max_items: Optional[int],
    max_bytes: Optional[int],
    update_usage: bool,
    emit_tasks: bool,
    owner_id: Optional[str] = None,
    work_id: Optional[str] = None,
) -> dict:
    """
    Read a context profile, optionally updating usage counters.

    Contract:
    - Returns consolidated ctx content for the named profile.
    - Updates usage_count and last_used_at when update_usage is True.
    - Applies policy limits to max_items and max_bytes.
    - Updates profile freshness fields when inputs drift.
    - Emits resurvey tasks when freshness changes and emit_tasks is True.

    Args:
        repo_root (Path): Repository root.
        profile_name (str): Profile name.
        agent_id (str): Agent identifier.
        max_items (Optional[int]): Optional max items override.
        max_bytes (Optional[int]): Optional max bytes override.
        update_usage (bool): Whether to increment usage_count.
        emit_tasks (bool): Whether to emit resurvey tasks.
        owner_id (Optional[str]): Lock owner id override.
        work_id (Optional[str]): Work identifier label.

    Returns:
        dict: Output payload with profile metadata and ctx items.
    """
    ensure_feature_enabled(repo_root, "context_profiles", "read context profiles")
    if emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    now = utc_now_iso()
    policies = _load_policies(repo_root, owner_id or agent_id)
    effective_max_items = _resolve_limit(policies["context_profiles_max_items_per_profile"], max_items)
    effective_max_bytes = _resolve_limit(policies["context_profiles_max_bytes_per_profile"], max_bytes)

    branch_name = _current_branch(repo_root)
    data, _exists = _load_profiles(repo_root, branch_name, owner_id or agent_id)
    profile = _find_profile(data, profile_name)
    paths = profile.get("paths", [])
    if not isinstance(paths, list):
        raise ValueError("Profile paths must be a list")

    ignore_config = load_ignore_config(repo_root)
    language_config = load_language_config(repo_root)
    (
        freshness_state,
        staleness_reasons,
        inputs_hash,
        last_checked_at,
    ) = context_profiles_survey._compute_profile_inputs(
        repo_root,
        branch_name,
        paths,
        ignore_config,
        language_config,
        agent_id,
        now,
    )

    stored_state = profile.get("freshness_state")
    stored_reasons = profile.get("staleness_reasons") or []
    stored_inputs_hash = profile.get("inputs_hash")
    freshness_changed = stored_state != freshness_state
    reasons_changed = stored_reasons != staleness_reasons
    inputs_changed = stored_inputs_hash != inputs_hash
    should_update_profile = update_usage or freshness_changed or reasons_changed or inputs_changed
    effective_checked_at = last_checked_at if should_update_profile else profile.get("last_checked_at")

    items: list[dict] = []
    missing_paths: list[str] = []
    errors: list[dict] = []
    total_bytes = 0
    truncated = False

    for rel_path in paths:
        if effective_max_items > 0 and len(items) >= effective_max_items:
            truncated = True
            break
        ctx_payload, size_bytes, error = _read_ctx_item(
            repo_root, branch_name, rel_path, agent_id
        )
        if error == "missing":
            missing_paths.append(rel_path)
            continue
        if ctx_payload is None:
            errors.append({"path": rel_path, "error": error or "unknown"})
            continue
        if effective_max_bytes > 0 and total_bytes + size_bytes > effective_max_bytes:
            truncated = True
            break
        items.append({"path": rel_path, "size_bytes": size_bytes, "ctx": ctx_payload})
        total_bytes += size_bytes

    payload = {
        "profile": {
            "name": profile.get("name"),
            "grade": profile.get("grade"),
            "score": profile.get("score"),
            "usage_count": profile.get("usage_count"),
            "last_used_at": profile.get("last_used_at"),
            "last_review_at": profile.get("last_review_at"),
            "reason": profile.get("reason"),
            "freshness_state": freshness_state,
            "staleness_reasons": staleness_reasons,
            "inputs_hash": inputs_hash,
            "last_checked_at": effective_checked_at,
        },
        "limits": {"max_items": effective_max_items, "max_bytes": effective_max_bytes},
        "summary": {
            "total_items": len(items),
            "total_bytes": total_bytes,
            "truncated": truncated,
            "missing_paths": missing_paths,
            "errors": errors,
        },
        "items": items,
        "generated_at": now,
    }

    if should_update_profile:
        resource = _profiles_lock_resource(branch_name)
        lease.acquire_lock(
            repo_root,
            resource,
            owner_id or agent_id,
            ttl_seconds=policies["lease_ttl_seconds"],
        )
        try:
            latest, exists = _load_profiles(repo_root, branch_name, owner_id or agent_id)
            target = _find_profile(latest, profile_name)
            if update_usage:
                usage_count = int(target.get("usage_count") or 0)
                target["usage_count"] = usage_count + 1
                target["last_used_at"] = now
            if freshness_changed or reasons_changed or inputs_changed or update_usage:
                target["freshness_state"] = freshness_state
                target["staleness_reasons"] = staleness_reasons
                target["inputs_hash"] = inputs_hash
                target["last_checked_at"] = last_checked_at
            target["updated_at"] = now
            latest["updated_at"] = now
            _write_context_profiles(
                repo_root,
                branch_name,
                latest,
                actor_id=owner_id or agent_id,
                exists=exists,
            )
        finally:
            lease.release_lock(repo_root, resource, owner_id or agent_id)

    if emit_tasks and (freshness_changed or reasons_changed or inputs_changed) and freshness_state != "fresh":
        _emit_resurvey_task(repo_root, profile_name, freshness_state, staleness_reasons, owner_id or agent_id)

    return payload


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Read a context profile using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the context profile payload.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id and profile.
        - Enforces certification, feature flags, and work mode guards.
        - Returns context profile payloads (no JSON output emission).
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        profile_name = require_string(payload, "profile", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        max_items = optional_int(payload, "max_items", command_name=command_name)
        max_bytes = optional_int(payload, "max_bytes", command_name=command_name)
        update_usage = optional_bool(payload, "update_usage", command_name=command_name, default=True)
        emit_tasks = optional_bool(payload, "emit_tasks", command_name=command_name, default=True)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "context_profiles", "read context profiles")
        if emit_tasks:
            ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
        ensure_work_mode(repo_root, work_id, "read context profiles")
        profile_payload = read_profile(
            repo_root=repo_root,
            profile_name=profile_name,
            agent_id=agent_id,
            max_items=max_items,
            max_bytes=max_bytes,
            update_usage=bool(update_usage),
            emit_tasks=bool(emit_tasks),
            owner_id=agent_id,
            work_id=work_id,
        )
        return ok_result(
            output={
                "context_profile": profile_payload,
            }
        )
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for context profile reads.

    Contract:
    - Requires agent profile certification_state to be CERTIFIED.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Read a context profile")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--profile", required=True, help="Profile name")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--max-items", type=int, default=None, help="Max items (clamped to policy)")
    parser.add_argument("--max-bytes", type=int, default=None, help="Max bytes (clamped to policy)")
    parser.add_argument("--no-update", action="store_true", help="Do not update usage_count")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Do not emit resurvey tasks")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "profile": args.profile,
        "work_id": args.work_id,
        "max_items": args.max_items,
        "max_bytes": args.max_bytes,
        "update_usage": not args.no_update,
        "emit_tasks": not args.no_emit_tasks,
    }
    context = ExecutionContext(
        command_name="context_profiles_read",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("context_profiles_read failed: %s", result.errors)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
