"""
Resurvey context profiles in response to resurvey_context_profile tasks.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from context_compass.tools import context_profiles_survey, update_state, work_item_close
from context_compass.tools._shared import agent_presence, branch_paths
from context_compass.tools._shared.certification_guard import ensure_certified
from context_compass.tools._shared.feature_guard import ensure_feature_enabled
from context_compass.tools._shared.work_mode_guard import ensure_work_mode
from context_compass.tools._shared.json_io import load_json
from context_compass.tools._shared.timeutils import utc_now_iso


def _queue_path(repo_root: Path) -> Path:
    """
    Return the active tasks queue path.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Tasks queue path.
    """
    return branch_paths.work_root(repo_root) / "active" / "tasks.json"


def _resurvey_kind() -> str:
    """
    Return the task kind used for resurvey requests.

    Returns:
        str: Resurvey task kind.
    """
    return "resurvey_context_profile"


def _load_queue(queue_path: Path) -> dict:
    """
    Load the active tasks queue.

    Args:
        queue_path (Path): Queue path.

    Returns:
        dict: Queue payload.

    Raises:
        FileNotFoundError: If the queue file does not exist.
        ValueError: If the queue payload is invalid.
    """
    if not queue_path.exists():
        raise FileNotFoundError(f"Missing tasks queue: {queue_path}")
    data = load_json(queue_path)
    if not isinstance(data, dict):
        raise ValueError("Tasks queue must be a JSON object")
    return data


def _select_resurvey_tasks(queue: list[dict], work_id: Optional[str], select_all: bool) -> list[dict]:
    """
    Select resurvey tasks from the queue.

    Args:
        queue (list[dict]): Queue items.
        work_id (Optional[str]): Specific work id to select.
        select_all (bool): Whether to select all queued resurvey tasks.

    Returns:
        list[dict]: Selected task items.
    """
    resurvey_tasks = [item for item in queue if item.get("kind") == _resurvey_kind()]
    if work_id:
        return [item for item in resurvey_tasks if item.get("work_id") == work_id]
    if select_all:
        return [item for item in resurvey_tasks if item.get("state") == "queued"]
    for item in resurvey_tasks:
        if item.get("state") == "queued":
            return [item]
    return []


def _mark_in_progress(repo_root: Path, work_id: str, owner_id: str) -> None:
    """
    Mark a work item as in_progress.

    Args:
        repo_root (Path): Repository root.
        work_id (str): Work identifier.
        owner_id (str): Lock owner id.
    """
    update_state.update_work_item_state(
        repo_root,
        "active",
        "task",
        work_id,
        owner_id=owner_id,
        state="in_progress",
    )


def _close_task(repo_root: Path, work_id: str, owner_id: str, queue_agent_id: Optional[str]) -> None:
    """
    Close a resurvey task and move it to completed.

    Args:
        repo_root (Path): Repository root.
        work_id (str): Work identifier.
        owner_id (str): Lock owner id.
        queue_agent_id (Optional[str]): Agent queue to clean up.
    """
    work_item_close.close_work_item(
        repo_root,
        work_id,
        "task",
        "active",
        "completed",
        owner_id,
        new_state="done",
        queue_agent_id=queue_agent_id,
    )


def resurvey_context_profiles(
    repo_root: Path,
    agent_id: str,
    mode: str,
    work_id: Optional[str],
    select_all: bool,
    emit_tasks: bool,
) -> list[str]:
    """
    Resurvey context profiles and close corresponding resurvey tasks.

    Contract:
    - Runs context_profiles_survey once per invocation.
    - Closes selected resurvey tasks on success.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        mode (str): Agent mode for heartbeat.
        work_id (Optional[str]): Specific work id to process.
        select_all (bool): Whether to process all queued resurvey tasks.
        emit_tasks (bool): Whether to emit optimize/prune tasks during survey.

    Returns:
        list[str]: Work ids closed.
    """
    ensure_feature_enabled(repo_root, "context_profiles", "resurvey context profiles")
    ensure_feature_enabled(repo_root, "work_management", "update work queues")
    ensure_work_mode(repo_root, work_id, "resurvey context profiles")
    queue_path = _queue_path(repo_root)
    data = _load_queue(queue_path)
    queue = data.get("queue", [])
    if not isinstance(queue, list):
        raise ValueError("Tasks queue must contain a list")

    selected = _select_resurvey_tasks(queue, work_id, select_all)
    if not selected:
        raise ValueError("No resurvey_context_profile tasks found to process")

    for item in selected:
        if item.get("state") != "queued":
            raise ValueError(f"Task not queued: {item.get('work_id')}")

    for item in selected:
        _mark_in_progress(repo_root, item.get("work_id"), owner_id=agent_id)

    context_profiles_survey.survey_profiles(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        dry_run=False,
        emit_tasks=emit_tasks,
        work_id=work_id,
    )

    closed: list[str] = []
    for item in selected:
        _close_task(repo_root, item.get("work_id"), owner_id=agent_id, queue_agent_id=agent_id)
        closed.append(item.get("work_id"))

    agent_presence.record_heartbeat(
        repo_root,
        agent_id=agent_id,
        mode=mode,
        current_task_id=work_id,
        current_target=str(queue_path),
        notes=None,
        command_name="context_profiles_resurvey",
        command_args=sys.argv[1:],
    )
    return closed


def main() -> None:
    """
    CLI entrypoint for context profile resurvey tasks.
    """
    parser = argparse.ArgumentParser(description="Resurvey context profiles from queued tasks")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--mode", default="agent", help="Agent mode for heartbeat")
    parser.add_argument("--work-id", default=None, help="Specific resurvey work id")
    parser.add_argument("--all", action="store_true", help="Process all queued resurvey tasks")
    parser.add_argument("--no-emit-tasks", action="store_true", help="Do not emit optimize/prune tasks")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    repo_root = Path(args.repo_root).resolve()
    ensure_certified(repo_root)
    ensure_feature_enabled(repo_root, "context_profiles", "resurvey context profiles")
    ensure_feature_enabled(repo_root, "work_management", "update work queues")
    ensure_work_mode(repo_root, args.work_id, "resurvey context profiles")

    closed = resurvey_context_profiles(
        repo_root,
        agent_id=args.agent_id,
        mode=args.mode,
        work_id=args.work_id,
        select_all=args.all,
        emit_tasks=not args.no_emit_tasks,
    )
    logger.info("resurvey completed, closed tasks: %s", ", ".join(closed))


if __name__ == "__main__":
    main()
