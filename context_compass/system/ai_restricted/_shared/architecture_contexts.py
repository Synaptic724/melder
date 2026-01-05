"""
Helpers for architecture/component context artifacts.
"""

import os
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared.hashing import hash_json
from context_compass.system.ai_restricted._shared.ignore_rules import (
    is_dir_relevant,
    is_ignored_path,
    is_included_path,
)
from context_compass.system.ai_restricted._shared.paths import repo_relative_dir, repo_relative_path
from context_compass.system.ai_restricted._shared.source_roots import load_source_roots
from context_compass.system.ai_restricted.database_management import sqlite_query


def default_architecture_context(kind: str, now: str) -> dict:
    """
    Return a default architecture_context payload.

    Args:
        kind (str): Artifact kind.
        now (str): Current timestamp.

    Returns:
        dict: Default architecture context payload.
    """
    return {
        "schema_version": 1,
        "kind": kind,
        "updated_at": now,
        "agent": {
            "summary": {
                "one_liner": "Architecture context derived from directory ctx.",
                "detail": "This artifact is generated from directory ctx only.",
            },
            "directories": [],
        },
        "computed": {
            "freshness_state": "blocked",
            "holes_count": 0,
            "holes_ratio": None,
            "good_ratio": None,
            "inputs_hash": hash_json({"matrix": []}),
            "last_checked_at": None,
            "matrix": [],
            "staleness_reasons": ["no_citations"],
        },
    }


def default_component_contexts(kind: str, now: str) -> dict:
    """
    Return a default component_contexts payload.

    Args:
        kind (str): Artifact kind.
        now (str): Current timestamp.

    Returns:
        dict: Default component contexts payload.
    """
    return {
        "schema_version": 1,
        "kind": kind,
        "updated_at": now,
        "agent": {
            "summary": {
                "one_liner": "Component contexts derived from directory ctx.",
                "detail": "Each component references directory ctx citations only.",
            }
        },
        "components": [],
        "computed": {
            "freshness_state": "blocked",
            "holes_count": 0,
            "holes_ratio": None,
            "good_ratio": None,
            "inputs_hash": hash_json({"matrix": []}),
            "last_checked_at": None,
            "matrix": [],
            "staleness_reasons": ["no_citations"],
        },
    }


def _normalize_roots(roots: list[str], ignore_roots: list[str]) -> list[str]:
    """
    Return effective roots for ctx collection.

    Args:
        roots (list[str]): Target roots from SQLite source root configuration.
        ignore_roots (list[str]): include_dirs from ignore configuration.

    Returns:
        list[str]: Effective roots list.
    """
    if roots:
        return roots
    return ignore_roots


def _roots_for_target(repo_root: Path, target: str, ignore_config: dict) -> Optional[list[str]]:
    """
    Return source roots for prod/test targets.

    Args:
        repo_root (Path): Repository root.
        target (str): Target scope ("prod" or "test").
        ignore_config (dict): Ignore configuration.

    Returns:
        list[str]: Root paths.
    """
    source_roots = load_source_roots(repo_root)
    prod_roots = source_roots.get("prod_roots", [])
    test_roots = source_roots.get("test_roots", [])
    if target == "test":
        if not test_roots:
            return None
        return _normalize_roots(test_roots, [])
    return _normalize_roots(prod_roots, ignore_config.get("include_dirs", []))


def collect_dir_ctx_payloads(
    repo_root: Path,
    branch_name: str,
    target: str,
    ignore_config: dict,
    actor_id: str,
) -> list[dict]:
    """
    Collect directory ctx payloads for the given target scope.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        target (str): Target scope ("prod" or "test").
        ignore_config (dict): Ignore configuration.
        actor_id (str): Actor identifier for query audit logging.

    Returns:
        list[dict]: Directory ctx payloads for the branch.

    Raises:
        ValueError: If query payloads or ctx payloads are malformed.
        sqlite_query.SqliteQueryError: If the query request fails.

    Contract:
        - Requires a registered list_dir_ctx_payloads query.
        - Applies ignore/include filters before returning payloads.
    """
    include_dirs = _roots_for_target(repo_root, target, ignore_config)
    if target == "test" and not include_dirs:
        return []

    ctx_payloads = _list_dir_ctx_payloads(repo_root, branch_name, actor_id)
    filtered: list[dict] = []
    for payload in ctx_payloads:
        if not isinstance(payload, dict):
            continue
        identity = payload.get("identity", {})
        if not isinstance(identity, dict):
            continue
        dir_path = identity.get("dir_path")
        ctx_path = identity.get("ctx_path")
        if not isinstance(dir_path, str) or not dir_path:
            continue
        if not isinstance(ctx_path, str) or not ctx_path:
            continue
        rel_dir = Path(dir_path)
        if not is_dir_relevant(rel_dir, include_dirs):
            continue
        if is_ignored_path(repo_root, repo_root / dir_path, ignore_config):
            continue
        if not is_included_path(repo_root, repo_root / ctx_path, ignore_config):
            continue
        filtered.append(payload)

    filtered.sort(
        key=lambda payload: repo_relative_path(
            repo_root, repo_root / payload.get("identity", {}).get("ctx_path", "")
        )
    )
    return filtered


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

    Contract:
        - Returns only payload dictionaries (raw payloads from query output).
        - Does not filter or mutate payload contents.
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


def _ctx_snapshot(
    repo_root: Path,
    branch_name: str,
    ctx_path: str,
    actor_id: str,
) -> dict:
    """
    Return a snapshot of ctx checksums and state.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        ctx_path (str): Context path.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Snapshot payload.

    Raises:
        ValueError: If the query response payload is invalid.
        sqlite_query.SqliteQueryError: If the query request fails.

    Contract:
        - Returns a normalized snapshot with checksums and freshness state.
        - Missing records yield a snapshot with exists=False and missing state.
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
    if not isinstance(exists, bool):
        raise ValueError("dir_ctx read returned an invalid exists flag.")
    if not exists:
        return {
            "exists": False,
            "freshness_state": "missing",
            "code_hash_sha256": None,
            "subtree_hash_sha256": None,
            "ctx_semantic_hash_sha256": None,
        }
    if not isinstance(record, dict):
        raise ValueError("dir_ctx read returned an invalid record payload.")
    data = record
    if not isinstance(data, dict):
        return {
            "exists": False,
            "freshness_state": "blocked",
            "code_hash_sha256": None,
            "subtree_hash_sha256": None,
            "ctx_semantic_hash_sha256": None,
        }
    computed = data.get("computed", {})
    checksums = computed.get("checksums", {}) if isinstance(computed, dict) else {}
    return {
        "exists": True,
        "freshness_state": computed.get("freshness_state"),
        "code_hash_sha256": checksums.get("code_hash_sha256"),
        "subtree_hash_sha256": checksums.get("subtree_hash_sha256"),
        "ctx_semantic_hash_sha256": checksums.get("ctx_semantic_hash_sha256"),
    }


def build_matrix(
    repo_root: Path,
    branch_name: str,
    ctx_payloads: list[dict],
    actor_id: str,
) -> list[dict]:
    """
    Build a citation matrix from directory ctx payloads.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        ctx_payloads (list[dict]): Directory ctx payloads.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Matrix entries.

    Raises:
        ValueError: If any dir_ctx payload is malformed.
        sqlite_query.SqliteQueryError: If snapshot reads fail.

    Contract:
        - Each matrix entry corresponds to one ctx_path.
        - Snapshot values are sourced from SQLite at execution time.
    """
    matrix: list[dict] = []
    for payload in ctx_payloads:
        if not isinstance(payload, dict):
            continue
        identity = payload.get("identity", {})
        if not isinstance(identity, dict):
            continue
        ctx_path = identity.get("ctx_path")
        if not isinstance(ctx_path, str) or not ctx_path:
            raise ValueError("dir_ctx.identity.ctx_path must be a string.")
        snapshot = _ctx_snapshot(repo_root, branch_name, ctx_path, actor_id)
        matrix.append(
            {
                "ctx_path": ctx_path,
                "ctx_kind": "dir_ctx",
                "code_hash_sha256": snapshot.get("code_hash_sha256"),
                "subtree_hash_sha256": snapshot.get("subtree_hash_sha256"),
                "ctx_semantic_hash_sha256": snapshot.get("ctx_semantic_hash_sha256"),
                "freshness_state": snapshot.get("freshness_state"),
            }
        )
    return matrix


def evaluate_matrix(
    repo_root: Path,
    branch_name: Optional[str],
    matrix: list[dict],
    actor_id: str,
) -> dict:
    """
    Evaluate the matrix against current ctx artifacts.

    Args:
        repo_root (Path): Repository root.
        branch_name (Optional[str]): Branch identifier (defaults to current branch).
        matrix (list[dict]): Stored matrix entries.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Evaluation results.

    Raises:
        ValueError: If snapshot reads return malformed payloads.
        sqlite_query.SqliteQueryError: If snapshot queries fail.

    Contract:
        - Uses current dir_ctx snapshots to evaluate staleness.
        - Returns updated matrix entries with refreshed freshness_state values.
    """
    holes_count = 0
    staleness_reasons: list[str] = []
    updated_matrix: list[dict] = []

    if branch_name is None:
        from context_compass.system.ai_restricted._shared import branch_paths

        branch_name = branch_paths.load_current_branch(repo_root)

    for entry in matrix:
        ctx_path = entry.get("ctx_path")
        if not isinstance(ctx_path, str):
            continue
        snapshot = _ctx_snapshot(repo_root, branch_name, ctx_path, actor_id)
        current_state = snapshot.get("freshness_state")
        entry_updated = dict(entry)
        entry_updated["freshness_state"] = current_state

        reasons: list[str] = []
        if not snapshot.get("exists"):
            reasons.append("ctx_missing")
        if current_state in ("missing", "stale", "needs_review", "blocked"):
            reasons.append(f"ctx_state:{current_state}")

        expected_subtree = entry.get("subtree_hash_sha256")
        expected_code = entry.get("code_hash_sha256")
        expected_semantic = entry.get("ctx_semantic_hash_sha256")
        current_subtree = snapshot.get("subtree_hash_sha256")
        current_code = snapshot.get("code_hash_sha256")
        current_semantic = snapshot.get("ctx_semantic_hash_sha256")

        if expected_subtree and current_subtree and expected_subtree != current_subtree:
            reasons.append("subtree_hash_mismatch")
        if expected_code and current_code and expected_code != current_code:
            reasons.append("code_hash_mismatch")
        if expected_semantic and current_semantic and expected_semantic != current_semantic:
            reasons.append("ctx_semantic_hash_mismatch")
        if (expected_subtree or expected_code) and not (current_subtree or current_code):
            reasons.append("ctx_hash_missing")
        if (current_subtree or current_code) and not (expected_subtree or expected_code):
            reasons.append("missing_expected_hash")
        if current_semantic and not expected_semantic:
            reasons.append("missing_expected_semantic_hash")

        if reasons:
            holes_count += 1
            for reason in reasons:
                if reason not in staleness_reasons:
                    staleness_reasons.append(reason)

        updated_matrix.append(entry_updated)

    total = len(matrix)
    good_ratio: Optional[float]
    holes_ratio: Optional[float]
    if total == 0:
        good_ratio = None
        holes_ratio = None
        staleness_reasons.append("no_citations")
    else:
        good_ratio = max(0.0, min(1.0, (total - holes_count) / total))
        holes_ratio = max(0.0, min(1.0, holes_count / total))

    return {
        "matrix": updated_matrix,
        "holes_count": holes_count,
        "holes_ratio": holes_ratio,
        "good_ratio": good_ratio,
        "staleness_reasons": staleness_reasons,
        "inputs_hash": hash_json({"matrix": updated_matrix}),
    }


def derive_state(good_ratio: Optional[float], thresholds: dict) -> str:
    """
    Derive a freshness state from the good_ratio and thresholds.

    Args:
        good_ratio (Optional[float]): Ratio of good citations.
        thresholds (dict): Thresholds for good/stale/faulty.

    Returns:
        str: Freshness state.
    """
    if good_ratio is None:
        return "blocked"
    good = float(thresholds["good"])
    stale = float(thresholds["stale"])
    faulty = float(thresholds["faulty"])
    if good_ratio >= good:
        return "good"
    if good_ratio >= stale:
        return "stale"
    if good_ratio >= faulty:
        return "faulty"
    return "faulty"


def thresholds_from_policies(policies: dict) -> dict:
    """
    Build threshold values from policy config.

    Args:
        policies (dict): Policies payload.

    Returns:
        dict: Threshold mapping.
    """
    return {
        "good": float(policies["architecture_context_good_ratio_threshold"]),
        "stale": float(policies["architecture_context_stale_ratio_threshold"]),
        "faulty": float(policies["architecture_context_faulty_ratio_threshold"]),
    }
