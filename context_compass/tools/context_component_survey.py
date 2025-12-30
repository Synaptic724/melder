"""
Survey and build component_contexts artifacts from directory ctx only.
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
from context_compass.tools._shared.hashing import hash_json
from context_compass.tools._shared.ignore_rules import load_ignore_config
from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.paths import repo_relative_path
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values for component contexts.

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


def _load_dir_ctx(path: Path) -> Optional[dict]:
    """
    Load a directory ctx JSON payload.

    Args:
        path (Path): Directory ctx path.

    Returns:
        Optional[dict]: Parsed payload or None if invalid.
    """
    try:
        data = load_json(path)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _component_from_dir_ctx(repo_root: Path, ctx_path: Path) -> dict:
    """
    Build a component entry from a directory ctx payload.

    Args:
        repo_root (Path): Repository root.
        ctx_path (Path): Directory ctx path.

    Returns:
        dict: Component entry.
    """
    rel_ctx = repo_relative_path(repo_root, ctx_path)
    payload = _load_dir_ctx(ctx_path)
    name = ctx_path.stem.replace("__", "").replace(".dir", "")
    summary = {"one_liner": None, "detail": None}
    responsibilities: list[str] = []
    key_flows: list[str] = []
    boundaries: list[str] = []

    if payload:
        identity = payload.get("identity", {})
        if isinstance(identity, dict):
            identity_name = identity.get("name")
            if isinstance(identity_name, str) and identity_name:
                name = identity_name
        agent = payload.get("agent", {})
        if isinstance(agent, dict):
            summary_data = agent.get("summary", {})
            if isinstance(summary_data, dict):
                summary["one_liner"] = summary_data.get("one_liner")
                summary["detail"] = summary_data.get("detail")
            architecture = agent.get("architecture", {})
            if isinstance(architecture, dict):
                resp = architecture.get("responsibilities")
                if isinstance(resp, list):
                    responsibilities = [item for item in resp if isinstance(item, str)]
                flows = architecture.get("key_flows")
                if isinstance(flows, list):
                    key_flows = [
                        flow.get("name")
                        for flow in flows
                        if isinstance(flow, dict) and isinstance(flow.get("name"), str)
                    ]
                deps = architecture.get("dependency_rules")
                if isinstance(deps, dict):
                    allowed = deps.get("allowed_outbound")
                    if isinstance(allowed, list):
                        boundaries.extend([item for item in allowed if isinstance(item, str)])

    component_id = f"component_{hash_json({'ctx_path': rel_ctx})[:8]}"
    return {
        "component_id": component_id,
        "name": name,
        "summary": summary,
        "responsibilities": responsibilities,
        "boundaries": boundaries,
        "key_flows": key_flows,
        "ctx_paths": [rel_ctx],
    }


def _build_components(repo_root: Path, ctx_paths: list[Path]) -> list[dict]:
    """
    Build component entries from directory ctx paths.

    Args:
        repo_root (Path): Repository root.
        ctx_paths (list[Path]): Directory ctx paths.

    Returns:
        list[dict]: Component list.
    """
    return [_component_from_dir_ctx(repo_root, path) for path in ctx_paths]


def _build_agent_section(target: str, components: list[dict]) -> dict:
    """
    Build the agent section for component_contexts.

    Args:
        target (str): Target scope.
        components (list[dict]): Component list.

    Returns:
        dict: Agent section payload.
    """
    return {
        "summary": {
            "one_liner": f"{target} component contexts derived from directory ctx.",
            "detail": f"Derived from {len(components)} components.",
        }
    }


def _write_if_changed(
    repo_root: Path,
    path: Path,
    payload: dict,
    owner_id: str,
    policies: dict,
) -> bool:
    """
    Write the component contexts payload if it changed.

    Args:
        repo_root (Path): Repository root.
        path (Path): Target path.
        payload (dict): Payload to write.
        owner_id (str): Lock owner id.
        policies (dict): Policy values.

    Returns:
        bool: True if the file was updated.
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


def survey_components(
    repo_root: Path,
    agent_id: str,
    mode: str,
    work_id: Optional[str],
    target: str,
    dry_run: bool,
) -> dict:
    """
    Build component_contexts from directory ctx.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        mode (str): Agent mode for heartbeat.
        work_id (Optional[str]): Work id for hard mode enforcement.
        target (str): Target scope ("prod" or "test").
        dry_run (bool): If True, do not write output.

    Returns:
        dict: Component contexts payload.
    """
    ensure_feature_enabled(repo_root, "architecture_contexts", "survey component contexts")
    ensure_work_mode(repo_root, work_id, "survey component contexts")
    now = utc_now_iso()
    policies = _load_policies(repo_root)
    ignore_config = load_ignore_config(repo_root)
    ctx_paths = architecture_contexts.collect_dir_ctx_paths(repo_root, target, ignore_config)
    components = _build_components(repo_root, ctx_paths)
    matrix = architecture_contexts.build_matrix(repo_root, ctx_paths)
    evaluation = architecture_contexts.evaluate_matrix(repo_root, matrix)
    thresholds = architecture_contexts.thresholds_from_policies(policies)
    state = architecture_contexts.derive_state(evaluation["good_ratio"], thresholds)

    payload = {
        "schema_version": 1,
        "kind": "component_contexts" if target == "prod" else "test_component_contexts",
        "updated_at": now,
        "agent": _build_agent_section(target, components),
        "components": components,
        "computed": {
            "freshness_state": state,
            "holes_count": evaluation["holes_count"],
            "holes_ratio": evaluation["holes_ratio"],
            "good_ratio": evaluation["good_ratio"],
            "inputs_hash": evaluation["inputs_hash"],
            "last_checked_at": now,
            "matrix": evaluation["matrix"],
            "staleness_reasons": evaluation["staleness_reasons"],
        },
    }

    if not dry_run:
        path = architecture_contexts.artifact_path(repo_root, payload["kind"])
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_if_changed(repo_root, path, payload, agent_id, policies)

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=f"component_contexts:{target}",
        notes=None,
        command_name="context_component_survey",
        command_args=sys.argv[1:],
    )
    return payload


def main() -> None:
    """
    CLI entrypoint for component context surveys.
    """
    parser = argparse.ArgumentParser(description="Survey component_contexts from directory ctx")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--target", choices=["prod", "test"], default="prod", help="Target scope")
    parser.add_argument("--dry-run", action="store_true", help="Do not write outputs")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root, args.agent_id)
    ensure_feature_enabled(repo_root, "architecture_contexts", "survey component contexts")
    payload = survey_components(
        repo_root=repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        work_id=args.work_id,
        target=args.target,
        dry_run=args.dry_run,
    )
    logger.info("component_contexts refreshed: kind=%s", payload.get("kind"))


if __name__ == "__main__":
    main()
