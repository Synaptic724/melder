"""
Helpers for architecture/component context artifacts.
"""

import os
from pathlib import Path
from typing import Optional

from context_compass.tools._shared.hashing import hash_json
from context_compass.tools._shared.ignore_rules import (
    is_dir_relevant,
    is_ignored_path,
    is_within_only_roots,
)
from context_compass.tools._shared.json_io import load_json
from context_compass.tools._shared.paths import repo_relative_dir, repo_relative_path
from context_compass.tools._shared.source_roots import load_source_roots


def artifact_path(repo_root: Path, kind: str) -> Path:
    """
    Resolve the branch-scoped path for architecture/component context artifacts.

    Args:
        repo_root (Path): Repository root.
        kind (str): Artifact kind.

    Returns:
        Path: Artifact path.

    Raises:
        ValueError: If the kind is unknown.
    """
    from context_compass.tools._shared import branch_paths

    filename_map = {
        "architecture_context": "architecture_context.json",
        "component_contexts": "component_contexts.json",
        "test_architecture_context": "test_architecture_context.json",
        "test_component_contexts": "test_component_contexts.json",
    }
    filename = filename_map.get(kind)
    if not filename:
        raise ValueError(f"Unknown architecture context kind: {kind}")
    return branch_paths.state_root(repo_root) / filename


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
        roots (list[str]): Target roots from source_roots.json.
        ignore_roots (list[str]): only_roots from ignore.json.

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
    return _normalize_roots(prod_roots, ignore_config.get("only_roots", []))


def collect_dir_ctx_paths(repo_root: Path, target: str, ignore_config: dict) -> list[Path]:
    """
    Collect directory ctx paths for the given target scope.

    Args:
        repo_root (Path): Repository root.
        target (str): Target scope ("prod" or "test").
        ignore_config (dict): Ignore configuration.

    Returns:
        list[Path]: Directory ctx paths.
    """
    only_roots = _roots_for_target(repo_root, target, ignore_config)
    if target == "test" and not only_roots:
        return []
    ctx_paths: list[Path] = []

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
            if not filename.endswith(".dir.json"):
                continue
            path = current_dir / filename
            if is_ignored_path(repo_root, path, ignore_config):
                continue
            if not is_within_only_roots(repo_root, path, only_roots):
                continue
            ctx_paths.append(path)

    ctx_paths.sort(key=lambda path: repo_relative_path(repo_root, path))
    return ctx_paths


def _ctx_snapshot(repo_root: Path, ctx_path: Path) -> dict:
    """
    Return a snapshot of ctx checksums and state.

    Args:
        repo_root (Path): Repository root.
        ctx_path (Path): Context path.

    Returns:
        dict: Snapshot payload.
    """
    if not ctx_path.exists():
        return {
            "exists": False,
            "freshness_state": "missing",
            "code_hash_sha256": None,
            "subtree_hash_sha256": None,
            "ctx_semantic_hash_sha256": None,
        }
    data = load_json(ctx_path)
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


def build_matrix(repo_root: Path, ctx_paths: list[Path]) -> list[dict]:
    """
    Build a citation matrix from directory ctx paths.

    Args:
        repo_root (Path): Repository root.
        ctx_paths (list[Path]): Directory ctx paths.

    Returns:
        list[dict]: Matrix entries.
    """
    matrix: list[dict] = []
    for path in ctx_paths:
        snapshot = _ctx_snapshot(repo_root, path)
        rel_path = repo_relative_path(repo_root, path)
        matrix.append(
            {
                "ctx_path": rel_path,
                "ctx_kind": "dir_ctx",
                "code_hash_sha256": snapshot.get("code_hash_sha256"),
                "subtree_hash_sha256": snapshot.get("subtree_hash_sha256"),
                "ctx_semantic_hash_sha256": snapshot.get("ctx_semantic_hash_sha256"),
                "freshness_state": snapshot.get("freshness_state"),
            }
        )
    return matrix


def evaluate_matrix(repo_root: Path, matrix: list[dict]) -> dict:
    """
    Evaluate the matrix against current ctx artifacts.

    Args:
        repo_root (Path): Repository root.
        matrix (list[dict]): Stored matrix entries.

    Returns:
        dict: Evaluation results.
    """
    holes_count = 0
    staleness_reasons: list[str] = []
    updated_matrix: list[dict] = []

    for entry in matrix:
        ctx_path = entry.get("ctx_path")
        if not isinstance(ctx_path, str):
            continue
        current_path = repo_root / ctx_path
        snapshot = _ctx_snapshot(repo_root, current_path)
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
