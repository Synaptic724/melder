"""
Survey and rebuild context_profiles from SQLite-backed ctx records and work queues.
"""

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Iterable, Optional

from context_compass.system.ai_restricted.database_management import sqlite_crud, sqlite_query
from context_compass.system.ai_restricted.system_management import lease
from context_compass.system.ai_restricted._shared import branch_paths
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
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.hashing import hash_file, hash_json, hash_subtree
from context_compass.system.ai_restricted._shared.ignore_rules import (
    is_code_file,
    is_dir_relevant,
    is_ignored_path,
    is_included_path,
    load_ignore_config,
    load_language_config,
)
from context_compass.system.ai_restricted._shared.paths import repo_relative_dir, repo_relative_path
from context_compass.system.ai_restricted._shared.source_roots import load_source_roots
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
DEFAULT_MAX_ITEMS_PER_PROFILE = 25
DEFAULT_MAX_BYTES_PER_PROFILE = 120000
DEFAULT_POPULAR_USAGE_THRESHOLD = 10
DEFAULT_PRUNE_SCORE_THRESHOLD = 0.3
DEFAULT_OPTIMIZE_SCORE_THRESHOLD = 0.6


def _default_policies() -> dict:
    """
    Return default policy values for context_profiles.

    Returns:
        dict: Default policy values for context_profiles.
    """
    return {
        "lease_ttl_seconds": DEFAULT_LEASE_TTL_SECONDS,
        "lock_wait_seconds": DEFAULT_LOCK_WAIT_SECONDS,
        "context_profiles_max_items_per_profile": DEFAULT_MAX_ITEMS_PER_PROFILE,
        "context_profiles_max_bytes_per_profile": DEFAULT_MAX_BYTES_PER_PROFILE,
        "context_profiles_popular_usage_threshold": DEFAULT_POPULAR_USAGE_THRESHOLD,
        "context_profiles_prune_score_threshold": DEFAULT_PRUNE_SCORE_THRESHOLD,
        "context_profiles_optimize_score_threshold": DEFAULT_OPTIMIZE_SCORE_THRESHOLD,
    }


def _load_policies(repo_root: Path, actor_id: str) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies for context_profiles.

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
    popular_threshold = record.get("context_profiles_popular_usage_threshold")
    prune_threshold = record.get("context_profiles_prune_score_threshold")
    optimize_threshold = record.get("context_profiles_optimize_score_threshold")
    if isinstance(lease_ttl, int):
        defaults["lease_ttl_seconds"] = lease_ttl
    if isinstance(lock_wait, int):
        defaults["lock_wait_seconds"] = lock_wait
    if isinstance(max_items, int):
        defaults["context_profiles_max_items_per_profile"] = max_items
    if isinstance(max_bytes, int):
        defaults["context_profiles_max_bytes_per_profile"] = max_bytes
    if isinstance(popular_threshold, int):
        defaults["context_profiles_popular_usage_threshold"] = popular_threshold
    if isinstance(prune_threshold, (int, float)):
        defaults["context_profiles_prune_score_threshold"] = prune_threshold
    if isinstance(optimize_threshold, (int, float)):
        defaults["context_profiles_optimize_score_threshold"] = optimize_threshold
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
        bucket (str): Queue bucket name.
        work_type (str): Work kind name.

    Returns:
        Path: Resource path for lease locks.

    Contract:
        - Matches the lock resource format used by branch work queues.
        - Does not touch the filesystem.
    """

    return Path(f"branch_work_queue::{branch_name}::{bucket}::{work_type}")


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

    Contract:
        - Returns a payload dict even when exists is False.
        - Does not mutate the underlying payload.
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


def _load_existing_profiles(repo_root: Path, branch_name: str, actor_id: str) -> tuple[dict, bool]:
    """
    Load existing context_profiles record if present.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        tuple[dict, bool]: Existing profiles payload and existence flag.
    """
    record, exists = _read_context_profiles(repo_root, branch_name, actor_id)
    if not isinstance(record, dict):
        return {}, exists
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


def _ctx_payload_size(payload: dict) -> int:
    """
    Compute the serialized size for a ctx payload.

    Args:
        payload (dict): Ctx payload.

    Returns:
        int: Size in bytes for minified JSON.
    """
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return len(data.encode("utf-8"))


def _list_file_ctx_payloads(repo_root: Path, branch_name: str, actor_id: str) -> list[dict]:
    """
    List file_ctx payloads for a branch via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: List of file_ctx payloads.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="list_file_ctx_payloads",
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    records = result.get("records")
    if not isinstance(records, list):
        raise ValueError("list_file_ctx_payloads returned an invalid records payload.")
    return records


def _list_dir_ctx_payloads(repo_root: Path, branch_name: str, actor_id: str) -> list[dict]:
    """
    List dir_ctx payloads for a branch via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: List of dir_ctx payloads.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="list_dir_ctx_payloads",
            payload={"branch_name": branch_name},
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    records = result.get("records")
    if not isinstance(records, list):
        raise ValueError("list_dir_ctx_payloads returned an invalid records payload.")
    return records


def _collect_ctx_payloads(
    repo_root: Path,
    branch_name: str,
    ignore_config: dict,
    actor_id: str,
) -> list[dict]:
    """
    Collect ctx payloads from SQLite using ignore rules.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        ignore_config (dict): Ignore configuration.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Context payloads.
    """
    include_dirs = ignore_config.get("include_dirs", [])
    payloads = _list_file_ctx_payloads(repo_root, branch_name, actor_id)
    payloads.extend(_list_dir_ctx_payloads(repo_root, branch_name, actor_id))
    filtered: list[dict] = []
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        identity = payload.get("identity", {})
        if not isinstance(identity, dict):
            continue
        kind = payload.get("kind")
        if kind == "file_ctx":
            file_path = identity.get("path")
            ctx_path = identity.get("ctx_path")
            if not isinstance(file_path, str) or not isinstance(ctx_path, str):
                continue
            if not is_dir_relevant(
                repo_relative_dir(repo_root, repo_root / file_path),
                include_dirs,
            ):
                continue
            if is_ignored_path(repo_root, repo_root / file_path, ignore_config):
                continue
            if not is_included_path(repo_root, repo_root / ctx_path, ignore_config):
                continue
        elif kind == "dir_ctx":
            dir_path = identity.get("dir_path")
            ctx_path = identity.get("ctx_path")
            if not isinstance(dir_path, str) or not isinstance(ctx_path, str):
                continue
            if not is_dir_relevant(
                repo_relative_dir(repo_root, repo_root / dir_path),
                include_dirs,
            ):
                continue
            if is_ignored_path(repo_root, repo_root / dir_path, ignore_config):
                continue
            if not is_included_path(repo_root, repo_root / ctx_path, ignore_config):
                continue
        else:
            continue
        filtered.append(payload)
    filtered.sort(
        key=lambda payload: payload.get("identity", {}).get("ctx_path", "")
    )
    return filtered


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


def _load_ctx_payload(
    repo_root: Path,
    branch_name: str,
    ctx_path: str,
    actor_id: str,
) -> Optional[dict]:
    """
    Load a ctx payload from SQLite by ctx_path.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        ctx_path (str): Repo-relative ctx path.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        Optional[dict]: Ctx payload or None if missing/invalid.
    """
    file_payload, file_exists = _read_file_ctx_by_ctx_path(
        repo_root, branch_name, ctx_path, actor_id
    )
    if file_exists and isinstance(file_payload, dict):
        return file_payload
    dir_payload, dir_exists = _read_dir_ctx_by_ctx_path(
        repo_root, branch_name, ctx_path, actor_id
    )
    if dir_exists and isinstance(dir_payload, dict):
        return dir_payload
    return None


def _normalize_code_file(path: Path) -> bool:
    """
    Return True if the path should be excluded from code scanning.

    Args:
        path (Path): File path.

    Returns:
        bool: True if the file should be skipped.
    """
    name = path.name
    if name == "__init__.py":
        return True
    if os.name == "nt" and name.lower() == "__init__.py":
        return True
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
    include_dirs = ignore_config.get("include_dirs", [])
    for dirpath, dirnames, filenames in os.walk(start_dir):
        current_dir = Path(dirpath)
        rel_dir = repo_relative_dir(repo_root, current_dir)
        if not is_dir_relevant(rel_dir, include_dirs):
            dirnames[:] = []
            continue
        if is_ignored_path(repo_root, current_dir, ignore_config):
            dirnames[:] = []
            continue

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
            if is_ignored_path(repo_root, path, ignore_config):
                continue
            if not is_included_path(repo_root, path, ignore_config):
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
    branch_name: str,
    paths: list[str],
    ignore_config: dict,
    language_config: dict,
    actor_id: str,
    now: str,
) -> tuple[str, list[str], str, str]:
    """
    Compute profile freshness inputs and staleness state.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        paths (list[str]): Repo-relative ctx paths.
        ignore_config (dict): Ignore configuration.
        language_config (dict): Language configuration.
        actor_id (str): Actor identifier for audit logging.
        now (str): Current timestamp.

    Returns:
        tuple[str, list[str], str, str]: (freshness_state, reasons, inputs_hash, last_checked_at).
    """
    records: list[dict] = []
    reasons: list[str] = []

    for rel_ctx in paths:
        ctx = _load_ctx_payload(repo_root, branch_name, rel_ctx, actor_id)
        if ctx is None:
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
    branch_name = _current_branch(repo_root)

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
            "ctx_path": _profiles_ref(branch_name),
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

    queue: list[dict] = []
    for task in tasks:
        _upsert_task(queue, task, now)

    lease_ttl = int(policies["lease_ttl_seconds"])
    resource = _work_queue_lock_resource(branch_name, "ready", "task")
    lease.acquire_lock(repo_root, resource, owner_id, ttl_seconds=lease_ttl)
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

    return emitted


def _list_active_ctx_paths(
    repo_root: Path,
    branch_name: str,
    actor_id: str,
) -> list[str]:
    """
    List ctx_path values referenced by active work queues via sqlite_query.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[str]: Context paths.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.

    Contract:
        - Uses default ready/active buckets and epic/story/task work types.
        - Includes agent work queues in the result payload.
    """

    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name="list_active_ctx_paths",
            payload={
                "branch_name": branch_name,
                "buckets": ["ready", "active"],
                "work_types": ["epic", "story", "task"],
                "include_agent_queues": True,
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    ctx_paths = result.get("ctx_paths")
    if not isinstance(ctx_paths, list):
        raise ValueError("list_active_ctx_paths returned an invalid ctx_paths payload.")
    return ctx_paths


def _collect_active_ctx_paths(repo_root: Path) -> list[str]:
    """
    Collect ctx_path values referenced by ready/active work queues and agent queues.

    Args:
        repo_root (Path): Repository root.

    Returns:
        list[str]: Context paths.
    """
    branch_name = _current_branch(repo_root)
    actor_id = "system:context_profiles_survey"
    return _list_active_ctx_paths(repo_root, branch_name, actor_id)


def survey_profiles(
    repo_root: Path,
    agent_id: str,
    dry_run: bool,
    emit_tasks: bool,
    work_id: Optional[str] = None,
) -> dict:
    """
    Rebuild context_profiles records from ctx JSON and work queues.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        dry_run (bool): If True, do not write files.
        emit_tasks (bool): Whether to emit tasks.
        work_id (Optional[str]): Work identifier label.

    Returns:
        dict: Context profiles payload.
    """
    ensure_feature_enabled(repo_root, "context_profiles", "survey context profiles")
    if emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    now = utc_now_iso()
    actor_id = agent_id
    policies = _load_policies(repo_root, actor_id)
    limits = {
        "max_items_per_profile": int(policies["context_profiles_max_items_per_profile"]),
        "max_bytes_per_profile": int(policies["context_profiles_max_bytes_per_profile"]),
    }

    ignore_config = load_ignore_config(repo_root)
    language_config = load_language_config(repo_root)
    branch_name = _current_branch(repo_root)
    ctx_payloads = _collect_ctx_payloads(repo_root, branch_name, ignore_config, actor_id)
    size_by_path: dict[str, int] = {}
    ctx_rel_paths: list[str] = []

    entrypoints: list[str] = []
    high_coupling: list[tuple[str, int]] = []
    top_dirs_by_inventory: list[tuple[str, int]] = []
    top_level_dirs: list[str] = []

    source_roots = load_source_roots(repo_root)
    prod_roots = source_roots.get("prod_roots", [])
    test_roots = source_roots.get("test_roots", [])

    for payload in ctx_payloads:
        if not isinstance(payload, dict):
            continue
        identity = payload.get("identity", {})
        if not isinstance(identity, dict):
            continue
        ctx_path = identity.get("ctx_path")
        if not isinstance(ctx_path, str) or not ctx_path:
            continue
        rel_ctx = repo_relative_path(repo_root, repo_root / ctx_path)
        size_by_path[rel_ctx] = _ctx_payload_size(payload)
        ctx_rel_paths.append(rel_ctx)
        ctx = payload
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

    existing, exists = _load_existing_profiles(repo_root, branch_name, agent_id)
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
            branch_name,
            paths,
            ignore_config,
            language_config,
            agent_id,
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
        resource = _profiles_lock_resource(branch_name)
        lease.acquire_lock(repo_root, resource, agent_id, ttl_seconds=policies_lock)
        try:
            if existing != payload:
                _write_context_profiles(
                    repo_root,
                    branch_name,
                    payload,
                    actor_id=agent_id,
                    exists=exists,
                )
        finally:
            lease.release_lock(repo_root, resource, agent_id)

        if emit_tasks:
            _emit_profile_tasks(repo_root, profiles_sorted, policies, agent_id, dry_run=False)

    return payload


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Survey context profiles using the command runner contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing the context profiles payload.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id.
        - Enforces certification, feature flags, and work mode guards.
        - emit_tasks defaults to True.
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        dry_run = optional_bool(payload, "dry_run", command_name=command_name, default=False)
        emit_tasks = optional_bool(payload, "emit_tasks", command_name=command_name, default=True)
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "context_profiles", "survey context profiles")
        if emit_tasks:
            ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
        ensure_work_mode(repo_root, work_id, "survey context profiles")
        profiles_payload = survey_profiles(
            repo_root,
            agent_id=agent_id,
            dry_run=bool(dry_run),
            emit_tasks=bool(emit_tasks),
            work_id=work_id,
        )
        return ok_result(output={"context_profiles": profiles_payload})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for context_profiles survey.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Survey and rebuild context_profiles records")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--dry-run", action="store_true", help="Do not write outputs")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Do not emit tasks")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "dry_run": args.dry_run,
        "emit_tasks": not args.no_emit_tasks,
    }
    context = ExecutionContext(
        command_name="context_profiles_survey",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("context_profiles_survey failed: %s", result.errors)
        raise SystemExit(1)
    profiles_payload = result.output.get("context_profiles", {})
    logger.info(
        "context profiles updated: %s profiles",
        len(profiles_payload.get("profiles", [])),
    )


if __name__ == "__main__":
    main()
