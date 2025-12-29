"""
Review a context profile and update its grade, notes, and review counters.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.hashing import hash_json
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.paths import repo_relative_path


def _default_policies() -> dict:
    """
    Return default policy values for context profile reviews.

    Contract:
    - Only includes keys consumed by this module.
    - Values act as safe defaults when policies.json is missing.

    Returns:
        dict: Default policy values.
    """
    return {
        "lease_ttl_seconds": 300,
        "lock_wait_seconds": 10,
        "context_profiles_popular_usage_threshold": 10,
    }


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration with defaults applied.

    Contract:
    - Missing or invalid config leaves defaults intact.
    - Only whitelisted keys are applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies.
    """
    policies = _default_policies()
    config_path = repo_root / "context_compass" / "config" / "policies.json"
    if config_path.exists():
        data = load_json(config_path)
        if isinstance(data, dict):
            policies.update({key: value for key, value in data.items() if key in policies})
    return policies


def _profiles_path(repo_root: Path) -> Path:
    """
    Return the context profiles file path.

    Contract:
    - Always resolves under the active branch state root.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Context profiles JSON path.
    """
    return branch_paths.state_root(repo_root) / "context_profiles.json"


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


def _load_profiles(path: Path) -> dict:
    """
    Load context profiles data from disk.

    Contract:
    - Returns a JSON object payload on success.
    - Raises on missing files or invalid JSON.

    Args:
        path (Path): Context profiles path.

    Returns:
        dict: Context profiles data.

    Raises:
        FileNotFoundError: If the profiles file is missing.
        ValueError: If the profiles file is not valid JSON.
    """
    if not path.exists():
        raise FileNotFoundError(f"Missing context profiles file: {path}")
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("Context profiles JSON must be an object")
    return data


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
    - Matches work_management/tasks.json schema defaults.

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

    profiles_path = _profiles_path(repo_root)
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
        "ctx_path": repo_relative_path(repo_root, profiles_path),
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

    tasks_path = branch_paths.work_root(repo_root) / "active" / "tasks.json"
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lease.acquire_lock(locks_dir, tasks_path, owner_id, ttl_seconds=int(policies["lease_ttl_seconds"]))
    try:
        if tasks_path.exists():
            data = load_json(tasks_path)
            if not isinstance(data, dict):
                data = _default_tasks_queue(now)
        else:
            data = _default_tasks_queue(now)
        queue = data.setdefault("queue", [])
        if _upsert_task(queue, task, now):
            data["updated_at"] = now
            write_json_atomic(tasks_path, data)
    finally:
        lease.release_lock(locks_dir, tasks_path, owner_id)

    return work_id


def review_profile(
    repo_root: Path,
    profile_name: str,
    grade: str,
    reviewer: str,
    notes: Optional[str],
    agent_id: str,
    mode: str,
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
        mode (str): Agent mode for heartbeat.
        emit_tasks (bool): Whether to emit tasks based on review.
        owner_id (Optional[str]): Lock owner id override.
        work_id (Optional[str]): Work identifier for heartbeat.

    Returns:
        dict: Updated profile payload.
    """
    ensure_feature_enabled(repo_root, "context_profiles", "review context profiles")
    if emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    now = utc_now_iso()
    policies = _load_policies(repo_root)
    normalized_grade = grade.strip().lower()
    if normalized_grade not in _allowed_grades():
        raise ValueError(f"Invalid grade: {grade}")

    profiles_path = _profiles_path(repo_root)
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lease.acquire_lock(locks_dir, profiles_path, owner_id or agent_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        data = _load_profiles(profiles_path)
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
        write_json_atomic(profiles_path, data)
    finally:
        lease.release_lock(locks_dir, profiles_path, owner_id or agent_id)

    _emit_review_task(repo_root, profile, policies, owner_id or agent_id, emit_tasks)

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=str(profiles_path),
        notes=None,
        command_name="context_profiles_review",
        command_args=sys.argv[1:],
    )
    return profile


def main() -> None:
    """
    CLI entrypoint for context profile reviews.

    Contract:
    - Requires certification_state.json to be CERTIFIED.
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
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Do not emit optimize/prune tasks")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_feature_enabled(repo_root, "context_profiles", "review context profiles")
    if not args.no_emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    ensure_work_mode(repo_root, args.work_id, "review context profiles")

    reviewer = args.reviewer or args.agent_id
    profile = review_profile(
        repo_root=repo_root,
        profile_name=args.profile,
        grade=args.grade,
        reviewer=reviewer,
        notes=args.notes,
        agent_id=args.agent_id,
        mode=args.mode,
        emit_tasks=not args.no_emit_tasks,
        owner_id=args.agent_id,
        work_id=args.work_id,
    )
    logger.info("context profile reviewed: %s (%s)", profile.get("name"), profile.get("grade"))


if __name__ == "__main__":
    main()
