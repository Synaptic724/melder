"""
Resurvey component_contexts in response to resurvey tasks.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted.context_management import context_component_survey
from context_compass.system.ai_restricted.system_management import update_state
from context_compass.system.ai_restricted.work_management import work_item_close
from context_compass.system.ai_restricted._shared import branch_paths
from context_compass.system.ai_restricted._shared.command_payload import (
    PayloadError,
    optional_bool,
    optional_string,
    require_string,
)
from context_compass.system.ai_restricted._shared.command_results import (
    exception_result,
    ok_result,
    payload_error_result,
)
from context_compass.system.ai_restricted._shared.certification_guard import ensure_certified
from context_compass.system.ai_restricted._shared.feature_guard import ensure_feature_enabled
from context_compass.system.ai_restricted._shared.work_mode_guard import ensure_work_mode
from context_compass.system.ai_restricted._shared.command_contracts import (
    CommandResult,
    ExecutionContext,
)
from context_compass.system.ai_restricted.database_management import sqlite_query

QUERY_READ_BRANCH_WORK_QUEUE = "read_branch_work_queue"


def _resurvey_kind(target: str) -> str:
    """
    Return the task kind used for resurvey requests.

    Args:
        target (str): Target scope.

    Returns:
        str: Resurvey task kind.
    """
    return "resurvey_component_contexts" if target == "prod" else "resurvey_test_component_contexts"


def _load_queue(repo_root: Path, branch_name: str, actor_id: str) -> dict:
    """
    Load the active tasks queue from SQLite.

    Args:
        repo_root (Path): Repository root.
        branch_name (str): Branch identifier.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Queue payload.

    Raises:
        FileNotFoundError: If the queue record does not exist.
        ValueError: If the queue payload is invalid.
    """
    response = sqlite_query.execute_request(
        repo_root,
        sqlite_query.SqliteQueryRequest(
            scope="user",
            query_name=QUERY_READ_BRANCH_WORK_QUEUE,
            payload={
                "branch_name": branch_name,
                "bucket": "active",
                "work_type": "task",
            },
            actor_id=actor_id,
        ),
    )
    result = response.output.get("result", {})
    queue_payload = result.get("queue")
    exists = result.get("exists")
    if not isinstance(exists, bool):
        raise ValueError("branch work queue read returned an invalid exists flag.")
    if not exists:
        raise FileNotFoundError("Missing tasks queue: active/task")
    if not isinstance(queue_payload, dict):
        raise ValueError("Tasks queue must be a JSON object")
    return queue_payload


def _select_resurvey_tasks(queue: list[dict], work_id: Optional[str], select_all: bool, target: str) -> list[dict]:
    """
    Select resurvey tasks from the queue.

    Args:
        queue (list[dict]): Queue items.
        work_id (Optional[str]): Specific work id to select.
        select_all (bool): Whether to select all queued resurvey tasks.
        target (str): Target scope.

    Returns:
        list[dict]: Selected task items.
    """
    resurvey_tasks = [item for item in queue if item.get("kind") == _resurvey_kind(target)]
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


def resurvey_components(
    repo_root: Path,
    agent_id: str,
    work_id: Optional[str],
    select_all: bool,
    target: str,
) -> list[str]:
    """
    Resurvey component_contexts and close corresponding resurvey tasks.

    Args:
        repo_root (Path): Repository root.
        agent_id (str): Agent identifier.
        work_id (Optional[str]): Specific work id to process.
        select_all (bool): Whether to process all queued resurvey tasks.
        target (str): Target scope ("prod" or "test").

    Returns:
        list[str]: Work ids closed.
    """
    ensure_feature_enabled(repo_root, "architecture_contexts", "resurvey component contexts")
    ensure_feature_enabled(repo_root, "work_management", "update work queues")
    ensure_work_mode(repo_root, work_id, "resurvey component contexts")
    branch_name = branch_paths.load_current_branch(repo_root)
    data = _load_queue(repo_root, branch_name, agent_id)
    queue = data.get("queue", [])
    if not isinstance(queue, list):
        raise ValueError("Tasks queue must contain a list")

    selected = _select_resurvey_tasks(queue, work_id, select_all, target)
    if not selected:
        raise ValueError("No resurvey_component_contexts tasks found to process")

    for item in selected:
        if item.get("state") != "queued":
            raise ValueError(f"Task not queued: {item.get('work_id')}")

    for item in selected:
        _mark_in_progress(repo_root, item.get("work_id"), owner_id=agent_id)

    context_component_survey.survey_components(
        repo_root,
        agent_id=agent_id,
        work_id=work_id,
        target=target,
        dry_run=False,
    )

    closed: list[str] = []
    for item in selected:
        _close_task(repo_root, item.get("work_id"), owner_id=agent_id, queue_agent_id=agent_id)
        closed.append(item.get("work_id"))

    return closed


def run(payload: dict, ctx: ExecutionContext) -> CommandResult:
    """
    Resurvey component contexts using the ToolCommandAPI contract.

    Args:
        payload (dict): JSON-serializable kwargs payload.
        ctx (ExecutionContext): Execution context for the command.

    Returns:
        CommandResult: Result containing closed work ids.

    Raises:
        None: All errors are captured and returned in the CommandResult.

    Contract:
        - Requires agent_id.
        - Enforces certification, feature flags, and work mode guards.
        - target defaults to "prod".
    """

    command_name = ctx.command_name
    try:
        repo_root_value = optional_string(
            payload, "repo_root", command_name=command_name, default="."
        )
        repo_root = Path(repo_root_value or ".").resolve()
        agent_id = require_string(payload, "agent_id", command_name)
        work_id = optional_string(payload, "work_id", command_name=command_name)
        select_all = optional_bool(payload, "select_all", command_name=command_name, default=False)
        target = optional_string(payload, "target", command_name=command_name, default="prod")
    except PayloadError as exc:
        return payload_error_result(command_name, exc)

    if target not in ("prod", "test"):
        return payload_error_result(
            command_name,
            PayloadError(
                code="payload_value_error",
                details={
                    "command_name": command_name,
                    "field": "target",
                    "expected": "prod or test",
                    "actual": target,
                },
            ),
        )

    try:
        ensure_certified(repo_root, agent_id)
        ensure_feature_enabled(repo_root, "architecture_contexts", "resurvey component contexts")
        closed = resurvey_components(
            repo_root=repo_root,
            agent_id=agent_id,
            work_id=work_id,
            select_all=bool(select_all),
            target=target,
        )
        return ok_result(output={"closed_work_ids": closed})
    except Exception as exc:
        return exception_result(command_name, exc)


def main() -> None:
    """
    CLI entrypoint for component resurvey tasks.

    Returns:
        None: Exits with status 1 on command failure.

    Raises:
        SystemExit: When the command returns a non-ok result.
    """
    parser = argparse.ArgumentParser(description="Resurvey component_contexts from queued tasks")
    parser.add_argument("--repo-root", default=".", help="Repo root path")
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument("--work-id", default=None, help="Specific resurvey work id")
    parser.add_argument("--all", action="store_true", help="Process all queued resurvey tasks")
    parser.add_argument("--target", choices=["prod", "test"], default="prod", help="Target scope")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    payload = {
        "repo_root": args.repo_root,
        "agent_id": args.agent_id,
        "work_id": args.work_id,
        "select_all": args.all,
        "target": args.target,
    }
    context = ExecutionContext(
        command_name="context_component_resurvey",
        agent_id=args.agent_id,
        work_id=args.work_id,
        correlation_id=None,
    )
    result = run(payload, context)
    if result.status != "ok":
        logger.error("context_component_resurvey failed: %s", result.errors)
        raise SystemExit(1)
    closed = result.output.get("closed_work_ids", [])
    logger.info("resurveyed component contexts: closed=%s", ",".join(closed))


if __name__ == "__main__":
    main()
