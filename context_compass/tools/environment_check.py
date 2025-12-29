"""
Collect environment metadata for context_compass and optionally persist it.
"""

import argparse
import logging
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import lease
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import dump_minified, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _default_policies() -> dict:
    """
    Return default policy values for environment checks.

    Returns:
        dict: Policy defaults.
    """
    return {"lease_ttl_seconds": 300, "lock_wait_seconds": 10}


def _load_policies(repo_root: Path) -> dict:
    """
    Load policy configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Effective policies.
    """
    policies = _default_policies()
    data = agent_presence.load_policies(repo_root)
    if isinstance(data, dict):
        policies.update({key: value for key, value in data.items() if key in policies})
    return policies


def _tool_entry(name: str) -> dict:
    """
    Build a tool availability payload.

    Args:
        name (str): Executable name.

    Returns:
        dict: Availability payload with path if present.
    """
    path = shutil.which(name)
    return {"available": path is not None, "path": path}


def _os_payload() -> dict:
    """
    Collect OS metadata for the current runtime.

    Returns:
        dict: OS payload matching environment_state schema.
    """
    name = platform.system() or ""
    platform_id = sys.platform or ""
    release = platform.release() or ""
    version = platform.version() or ""
    machine = platform.machine() or ""
    processor = platform.processor() or ""
    lower = name.lower()
    return {
        "name": str(name),
        "platform": str(platform_id),
        "release": str(release),
        "version": str(version),
        "machine": str(machine),
        "processor": str(processor),
        "is_windows": "win" in lower,
        "is_linux": "linux" in lower,
        "is_macos": "darwin" in lower or "mac" in lower,
    }


def _python_payload() -> dict:
    """
    Collect Python runtime metadata.

    Returns:
        dict: Python payload matching environment_state schema.
    """
    version_info = [int(sys.version_info.major), int(sys.version_info.minor), int(sys.version_info.micro)]
    return {
        "available": True,
        "executable": str(sys.executable) if sys.executable else None,
        "version": str(platform.python_version()),
        "version_info": version_info,
        "implementation": str(platform.python_implementation()),
    }


def _environment_payload(now: str) -> dict:
    """
    Build the full environment state payload.

    Args:
        now (str): Current timestamp.

    Returns:
        dict: Environment payload.
    """
    return {
        "schema_version": 1,
        "checked_at": now,
        "os": _os_payload(),
        "python": _python_payload(),
        "tools": {
            "git": _tool_entry("git"),
            "rg": _tool_entry("rg"),
            "pytest": _tool_entry("pytest"),
        },
    }


def _environment_state_path(repo_root: Path, branch_name: Optional[str]) -> Path:
    """
    Resolve the environment state path for the active branch.

    Args:
        repo_root (Path): Repository root.
        branch_name (Optional[str]): Optional branch override.

    Returns:
        Path: Environment state JSON path.
    """
    return branch_paths.state_root(repo_root, branch_name) / "environment.json"


def _write_state(
    repo_root: Path,
    state_path: Path,
    payload: dict,
    owner_id: str,
) -> None:
    """
    Write environment state using a lease lock and atomic publish.

    Args:
        repo_root (Path): Repository root.
        state_path (Path): Environment state path.
        payload (dict): Environment payload.
        owner_id (str): Lock owner id.
    """
    locks_dir = state_path.parent / "locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    policies = _load_policies(repo_root)
    lease.acquire_lock(locks_dir, state_path, owner_id, ttl_seconds=policies["lease_ttl_seconds"])
    try:
        write_json_atomic(state_path, payload)
    finally:
        lease.release_lock(locks_dir, state_path, owner_id)


def run_environment_check(
    repo_root: Path,
    agent_id: str,
    work_id: Optional[str],
    mode: str,
    owner_id: Optional[str],
    branch_name: Optional[str],
    write_state: bool,
) -> dict:
    """
    Execute the environment check and optionally persist state.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier for heartbeat.
        work_id (Optional[str]): Work identifier for hard mode.
        mode (str): Agent mode.
        owner_id (Optional[str]): Optional lock owner override.
        branch_name (Optional[str]): Optional branch override.
        write_state (bool): Whether to write environment state to disk.

    Returns:
        dict: Environment payload.
    """
    now = utc_now_iso()
    payload = _environment_payload(now)
    if write_state:
        state_path = _environment_state_path(repo_root, branch_name)
        _write_state(repo_root, state_path, payload, owner_id or agent_id)
        current_target = str(state_path)
    else:
        current_target = None

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=current_target,
        notes=None,
        command_name="environment_check",
        command_args=sys.argv[1:],
        owner_id=owner_id,
    )
    return payload


def main() -> None:
    """
    CLI entrypoint for environment_check.
    """
    parser = argparse.ArgumentParser(description="Collect environment metadata for context_compass")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--owner-id", default=None, help="Lock owner id override")
    parser.add_argument("--branch-name", default=None, help="Optional branch override")
    parser.add_argument("--no-write", action="store_true", help="Skip writing environment.json to disk")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_feature_enabled(repo_root, "environment_check", "run environment check")
    ensure_work_mode(repo_root, args.work_id, "run environment check")

    try:
        payload = run_environment_check(
            repo_root=repo_root,
            agent_id=args.agent_id,
            work_id=args.work_id,
            mode=args.mode,
            owner_id=args.owner_id,
            branch_name=args.branch_name,
            write_state=not args.no_write,
        )
    except Exception as exc:
        logger.exception("environment check failed: %s", exc)
        raise SystemExit(1)

    sys.stdout.write(dump_minified(payload) + "\n")


if __name__ == "__main__":
    main()
