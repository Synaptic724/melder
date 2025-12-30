"""
Read a context profile and emit consolidated context JSON for agent consumption.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import context_profiles_survey, lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.hashing import hash_json
from context_compass.tools._shared.ignore_rules import load_ignore_config, load_language_config
from context_compass.tools._shared.json_io import dump_minified, load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.paths import repo_relative_path


def _default_policies() -> dict:
    """
    Return default policy values for context profile reading.

    Contract:
    - Only includes keys consumed by this module.
    - Values act as safe defaults when policies.json is missing.

    Returns:
        dict: Default policy values.
    """
    return {
        "lease_ttl_seconds": 300,
        "lock_wait_seconds": 10,
        "context_profiles_max_items_per_profile": 25,
        "context_profiles_max_bytes_per_profile": 120000,
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

    profiles_path = _profiles_path(repo_root)
    now = utc_now_iso()
    work_id = _task_work_id("resurvey_context_profile", profile_name)
    task = {
        "work_id": work_id,
        "state": "queued",
        "kind": "resurvey_context_profile",
        "target_path": f"context_profile:{profile_name}",
        "ctx_path": repo_relative_path(repo_root, profiles_path),
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

    tasks_path = branch_paths.work_root(repo_root) / "active" / "tasks.json"
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    policies = _load_policies(repo_root)
    lease.acquire_lock(locks_dir, tasks_path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
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


def _read_ctx_item(repo_root: Path, rel_path: str) -> tuple[Optional[dict], int, Optional[str]]:
    """
    Read a ctx JSON file and return its payload and size.

    Contract:
    - Returns a payload, size_bytes, and optional error string.
    - Does not raise on parse errors; returns an error message instead.

    Args:
        repo_root (Path): Repository root.
        rel_path (str): Repo-relative ctx path.

    Returns:
        tuple[Optional[dict], int, Optional[str]]: Payload, size bytes, error message.
    """
    full_path = repo_root / rel_path
    if not full_path.exists():
        return None, 0, "missing"
    size_bytes = full_path.stat().st_size
    try:
        data = load_json(full_path)
    except Exception as exc:
        return None, size_bytes, str(exc)
    if not isinstance(data, dict):
        return None, size_bytes, "ctx JSON must be an object"
    return data, size_bytes, None


def read_profile(
    repo_root: Path,
    profile_name: str,
    agent_id: str,
    mode: str,
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
        mode (str): Agent mode for heartbeat.
        max_items (Optional[int]): Optional max items override.
        max_bytes (Optional[int]): Optional max bytes override.
        update_usage (bool): Whether to increment usage_count.
        emit_tasks (bool): Whether to emit resurvey tasks.
        owner_id (Optional[str]): Lock owner id override.
        work_id (Optional[str]): Work identifier for heartbeat.

    Returns:
        dict: Output payload with profile metadata and ctx items.
    """
    ensure_feature_enabled(repo_root, "context_profiles", "read context profiles")
    if emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    now = utc_now_iso()
    policies = _load_policies(repo_root)
    effective_max_items = _resolve_limit(policies["context_profiles_max_items_per_profile"], max_items)
    effective_max_bytes = _resolve_limit(policies["context_profiles_max_bytes_per_profile"], max_bytes)

    profiles_path = _profiles_path(repo_root)
    data = _load_profiles(profiles_path)
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
        paths,
        ignore_config,
        language_config,
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
        ctx_payload, size_bytes, error = _read_ctx_item(repo_root, rel_path)
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
        locks_dir = branch_paths.state_root(repo_root) / "locks"
        locks_dir.mkdir(parents=True, exist_ok=True)
        lease.acquire_lock(locks_dir, profiles_path, owner_id or agent_id, ttl_seconds=policies["lease_ttl_seconds"])
        try:
            latest = _load_profiles(profiles_path)
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
            write_json_atomic(profiles_path, latest)
        finally:
            lease.release_lock(locks_dir, profiles_path, owner_id or agent_id)

    if emit_tasks and (freshness_changed or reasons_changed or inputs_changed) and freshness_state != "fresh":
        _emit_resurvey_task(repo_root, profile_name, freshness_state, staleness_reasons, owner_id or agent_id)

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=str(profiles_path),
        notes=None,
        command_name="context_profiles_read",
        command_args=sys.argv[1:],
    )
    return payload


def main() -> None:
    """
    CLI entrypoint for context profile reads.

    Contract:
    - Emits minified JSON to stdout unless --output is provided.
    - Requires agent profile certification_state to be CERTIFIED.
    """
    parser = argparse.ArgumentParser(description="Read a context profile and emit ctx JSON")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--profile", required=True, help="Profile name")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--max-items", type=int, default=None, help="Max items (clamped to policy)")
    parser.add_argument("--max-bytes", type=int, default=None, help="Max bytes (clamped to policy)")
    parser.add_argument("--no-update", action="store_true", help="Do not update usage_count")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Do not emit resurvey tasks")
    parser.add_argument("--output", default=None, help="Optional output JSON path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    ensure_feature_enabled(repo_root, "context_profiles", "read context profiles")
    if not args.no_emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    ensure_work_mode(repo_root, args.work_id, "read context profiles")

    payload = read_profile(
        repo_root=repo_root,
        profile_name=args.profile,
        agent_id=args.agent_id,
        mode=args.mode,
        max_items=args.max_items,
        max_bytes=args.max_bytes,
        update_usage=not args.no_update,
        emit_tasks=not args.no_emit_tasks,
        owner_id=args.agent_id,
        work_id=args.work_id,
    )

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(output_path, payload)
        logger.info("context profile output written to %s", output_path)
        return

    sys.stdout.write(dump_minified(payload) + "\n")


if __name__ == "__main__":
    main()
