"""
Switch the active branch for context_compass state and work queues.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools._shared import agent_presence
from context_compass.tools._shared import branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


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


def switch_branch(
    repo_root: Path,
    branch_name: str,
    agent_id: str,
    mode: str,
    work_id: Optional[str],
) -> None:
    """
    Switch the active branch pointer.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch name to activate.
        agent_id (str): Agent id for heartbeat.
        mode (str): Agent mode.
        work_id (Optional[str]): Work id for work_mode enforcement.

    Raises:
        FileNotFoundError: If the branch directory is missing.
    """
    ensure_certified(repo_root, args.agent_id)
    ensure_work_mode(repo_root, work_id, "switch branch management state")
    now = utc_now_iso()
    branch_root = branch_paths.branch_root(repo_root, branch_name)
    if not branch_root.exists():
        raise FileNotFoundError(
            f"Branch directory does not exist: {branch_root}. Run branch_init.py first."
        )
    _write_current_branch(repo_root, branch_name, now)
    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=f"branch:{branch_name}",
        notes=None,
        command_name="branch_switch",
        command_args=sys.argv[1:],
    )


def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Switch the active context_compass branch state.")
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--branch-name", required=True, help="Branch name to activate.")
    parser.add_argument("--agent-id", required=True, help="Agent id for heartbeat.")
    parser.add_argument("--mode", default="agent", help="Agent mode label.")
    parser.add_argument("--work-id", default=None, help="Work id for hard work_mode enforcement.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    repo_root = Path(args.repo_root).resolve()
    switch_branch(
        repo_root=repo_root,
        branch_name=args.branch_name,
        agent_id=args.agent_id,
        mode=args.mode,
        work_id=args.work_id,
    )


if __name__ == "__main__":
    main()
