"""
Clone branch state and work queues from a source branch into a new branch.
"""

import argparse
import logging
import shutil
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import branch_copy_context, branch_copy_work
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.timeutils import utc_now_iso
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools import branch_init, branch_switch


def _ensure_source_branch(repo_root: Path, branch_name: str) -> Path:
    """
    Ensure the source branch exists.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Source branch name.

    Returns:
        Path: Source branch root.

    Raises:
        FileNotFoundError: If the branch directory is missing.
    """
    source_root = branch_paths.branch_root(repo_root, branch_name)
    if not source_root.exists():
        raise FileNotFoundError(f"Source branch does not exist: {source_root}")
    return source_root


def _prepare_destination(repo_root: Path, branch_name: str, force: bool) -> Path:
    """
    Prepare a destination branch root, deleting if forced.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Destination branch name.
        force (bool): Whether to delete an existing destination.

    Returns:
        Path: Destination branch root.

    Raises:
        FileExistsError: If destination exists and force is False.
    """
    dest_root = branch_paths.branch_root(repo_root, branch_name)
    if dest_root.exists():
        if not force:
            raise FileExistsError(f"Destination branch already exists: {dest_root}")
        shutil.rmtree(dest_root)
    return dest_root


def clone_branch(
    repo_root: Path,
    source_branch: str,
    dest_branch: str,
    agent_id: str,
    mode: str,
    work_id: Optional[str],
    copy_context: bool,
    copy_work: bool,
    preserve_repo_state: bool,
    preserve_work_state: bool,
    activate: bool,
    force: bool,
) -> None:
    """
    Clone branch context and work queues into a destination branch.

    Args:
        repo_root (Path): Repository root.
        source_branch (str): Source branch name.
        dest_branch (str): Destination branch name.
        agent_id (str): Agent identifier.
        mode (str): Agent mode.
        work_id (Optional[str]): Work id for work_mode enforcement.
        copy_context (bool): Copy context files if True.
        copy_work (bool): Copy work queues if True.
        preserve_repo_state (bool): Preserve scan counters/timestamps.
        preserve_work_state (bool): Preserve leases/in_progress if True.
        activate (bool): Switch active branch to the destination if True.
        force (bool): Overwrite destination branch if it exists.
    """
    ensure_certified(repo_root, args.agent_id)
    ensure_work_mode(repo_root, work_id, "clone branch state")
    _ensure_source_branch(repo_root, source_branch)
    _prepare_destination(repo_root, dest_branch, force)

    now = utc_now_iso()
    branch_init._seed_branch_state(repo_root, dest_branch, now)

    if copy_context:
        branch_copy_context.copy_context(
            repo_root=repo_root,
            source_branch=source_branch,
            dest_branch=dest_branch,
            preserve_repo_state=preserve_repo_state,
            owner_id=agent_id,
        )
    if copy_work:
        branch_copy_work.copy_work(
            repo_root=repo_root,
            source_branch=source_branch,
            dest_branch=dest_branch,
            preserve_state=preserve_work_state,
            owner_id=agent_id,
        )

    if activate:
        branch_switch.switch_branch(
            repo_root=repo_root,
            branch_name=dest_branch,
            agent_id=agent_id,
            mode=mode,
            work_id=work_id,
        )

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=f"branch_clone:{source_branch}->{dest_branch}",
        notes=None,
        command_name="branch_clone",
        command_args=sys.argv[1:],
    )


def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Clone branch state and work queues.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--source-branch", required=True, help="Source branch name")
    parser.add_argument("--dest-branch", required=True, help="Destination branch name")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Work identifier for hard mode")
    parser.add_argument("--mode", default="agent", help="Agent mode label")
    parser.add_argument("--no-context", action="store_true", help="Do not copy context state")
    parser.add_argument("--no-work", action="store_true", help="Do not copy work queues")
    parser.add_argument(
        "--preserve-repo-state",
        action="store_true",
        help="Preserve scan counters and timestamps",
    )
    parser.add_argument(
        "--preserve-work-state",
        action="store_true",
        help="Preserve leases and in_progress states",
    )
    parser.add_argument("--activate", action="store_true", help="Switch to the destination branch")
    parser.add_argument("--force", action="store_true", help="Overwrite destination branch if it exists")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    repo_root = Path(args.repo_root).resolve()
    clone_branch(
        repo_root=repo_root,
        source_branch=args.source_branch,
        dest_branch=args.dest_branch,
        agent_id=args.agent_id,
        mode=args.mode,
        work_id=args.work_id,
        copy_context=not args.no_context,
        copy_work=not args.no_work,
        preserve_repo_state=args.preserve_repo_state,
        preserve_work_state=args.preserve_work_state,
        activate=args.activate,
        force=args.force,
    )


if __name__ == "__main__":
    main()
