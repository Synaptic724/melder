"""
context_compass.tools.scan

Repository scanner for ctx staleness detection and task emission.
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

from context_compass.tools import lease, update_state
from context_compass.tools._shared import agent_presence, architecture_contexts, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.context_compass_configuration import load_configuration
from context_compass.tools._shared.feature_guard import (
    FeatureDisabledError,
    RepoStateDisabledError,
    ensure_feature_enabled,
)
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
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values used by the scanner.

    Returns:
        dict: Default policy values.
    """
    return {
        "lease_ttl_seconds": 300,
        "lock_wait_seconds": 10,
        "review_every_n_scans_default": 30,
        "dir_review_every_n_scans_default": 20,
        "max_task_attempts": 3,
        "architecture_context_good_ratio_threshold": 0.9,
        "architecture_context_stale_ratio_threshold": 0.75,
        "architecture_context_faulty_ratio_threshold": 0.6,
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
    locks_dir: Path, resource: Path, owner_id: str, ttl_seconds: int, wait_seconds: int
) -> dict:
    """
    Acquire a lock, waiting up to wait_seconds if necessary.

    Args:
        locks_dir (Path): Locks directory.
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
            return lease.acquire_lock(locks_dir, resource, owner_id, ttl_seconds)
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


def _load_ctx(path: Path) -> dict:
    """
    Load a ctx JSON file.

    Args:
        path (Path): Ctx file path.

    Returns:
        dict: Parsed ctx payload.

    Raises:
        ValueError: If the file is not valid JSON.
    """
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError("ctx file must be a JSON object")
    return data


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
    Write an error record and return its path.

    Args:
        repo_root (Path): Repository root.
        owner_id (str): Error owner id.
        target_path (Optional[str]): Target path.
        ctx_path (Optional[str]): Context path.
        category (str): Error category.
        message (str): Error message.
        details (dict): Error details.

    Returns:
        str: Repo-relative error record path.
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
    errors_dir = branch_paths.state_root(repo_root) / "errors"
    errors_dir.mkdir(parents=True, exist_ok=True)
    path = errors_dir / f"{error_id}.json"
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    policies = _load_policies(repo_root)
    _acquire_with_wait(locks_dir, path, owner_id, policies["lease_ttl_seconds"], policies["lock_wait_seconds"])
    try:
        write_json_atomic(path, record)
    finally:
        lease.release_lock(locks_dir, path, owner_id)
    return repo_relative_path(repo_root, path)


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


def _upsert_task(queue: list[dict], task: dict, now: str) -> bool:
    """
    Insert or update a task in a queue.

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


def _walk_repo(
    repo_root: Path,
    ignore_config: dict,
    language_config: dict,
) -> tuple[list[Path], list[Path]]:
    """
    Walk the repo and collect directories and code files.

    Args:
        repo_root (Path): Repository root.
        ignore_config (dict): Ignore configuration.
        language_config (dict): Language configuration.

    Returns:
        tuple[list[Path], list[Path]]: (directories, code files).
    """
    directories: list[Path] = []
    code_files: list[Path] = []
    only_roots = ignore_config.get("only_roots", [])

    for dirpath, dirnames, filenames in os.walk(repo_root):
        current_dir = Path(dirpath)
        rel_dir = repo_relative_dir(repo_root, current_dir)
        if not is_dir_relevant(rel_dir, only_roots):
            dirnames[:] = []
            continue
        if is_ignored_path(repo_root, current_dir, ignore_config):
            dirnames[:] = []
            continue

        directories.append(current_dir)
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
            if is_code:
                code_files.append(path)
    return directories, code_files


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


def _write_ctx_if_changed(
    repo_root: Path,
    ctx_path: Path,
    ctx: dict,
    original_computed: dict,
    new_computed: dict,
    owner_id: str,
    policies: dict,
) -> bool:
    """
    Write ctx JSON if computed content changed.

    Args:
        repo_root (Path): Repository root.
        ctx_path (Path): Ctx path.
        ctx (dict): Updated ctx payload.
        original_computed (dict): Original computed block.
        new_computed (dict): New computed block.
        owner_id (str): Lock owner id.
        policies (dict): Policy values.

    Returns:
        bool: True if file was written.
    """
    if original_computed == new_computed:
        return False
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    _acquire_with_wait(
        locks_dir,
        ctx_path,
        owner_id,
        policies["lease_ttl_seconds"],
        policies["lock_wait_seconds"],
    )
    try:
        write_json_atomic(ctx_path, ctx)
    finally:
        lease.release_lock(locks_dir, ctx_path, owner_id)


def _write_architecture_if_changed(
    repo_root: Path,
    target_path: Path,
    payload: dict,
    original_computed: dict,
    updated_computed: dict,
    owner_id: str,
    policies: dict,
) -> None:
    """
    Write architecture/component context JSON if computed content changed.

    Args:
        repo_root (Path): Repository root.
        target_path (Path): Target path.
        payload (dict): Updated payload.
        original_computed (dict): Original computed block.
        updated_computed (dict): Updated computed block.
        owner_id (str): Lock owner id.
        policies (dict): Policy values.
    """
    if original_computed == updated_computed:
        return
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lease.acquire_lock(locks_dir, target_path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        write_json_atomic(target_path, payload)
    finally:
        lease.release_lock(locks_dir, target_path, owner_id)


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
    target_path = architecture_contexts.artifact_path(repo_root, kind)
    rel_target = repo_relative_path(repo_root, target_path)
    task_kind = _architecture_task_kind(kind)

    if not target_path.exists():
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
            {"path": rel_target, "kind": kind, "state": "missing", "reasons": ["missing_architecture_context"]}
        )
        return

    try:
        payload = load_json(target_path)
    except Exception as exc:
        error_ref = _write_error_record(
            repo_root,
            agent_id,
            target_path=rel_target,
            ctx_path=rel_target,
            category="parse_error",
            message="invalid architecture context JSON",
            details={"error": str(exc)},
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

    if not isinstance(payload, dict):
        tasks.append(
            _build_task(
                task_kind,
                rel_target,
                rel_target,
                ["ctx_parse_error"],
                _priority_for_state("blocked"),
                now,
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

    evaluation = architecture_contexts.evaluate_matrix(repo_root, matrix)
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
            target_path,
            payload,
            original_computed,
            updated_computed,
            agent_id,
            policies,
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
    mode: str,
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
        mode (str): Agent mode for heartbeat.

    Returns:
        dict: Scan record payload.
    """
    now = utc_now_iso()
    policies = _load_policies(repo_root)
    ignore_config = load_ignore_config(repo_root)
    language_config = load_language_config(repo_root)

    repo_state_path = branch_paths.state_root(repo_root) / "repo_state.json"
    if repo_state_path.exists():
        repo_state = load_json(repo_state_path)
        if not isinstance(repo_state, dict):
            repo_state = {"scan_counter": 0}
    else:
        repo_state = {"scan_counter": 0}

    scan_counter = int(repo_state.get("scan_counter") or 0) + 1
    scan_id_value = scan_id or f"scan_{scan_counter:06d}"

    directories, code_files = _walk_repo(repo_root, ignore_config, language_config)

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
            "tasks_emitted": 0,
            "missing": 0,
            "stale": 0,
            "needs_review": 0,
            "blocked": 0,
        },
    }

    tasks: list[dict] = []
    error_records: list[str] = []

    for file_path in code_files:
        rel_path = repo_relative_path(repo_root, file_path)
        ctx_path = file_path.parent / f"__{file_path.stem}__.json"
        rel_ctx = repo_relative_path(repo_root, ctx_path)
        code_hash = file_hashes[rel_path]

        if not ctx_path.exists():
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

        try:
            ctx = _load_ctx(ctx_path)
        except Exception as exc:
            error_ref = _write_error_record(
                repo_root,
                agent_id,
                target_path=rel_path,
                ctx_path=rel_ctx,
                category="parse_error",
                message="invalid ctx JSON",
                details={"error": str(exc)},
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
            _write_ctx_if_changed(
                repo_root, ctx_path, updated, original_computed, updated.get("computed", {}), agent_id, policies
            )

    for directory in directories:
        rel_dir = repo_relative_dir(repo_root, directory)
        dir_name = directory.name
        ctx_path = directory / f"__{dir_name}__.dir.json"
        rel_ctx = repo_relative_path(repo_root, ctx_path)
        subtree_entries = dir_entries.get(rel_dir, [])
        subtree_hash = hash_subtree(subtree_entries)

        if not ctx_path.exists():
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

        try:
            ctx = _load_ctx(ctx_path)
        except Exception as exc:
            error_ref = _write_error_record(
                repo_root,
                agent_id,
                target_path=rel_dir,
                ctx_path=rel_ctx,
                category="parse_error",
                message="invalid ctx JSON",
                details={"error": str(exc)},
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
            _write_ctx_if_changed(
                repo_root, ctx_path, updated, original_computed, updated.get("computed", {}), agent_id, policies
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
        tasks_path = branch_paths.work_root(repo_root) / "active" / "tasks.json"
        tasks_path.parent.mkdir(parents=True, exist_ok=True)
        locks_dir = branch_paths.state_root(repo_root) / "locks"
        locks_dir.mkdir(parents=True, exist_ok=True)
        _acquire_with_wait(
            locks_dir,
            tasks_path,
            agent_id,
            policies["lease_ttl_seconds"],
            policies["lock_wait_seconds"],
        )
        try:
            if tasks_path.exists():
                data = load_json(tasks_path)
                if not isinstance(data, dict):
                    data = _default_queue(now)
            else:
                data = _default_queue(now)
            queue = data.setdefault("queue", [])
            updated_any = False
            for task in tasks:
                updated_any = _upsert_task(queue, task, now) or updated_any
            if updated_any:
                data["updated_at"] = now
                write_json_atomic(tasks_path, data)
        finally:
            lease.release_lock(locks_dir, tasks_path, agent_id)

    if not dry_run:
        scans_dir = branch_paths.state_root(repo_root) / "scans"
        scans_dir.mkdir(parents=True, exist_ok=True)
        scan_path = scans_dir / f"{scan_id_value}.json"
        locks_dir = branch_paths.state_root(repo_root) / "locks"
        locks_dir.mkdir(parents=True, exist_ok=True)
        _acquire_with_wait(
            locks_dir,
            scan_path,
            agent_id,
            policies["lease_ttl_seconds"],
            policies["lock_wait_seconds"],
        )
        try:
            write_json_atomic(scan_path, scan_record)
        finally:
            lease.release_lock(locks_dir, scan_path, agent_id)

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

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=None,
        notes=None,
        command_name="scan",
        command_args=sys.argv[1:],
    )
    return scan_record


def main() -> None:
    """
    CLI entrypoint for scanner execution.
    """
    parser = argparse.ArgumentParser(description="Scan repository for ctx staleness")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--scan-id", default=None, help="Scan identifier override")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--dry-run", action="store_true", help="Do not write outputs")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Disable task emission")
    parser.add_argument("--no-update-ctx", action="store_true", help="Do not update ctx computed fields")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_feature_enabled(repo_root, "scan", "run scanner")
    if not args.no_emit_tasks:
        ensure_feature_enabled(repo_root, "work_management", "emit work tasks")
    ensure_work_mode(repo_root, args.work_id, "run scanner")

    record = scan_repo(
        repo_root,
        agent_id=args.agent_id,
        scan_id=args.scan_id,
        work_id=args.work_id,
        dry_run=args.dry_run,
        emit_tasks=not args.no_emit_tasks,
        update_ctx=not args.no_update_ctx,
        mode=args.mode,
    )
    logger.info("scan completed: %s", record.get("scan_id"))


if __name__ == "__main__":
    main()
