"""
Assess repo lifecycle stage and update repo_state.json.
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
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _allowed_stages() -> list[str]:
    """
    Return allowed lifecycle stage values.

    Returns:
        list[str]: Allowed stage values.
    """
    return ["new", "active_dev", "stable", "production", "maintenance", "experimental", "archived"]


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


def _load_repo_state(path: Path, repo_root: Path, now: str) -> dict:
    """
    Load repo_state.json or initialize a default structure.

    Args:
        path (Path): Repo state path.
        repo_root (Path): Repository root.
        now (str): Current timestamp.

    Returns:
        dict: Repo state payload.
    """
    if path.exists():
        data = load_json(path)
        if isinstance(data, dict):
            return data
    return _default_repo_state(repo_root, now)


def _apply_defaults_for_stage(stage: str) -> dict:
    """
    Return default tooling policy updates for a given stage.

    Args:
        stage (str): Lifecycle stage.

    Returns:
        dict: Tooling policy defaults.
    """
    if stage == "new":
        return {
            "mode": "restricted",
            "disabled_features": ["scan", "context_profiles"],
            "notes": "Auto-restricted for new repos; update repo_state to enable.",
        }
    return {"mode": "normal", "disabled_features": [], "notes": None}


def assess_repo_state(
    repo_root: Path,
    agent_id: str,
    mode: str,
    work_id: Optional[str],
    stage: str,
    assessment: Optional[str],
    confidence: float,
    tooling_mode: Optional[str],
    disabled_features: list[str],
    clear_disabled: bool,
    notes: Optional[str],
    owner_id: Optional[str],
) -> dict:
    """
    Update repo_state.json with lifecycle and tooling assessment.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        mode (str): Agent mode for heartbeat.
        work_id (Optional[str]): Work id for hard mode.
        stage (str): Lifecycle stage.
        assessment (Optional[str]): Assessment notes.
        confidence (float): Confidence score (0-1).
        tooling_mode (Optional[str]): Tooling policy mode override.
        disabled_features (list[str]): Disabled features list.
        clear_disabled (bool): Whether to clear disabled features.
        notes (Optional[str]): Tooling policy notes.
        owner_id (Optional[str]): Lock owner id override.

    Returns:
        dict: Updated repo state payload.
    """
    now = utc_now_iso()
    state_path = branch_paths.state_root(repo_root) / "repo_state.json"
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    policies = agent_presence.load_policies(repo_root)
    lock_owner = owner_id or agent_id

    lease.acquire_lock(locks_dir, state_path, lock_owner, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        state = _load_repo_state(state_path, repo_root, now)
        lifecycle = state.get("lifecycle")
        if not isinstance(lifecycle, dict):
            lifecycle = {}
        lifecycle["stage"] = stage
        if assessment is not None:
            lifecycle["assessment"] = assessment
        lifecycle["confidence"] = max(0.0, min(1.0, float(confidence)))
        lifecycle["assessed_at"] = now
        state["lifecycle"] = lifecycle

        tooling = state.get("tooling_policy")
        if not isinstance(tooling, dict):
            tooling = {}

        if tooling_mode is None and not tooling:
            tooling.update(_apply_defaults_for_stage(stage))
        if tooling_mode is not None:
            tooling["mode"] = tooling_mode
        if clear_disabled:
            tooling["disabled_features"] = []
        elif disabled_features:
            tooling["disabled_features"] = sorted({str(item) for item in disabled_features})
        if notes is not None:
            tooling["notes"] = notes
        tooling["updated_at"] = now
        state["tooling_policy"] = tooling

        state["updated_at"] = now
        if state.get("created_at") is None:
            state["created_at"] = now
        write_json_atomic(state_path, state)
    finally:
        lease.release_lock(locks_dir, state_path, lock_owner)

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=str(state_path),
        notes=None,
        command_name="repo_state_assess",
        command_args=sys.argv[1:],
        owner_id=owner_id,
    )
    return state


def main() -> None:
    """
    CLI entrypoint for repo_state assessment.
    """
    parser = argparse.ArgumentParser(description="Assess repo lifecycle and update repo_state.json")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--stage", required=True, choices=_allowed_stages(), help="Lifecycle stage")
    parser.add_argument("--assessment", default=None, help="Assessment notes")
    parser.add_argument("--confidence", type=float, default=0.5, help="Confidence (0-1)")
    parser.add_argument("--tooling-mode", choices=["normal", "restricted"], default=None, help="Tooling mode override")
    parser.add_argument("--disable-feature", action="append", default=[], help="Feature to disable (repeatable)")
    parser.add_argument("--clear-disabled", action="store_true", help="Clear disabled feature list")
    parser.add_argument("--notes", default=None, help="Tooling policy notes")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_feature_enabled(repo_root, "repo_state", "update repo state")
    ensure_work_mode(repo_root, args.work_id, "update repo state")

    state = assess_repo_state(
        repo_root=repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        work_id=args.work_id,
        stage=args.stage,
        assessment=args.assessment,
        confidence=args.confidence,
        tooling_mode=args.tooling_mode,
        disabled_features=args.disable_feature,
        clear_disabled=args.clear_disabled,
        notes=args.notes,
        owner_id=args.owner_id,
    )
    logger.info("repo_state updated: stage=%s", state.get("lifecycle", {}).get("stage"))


if __name__ == "__main__":
    main()
