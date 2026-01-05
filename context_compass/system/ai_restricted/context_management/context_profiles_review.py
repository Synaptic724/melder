"""
Review a context profile and update its grade, notes, and review counters.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_string,
    require_choice,
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
from context_compass.system.ai_restricted._shared.timeutils import utc_now_iso
from context_compass.system.ai_restricted.system_management.command_runner import (
    CommandResult,
    ExecutionContext,
)

CONFIG_POLICIES_TABLE = "config_policies_core"
CONFIG_POLICIES_ACTION = "by_config_id"
CONFIG_POLICIES_ID = 1
DEFAULT_LEASE_TTL_SECONDS = 300
DEFAULT_LOCK_WAIT_SECONDS = 10
DEFAULT_POPULAR_USAGE_THRESHOLD = 10


def _default_policies() -> dict:
    """
    Return default policy values for context profile reviews.

    Contract:
    - Only includes keys consumed by this module.
    - Values act as safe defaults when policy tables are unavailable.

    Returns:
        dict: Default policy values for context profile reviews.
    """
    return {
        "lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS,
        "lock_wait_seconds": DEFAULT_LOCK_WAIT_SECONDS,
        "context_profiles_popular_usage_threshold": DEFAULT_POPULAR_USAGE_THRESHOLD,
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
        dict: Effective policies for context profile reviews.

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
    popular_threshold = record.get("context_profiles_popular_usage_threshold")
    if isinstance(lease_ttl, int):
        defaults["lease_ttl_seconds"] = lease_ttl
    if isinstance(lock_wait, int):
        defaults["lock_wait_seconds"] = lock_wait
    if isinstance(popular_threshold, int):
        defaults["context_profiles_popular_usage_threshold"] = popular_threshold
    return defaults


def _current_branch(repo_root: Path) -> str:
    """
    Load the active branch name for SQLite-backed profile updates.

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


def _allowed_grades() -> list[str]:
    """
    Return allowed grade values.

    Contract:
    - Grade values are lowercase and stable across tools.

    Returns:
        list[str]: Allowed grades.
    """
    return ["excellent", "good", "ok", "poor", "bad"]


def _review_counts_template() -> dict:
    """
    Return a review counts payload template.

    Contract:
    - Includes all grade keys with integer counts.

    Returns:
        dict: Review counts template.
    """
    return {"excellent": 0, "good": 0, "ok": 0, "poor": 0, "bad": 0}


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


def _score_profile(usage_count: int, path_count: int, threshold: int) -> float:
    """
    Compute a deterministic profile score.

    Contract:
    - Output is stable for identical inputs.
    - Score ranges from 0.0 to 1.0.

    Args:
        usage_count (int): Usage count.
        path_count (int): Number of paths.
        threshold (int): Popular usage threshold.

    Returns:
        float: Score between 0 and 1.
    """
    if path_count <= 0:
        return 0.0
    if threshold <= 0:
        usage_score = 0.0
    else:
        usage_score = min(1.0, float(usage_count) / float(threshold))
    score = (0.7 * usage_score) + 0.3
    return round(score, 4)


def _task_work_id(kind: str, profile_name: str) -> str:
    """
    Build a stable work id for profile tasks.

    Contract:
    - Identical kind/profile pairs always yield the same work_id.

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

    Contract:
    - Matches tasks.schema.json defaults for queue payloads.

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
    - Updates timestamps when changes are applied.

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


def _emit_review_task(
    repo_root: Path,
    profile: dict,
    policies: dict,
    owner_id: str,
    emit_tasks: bool,
) -> Optional[str]:
    """
    Emit a work_management task based on review grade.

    Contract:
    - Emits optimize/prune tasks only for poor/bad grades.
    - Uses stable work_id and upsert semantics.

    Args:
        repo_root (Path): Repository root.
        profile (dict): Profile payload.
        policies (dict): Policy values.
        owner_id (str): Lock owner id.
        emit_tasks (bool): Whether to emit tasks.

    Returns:
        Optional[str]: Work id emitted or None.
    """
    grade = str(profile.get("grade") or "").lower()
    if grade not in ("poor", "bad"):
        return None
    if not emit_tasks:
        return None

    branch_name = _current_branch(repo_root)
    usage_count = int(profile.get("usage_count") or 0)
    threshold = int(policies["context_profiles_popular_usage_threshold"])
    if usage_count >= threshold:
        kind = "optimize_context_profile"
        priority = 70
    else:
        kind = "prune_context_profile"
        priority = 50

    now = utc_now_iso()
    work_id = _task_work_id(kind, str(profile.get("name")))
    task = {
        "work_id": work_id,
        "state": "queued",
        "kind": kind,
        "target_path": f"context_profile:{profile.get('name')}",
        "ctx_path": _profiles_ref(branch_name),
        "reason": ["context_profile_review", f"profile:{profile.get('name')}", f"grade:{grade}"],
        "parent_work_id": None,
        "root_work_id": work_id,
        "priority": priority,
        "lease": None,
        "attempts": 0,
        "last_error_ref": None,
        "created_at": now,
        "updated_at": now,
    }

    queue: list[dict] = []
    _upsert_task(queue, task, now)

    resource = _work_queue_lock_resource(branch_name, "ready", "task")
    lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds=int(policies["lease_ttl_seconds"]))
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


def review_profile(
    repo_root: Path,
    profile_name: str,
    grade: str,
    reviewer: str,
    notes: Optional[str],
    agent_id: str,
    emit_tasks: bool,
    owner_id: Optional[str] = None,
    work_id: Optional[str] = None,
) -> dict:
    """
    Review a context profile and update its grade and review counters.

    Contract:
    - Updates grade, last_review_at, review_counts, and updated_at.
    - Recomputes score based on usage and path count.
    - Optionally emits optimize/prune tasks when grade is poor/bad.

    Args:
        repo_root (Path): Repository root.
        profile_name (str): Profile name.
        grade (str): Review grade.
        reviewer (str): Reviewer identifier.
        notes (Optional[str]): Optional review notes.
        agent_id (str): Agent identifier.
        emit_tasks (bool): Whether to emit tasks based on review.
        owner_id (Optional[str]): Lock owner id override.
        work_id (Optional[str]): Work identifier label.

    Returns:
        dict: Updated profile payload.
    """
    ensure_feature_enabled(repo_root, "context_profiles", "review context profiles")
    if emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    now = utc_now_iso()
    policies = _load_policies(repo_root, owner_id or agent_id)
    normalized_grade = grade.strip().lower()
    if normalized_grade not in _allowed_grades():
        raise ValueError(f"Invalid grade: {grade}")

    branch_name = _current_branch(repo_root)
    resource = _profiles_lock_resource(branch_name)
    lease.acquire_lock(
        repo_root,
        resource,
        owner_id or agent_id,
        ttl_seconds=policies["lease_ttl_seconds"],
    )
    try:
        data, exists = _load_profiles(repo_root, branch_name, owner_id or agent_id)
        profile = _find_profile(data, profile_name)
        paths = profile.get("paths", [])
        path_count = len(paths) if isinstance(paths, list) else 0
        usage_count = int(profile.get("usage_count") or 0)
        score = _score_profile(usage_count, path_count, int(policies["context_profiles_popular_usage_threshold"]))

        review_counts = profile.get("review_counts") or _review_counts_template()
        for key, value in _review_counts_template().items():
            review_counts.setdefault(key, value)
        review_counts[normalized_grade] = int(review_counts.get(normalized_grade) or 0) + 1

        profile["grade"] = normalized_grade
        profile["score"] = score
        profile["last_review_at"] = now
        profile["last_reviewed_by"] = reviewer
        profile["last_review_notes"] = notes
        profile["review_counts"] = review_counts
        profile["updated_at"] = now
        data["updated_at"] = now
        _write_context_profiles(
            repo_root,
            branch_name,
            data,
            actor_id=owner_id or agent_id,
            exists=exists,
        )
    finally:
        lease.release_lock(repo_root, resource, owner_id or agent_id)

    _emit_review_task(repo_root, profile, policies, owner_id or agent_id, emit_tasks)

    return profile


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Review a context profile using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the reviewed profile payload.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id, profile, and grade.
        - Enforces certification, feature flags, and work mode guards.
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
        grade = require_choice(payload, "grade", command_name, _allowed_grades())
        reviewer = optional_string(payload, "reviewer", command_name=command_name)
        notes = optional_string(payload, "notes", command_name=command_name)
        emit_tasks = optional_bool(payload, "emit_tasks", command_name=command_name, default=True)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "context_profiles", "review context profiles")
        if emit_tasks:
            ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
        ensure_work_mode(repo_root, work_id, "review context profiles")
        profile = review_profile(
            repo_root=repo_root,
            profile_name=profile_name,
            grade=grade,
            reviewer=reviewer or agent_id,
            notes=notes,
            agent_id=agent_id,
            emit_tasks=bool(emit_tasks),
            owner_id=agent_id,
            work_id=work_id,
        )
        return ok_result(output={"profile": profile})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for context profile reviews.

    Contract:
    - Requires agent profile certification_state to be CERTIFIED.
    - Emits optimize/prune tasks unless --no-emit-tasks is set.
    """
    parser = argparse.ArgumentParser(description="Review a context profile")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--profile", required=True, help="Profile name")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--grade", required=True, help="Review grade")
    parser.add_argument("--reviewer", default=None, help="Reviewer identifier (defaults to agent-id)")
    parser.add_argument("--notes", default=None, help="Optional review notes")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Do not emit optimize/prune tasks")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "profile": args.profile,
        "work_id": args.work_id,
        "grade": args.grade,
        "reviewer": args.reviewer,
        "notes": args.notes,
        "emit_tasks": not args.no_emit_tasks,
    }
    context = ExecutionContext(
        command_name="context_profiles_review",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("context_profiles_review failed: %s", result.errors)
        raise SystemExit(1)
    profile = result.output.get("profile", {})
    logger.info("context profile reviewed: %s (%s)", profile.get("name"), profile.get("grade"))


if __name__ == "__main__":
    main()
