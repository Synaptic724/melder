"""
Check architecture_context freshness against the citation matrix.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, architecture_contexts, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values for architecture contexts.

    Returns:
        dict: Default policy values.
    """
    return {
        "lease_ttl_seconds": 300,
        "lock_wait_seconds": 10,
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


def _write_if_changed(repo_root: Path, path: Path, payload: dict, owner_id: str, policies: dict) -> bool:
    """
    Write the payload if it changed.

    Args:
        repo_root (Path): Repository root.
        path (Path): Target path.
        payload (dict): Payload to write.
        owner_id (str): Lock owner id.
        policies (dict): Policy values.

    Returns:
        bool: True if updated.
    """
    locks_dir = branch_paths.state_root(repo_root) / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lease.acquire_lock(locks_dir, path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        existing = load_json(path) if path.exists() else None
        if existing == payload:
            return False
        write_json_atomic(path, payload)
        return True
    finally:
        lease.release_lock(locks_dir, path, owner_id)


def check_architecture(
    repo_root: Path,
    agent_id: str,
    mode: str,
    work_id: Optional[str],
    target: str,
    update: bool,
) -> dict:
    """
    Evaluate architecture_context freshness and optionally update computed fields.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        mode (str): Agent mode for heartbeat.
        work_id (Optional[str]): Work id for hard mode enforcement.
        target (str): Target scope ("prod" or "test").
        update (bool): Whether to write updated computed fields.

    Returns:
        dict: Updated architecture_context payload.
    """
    ensure_feature_enabled(repo_root, "architecture_contexts", "check architecture contexts")
    ensure_work_mode(repo_root, work_id, "check architecture contexts")
    policies = _load_policies(repo_root)
    now = utc_now_iso()
    kind = "architecture_context" if target == "prod" else "test_architecture_context"
    path = architecture_contexts.artifact_path(repo_root, kind)
    if not path.exists():
        raise FileNotFoundError(f"Missing architecture context: {path}")
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("architecture_context.json must be a JSON object")

    matrix = payload.get("computed", {}).get("matrix", [])
    if not isinstance(matrix, list):
        raise ValueError("architecture_context matrix must be a list")
    evaluation = architecture_contexts.evaluate_matrix(repo_root, matrix)
    thresholds = architecture_contexts.thresholds_from_policies(policies)
    state = architecture_contexts.derive_state(evaluation["good_ratio"], thresholds)

    computed = dict(payload.get("computed", {}))
    computed.update(
        {
            "freshness_state": state,
            "holes_count": evaluation["holes_count"],
            "holes_ratio": evaluation["holes_ratio"],
            "good_ratio": evaluation["good_ratio"],
            "inputs_hash": evaluation["inputs_hash"],
            "last_checked_at": now,
            "matrix": evaluation["matrix"],
            "staleness_reasons": evaluation["staleness_reasons"],
        }
    )
    payload["computed"] = computed
    payload["updated_at"] = now

    if update:
        _write_if_changed(repo_root, path, payload, agent_id, policies)

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=str(path),
        notes=None,
        command_name="context_architecture_check",
        command_args=sys.argv[1:],
    )
    return payload


def main() -> None:
    """
    CLI entrypoint for architecture context checks.
    """
    parser = argparse.ArgumentParser(description="Check architecture_context freshness")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--target", choices=["prod", "test"], default="prod", help="Target scope")
    parser.add_argument("--no-update", action="store_true", help="Do not write computed updates")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    payload = check_architecture(
        repo_root=repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        work_id=args.work_id,
        target=args.target,
        update=not args.no_update,
    )
    state = payload.get("computed", {}).get("freshness_state")
    if state == "faulty":
        logger.warning("architecture_context is faulty; run scan and resurvey.")
    elif state == "stale":
        logger.warning("architecture_context is stale; consider resurveying.")
    else:
        logger.info("architecture_context state=%s", state)


if __name__ == "__main__":
    main()
