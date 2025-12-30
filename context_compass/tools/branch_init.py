"""
Initialize branch-scoped state and work_management directories.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools._shared import agent_presence
from context_compass.tools._shared import architecture_contexts
from context_compass.tools._shared import branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


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


def _default_context_profiles(now: str, limits: dict) -> dict:
    """
    Return a default context_profiles payload.

    Args:
        now (str): Current timestamp.
        limits (dict): Limits payload.

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


def _default_limits() -> dict:
    """
    Return default context profile limits.

    Returns:
        dict: Limits payload.
    """
    return {"max_items_per_profile": 25, "max_bytes_per_profile": 120000}


def _load_limits(repo_root: Path) -> dict:
    """
    Load context profile limits from policies.json with defaults.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Limits payload.
    """
    limits = _default_limits()
    policies_path = repo_root / "context_compass" / "config" / "policies.json"
    if policies_path.exists():
        data = load_json(policies_path)
        if isinstance(data, dict):
            max_items = data.get("context_profiles_max_items_per_profile")
            max_bytes = data.get("context_profiles_max_bytes_per_profile")
            if isinstance(max_items, int):
                limits["max_items_per_profile"] = max_items
            if isinstance(max_bytes, int):
                limits["max_bytes_per_profile"] = max_bytes
    return limits


def _default_queue(now: str) -> dict:
    """
    Return a default work queue payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Queue payload.
    """
    return {"schema_version": 1, "repo_id": None, "updated_at": now, "queue": []}


def _write_current_branch(repo_root: Path, branch_name: str, now: str) -> Path:
    """
    Write current_branch.json with the active branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        now (str): Current timestamp.

    Returns:
        Path: current_branch.json path.
    """
    payload = {
        "schema_version": 1,
        "branch_name": branch_name,
        "updated_at": now,
        "notes": None,
    }
    path = branch_paths.current_branch_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(path, payload)
    return path


def _seed_branch_state(repo_root: Path, branch_name: str, now: str) -> Path:
    """
    Seed branch state files and directories.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        now (str): Current timestamp.

    Returns:
        Path: Branch root path.
    """
    branch_root = branch_paths.branch_root(repo_root, branch_name)
    state_root = branch_root / "state"
    work_root = branch_root / "work_management"
    state_root.mkdir(parents=True, exist_ok=True)
    (state_root / "locks").mkdir(parents=True, exist_ok=True)
    (state_root / "errors").mkdir(parents=True, exist_ok=True)
    (state_root / "scans").mkdir(parents=True, exist_ok=True)

    repo_state_path = state_root / "repo_state.json"
    if not repo_state_path.exists():
        write_json_atomic(repo_state_path, _default_repo_state(repo_root, now))

    limits = _load_limits(repo_root)
    profiles_path = state_root / "context_profiles.json"
    if not profiles_path.exists():
        write_json_atomic(profiles_path, _default_context_profiles(now, limits))

    architecture_path = state_root / "architecture_context.json"
    if not architecture_path.exists():
        write_json_atomic(
            architecture_path,
            architecture_contexts.default_architecture_context("architecture_context", now),
        )

    components_path = state_root / "component_contexts.json"
    if not components_path.exists():
        write_json_atomic(
            components_path,
            architecture_contexts.default_component_contexts("component_contexts", now),
        )

    test_architecture_path = state_root / "test_architecture_context.json"
    if not test_architecture_path.exists():
        write_json_atomic(
            test_architecture_path,
            architecture_contexts.default_architecture_context("test_architecture_context", now),
        )

    test_components_path = state_root / "test_component_contexts.json"
    if not test_components_path.exists():
        write_json_atomic(
            test_components_path,
            architecture_contexts.default_component_contexts("test_component_contexts", now),
        )

    for bucket in ("active", "backlog", "completed", "denied"):
        bucket_dir = work_root / bucket
        bucket_dir.mkdir(parents=True, exist_ok=True)
        for name in ("epics.json", "stories.json", "tasks.json"):
            queue_path = bucket_dir / name
            if not queue_path.exists():
                write_json_atomic(queue_path, _default_queue(now))
    return branch_root


def init_branch(
    repo_root: Path,
    branch_name: str,
    agent_id: str,
    mode: str,
    work_id: Optional[str],
) -> None:
    """
    Initialize a branch directory and mark it as active.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name.
        agent_id (str): Agent id for heartbeat.
        mode (str): Agent mode.
        work_id (Optional[str]): Work id for work_mode enforcement.
    """
    ensure_certified(repo_root, args.agent_id)
    ensure_work_mode(repo_root, work_id, "initialize branch management state")
    now = utc_now_iso()
    _seed_branch_state(repo_root, branch_name, now)
    _write_current_branch(repo_root, branch_name, now)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=f"branch:{branch_name}",
        notes=None,
        command_name="branch_init",
        command_args=sys.argv[1:],
    )


def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Initialize branch-scoped context_compass state.")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--branch-name", required=True, help="Branch name to initialize.")
    parser.add_argument("--agent-id", required=True, help="Agent id for heartbeat.")
    parser.add_argument("--mode", default="agent", help="Agent mode label.")
    parser.add_argument("--work-id", default=None, help="Work id for hard work_mode enforcement.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    repo_root = Path(args.repo_root).resolve()
    init_branch(
        repo_root=repo_root,
        branch_name=args.branch_name,
        agent_id=args.agent_id,
        mode=args.mode,
        work_id=args.work_id,
    )


if __name__ == "__main__":
    main()
