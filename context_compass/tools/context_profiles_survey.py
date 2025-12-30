"""
Survey and rebuild context_profiles from existing ctx JSON and work queues.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Iterable, Optional

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.hashing import hash_file, hash_json, hash_subtree
from context_compass.tools._shared.ignore_rules import (
    is_code_file,
    is_dir_relevant,
    is_ignored_path,
    is_within_only_roots,
    load_ignore_config,
    load_language_config,
)
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.paths import repo_relative_dir, repo_relative_path
from context_compass.tools._shared.source_roots import load_source_roots
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values for context_profiles.

    Returns:
        dict: Default policy values.
    """
    return {
        "lease_ttl_seconds": 300,
        "lock_wait_seconds": 10,
        "context_profiles_max_items_per_profile": 25,
        "context_profiles_max_bytes_per_profile": 120000,
        "context_profiles_popular_usage_threshold": 10,
        "context_profiles_prune_score_threshold": 0.3,
        "context_profiles_optimize_score_threshold": 0.6,
    }


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration with defaults applied.

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
            policies.update({k: v for k, v in data.items() if k in policies})
    return policies


def _profiles_path(repo_root: Path) -> Path:
    """
    Return the context_profiles.json path.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Context profiles path.
    """
    return branch_paths.state_root(repo_root) / "context_profiles.json"


def _review_counts_template() -> dict:
    """
    Return an empty review counts payload.

    Returns:
        dict: Review counts payload.
    """
    return {"excellent": 0, "good": 0, "ok": 0, "poor": 0, "bad": 0}


def _default_profiles(now: str, limits: dict) -> dict:
    """
    Return a default context_profiles payload.

    Args:
        now (str): Current timestamp.
        limits (dict): Limits snapshot.

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


def _load_existing_profiles(path: Path) -> dict:
    """
    Load existing context_profiles.json if present.

    Args:
        path (Path): Context profiles path.

    Returns:
        dict: Existing profiles payload or empty default.
    """
    if not path.exists():
        return {}
    data = load_json(path)
    if isinstance(data, dict):
        return data
    return {}


def _collect_ctx_files(repo_root: Path, ignore_config: dict) -> list[Path]:
    """
    Collect ctx JSON files from the repo using ignore rules.

    Args:
        repo_root (Path): Repository root.
        ignore_config (dict): Ignore configuration.

    Returns:
        list[Path]: Context JSON paths.
    """
    only_roots = ignore_config.get("only_roots", [])
    ctx_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        current_dir = Path(dirpath)
        rel_dir = repo_relative_dir(repo_root, current_dir)
        if not is_dir_relevant(rel_dir, only_roots):
            dirnames[:] = []
            continue
        if is_ignored_path(repo_root, current_dir, ignore_config):
            dirnames[:] = []
            continue

        pruned_dirs = []
        for name in dirnames:
            candidate = current_dir / name
            rel_candidate = repo_relative_dir(repo_root, candidate)
            if not is_dir_relevant(rel_candidate, only_roots):
                continue
            if is_ignored_path(repo_root, candidate, ignore_config):
                continue
            pruned_dirs.append(name)
        dirnames[:] = pruned_dirs

        for filename in filenames:
            if not filename.startswith("__"):
                continue
            if not (filename.endswith(".json") or filename.endswith(".dir.json")):
                continue
            path = current_dir / filename
            if is_ignored_path(repo_root, path, ignore_config):
                continue
            if not is_within_only_roots(repo_root, path, only_roots):
                continue
            ctx_files.append(path)
    return ctx_files


def _load_ctx(path: Path) -> Optional[dict]:
    """
    Load a ctx JSON file safely.

    Args:
        path (Path): Ctx file path.

    Returns:
        Optional[dict]: Ctx payload or None if invalid.
    """
    try:
        data = load_json(path)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _normalize_code_file(path: Path) -> bool:
    """
    Return True if the path is a context artifact that should be skipped.

    Args:
        path (Path): File path.

    Returns:
        bool: True if this is a ctx artifact.
    """
    name = path.name
    if name.startswith("__") and name.endswith(".json"):
        return True
    if name.startswith("__") and name.endswith(".dir.json"):
        return True
    return False


def _collect_code_entries(
    repo_root: Path,
    start_dir: Path,
    ignore_config: dict,
    language_config: dict,
) -> list[str]:
    """
    Collect code file hash entries under a directory.

    Args:
        repo_root (Path): Repository root.
        start_dir (Path): Directory to scan.
        ignore_config (dict): Ignore configuration.
        language_config (dict): Language configuration.

    Returns:
        list[str]: Hash entries of the form "path:hash".
    """
    entries: list[str] = []
    only_roots = ignore_config.get("only_roots", [])
    for dirpath, dirnames, filenames in os.walk(start_dir):
        current_dir = Path(dirpath)
        rel_dir = repo_relative_dir(repo_root, current_dir)
        if not is_dir_relevant(rel_dir, only_roots):
            dirnames[:] = []
            continue
        if is_ignored_path(repo_root, current_dir, ignore_config):
            dirnames[:] = []
            continue

        pruned_dirs = []
        for name in dirnames:
            candidate = current_dir / name
            rel_candidate = repo_relative_dir(repo_root, candidate)
            if not is_dir_relevant(rel_candidate, only_roots):
                continue
            if is_ignored_path(repo_root, candidate, ignore_config):
                continue
            pruned_dirs.append(name)
        dirnames[:] = pruned_dirs

        for filename in filenames:
            path = current_dir / filename
            if is_ignored_path(repo_root, path, ignore_config):
                continue
            if not is_within_only_roots(repo_root, path, only_roots):
                continue
            if _normalize_code_file(path):
                continue
            is_code, _language = is_code_file(path, ignore_config, language_config)
            if not is_code:
                continue
            rel_path = repo_relative_path(repo_root, path)
            entries.append(f"{rel_path}:{hash_file(path)}")
    return entries


def _compute_dir_subtree_hash(
    repo_root: Path,
    dir_path: Path,
    ignore_config: dict,
    language_config: dict,
) -> str:
    """
    Compute a subtree hash for a directory using code files only.

    Args:
        repo_root (Path): Repository root.
        dir_path (Path): Directory path.
        ignore_config (dict): Ignore configuration.
        language_config (dict): Language configuration.

    Returns:
        str: SHA256 subtree hash.
    """
    entries = _collect_code_entries(repo_root, dir_path, ignore_config, language_config)
    return hash_subtree(entries)


def _dedupe_list(values: list[str]) -> list[str]:
    """
    Deduplicate a list while preserving order.

    Args:
        values (list[str]): Input values.

    Returns:
        list[str]: Deduplicated list.
    """
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _profile_state_from_reasons(reasons: list[str]) -> str:
    """
    Map staleness reasons to a profile freshness state.

    Args:
        reasons (list[str]): Staleness reasons.

    Returns:
        str: Freshness state.
    """
    if not reasons:
        return "fresh"
    lowered = {reason.lower() for reason in reasons}
    if "ctx_blocked" in lowered or "ctx_parse_error" in lowered:
        return "blocked"
    if lowered == {"ctx_needs_review"}:
        return "needs_review"
    return "stale"


def _compute_profile_inputs(
    repo_root: Path,
    paths: list[str],
    ignore_config: dict,
    language_config: dict,
    now: str,
) -> tuple[str, list[str], str, str]:
    """
    Compute profile freshness inputs and staleness state.

    Args:
        repo_root (Path): Repository root.
        paths (list[str]): Repo-relative ctx paths.
        ignore_config (dict): Ignore configuration.
        language_config (dict): Language configuration.
        now (str): Current timestamp.

    Returns:
        tuple[str, list[str], str, str]: (freshness_state, reasons, inputs_hash, last_checked_at).
    """
    records: list[dict] = []
    reasons: list[str] = []

    for rel_ctx in paths:
        ctx_path = repo_root / rel_ctx
        if not ctx_path.exists():
            reasons.append("ctx_missing")
            records.append(
                {
                    "ctx_path": rel_ctx,
                    "kind": None,
                    "ctx_state": "missing",
                    "expected_hash": None,
                    "actual_hash": None,
                }
            )
            continue

        ctx = _load_ctx(ctx_path)
        if ctx is None:
            reasons.append("ctx_parse_error")
            records.append(
                {
                    "ctx_path": rel_ctx,
                    "kind": None,
                    "ctx_state": "blocked",
                    "expected_hash": None,
                    "actual_hash": None,
                }
            )
            continue

        kind = ctx.get("kind")
        computed = ctx.get("computed", {})
        ctx_state = computed.get("freshness_state")
        checksums = computed.get("checksums", {})

        if ctx_state == "needs_review":
            reasons.append("ctx_needs_review")
        elif ctx_state in ("stale", "missing"):
            reasons.append("ctx_stale" if ctx_state == "stale" else "ctx_missing")
        elif ctx_state == "blocked":
            reasons.append("ctx_blocked")

        expected_hash = None
        actual_hash = None
        if kind == "file_ctx":
            expected_hash = checksums.get("code_hash_sha256")
            identity = ctx.get("identity", {})
            code_path = identity.get("path") if isinstance(identity, dict) else None
            if code_path:
                full_code = repo_root / code_path
                if full_code.exists():
                    actual_hash = hash_file(full_code)
                else:
                    reasons.append("code_missing")
        elif kind == "dir_ctx":
            expected_hash = checksums.get("subtree_hash_sha256")
            identity = ctx.get("identity", {})
            dir_path = identity.get("dir_path") if isinstance(identity, dict) else None
            if dir_path:
                full_dir = repo_root / dir_path
                if full_dir.exists():
                    actual_hash = _compute_dir_subtree_hash(repo_root, full_dir, ignore_config, language_config)
                else:
                    reasons.append("code_missing")
        else:
            reasons.append("ctx_unknown_kind")

        if expected_hash is None or actual_hash is None or expected_hash != actual_hash:
            reasons.append("hash_mismatch")

        records.append(
            {
                "ctx_path": rel_ctx,
                "kind": kind,
                "ctx_state": ctx_state,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
            }
        )

    reasons = _dedupe_list(reasons)
    inputs_hash = hash_json({"inputs": sorted(records, key=lambda item: item["ctx_path"])})
    freshness_state = _profile_state_from_reasons(reasons)
    return freshness_state, reasons, inputs_hash, now


def _paths_unique(paths: Iterable[str]) -> list[str]:
    """
    Deduplicate paths while preserving order.

    Args:
        paths (Iterable[str]): Input paths.

    Returns:
        list[str]: Unique paths in original order.
    """
    seen: set[str] = set()
    ordered: list[str] = []
    for item in paths:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _normalize_roots(roots: Iterable[str]) -> list[str]:
    """
    Normalize root entries to repo-relative POSIX paths.

    Args:
        roots (Iterable[str]): Root entries.

    Returns:
        list[str]: Normalized roots.
    """
    normalized: list[str] = []
    for root in roots:
        text = str(root).replace("\\", "/").lstrip("./").rstrip("/")
        if text:
            normalized.append(text)
    return normalized


def _paths_within_roots(paths: Iterable[str], roots: Iterable[str]) -> list[str]:
    """
    Filter paths to those within any root prefix.

    Args:
        paths (Iterable[str]): Repo-relative paths.
        roots (Iterable[str]): Root prefixes.

    Returns:
        list[str]: Paths within the given roots.
    """
    normalized_roots = _normalize_roots(roots)
    if not normalized_roots:
        return []
    selected: list[str] = []
    for path in paths:
        for root in normalized_roots:
            if path == root or path.startswith(root + "/"):
                selected.append(path)
                break
    return selected


def _apply_limits(paths: list[str], size_by_path: dict, max_items: int, max_bytes: int) -> tuple[list[str], int]:
    """
    Apply item and byte limits to a path list.

    Args:
        paths (list[str]): Candidate paths.
        size_by_path (dict): Size mapping.
        max_items (int): Maximum items.
        max_bytes (int): Maximum bytes.

    Returns:
        tuple[list[str], int]: Limited paths and total size.
    """
    selected: list[str] = []
    total = 0
    for path in paths:
        if len(selected) >= max_items:
            break
        size = int(size_by_path.get(path, 0))
        if max_bytes > 0 and total + size > max_bytes:
            break
        selected.append(path)
        total += size
    return selected, total


def _score_profile(usage_count: int, path_count: int, threshold: int) -> float:
    """
    Compute a deterministic score for a profile.

    Args:
        usage_count (int): Usage count.
        path_count (int): Number of paths in the profile.
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
    content_score = 1.0
    score = (0.7 * usage_score) + (0.3 * content_score)
    return round(score, 4)


def _grade_for_score(score: float) -> str:
    """
    Map a score to a grade.

    Args:
        score (float): Score value.

    Returns:
        str: Grade label.
    """
    if score >= 0.85:
        return "excellent"
    if score >= 0.7:
        return "good"
    if score >= 0.55:
        return "ok"
    if score >= 0.35:
        return "poor"
    return "bad"


def _task_work_id(kind: str, profile_name: str) -> str:
    """
    Build a stable work id for profile tasks.

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


def _emit_profile_tasks(
    repo_root: Path,
    profiles: list[dict],
    policies: dict,
    owner_id: str,
    dry_run: bool,
) -> list[str]:
    """
    Emit tasks based on profile grades and usage.

    Args:
        repo_root (Path): Repository root.
        profiles (list[dict]): Profile payloads.
        policies (dict): Policy values.
        owner_id (str): Lock owner id.
        dry_run (bool): If True, do not write tasks.

    Returns:
        list[str]: Work ids emitted.
    """
    threshold = int(policies["context_profiles_popular_usage_threshold"])
    emitted: list[str] = []
    tasks: list[dict] = []
    now = utc_now_iso()

    for profile in profiles:
        name = profile["name"]
        grade = profile["grade"]
        usage_count = int(profile.get("usage_count") or 0)
        if grade not in ("poor", "bad"):
            continue
        if usage_count >= threshold:
            kind = "optimize_context_profile"
            priority = 70
        else:
            kind = "prune_context_profile"
            priority = 50
        work_id = _task_work_id(kind, name)
        reason = [f"profile:{name}", f"grade:{grade}"]
        task = {
            "work_id": work_id,
            "state": "queued",
            "kind": kind,
            "target_path": f"context_profile:{name}",
            "ctx_path": repo_relative_path(repo_root, profiles_path),
            "reason": reason,
            "parent_work_id": None,
            "root_work_id": work_id,
            "priority": priority,
            "lease": None,
            "attempts": 0,
            "last_error_ref": None,
            "created_at": now,
            "updated_at": now,
        }
        tasks.append(task)
        emitted.append(work_id)

    if dry_run or not tasks:
        return emitted

    tasks_path = branch_paths.work_root(repo_root) / "active" / "tasks.json"
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lock_wait = int(policies["lock_wait_seconds"])
    lease_ttl = int(policies["lease_ttl_seconds"])
    lease.acquire_lock(locks_dir, tasks_path, owner_id, ttl_seconds=lease_ttl)
    try:
        if tasks_path.exists():
            data = load_json(tasks_path)
            if not isinstance(data, dict):
                data = _default_tasks_queue(now)
        else:
            data = _default_tasks_queue(now)
        queue = data.setdefault("queue", [])
        updated_any = False
        for task in tasks:
            updated_any = _upsert_task(queue, task, now) or updated_any
        if updated_any:
            data["updated_at"] = now
            write_json_atomic(tasks_path, data)
    finally:
        lease.release_lock(locks_dir, tasks_path, owner_id)

    return emitted


def _collect_active_ctx_paths(repo_root: Path) -> list[str]:
    """
    Collect ctx_path values referenced by active work queues and agent queues.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Context paths.
    """
    ctx_paths: list[str] = []
    active_dir = branch_paths.work_root(repo_root) / "active"
    for name in ("epics.json", "stories.json", "tasks.json"):
        queue_path = active_dir / name
        if not queue_path.exists():
            continue
        data = load_json(queue_path)
        if not isinstance(data, dict):
            continue
        for item in data.get("queue", []):
            if isinstance(item, dict) and item.get("ctx_path"):
                ctx_paths.append(item["ctx_path"])

    agents_dir = repo_root / "context_compass" / "self_context" / "agents"
    if agents_dir.exists():
        for work_path in agents_dir.glob("*.work.json"):
            data = load_json(work_path)
            if not isinstance(data, dict):
                continue
            for item in data.get("queue", []):
                if isinstance(item, dict) and item.get("ctx_path"):
                    ctx_paths.append(item["ctx_path"])

    return ctx_paths


def survey_profiles(
    repo_root: Path,
    agent_id: str,
    mode: str,
    dry_run: bool,
    emit_tasks: bool,
    work_id: Optional[str] = None,
) -> dict:
    """
    Rebuild context_profiles.json from ctx JSON and work queues.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        mode (str): Agent mode.
        dry_run (bool): If True, do not write files.
        emit_tasks (bool): Whether to emit tasks.
        work_id (Optional[str]): Work identifier for heartbeat.

    Returns:
        dict: Context profiles payload.
    """
    ensure_feature_enabled(repo_root, "context_profiles", "survey context profiles")
    if emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    now = utc_now_iso()
    policies = _load_policies(repo_root)
    limits = {
        "max_items_per_profile": int(policies["context_profiles_max_items_per_profile"]),
        "max_bytes_per_profile": int(policies["context_profiles_max_bytes_per_profile"]),
    }

    ignore_config = load_ignore_config(repo_root)
    language_config = load_language_config(repo_root)
    ctx_paths = _collect_ctx_files(repo_root, ignore_config)
    size_by_path: dict[str, int] = {}
    ctx_rel_paths: list[str] = []

    entrypoints: list[str] = []
    high_coupling: list[tuple[str, int]] = []
    top_dirs_by_inventory: list[tuple[str, int]] = []
    top_level_dirs: list[str] = []

    source_roots = load_source_roots(repo_root)
    prod_roots = source_roots.get("prod_roots", [])
    test_roots = source_roots.get("test_roots", [])

    for ctx_path in ctx_paths:
        rel_ctx = repo_relative_path(repo_root, ctx_path)
        size_by_path[rel_ctx] = ctx_path.stat().st_size if ctx_path.exists() else 0
        ctx_rel_paths.append(rel_ctx)
        ctx = _load_ctx(ctx_path)
        if ctx is None:
            continue
        kind = ctx.get("kind")
        agent_section = ctx.get("agent", {})
        if not isinstance(agent_section, dict):
            agent_section = {}

        if kind == "file_ctx":
            public_surface = agent_section.get("public_surface", {})
            entry = public_surface.get("entrypoints", []) if isinstance(public_surface, dict) else []
            if entry:
                entrypoints.append(rel_ctx)
            dependents = agent_section.get("dependents", {})
            used_by_files = dependents.get("used_by_files", []) if isinstance(dependents, dict) else []
            high_coupling.append((rel_ctx, len(used_by_files)))
        elif kind == "dir_ctx":
            integration = agent_section.get("integration", {})
            entry = integration.get("entrypoints", []) if isinstance(integration, dict) else []
            if entry:
                entrypoints.append(rel_ctx)
            inventory = agent_section.get("inventory", {})
            files = inventory.get("files", []) if isinstance(inventory, dict) else []
            top_dirs_by_inventory.append((rel_ctx, len(files)))

            parent = Path(rel_ctx).parent
            if len(parent.parts) <= 1:
                top_level_dirs.append(rel_ctx)

    active_ctx_paths = _collect_active_ctx_paths(repo_root)
    active_ctx_paths = _paths_unique(active_ctx_paths)
    entrypoints = _paths_unique(entrypoints)
    top_level_dirs = _paths_unique(top_level_dirs)

    prod_ctx_paths = _paths_unique(_paths_within_roots(ctx_rel_paths, prod_roots))
    test_ctx_paths = _paths_unique(_paths_within_roots(ctx_rel_paths, test_roots))

    high_coupling_sorted = [path for path, _count in sorted(high_coupling, key=lambda item: item[1], reverse=True)]
    top_dirs_sorted = [path for path, _count in sorted(top_dirs_by_inventory, key=lambda item: item[1], reverse=True)]

    profile_defs = [
        {"name": "repo_overview", "paths": top_level_dirs, "reason": "top_level_dirs"},
        {"name": "prod_overview", "paths": prod_ctx_paths, "reason": "prod_roots"},
        {"name": "tests_overview", "paths": test_ctx_paths, "reason": "test_roots"},
        {"name": "active_work", "paths": active_ctx_paths, "reason": "active_work_queue"},
        {"name": "entrypoints", "paths": entrypoints, "reason": "entrypoints"},
        {"name": "high_coupling", "paths": high_coupling_sorted, "reason": "dependents"},
        {"name": "top_dirs_by_inventory", "paths": top_dirs_sorted, "reason": "inventory"},
    ]

    profiles_path = _profiles_path(repo_root)
    existing = _load_existing_profiles(profiles_path)
    existing_profiles = {p.get("name"): p for p in existing.get("profiles", []) if isinstance(p, dict)}

    profiles: list[dict] = []
    for profile_def in profile_defs:
        name = profile_def["name"]
        paths = _paths_unique(profile_def["paths"])
        paths, size_bytes = _apply_limits(paths, size_by_path, limits["max_items_per_profile"], limits["max_bytes_per_profile"])
        existing_profile = existing_profiles.get(name, {})
        usage_count = int(existing_profile.get("usage_count") or 0)
        score = _score_profile(usage_count, len(paths), int(policies["context_profiles_popular_usage_threshold"]))
        grade = existing_profile.get("grade")
        last_review_at = existing_profile.get("last_review_at")
        if grade is None or last_review_at is None:
            grade = _grade_for_score(score)
            last_review_at = existing_profile.get("last_review_at")

        review_counts = existing_profile.get("review_counts") or _review_counts_template()
        for key in _review_counts_template():
            review_counts.setdefault(key, 0)

        freshness_state, staleness_reasons, inputs_hash, last_checked_at = _compute_profile_inputs(
            repo_root,
            paths,
            ignore_config,
            language_config,
            now,
        )

        profiles.append(
            {
                "name": name,
                "paths": paths,
                "score": score,
                "grade": grade,
                "usage_count": usage_count,
                "last_used_at": existing_profile.get("last_used_at"),
                "last_review_at": last_review_at,
                "last_review_notes": existing_profile.get("last_review_notes"),
                "last_reviewed_by": existing_profile.get("last_reviewed_by"),
                "review_counts": review_counts,
                "reason": profile_def["reason"],
                "size_bytes": size_bytes,
                "freshness_state": freshness_state,
                "staleness_reasons": staleness_reasons,
                "inputs_hash": inputs_hash,
                "last_checked_at": last_checked_at,
                "updated_at": now,
            }
        )

    profiles_sorted = sorted(profiles, key=lambda item: item["name"])
    payload = _default_profiles(now, limits)
    payload["profiles"] = profiles_sorted

    if not dry_run:
        policies_lock = int(policies["lease_ttl_seconds"])
        lock_wait = int(policies["lock_wait_seconds"])
        locks_dir = branch_paths.state_root(repo_root) / "locks"
        locks_dir.mkdir(parents=True, exist_ok=True)
        profiles_path.parent.mkdir(parents=True, exist_ok=True)
        lease.acquire_lock(locks_dir, profiles_path, agent_id, ttl_seconds=policies_lock)
        try:
            if existing != payload:
                write_json_atomic(profiles_path, payload)
        finally:
            lease.release_lock(locks_dir, profiles_path, agent_id)

        if emit_tasks:
            _emit_profile_tasks(repo_root, profiles_sorted, policies, agent_id, dry_run=False)

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=str(profiles_path),
        notes=None,
        command_name="context_profiles_survey",
        command_args=sys.argv[1:],
    )
    return payload


def main() -> None:
    """
    CLI entrypoint for context_profiles survey.
    """
    parser = argparse.ArgumentParser(description="Survey and rebuild context_profiles.json")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--dry-run", action="store_true", help="Do not write outputs")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Do not emit tasks")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    ensure_feature_enabled(repo_root, "context_profiles", "survey context profiles")
    if not args.no_emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    ensure_work_mode(repo_root, args.work_id, "survey context profiles")

    payload = survey_profiles(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        dry_run=args.dry_run,
        emit_tasks=not args.no_emit_tasks,
        work_id=args.work_id,
    )
    logger.info("context profiles updated: %s profiles", len(payload.get("profiles", [])))


if __name__ == "__main__":
    main()
